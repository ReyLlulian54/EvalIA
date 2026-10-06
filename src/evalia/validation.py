"""Lectura JSONL y validación estructural del contrato autoritativo."""

import json
from importlib import resources
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def _schema_validator() -> Draft202012Validator:
    packaged = resources.files("evalia").joinpath("schemas/evalia-case.schema.json")
    # El wheel incluye el esquema original. Esta ruta cubre la instalación editable.
    schema_file = packaged if packaged.is_file() else Path(__file__).resolve().parents[2] / (
        "schemas/evalia-case.schema.json"
    )
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_jsonl(path: Path) -> tuple[int, list[str]]:
    """Devuelve número de líneas con casos y errores estructurales legibles."""
    validator = _schema_validator()
    count = 0
    issues: list[str] = []

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
            label = f"línea {line_number} (caso {case_id})" if isinstance(case_id, str) else (
                f"línea {line_number}"
            )
            errors = sorted(validator.iter_errors(case), key=lambda error: (list(map(str, error.path)), error.message))
            for error in errors:
                field = ".".join(map(str, error.path)) or "$"
                issues.append(f"{label}: {field}: {error.message}")

    if count == 0 and not issues:
        issues.append("Archivo JSONL vacío: se esperaba al menos un caso")
    return count, issues
