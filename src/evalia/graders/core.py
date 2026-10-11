"""Puntaje determinista de una extracción validada frente a un caso revisado."""

from dataclasses import dataclass
from typing import Literal

from evalia.normalization import normalize_skill
from evalia.validation import case_issues, case_validator, extraction_validator


@dataclass(frozen=True)
class Ratio:
    """Conteo auditable; `value=None` si el denominador es cero."""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if not 0 <= self.numerator <= self.denominator:
            raise ValueError("Un ratio exige 0 <= numerator <= denominator")

    @property
    def value(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None


@dataclass(frozen=True)
class CaseGrade:
    """Resultados por campo de un único caso revisado."""

    case_id: str
    closing_date: Ratio
    modality: Ratio
    student_required: Ratio
    skills_exact: Ratio
    skills_tp: int
    skills_fp: int
    skills_fn: int
    skills_precision: Ratio
    skills_recall: Ratio
    skills_f1: Ratio
    failed_fields: tuple[str, ...]


@dataclass(frozen=True)
class ExcludedCase:
    """Caso sin denominadores hasta completar o resolver su revisión."""

    case_id: str
    reason: Literal["draft", "review_required"]


def _require_canonical_skills(skills: list[str], label: str) -> None:
    for skill in skills:
        if normalize_skill(skill) != skill:
            raise ValueError(f"{label}: habilidad no canónica: {skill!r}")


def grade_case(case: dict, prediction: dict) -> CaseGrade | ExcludedCase:
    """Puntúa valores canónicos; no normaliza ni comprueba respaldo semántico."""
    case_validator().validate(case)
    issues = case_issues(case, f"caso {case['id']}")
    if issues:
        raise ValueError("Referencia inválida: " + "; ".join(issues))
    extraction_validator().validate(prediction)

    expected = case["expected"]
    _require_canonical_skills(prediction["skills"], "Predicción")

    status = case["review_status"]
    if status != "reviewed":
        return ExcludedCase(case_id=case["id"], reason=status)

    closing_date = Ratio(int(expected["closing_date"] == prediction["closing_date"]), 1)
    modality = Ratio(int(expected["modality"] == prediction["modality"]), 1)
    student_required = Ratio(int(expected["student_required"] == prediction["student_required"]), 1)

    expected_skills = set(expected["skills"])
    predicted_skills = set(prediction["skills"])
    tp = len(expected_skills & predicted_skills)
    fp = len(predicted_skills - expected_skills)
    fn = len(expected_skills - predicted_skills)
    skills_exact = Ratio(int(expected_skills == predicted_skills), 1)

    failed_fields = tuple(
        field
        for field, result in (
            ("closing_date", closing_date),
            ("modality", modality),
            ("skills", skills_exact),
            ("student_required", student_required),
        )
        if result.numerator == 0
    )

    return CaseGrade(
        case_id=case["id"],
        closing_date=closing_date,
        modality=modality,
        student_required=student_required,
        skills_exact=skills_exact,
        skills_tp=tp,
        skills_fp=fp,
        skills_fn=fn,
        skills_precision=Ratio(tp, tp + fp),
        skills_recall=Ratio(tp, tp + fn),
        skills_f1=Ratio(2 * tp, 2 * tp + fp + fn),
        failed_fields=failed_fields,
    )
