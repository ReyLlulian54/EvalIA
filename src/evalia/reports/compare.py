"""Comparación pareada privada de dos corridas puntuadas y reauditoradas."""

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import ValidationError

from evalia.reports.schema import comparison_validator, score_report_validator
from evalia.reports.score import RunScoreError, _read_artifact, score_run
from evalia.runner.inputs import RunInputError

FIELDS = ("closing_date", "modality", "student_required", "skills_exact")
CATEGORIES = ("improvement", "regression", "correct_tie", "incorrect_tie", "not_comparable")
COMPATIBLE_RUN_KEYS = (
    "provider_id",
    "dataset_sha256",
    "prompt_sha256",
    "request_count",
    "temperature",
    "max_output_tokens",
    "timeout_seconds",
    "max_retries",
)
SOURCE_RUN_KEYS = (
    "run_id",
    "provider_id",
    "model_id",
    "model_digest",
    "source_commit",
    "manifest_sha256",
    "responses_sha256",
    "dataset_sha256",
    "prompt_sha256",
    "request_count",
    "temperature",
    "max_output_tokens",
    "timeout_seconds",
    "max_retries",
)


class RunComparisonError(ValueError):
    """Los insumos no permiten una comparación pareada confiable."""


def _verified_score(dataset: Path, prompt: Path, run_dir: Path) -> tuple[dict, str]:
    raw, saved = _read_artifact(run_dir / "score-report.json")
    try:
        score_report_validator().validate(saved)
    except ValidationError as error:
        raise RunComparisonError(f"Informe de puntuación inválido: {run_dir}") from error
    current = score_run(dataset, prompt, run_dir)
    # created_at es metadato de producción; el resto debe coincidir con la auditoría actual.
    if {k: v for k, v in saved.items() if k != "created_at"} != {
        k: v for k, v in current.items() if k != "created_at"
    }:
        raise RunComparisonError(f"Informe de puntuación desactualizado o alterado: {run_dir}")
    return saved, hashlib.sha256(raw).hexdigest()


def _category(base: dict, candidate: dict, field: str) -> str:
    if base["outcome"] != "scored" or candidate["outcome"] != "scored":
        return "not_comparable"
    base_correct = base["field_correct"][field]
    candidate_correct = candidate["field_correct"][field]
    if not base_correct and candidate_correct:
        return "improvement"
    if base_correct and not candidate_correct:
        return "regression"
    return "correct_tie" if base_correct else "incorrect_tie"


def compare_runs(dataset: Path, prompt: Path, base_dir: Path, candidate_dir: Path) -> dict:
    """Reaudita ambos reportes y conserva la dirección base → candidata."""
    try:
        base, base_hash = _verified_score(dataset, prompt, base_dir)
        candidate, candidate_hash = _verified_score(dataset, prompt, candidate_dir)
    except (RunScoreError, RunInputError) as error:
        raise RunComparisonError(f"Auditoría de entrada fallida: {error}") from error
    for key in COMPATIBLE_RUN_KEYS:
        if base["run"][key] != candidate["run"][key]:
            raise RunComparisonError(f"Corridas incompatibles: {key}")
    if base["run"]["run_id"] == candidate["run"]["run_id"]:
        raise RunComparisonError("La base y la candidata deben ser corridas distintas")
    base_ids = [(case["case_id"], case["split"]) for case in base["cases"]]
    candidate_ids = [(case["case_id"], case["split"]) for case in candidate["cases"]]
    if base_ids != candidate_ids or len(base_ids) != len(set(base_ids)):
        raise RunComparisonError("IDs, partición u orden de casos incompatibles")
    if len(base_ids) != base["run"]["request_count"]:
        raise RunComparisonError("El reporte no contiene todos los casos solicitados")

    cases = []
    for left, right in zip(base["cases"], candidate["cases"], strict=True):
        cases.append(
            {
                "case_id": left["case_id"],
                "split": left["split"],
                "base_outcome": {"status": left["outcome"], "error_code": left.get("error_code")},
                "candidate_outcome": {
                    "status": right["outcome"],
                    "error_code": right.get("error_code"),
                },
                "fields": {field: _category(left, right, field) for field in FIELDS},
            }
        )

    splits = {}
    for split in ("dev", "test"):
        left = base["splits"][split]
        right = candidate["splits"][split]
        selected = [case for case in cases if case["split"] == split]
        if (
            left["eligible_count"] != right["eligible_count"]
            or len(selected) != left["eligible_count"]
        ):
            raise RunComparisonError(f"Denominador incompatible en {split}")
        fields = {
            field: {
                category: {
                    "count": len(
                        ids := [c["case_id"] for c in selected if c["fields"][field] == category]
                    ),
                    "case_ids": ids,
                }
                for category in CATEGORIES
            }
            for field in FIELDS
        }
        coverage_keys = (
            "scored_count",
            "provider_error_count",
            "internal_error_count",
            "format_error_count",
        )
        splits[split] = {
            "eligible_count": len(selected),
            "coverage": {
                "base": {key: left[key] for key in coverage_keys},
                "candidate": {key: right[key] for key in coverage_keys},
            },
            "fields": fields,
            "skills_counts": {"base": left["skills_counts"], "candidate": right["skills_counts"]},
            "telemetry": {
                "base": left["telemetry"],
                "candidate": right["telemetry"],
                "interpretation": "descriptive_only_load_and_gpu_conditions_differ",
            },
        }
    report = {
        "schema_version": comparison_validator().schema["properties"]["schema_version"]["const"],
        "created_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "direction": "base_to_candidate",
        "base": {
            "score_report_sha256": base_hash,
            "run": {k: base["run"][k] for k in SOURCE_RUN_KEYS},
        },
        "candidate": {
            "score_report_sha256": candidate_hash,
            "run": {k: candidate["run"][k] for k in SOURCE_RUN_KEYS},
        },
        "evidence_literal": base["evidence_literal"],
        "splits": splits,
        "cases": cases,
    }
    comparison_validator().validate(report)
    return report


def write_comparison(path: Path, report: dict) -> Path:
    """Crea una salida privada sin reemplazar artefactos existentes."""
    comparison_validator().validate(report)
    created = False
    try:
        stream = path.open("x", encoding="utf-8", newline="\n")
        created = True
        with stream:
            stream.write(
                json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
                + "\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        if created:
            path.unlink(missing_ok=True)
        raise
    return path
