"""Comprueba los diez casos de arranque; no es la futura CLI de validación."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_span(text, span, label):
    require(0 <= span["start"] < span["end"] <= len(text), f"{label}: límites inválidos")
    require(text[span["start"]:span["end"]] == span["quote"], f"{label}: cita no coincide")


def main():
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "schemas/evalia-case.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    raw = (root / "datasets/seed.jsonl").read_text(encoding="utf-8")
    lines = raw.splitlines()
    require(len(lines) == 10, "Se esperan diez líneas JSONL, sin líneas vacías")
    cases = [json.loads(line) for line in lines]
    require(len({case["id"] for case in cases}) == 10, "Identificadores repetidos")
    require(len({case["text"] for case in cases}) == 10, "Textos repetidos")
    evidence_count = 0

    for case in cases:
        validator.validate(case)
        case_id, text = case["id"], case["text"]
        require(bool(text.strip()), f"{case_id}: texto vacío")
        require(case["split"] == "seed", f"{case_id}: no pertenece a seed")
        require(case.get("source_url") is None, f"{case_id}: fuente externa inesperada")
        require(case["source_license"] == "LicenseRef-EvalIA-Original", f"{case_id}: procedencia inesperada")
        require(case["redistribution_allowed"] is True, f"{case_id}: publicación no permitida")
        expected, evidence = case["expected"], case["evidence"]

        for field in ("closing_date", "modality", "student_required"):
            span = evidence[field]
            if span is not None:
                check_span(text, span, f"{case_id}.{field}")
                evidence_count += 1

        skills = [span["skill"] for span in evidence["skills"]]
        require(len(skills) == len(set(skills)), f"{case_id}: evidencia de habilidad repetida")
        require(set(skills) == set(expected["skills"]), f"{case_id}: habilidades y citas distintas")
        for span in evidence["skills"]:
            check_span(text, span, f"{case_id}.skills.{span['skill']}")
            evidence_count += 1

    dates = Counter(case["expected"]["closing_date"] is None for case in cases)
    students = Counter(case["expected"]["student_required"] for case in cases)
    statuses = Counter(case["review_status"] for case in cases)
    require(dates[True] >= 2, "Faltan casos sin fecha determinable")
    require(students[None] >= 1 and students[False] >= 1, "Faltan ausencias o negaciones de requisito")
    require(statuses["review_required"] >= 1, "Falta el caso contradictorio pendiente")
    require(any("👩‍💻" in case["text"] and "\n" in case["text"] for case in cases), "Falta el caso Unicode multilínea")

    print(f"Seed conforme: {len(cases)} casos; {evidence_count} citas exactas; IDs y textos únicos.")
    print(f"Fecha nula: {dates[True]}; estudiante true/false/null: {students[True]}/{students[False]}/{students[None]}.")
    print(f"Revisión: {dict(statuses)}. La conformidad estructural no acredita revisión humana.")
    print(f"SHA-256 del JSONL UTF-8 con saltos LF: {hashlib.sha256(raw.encode('utf-8')).hexdigest()}")


if __name__ == "__main__":
    main()
