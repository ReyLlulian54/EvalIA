"""Verifica el contrato 0.1; no reemplaza el futuro validador de conjuntos."""

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

repository_root = Path(__file__).resolve().parents[1]
schema = json.loads((repository_root / "schemas/evalia-case.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema, format_checker=FormatChecker())

empty = {
    "schema_version": "0.1.0",
    "id": "fixture-001",
    "text": "Este texto ficticio no describe requisitos.",
    "source_license": "LicenseRef-Verification-Only",
    "redistribution_allowed": False,
    "split": "seed",
    "review_status": "draft",
    "expected": {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    },
    "evidence": {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    },
}


def span(text, quote):
    start = text.index(quote)
    return {"quote": quote, "start": start, "end": start + len(quote)}


full = copy.deepcopy(empty)
full["text"] = "📌 Cierre: 15 de noviembre de 2026. Modalidad híbrida. Se exige Python 3. No es necesario ser estudiante."
full["expected"] = {
    "closing_date": "2026-11-15",
    "modality": "hibrida",
    "skills": ["Python"],
    "student_required": False,
}
full["evidence"] = {
    "closing_date": span(full["text"], "Cierre: 15 de noviembre de 2026"),
    "modality": span(full["text"], "Modalidad híbrida"),
    "skills": [{"skill": "Python", **span(full["text"], "Se exige Python 3")}],
    "student_required": span(full["text"], "No es necesario ser estudiante"),
}
nullable_source = copy.deepcopy(empty)
nullable_source["source_url"] = None
conflict = copy.deepcopy(empty)
conflict["review_status"] = "review_required"
conflict["review_notes"] = "Dos fechas incompatibles; revisar antes de puntuar."

valid = [empty, full, nullable_source, conflict]
for case in valid:
    validator.validate(case)

invalid = []


def add_bad(label, source, mutate):
    case = copy.deepcopy(source)
    mutate(case)
    invalid.append((label, case))


add_bad("fecha imposible", full, lambda c: c["expected"].update(closing_date="2026-13-32"))
add_bad("fecha sin año", full, lambda c: c["expected"].update(closing_date="15 de noviembre"))
add_bad("booleano como texto", full, lambda c: c["expected"].update(student_required="false"))
add_bad("modalidad no normalizada", full, lambda c: c["expected"].update(modality="híbrida"))
add_bad("clave desconocida", empty, lambda c: c.update(unexpected=True))
add_bad("versión desconocida", empty, lambda c: c.update(schema_version="9.0.0"))
add_bad("habilidad repetida", full, lambda c: c["expected"].update(skills=["Python", "Python"]))
add_bad("valor conocido sin cita", full, lambda c: c["evidence"].update(student_required=None))
add_bad("valor nulo con cita", empty, lambda c: c["evidence"].update(closing_date=span(c["text"], "texto")))
add_bad("habilidades sin evidencia", full, lambda c: c["evidence"].update(skills=[]))
add_bad("evidencia de habilidad sin habilidad", empty, lambda c: c["evidence"].update(skills=[{"skill": "Python", **span(c["text"], "texto") }]))
add_bad("conflicto sin notas", empty, lambda c: c.update(review_status="review_required"))
add_bad("posición negativa", full, lambda c: c["evidence"]["modality"].update(start=-1))
add_bad("campo requerido ausente", empty, lambda c: c.pop("review_status"))

for label, case in invalid:
    assert list(validator.iter_errors(case)), f"No se rechazó: {label}"

for value in full["evidence"].values():
    for item in value if isinstance(value, list) else [value]:
        assert full["text"][item["start"]:item["end"]] == item["quote"]

print(f"Contrato Draft 2020-12 válido: {len(valid)} ejemplos aceptados; {len(invalid)} ejemplos inválidos rechazados.")
print("Comprobadas posiciones Unicode del fixture; respaldo semántico y validación entre líneas quedan para sus etapas respectivas.")
