"""Puntuación privada de una corrida, sin alterar las respuestas del modelo."""

import hashlib
import json
import os
import statistics
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from jsonschema import ValidationError

from evalia.graders.core import CaseGrade, Ratio, grade_case
from evalia.reports.schema import score_report_schema_version, score_report_validator
from evalia.runner.core import _digest, _request_data
from evalia.runner.inputs import compose_requests, load_prompt, load_reviewed_cases
from evalia.runner.schema import manifest_validator, record_validator


class RunScoreError(ValueError):
    """Una corrida o sus entradas no superaron la auditoría previa."""


class _DuplicateKey(ValueError):
    pass


class _NonStandardConstant(ValueError):
    pass


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise _NonStandardConstant(value)


def _strict_json(text: str) -> object:
    return json.loads(text, object_pairs_hook=_unique_pairs, parse_constant=_reject_constant)


def _read_artifact(path: Path) -> tuple[bytes, dict]:
    try:
        raw = path.read_bytes()
        document = _strict_json(raw.decode("utf-8"))
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        _DuplicateKey,
        _NonStandardConstant,
    ) as error:
        raise RunScoreError(f"Artefacto inválido: {path.name}") from error
    if not isinstance(document, dict):
        raise RunScoreError(f"Artefacto inválido: {path.name} debe ser un objeto")
    return raw, document


