"""Criterios de aceptación de la línea base sin IA, definidos antes de implementarla."""

import json
from pathlib import Path

from evalia.graders.baseline import BASELINE_VERSION, baseline_prediction
from evalia.graders.dataset import evaluate_dataset
from evalia.validation import evidence_validator, extraction_validator

SEED = Path(__file__).resolve().parents[2] / "datasets/seed.jsonl"


def assert_literal_evidence(text: str, evidence: dict) -> None:
    spans = [value for key, value in evidence.items() if key != "skills" and value is not None]
    spans.extend(evidence["skills"])
    for span in spans:
        assert text[span["start"] : span["end"]] == span["quote"]


def test_extracts_explicit_fields_and_normalizes_known_skills() -> None:
    text = (
        "📌 Postula hasta el 5 de diciembre de 2026. Modalidad: híbrida. "
        "Se exige Python 3 y sql. No es necesario ser estudiante."
    )
    result = baseline_prediction("ejemplo-1", text)

    assert BASELINE_VERSION
    assert result["case_id"] == "ejemplo-1"
    assert result["extraction"] == {
        "closing_date": "2026-12-05",
        "modality": "hibrida",
        "skills": ["Python", "SQL"],
        "student_required": False,
    }
    extraction_validator().validate(result["extraction"])
    evidence_validator().validate(result["evidence"])
    assert_literal_evidence(text, result["evidence"])
    assert "No es necesario" in result["evidence"]["student_required"]["quote"]


def test_ignores_start_date_recommended_skills_and_implicit_modality() -> None:
    text = (
        "Publicación: 02 de octubre de 2026. Inicio: 01 de marzo de 2027. "
        "Git es deseable. Oficina de contacto en Santiago. Personas jóvenes pueden participar."
    )
    result = baseline_prediction("ejemplo-2", text)

    assert result["extraction"] == {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    }
    assert result["evidence"] == {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    }


def test_negated_skill_requirement_does_not_become_mandatory() -> None:
    text = "No se exige Python. Se requiere Git para el puesto."
    result = baseline_prediction("ejemplo-2b", text)
    assert result["extraction"]["skills"] == ["Git"]
    assert result["evidence"]["skills"][0]["quote"] == "Se requiere Git para el puesto"


def test_conflicting_dates_and_modalities_abstain() -> None:
    text = (
        "El plazo de postulación cierra el 10 de enero de 2027. "
        "El plazo de postulación cierra el 12 de enero de 2027. "
        "Modalidad remota o presencial."
    )
    result = baseline_prediction("ejemplo-3", text)
    assert result["extraction"]["closing_date"] is None
    assert result["extraction"]["modality"] is None
    assert result["evidence"]["closing_date"] is None
    assert result["evidence"]["modality"] is None


def test_explicit_extension_replaces_old_deadline() -> None:
    text = (
        "El plazo original para postular era el 10 de diciembre de 2026. "
        "Actualización: se amplía el plazo de postulaciones hasta el 20 de diciembre de 2026."
    )
    result = baseline_prediction("ejemplo-4", text)
    assert result["extraction"]["closing_date"] == "2026-12-20"
    assert "se amplía" in result["evidence"]["closing_date"]["quote"]
    assert_literal_evidence(text, result["evidence"])


def test_seed_predictions_are_structurally_valid_and_evaluable() -> None:
    cases = [json.loads(line) for line in SEED.read_text(encoding="utf-8").splitlines()]
    predictions = [
        baseline_prediction(case["id"], case["text"])
        for case in cases
        if case["review_status"] == "reviewed"
    ]
    report = evaluate_dataset(cases, predictions)

    assert report.metric("coverage").ratio.denominator == 9
    assert report.metric("coverage").ratio.numerator == 9
    assert report.format_errors == ()
    assert [item.case_id for item in report.excluded] == ["seed-008"]
    for case, prediction in zip(
        (c for c in cases if c["review_status"] == "reviewed"), predictions, strict=True
    ):
        assert_literal_evidence(case["text"], prediction["evidence"])
