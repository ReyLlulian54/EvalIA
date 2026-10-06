"""Lectura JSONL y validación mecánica del contrato autoritativo."""

import json
from collections import Counter
from importlib import resources
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from evalia.normalization import normalize_skill


def _schema_validator() -> Draft202012Validator:
    packaged = resources.files("evalia").joinpath("schemas/evalia-case.schema.json")
    # El wheel incluye el esquema original. Esta ruta cubre la instalación editable.
    schema_file = (
        packaged
        if packaged.is_file()
        else Path(__file__).resolve().parents[2] / ("schemas/evalia-case.schema.json")
    )
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _span_issues(text: str, span: dict, label: str) -> list[str]:
    start, end = span["start"], span["end"]
    if not 0 <= start < end <= len(text):
        return [f"{label}: rango inválido; se requiere 0 ≤ start < end ≤ {len(text)}"]
    if text[start:end] != span["quote"]:
        return [f"{label}: cita no coincide con text[start:end]"]
    return []


def _case_issues(case: dict, label: str) -> list[str]:
    text = case["text"]
    evidence = case["evidence"]
    issues: list[str] = []

    if not text.strip():
        issues.append(f"{label}: text: el texto contiene solo espacios")

    for field in ("closing_date", "modality", "student_required"):
        span = evidence[field]
        if span is not None:
            issues.extend(_span_issues(text, span, f"{label}: evidence.{field}"))

    expected_skills = Counter(case["expected"]["skills"])
    cited_skills = Counter(span["skill"] for span in evidence["skills"])
    for index, skill in enumerate(case["expected"]["skills"]):
        try:
            canonical = normalize_skill(skill)
        except ValueError:
            issues.append(f"{label}: expected.skills.{index}: habilidad vacía")
        else:
            if canonical != skill:
                issues.append(
                    f"{label}: expected.skills.{index}: valor no canónico; usar {canonical!r}"
                )
    if cited_skills != expected_skills:
        missing = sorted((expected_skills - cited_skills).elements())
        surplus = sorted((cited_skills - expected_skills).elements())
        issues.append(
            f"{label}: evidence.skills: correspondencia 1:1 incumplida; "
            f"faltan citas para {missing}; sobran citas para {surplus}"
        )

    for index, span in enumerate(evidence["skills"]):
        issues.extend(_span_issues(text, span, f"{label}: evidence.skills.{index}"))

    return issues


def validate_jsonl(path: Path) -> tuple[int, list[str]]:
    """Devuelve número de casos y errores estructurales y mecánicos legibles."""
    validator = _schema_validator()
    count = 0
    issues: list[str] = []
    seen_ids: dict[str, int] = {}
    seen_texts: dict[str, int] = {}

    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                issues.append(f"línea {line_number}: línea vacía; se esperaba un objeto JSON")
                continue

            count += 1
            try:
                case = json.loads(raw)
            except json.JSONDecodeError as error:
                issues.append(f"línea {line_number}: JSON inválido: {error.msg}")
                continue

            case_id = case.get("id") if isinstance(case, dict) else None
            label = (
                f"línea {line_number} (caso {case_id})"
                if isinstance(case_id, str)
                else (f"línea {line_number}")
            )
            errors = sorted(
                validator.iter_errors(case),
                key=lambda error: (list(map(str, error.path)), error.message),
            )
            for error in errors:
                field = ".".join(map(str, error.path)) or "$"
                issues.append(f"{label}: {field}: {error.message}")
            if errors:
                continue

            first_id_line = seen_ids.setdefault(case["id"], line_number)
            if first_id_line != line_number:
                issues.append(f"{label}: id: repetido; aparece primero en línea {first_id_line}")

            first_text_line = seen_texts.setdefault(case["text"], line_number)
            if first_text_line != line_number:
                issues.append(
                    f"{label}: text: repetido; aparece primero en línea {first_text_line}"
                )

            issues.extend(_case_issues(case, label))

    if count == 0 and not issues:
        issues.append("Archivo JSONL vacío: se esperaba al menos un caso")
    return count, issues
