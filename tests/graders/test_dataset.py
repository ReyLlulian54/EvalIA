"""Criterios de aceptación de la agregación, con predicciones sintéticas."""

import copy
import json
from pathlib import Path

import pytest

from evalia.graders.core import Ratio
from evalia.graders.dataset import evaluate_dataset

SEED = Path(__file__).resolve().parents[2] / "datasets/seed.jsonl"


def case(case_id: str) -> dict:
    return next(
        item
        for item in map(json.loads, SEED.read_text(encoding="utf-8").splitlines())
        if item["id"] == case_id
    )


def prediction(item: dict) -> dict:
    return {
        "case_id": item["id"],
        "extraction": copy.deepcopy(item["expected"]),
        "evidence": copy.deepcopy(item["evidence"]),
    }


def test_aggregate_counts_failures_and_excludes_unreviewed() -> None:
    first, second, excluded = case("seed-001"), case("seed-003"), case("seed-008")
    wrong = prediction(second)
    wrong["extraction"]["student_required"] = None  # referencia: false
    wrong["evidence"]["student_required"] = None
    report = evaluate_dataset([first, second, excluded], [prediction(first), wrong])

    assert report.metric("coverage").ratio == Ratio(2, 2)
    assert report.metric("student_required").ratio == Ratio(1, 2)
    assert report.metric("student_required").failed_case_ids == ("seed-003",)
    assert report.metric("skills_exact").ratio == Ratio(2, 2)
    assert report.metric("skills_f1").ratio == Ratio(6, 6)
    assert report.excluded[0].case_id == "seed-008"
    assert report.format_errors == ()


def test_missing_and_invalid_predictions_are_format_errors_not_content_scores() -> None:
    first, second = case("seed-001"), case("seed-004")
    invalid = prediction(first)
    invalid["extraction"]["modality"] = "virtual"
    report = evaluate_dataset([first, second], [invalid])

    assert report.metric("coverage").ratio == Ratio(0, 2)
    assert report.metric("closing_date").ratio == Ratio(0, 0)
    assert report.metric("closing_date").ratio.value is None
    assert {(error.case_id, error.field) for error in report.format_errors} == {
        ("seed-001", "extraction"),
        ("seed-004", "prediction"),
    }


def test_abstention_only_counts_null_reference_scalars() -> None:
    unknown, negative = case("seed-004"), case("seed-003")
    first, second = prediction(unknown), prediction(negative)
    first["extraction"]["student_required"] = False
    first["evidence"]["student_required"] = unknown["evidence"]["modality"]
    report = evaluate_dataset([unknown, negative], [first, second])

    assert report.metric("abstention.student_required").ratio == Ratio(0, 1)
    assert report.metric("abstention.student_required").failed_case_ids == ("seed-004",)
    assert report.metric("student_required").ratio == Ratio(1, 2)
    assert report.metric("abstention.modality").ratio.value is None


def test_evidence_checks_literal_unicode_and_reports_failed_case() -> None:
    item = case("seed-001")
    result = prediction(item)
    result["evidence"]["skills"][0]["quote"] = "cita incorrecta"
    report = evaluate_dataset([item], [result])

    assert report.metric("evidence_literal").ratio == Ratio(4, 5)
    assert report.metric("evidence_literal").failed_case_ids == (item["id"],)
    assert report.metric("skills_exact").ratio == Ratio(1, 1)
    assert report.format_errors == ()


def test_missing_evidence_keeps_content_score_but_reports_format_failure() -> None:
    item = case("seed-001")
    result = prediction(item)
    result.pop("evidence")
    report = evaluate_dataset([item], [result])

    assert report.metric("coverage").ratio == Ratio(1, 1)
    assert report.metric("closing_date").ratio == Ratio(1, 1)
    assert report.metric("evidence_literal").ratio == Ratio(0, 5)
    assert [(error.case_id, error.field) for error in report.format_errors] == [
        (item["id"], "evidence")
    ]


def test_skill_citations_must_correspond_to_predicted_skills() -> None:
    item = case("seed-001")
    result = prediction(item)
    result["evidence"]["skills"][0]["skill"] = "Docker"
    report = evaluate_dataset([item], [result])

    assert report.metric("skills_exact").ratio == Ratio(1, 1)
    assert report.metric("evidence_literal").ratio == Ratio(0, 5)
    assert report.format_errors[0].field == "evidence"


def test_skill_metrics_use_pooled_counts_across_cases() -> None:
    first, second = case("seed-001"), case("seed-003")
    first_result, second_result = prediction(first), prediction(second)
    first_result["extraction"]["skills"] = ["Python", "Docker"]
    second_result["extraction"]["skills"] = []
    report = evaluate_dataset([first, second], [first_result, second_result])

    assert report.metric("skills_precision").ratio == Ratio(1, 2)
    assert report.metric("skills_recall").ratio == Ratio(1, 3)
    assert report.metric("skills_f1").ratio == Ratio(2, 5)
    assert report.metric("skills_f1").failed_case_ids == ("seed-001", "seed-003")


def test_no_claimed_evidence_has_not_applicable_ratio() -> None:
    item = case("seed-003")
    result = prediction(item)
    result["extraction"] = {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    }
    result["evidence"] = {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    }
    report = evaluate_dataset([item], [result])
    assert report.metric("evidence_literal").ratio == Ratio(0, 0)
    assert report.metric("evidence_literal").ratio.value is None


def test_duplicate_prediction_ids_are_not_scored() -> None:
    item = case("seed-001")
    report = evaluate_dataset([item], [prediction(item), prediction(item)])
    assert report.metric("coverage").ratio == Ratio(0, 1)
    assert report.format_errors[0].field == "case_id"


def test_invalid_reference_fails_loudly() -> None:
    item = case("seed-001")
    item["evidence"]["closing_date"]["quote"] = "inventada"
    with pytest.raises(ValueError, match="Referencia inválida"):
        evaluate_dataset([item], [prediction(item)])
