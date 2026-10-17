"""Construye un candidato público desde datos reauditorados y permisos revisados."""

import hashlib
import json
import os
import statistics
from datetime import UTC, datetime
from pathlib import Path

from jsonschema import ValidationError

from evalia.graders.core import grade_case
from evalia.reports.compare import CATEGORIES, FIELDS, compare_runs
from evalia.reports.schema import (
    comparison_validator,
    public_report_validator,
    publication_approval_validator,
)
from evalia.reports.score import _prediction, _read_artifact, _read_records
from evalia.runner.inputs import load_reviewed_cases

EXTRACTION_FIELDS = ("closing_date", "modality", "skills", "student_required")
PRIVATE_OUTPUT_DIRS = ("work", "runs", "artifacts/private", "results/private")


class PublicExportError(ValueError):
    """La selección no cumple las puertas de publicación."""


def _validated_document(path: Path, validator, label: str) -> tuple[bytes, dict]:
    raw, document = _read_artifact(path)
    try:
        validator.validate(document)
    except ValidationError as error:
        raise PublicExportError(f"{label}: no cumple el contrato") from error
    return raw, document


def _projection(extraction: dict) -> dict:
    return {field: extraction[field] for field in EXTRACTION_FIELDS}


def _permission_cases(approval: dict, cases: list[dict]) -> set[str]:
    by_id = {case["id"]: case for case in cases}
    approved_ids: set[str] = set()
    for permission in approval["cases"]:
        case_id = permission["case_id"]
        if case_id in approved_ids:
            raise PublicExportError(f"Permiso duplicado: {case_id}")
        case = by_id.get(case_id)
        if case is None:
            raise PublicExportError(f"Caso sin correspondencia en la corrida: {case_id}")
        if case["review_status"] != "reviewed" or case["redistribution_allowed"] is not True:
            raise PublicExportError(f"Caso sin autorización de redistribución: {case_id}")
        if permission["source_license"] != case["source_license"]:
            raise PublicExportError(f"Licencia de origen distinta: {case_id}")
        if permission["basis"] == "original_created_for_project" and (
            case["source_license"] != "LicenseRef-EvalIA-Original"
            or case.get("source_url") is not None
        ):
            raise PublicExportError(f"Base de permiso incompatible: {case_id}")
        if (
            permission["basis"] == "third_party_permission_verified"
            and case["source_license"] == "LicenseRef-EvalIA-Original"
        ):
            raise PublicExportError(f"Base de permiso incompatible: {case_id}")
        approved_ids.add(case_id)
    return approved_ids


def _side(case: dict, compared: dict, record: dict) -> tuple[dict, dict[str, int]]:
    outcome = compared["status"]
    prediction = None
    counts = {"tp": 0, "fp": 0, "fn": 0}
    if outcome == "scored":
        parsed, error = _prediction(record["raw_text"])
        if error is not None or parsed is None:
            raise PublicExportError(f"Predicción no puntuable en {case['id']}")
        prediction = _projection(parsed)
        grade = grade_case(case, parsed)
        counts = {"tp": grade.skills_tp, "fp": grade.skills_fp, "fn": grade.skills_fn}
    return {
        "status": outcome,
        "error_code": compared["error_code"],
        "prediction": prediction,
        "elapsed_ms": record["elapsed_ms"],
    }, counts


def _summary(selected: list[dict], split: str, side_counts: dict[str, dict[str, dict]]) -> dict:
    rows = [case for case in selected if case["split"] == split]
    fields = {
        field: {
            category: sum(row["fields"][field] == category for row in rows)
            for category in CATEGORIES
        }
        for field in FIELDS
    }
    result = {"selected_count": len(rows), "fields": fields}
    for side in ("base", "candidate"):
        statuses = [row[side]["status"] for row in rows]
        elapsed = [row[side]["elapsed_ms"] for row in rows]
        counts = {name: 0 for name in ("tp", "fp", "fn")}
        for row in rows:
            for name, value in side_counts[row["case_id"]][side].items():
                counts[name] += value
        result[side] = {
            "scored_count": statuses.count("scored"),
            "provider_error_count": statuses.count("provider_error"),
            "internal_error_count": statuses.count("internal_error"),
            "format_error_count": statuses.count("format_error"),
            "skills_counts": counts,
            "elapsed_ms": {
                "observations": len(elapsed),
                "median": statistics.median(elapsed) if elapsed else None,
            },
        }
    return result


