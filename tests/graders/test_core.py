"""Rúbrica determinista por caso, sin llamadas a modelos."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from evalia.graders.core import CaseGrade, ExcludedCase, Ratio, grade_case

ROOT = Path(__file__).resolve().parents[2]


def seed_case(case_id: str) -> dict:
    lines = (ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines()
    for line in lines:
        case = json.loads(line)
        if case["id"] == case_id:
            return case
    raise ValueError(f"No existe el caso de prueba {case_id}")


def test_exact_prediction_gets_explicit_numerators_and_denominators() -> None:
    case = seed_case("seed-001")

    grade = grade_case(case, copy.deepcopy(case["expected"]))

    assert isinstance(grade, CaseGrade)
    assert grade.closing_date == Ratio(1, 1)
    assert grade.modality == Ratio(1, 1)
    assert grade.student_required == Ratio(1, 1)
    assert grade.skills_exact == Ratio(1, 1)
    assert (grade.skills_tp, grade.skills_fp, grade.skills_fn) == (2, 0, 0)
    assert grade.skills_precision == Ratio(2, 2)
    assert grade.skills_recall == Ratio(2, 2)
    assert grade.skills_f1 == Ratio(4, 4)
    assert grade.failed_fields == ()


def test_wrong_prediction_reports_field_failures_and_skill_counts() -> None:
    case = seed_case("seed-001")
    prediction = {
        "closing_date": None,
        "modality": "presencial",
        "skills": ["Python", "Docker"],
        "student_required": False,
    }

    grade = grade_case(case, prediction)

    assert isinstance(grade, CaseGrade)
    assert grade.closing_date == Ratio(0, 1)
    assert grade.modality == Ratio(0, 1)
    assert grade.student_required == Ratio(0, 1)
    assert grade.skills_exact == Ratio(0, 1)
    assert (grade.skills_tp, grade.skills_fp, grade.skills_fn) == (1, 1, 1)
    assert grade.skills_precision == Ratio(1, 2)
    assert grade.skills_recall == Ratio(1, 2)
    assert grade.skills_f1 == Ratio(2, 4)
    assert set(grade.failed_fields) == {"closing_date", "modality", "skills", "student_required"}


@pytest.mark.parametrize(
    ("case_id", "prediction_value"),
    [("seed-003", None), ("seed-004", False)],
)
def test_false_and_null_are_distinct(case_id: str, prediction_value: bool | None) -> None:
    case = seed_case(case_id)
    prediction = copy.deepcopy(case["expected"])
    prediction["student_required"] = prediction_value

    grade = grade_case(case, prediction)

    assert isinstance(grade, CaseGrade)
    assert grade.student_required == Ratio(0, 1)
    assert "student_required" in grade.failed_fields


def test_empty_skill_sets_are_exact_but_set_metrics_are_not_applicable() -> None:
    case = seed_case("seed-004")

    grade = grade_case(case, copy.deepcopy(case["expected"]))

    assert isinstance(grade, CaseGrade)
    assert grade.skills_exact == Ratio(1, 1)
    assert grade.skills_precision == Ratio(0, 0)
    assert grade.skills_recall == Ratio(0, 0)
    assert grade.skills_f1 == Ratio(0, 0)
    assert grade.skills_precision.value is None


def test_missing_all_skills_has_undefined_precision_and_zero_recall() -> None:
    case = seed_case("seed-001")
    prediction = copy.deepcopy(case["expected"])
    prediction["skills"] = []

    grade = grade_case(case, prediction)

    assert isinstance(grade, CaseGrade)
    assert (grade.skills_tp, grade.skills_fp, grade.skills_fn) == (0, 0, 2)
    assert grade.skills_precision == Ratio(0, 0)
    assert grade.skills_recall == Ratio(0, 2)
    assert grade.skills_f1 == Ratio(0, 2)
    assert grade.skills_exact == Ratio(0, 1)


@pytest.mark.parametrize("status", ["draft", "review_required"])
def test_unreviewed_case_is_excluded_from_scores(status: str) -> None:
    case = seed_case("seed-008" if status == "review_required" else "seed-001")
    case["review_status"] = status
    if status == "draft":
        case.pop("review_notes", None)

    grade = grade_case(case, copy.deepcopy(case["expected"]))

    assert grade == ExcludedCase(case_id=case["id"], reason=status)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda result: result.update(student_required="false"),
        lambda result: result.update(modality="virtual"),
        lambda result: result.pop("closing_date"),
    ],
)
def test_invalid_prediction_is_rejected_before_scoring(mutation) -> None:
    case = seed_case("seed-001")
    prediction = copy.deepcopy(case["expected"])
    mutation(prediction)

    with pytest.raises(ValidationError):
        grade_case(case, prediction)


def test_noncanonical_skill_is_rejected_before_scoring() -> None:
    case = seed_case("seed-001")
    prediction = copy.deepcopy(case["expected"])
    prediction["skills"][0] = "Python 3"

    with pytest.raises(ValueError, match="canónica"):
        grade_case(case, prediction)


def test_invalid_reference_case_is_rejected() -> None:
    case = seed_case("seed-001")
    case.pop("evidence")

    with pytest.raises(ValidationError):
        grade_case(case, copy.deepcopy(case["expected"]))


def test_reference_with_wrong_literal_quote_is_rejected() -> None:
    case = seed_case("seed-001")
    case["evidence"]["closing_date"]["quote"] = "fecha inexistente"

    with pytest.raises(ValueError, match="cita no coincide"):
        grade_case(case, copy.deepcopy(case["expected"]))
