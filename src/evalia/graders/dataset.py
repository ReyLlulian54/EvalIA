"""Agregación auditable de predicciones sintéticas o reales, sin proveedor."""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from jsonschema import ValidationError

from evalia.graders.core import CaseGrade, ExcludedCase, Ratio, grade_case
from evalia.validation import case_issues, case_validator, evidence_validator

SCALAR_FIELDS = ("closing_date", "modality", "student_required")


@dataclass(frozen=True)
class FormatError:
    """Error de entrada que impide puntuar una parte de la predicción."""

    case_id: str | None
    field: str
    message: str


@dataclass(frozen=True)
class Metric:
    """Razón y casos que aportaron fallos a su numerador."""

    ratio: Ratio
    failed_case_ids: tuple[str, ...]


@dataclass(frozen=True)
class DatasetReport:
    """Conteos del conjunto; no contiene resultados calculados por modelos."""

    metrics: dict[str, Metric]
    scored_case_ids: tuple[str, ...]
    excluded: tuple[ExcludedCase, ...]
    format_errors: tuple[FormatError, ...]

    def metric(self, name: str) -> Metric:
        return self.metrics[name]


def _evidence_units(extraction: dict) -> int:
    return sum(extraction[field] is not None for field in SCALAR_FIELDS) + len(extraction["skills"])


def _literal_match(text: str, span: dict) -> bool:
    start, end = span["start"], span["end"]
    return 0 <= start < end <= len(text) and text[start:end] == span["quote"]


def _grade_evidence(
    case: dict, extraction: dict, evidence: object
) -> tuple[Ratio, bool, str | None]:
    """Cuenta citas reclamadas; un error estructural invalida todas las citas."""
    denominator = _evidence_units(extraction)
    try:
        evidence_validator().validate(evidence)
    except ValidationError as error:
        return Ratio(0, denominator), denominator > 0, error.message

    for field in SCALAR_FIELDS:
        if (extraction[field] is None) != (evidence[field] is None):
            return Ratio(0, denominator), denominator > 0, f"{field}: valor y cita no corresponden"
    if Counter(extraction["skills"]) != Counter(span["skill"] for span in evidence["skills"]):
        return Ratio(0, denominator), denominator > 0, "skills: citas sin correspondencia 1:1"

    spans = [evidence[field] for field in SCALAR_FIELDS if extraction[field] is not None]
    spans.extend(evidence["skills"])
    numerator = sum(_literal_match(case["text"], span) for span in spans)
    return Ratio(numerator, denominator), numerator < denominator, None


def _metric(numerator: int, denominator: int, failures: list[str]) -> Metric:
    return Metric(Ratio(numerator, denominator), tuple(failures))


def evaluate_dataset(cases: Iterable[dict], predictions: Iterable[dict]) -> DatasetReport:
    """Puntúa casos revisados por ID; referencia inválida provoca error explícito.

    Cada predicción contiene `case_id`, `extraction` y `evidence`. Los dos últimos
    se derivan de las definiciones del esquema autoritativo. Un fallo de evidencia
    conserva el puntaje de contenido si la extracción es válida.
    """
    references: dict[str, dict] = {}
    validator = case_validator()
    for case in cases:
        validator.validate(case)
        issues = case_issues(case, f"caso {case['id']}")
        if issues:
            raise ValueError("Referencia inválida: " + "; ".join(issues))
        if case["id"] in references:
            raise ValueError(f"Referencia inválida: id duplicado {case['id']!r}")
        references[case["id"]] = case

    records: dict[str, list[dict]] = {}
    errors: list[FormatError] = []
    for record in predictions:
        if not isinstance(record, dict) or not isinstance(record.get("case_id"), str):
            errors.append(FormatError(None, "case_id", "Falta un identificador de caso válido"))
            continue
        case_id = record["case_id"]
        if case_id not in references:
            errors.append(FormatError(case_id, "case_id", "No existe en el conjunto de referencia"))
            continue
        records.setdefault(case_id, []).append(record)

    excluded: list[ExcludedCase] = []
    scored: list[tuple[dict, dict, CaseGrade]] = []
    evidence_results: list[tuple[str, Ratio, bool]] = []
    eligible_ids: list[str] = []

    for case_id, case in references.items():
        if case["review_status"] != "reviewed":
            excluded.append(ExcludedCase(case_id, case["review_status"]))
            continue
        eligible_ids.append(case_id)
        matches = records.get(case_id, [])
        if not matches:
            errors.append(FormatError(case_id, "prediction", "No se recibió predicción"))
            continue
        if len(matches) > 1:
            errors.append(FormatError(case_id, "case_id", "Predicción duplicada"))
            continue

        record = matches[0]
        extraction = record.get("extraction")
        try:
            grade = grade_case(case, extraction)
        except ValidationError as error:
            errors.append(FormatError(case_id, "extraction", error.message))
            continue
        except ValueError as error:
            errors.append(FormatError(case_id, "extraction", str(error)))
            continue
        assert isinstance(grade, CaseGrade)
        scored.append((case, extraction, grade))

        evidence_ratio, failed, problem = _grade_evidence(case, extraction, record.get("evidence"))
        if problem is not None:
            errors.append(FormatError(case_id, "evidence", problem))
        evidence_results.append((case_id, evidence_ratio, failed))

    scored_ids = [grade.case_id for _, _, grade in scored]
    metrics: dict[str, Metric] = {
        "coverage": _metric(
            len(scored),
            len(eligible_ids),
            [case_id for case_id in eligible_ids if case_id not in scored_ids],
        )
    }
    for field in SCALAR_FIELDS:
        metrics[field] = _metric(
            sum(getattr(grade, field).numerator for _, _, grade in scored),
            len(scored),
            [grade.case_id for _, _, grade in scored if field in grade.failed_fields],
        )
        absent = [
            (case, extraction) for case, extraction, _ in scored if case["expected"][field] is None
        ]
        metrics[f"abstention.{field}"] = _metric(
            sum(extraction[field] is None for _, extraction in absent),
            len(absent),
            [case["id"] for case, extraction in absent if extraction[field] is not None],
        )

    metrics["skills_exact"] = _metric(
        sum(grade.skills_exact.numerator for _, _, grade in scored),
        len(scored),
        [grade.case_id for _, _, grade in scored if "skills" in grade.failed_fields],
    )
    tp = sum(grade.skills_tp for _, _, grade in scored)
    fp = sum(grade.skills_fp for _, _, grade in scored)
    fn = sum(grade.skills_fn for _, _, grade in scored)
    metrics["skills_precision"] = _metric(
        tp, tp + fp, [grade.case_id for _, _, grade in scored if grade.skills_fp]
    )
    metrics["skills_recall"] = _metric(
        tp, tp + fn, [grade.case_id for _, _, grade in scored if grade.skills_fn]
    )
    metrics["skills_f1"] = _metric(
        2 * tp,
        2 * tp + fp + fn,
        [grade.case_id for _, _, grade in scored if grade.skills_fp or grade.skills_fn],
    )
    metrics["evidence_literal"] = _metric(
        sum(ratio.numerator for _, ratio, _ in evidence_results),
        sum(ratio.denominator for _, ratio, _ in evidence_results),
        [case_id for case_id, _, failed in evidence_results if failed],
    )
    return DatasetReport(metrics, tuple(scored_ids), tuple(excluded), tuple(errors))
