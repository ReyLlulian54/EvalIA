"""Reglas públicas y deterministas de normalización."""

import json
from pathlib import Path

import pytest

from evalia.normalization import (
    DATE_RULES_VERSION,
    normalize_date,
    normalize_skill,
    normalize_skills,
    skill_vocabulary_version,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-11-15", "2026-11-15"),
        ("5 de diciembre de 2026", "2026-12-05"),
        (" 05 DE NOVIEMBRE DE 2026 ", "2026-11-05"),
        ("29/02/2028", "2028-02-29"),
        ("1 de setiembre de 2027", "2027-09-01"),
    ],
)
def test_normalize_explicit_dates(raw: str, expected: str) -> None:
    assert normalize_date(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "15 de noviembre", "15/11"])
def test_missing_year_or_value_remains_unknown(raw: str | None) -> None:
    assert normalize_date(raw) is None


@pytest.mark.parametrize(
    "raw", ["2026-02-29", "31/04/2026", "31/04", "15 de foo de 2026", "01-02-2026"]
)
def test_impossible_or_unrecognized_dates_fail(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_date(raw)


def test_date_normalization_rejects_boolean_input() -> None:
    with pytest.raises(TypeError):
        normalize_date(False)


def test_skill_vocabulary_is_versioned_and_conservative() -> None:
    assert DATE_RULES_VERSION == "1.0.0"
    assert skill_vocabulary_version() == "1.0.0"
    assert normalize_skill(" Python  3 ") == "Python"
    assert normalize_skill("PYTHON3") == "Python"
    assert normalize_skill("sql") == "SQL"
    assert normalize_skill("git") == "Git"
    assert normalize_skill("Machine Learning") == "Machine Learning"
    assert normalize_skill("IA") == "IA"


def test_skill_list_normalizes_and_deduplicates_in_original_order() -> None:
    assert normalize_skills(["sql", "Python 3", "SQL", " Git ", "python"]) == [
        "SQL",
        "Python",
        "Git",
    ]


def test_empty_or_invalid_skill_is_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_skill("  ")
    with pytest.raises(TypeError):
        normalize_skill(None)
    with pytest.raises(TypeError):
        normalize_skills("Python 3")


def test_seed_expected_values_are_already_canonical() -> None:
    for raw_line in (ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines():
        case = json.loads(raw_line)
        expected = case["expected"]
        assert normalize_date(expected["closing_date"]) == expected["closing_date"]
        assert normalize_skills(expected["skills"]) == expected["skills"]