def export_public_candidate(
    dataset: Path,
    prompt: Path,
    base_run: Path,
    candidate_run: Path,
    comparison_path: Path,
    approval_path: Path,
) -> dict:
    """Reaudita fuentes y crea solo campos permitidos para casos con permiso revisado."""
    comparison_raw, comparison = _validated_document(
        comparison_path, comparison_validator(), "Comparación"
    )
    current = compare_runs(dataset, prompt, base_run, candidate_run)
    if {k: v for k, v in comparison.items() if k != "created_at"} != {
        k: v for k, v in current.items() if k != "created_at"
    }:
        raise PublicExportError("Comparación privada desactualizada o alterada")
    comparison_hash = hashlib.sha256(comparison_raw).hexdigest()
    approval_raw, approval = _validated_document(
        approval_path, publication_approval_validator(), "Revisión de permisos"
    )
    if approval["dataset_sha256"] != comparison["base"]["run"]["dataset_sha256"]:
        raise PublicExportError("La revisión de permisos corresponde a otro conjunto")
    if approval["comparison_sha256"] != comparison_hash:
        raise PublicExportError("La revisión de permisos corresponde a otra comparación")
    cases, dataset_hash = load_reviewed_cases(dataset, comparison["base"]["run"]["request_count"])
    if dataset_hash != approval["dataset_sha256"]:
        raise PublicExportError("El conjunto cambió desde la revisión de permisos")
    approved_ids = _permission_cases(approval, cases)
    records = {}
    for side, run_dir in (("base", base_run), ("candidate", candidate_run)):
        raw, rows = _read_records(run_dir / "responses.jsonl")
        if hashlib.sha256(raw).hexdigest() != comparison[side]["run"]["responses_sha256"]:
            raise PublicExportError(f"Los registros {side} cambiaron después de la auditoría")
        records[side] = {record["case_id"]: record for record in rows}
    compared = {row["case_id"]: row for row in comparison["cases"]}
    public_cases = []
    side_counts = {}
    for case in cases:
        case_id = case["id"]
        if case_id not in approved_ids:
            continue
        pair = compared[case_id]
        output = {
            "case_id": case_id,
            "split": case["split"],
            "expected": _projection(case["expected"]),
            "fields": {field: pair["fields"][field] for field in FIELDS},
        }
        counts_by_side = {}
        for side in ("base", "candidate"):
            output[side], counts_by_side[side] = _side(
                case, pair[f"{side}_outcome"], records[side][case_id]
            )
        side_counts[case_id] = counts_by_side
        public_cases.append(output)
    report = {
        "schema_version": public_report_validator().schema["properties"]["schema_version"]["const"],
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "publication_review": "pending_artifact_review",
        "provenance": {
            "dataset_sha256": dataset_hash,
            "prompt_sha256": comparison["base"]["run"]["prompt_sha256"],
            "comparison_sha256": comparison_hash,
            "approval_sha256": hashlib.sha256(approval_raw).hexdigest(),
            **{
                side: {
                    key: comparison[side]["run"][key]
                    for key in ("run_id", "model_id", "model_digest", "source_commit")
                }
                | {"score_report_sha256": comparison[side]["score_report_sha256"]}
                for side in ("base", "candidate")
            },
        },
        "limitations": {
            "dataset": "selected_cases_only",
            "evidence_literal": "not_observed",
            "interpretation": "descriptive_no_winner",
        },
        "splits": {split: _summary(public_cases, split, side_counts) for split in ("dev", "test")},
        "cases": public_cases,
    }
    public_report_validator().validate(report)
    return report


def write_public_candidate(path: Path, report: dict) -> Path:
    """Guarda un candidato solo en rutas privadas del checkout y nunca sobrescribe."""
    public_report_validator().validate(report)
    root = Path(__file__).resolve().parents[3]
    destination = path.resolve()
    if (root / ".git").exists() and destination.is_relative_to(root.resolve()):
        if not any(
            destination.is_relative_to((root / folder).resolve()) for folder in PRIVATE_OUTPUT_DIRS
        ):
            raise PublicExportError(
                "El candidato debe guardarse bajo una ruta privada excluida de Git"
            )
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