def _read_records(path: Path) -> tuple[bytes, list[dict]]:
    try:
        raw = path.read_bytes()
        lines = raw.decode("utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise RunScoreError("No se pudo leer responses.jsonl como UTF-8") from error
    records: list[dict] = []
    for number, line in enumerate(lines, 1):
        try:
            record = _strict_json(line)
            record_validator().validate(record)
        except (
            json.JSONDecodeError,
            _DuplicateKey,
            _NonStandardConstant,
            ValidationError,
        ) as error:
            raise RunScoreError(f"responses.jsonl: línea {number} inválida") from error
        assert isinstance(record, dict)
        records.append(record)
    return raw, records


def _audit_run(
    dataset_path: Path, prompt_path: Path, run_dir: Path
) -> tuple[dict, list[dict], list[dict], str, str]:
    manifest_raw, manifest = _read_artifact(run_dir / "manifest.json")
    try:
        manifest_validator().validate(manifest)
    except ValidationError as error:
        raise RunScoreError("manifest.json no cumple el contrato") from error
    if manifest["status"] != "completed":
        raise RunScoreError("La corrida no está completada")
    cases, dataset_hash = load_reviewed_cases(dataset_path, manifest["request_count"])
    prompt = load_prompt(prompt_path)
    if manifest["dataset_sha256"] != dataset_hash or manifest["prompt_sha256"] != prompt.sha256:
        raise RunScoreError("Los hashes del conjunto o prompt no coinciden con el manifiesto")
    if (manifest["prompt_id"], manifest["prompt_version"]) != (prompt.prompt_id, prompt.version):
        raise RunScoreError("La identidad o versión del prompt no coincide")
    # Este protocolo solo autorizó puntuar el prompt de 5.3, que no pidió citas.
    if prompt.sha256 != "2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e":
        raise RunScoreError("El prompt no es el fijado para la puntuación 6.b")
    if any(case["split"] not in {"dev", "test"} for case in cases):
        raise RunScoreError("El reporte 6.b solo admite particiones dev y test")
    records_raw, records = _read_records(run_dir / "responses.jsonl")
    expected_ids = [case["id"] for case in cases]
    if not (
        len(cases) == len(records) == manifest["request_count"] == manifest["recorded_count"]
        and [record["case_id"] for record in records] == expected_ids
        and [record["index"] for record in records] == list(range(len(records)))
        and manifest["last_case_id"] == expected_ids[-1]
    ):
        raise RunScoreError("IDs, orden, índices o conteos de la corrida no coinciden")
    successes = sum(record["status"] == "success" for record in records)
    if (manifest["success_count"], manifest["failure_count"]) != (
        successes,
        len(records) - successes,
    ):
        raise RunScoreError("Los conteos de éxito y error del manifiesto no coinciden")
    requests = compose_requests(
        cases,
        prompt,
        model_id=manifest["model_id"],
        temperature=manifest["temperature"],
        max_output_tokens=manifest["max_output_tokens"],
        timeout_seconds=manifest["timeout_seconds"],
    )
    payloads = [_request_data(request) for request in requests]
    if manifest["requests_sha256"] != _digest(payloads):
        raise RunScoreError("El hash del lote de solicitudes no coincide")
    for record, payload in zip(records, payloads, strict=True):
        if record["request_sha256"] != _digest(payload):
            raise RunScoreError(f"Hash de solicitud distinto en {record['case_id']}")
        if record["status"] == "success" and record["reported_model_id"] not in (
            None,
            manifest["model_id"],
        ):
            raise RunScoreError(f"Modelo informado distinto en {record['case_id']}")
    return (
        manifest,
        records,
        cases,
        hashlib.sha256(manifest_raw).hexdigest(),
        hashlib.sha256(records_raw).hexdigest(),
    )


def _prediction(raw_text: str) -> tuple[dict | None, str | None]:
    try:
        document = _strict_json(raw_text)
    except _DuplicateKey:
        return None, "duplicate_key"
    except _NonStandardConstant:
        return None, "nonstandard_constant"
    except json.JSONDecodeError:
        return None, "invalid_json"
    if not isinstance(document, dict):
        return None, "invalid_extraction"
    return document, None


def _ratio(numerator: int, denominator: int, failures: Iterable[str]) -> dict:
    ratio = Ratio(numerator, denominator)
    return {
        "numerator": ratio.numerator,
        "denominator": ratio.denominator,
        "value": ratio.value,
        "failed_case_ids": list(failures),
    }


def _usage(records: list[dict]) -> dict:
    elapsed = [record["elapsed_ms"] for record in records]
    result = {
        "elapsed_ms": {
            "observations": len(elapsed),
            "median": statistics.median(elapsed) if elapsed else None,
        }
    }
    for name in ("prompt_tokens", "completion_tokens"):
        values = [record[name] for record in records if record[name] is not None]
        result[name] = {"observations": len(values), "total": sum(values) if values else None}
    costs = [Decimal(record["cost_usd"]) for record in records if record["cost_usd"] is not None]
    result["cost_usd"] = {
        "observations": len(costs),
        "total": format(sum(costs), "f") if costs else None,
    }
    return result


def _split_report(
    rows: list[tuple[dict, dict, CaseGrade | None]],
    results: list[dict],
    source_records: list[dict],
) -> dict:
    scored = [(case, prediction, grade) for case, prediction, grade in rows if grade is not None]
    grades = [grade for _, _, grade in scored]
    missed_ids = [case["id"] for case, _, grade in rows if grade is None]
    metrics = {"coverage": _ratio(len(scored), len(rows), missed_ids)}
    for field in ("closing_date", "modality", "student_required"):
        metrics[field] = _ratio(
            sum(getattr(grade, field).numerator for grade in grades),
            len(grades),
            (grade.case_id for grade in grades if field in grade.failed_fields),
        )
    metrics["skills_exact"] = _ratio(
        sum(grade.skills_exact.numerator for grade in grades),
        len(grades),
        (grade.case_id for grade in grades if "skills" in grade.failed_fields),
    )
    tp = sum(grade.skills_tp for grade in grades)
    fp = sum(grade.skills_fp for grade in grades)
    fn = sum(grade.skills_fn for grade in grades)
    metrics["skills_precision"] = _ratio(tp, tp + fp, (g.case_id for g in grades if g.skills_fp))
    metrics["skills_recall"] = _ratio(tp, tp + fn, (g.case_id for g in grades if g.skills_fn))
    metrics["skills_f1"] = _ratio(
        2 * tp, 2 * tp + fp + fn, (g.case_id for g in grades if g.skills_fp or g.skills_fn)
    )
    metrics["abstention"] = {}
    for field in ("closing_date", "modality", "student_required"):
        absent = [
            (case, prediction) for case, prediction, _ in scored if case["expected"][field] is None
        ]
        metrics["abstention"][field] = _ratio(
            sum(prediction[field] is None for _, prediction in absent),
            len(absent),
            (case["id"] for case, prediction in absent if prediction[field] is not None),
        )
    outcomes = [result["outcome"] for result in results]
    return {
        "eligible_count": len(rows),
        "scored_count": len(scored),
        "provider_error_count": outcomes.count("provider_error"),
        "internal_error_count": outcomes.count("internal_error"),
        "format_error_count": outcomes.count("format_error"),
        "skills_counts": {"tp": tp, "fp": fp, "fn": fn},
        "metrics": metrics,
        "telemetry": _usage(source_records),
    }


def score_run(dataset_path: Path, prompt_path: Path, run_dir: Path) -> dict:
    """Valida insumos y artefactos antes de calcular un puntaje privado por split."""
    manifest, records, cases, manifest_hash, responses_hash = _audit_run(
        dataset_path, prompt_path, run_dir
    )
    rows_by_split: dict[str, list[tuple[dict, dict, CaseGrade | None]]] = {"dev": [], "test": []}
    results_by_split: dict[str, list[dict]] = {"dev": [], "test": []}
    source_records_by_split: dict[str, list[dict]] = {"dev": [], "test": []}
    results: list[dict] = []
    for case, record in zip(cases, records, strict=True):
        split = case["split"]
        result = {"case_id": case["id"], "split": split}
        prediction: dict = {}
        grade: CaseGrade | None = None
        if record["status"] != "success":
            result.update(outcome=record["status"], error_code=record["error_code"])
        else:
            prediction, error_code = _prediction(record["raw_text"])
            if error_code is None:
                try:
                    grade = grade_case(case, prediction)
                except ValidationError:
                    error_code = "invalid_extraction"
                except ValueError as error:
                    if "habilidad no canónica" not in str(error):
                        raise
                    error_code = "noncanonical_skill"
            if error_code is not None:
                result.update(outcome="format_error", error_code=error_code)
            else:
                assert isinstance(grade, CaseGrade)
                result.update(
                    outcome="scored",
                    field_correct={
                        field: getattr(grade, field).numerator == 1
                        for field in (
                            "closing_date",
                            "modality",
                            "student_required",
                            "skills_exact",
                        )
                    },
                    skills_counts={
                        "tp": grade.skills_tp,
                        "fp": grade.skills_fp,
                        "fn": grade.skills_fn,
                    },
                )
        rows_by_split[split].append((case, prediction or {}, grade))
        results_by_split[split].append(result)
        source_records_by_split[split].append(record)
        results.append(result)
    report = {
        "schema_version": score_report_schema_version(),
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "run": {
            **{
                key: manifest[key]
                for key in (
                    "run_id",
                    "provider_id",
                    "model_id",
                    "model_digest",
                    "source_commit",
                    "dataset_sha256",
                    "prompt_sha256",
                    "request_count",
                    "recorded_count",
                    "success_count",
                    "failure_count",
                    "temperature",
                    "max_output_tokens",
                    "timeout_seconds",
                    "max_retries",
                )
            },
            "manifest_sha256": manifest_hash,
            "responses_sha256": responses_hash,
        },
        "evidence_literal": {
            "status": "not_observed",
            "reason": "prompt_did_not_request_evidence",
        },
        "splits": {
            split: _split_report(
                rows_by_split[split], results_by_split[split], source_records_by_split[split]
            )
            for split in ("dev", "test")
        },
        "cases": results,
    }
    score_report_validator().validate(report)
    return report


def write_score_report(run_dir: Path, report: dict) -> Path:
    """Escribe el informe una sola vez junto a los artefactos privados de la corrida."""
    score_report_validator().validate(report)
    output = run_dir / "score-report.json"
    created = False
    try:
        stream = output.open("x", encoding="utf-8", newline="\n")
        created = True
        with stream:
            stream.write(
                json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
                + "\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        raise
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    return output
