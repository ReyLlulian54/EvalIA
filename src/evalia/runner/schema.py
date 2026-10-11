"""Validadores derivados del único esquema de artefactos de ejecución."""

import json
from functools import cache
from importlib import resources
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


@cache
def _run_schema() -> dict:
    packaged = resources.files("evalia").joinpath("schemas/evalia-run.schema.json")
    schema_file = (
        packaged
        if packaged.is_file()
        else Path(__file__).resolve().parents[3] / "schemas/evalia-run.schema.json"
    )
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def run_schema_version() -> str:
    """Lee la versión directamente del contrato autoritativo."""
    return _run_schema()["$defs"]["manifest"]["properties"]["schema_version"]["const"]


@cache
def manifest_validator() -> Draft202012Validator:
    """Valida manifest.json contra el esquema versionado."""
    return Draft202012Validator(_run_schema(), format_checker=FormatChecker())


@cache
def record_validator() -> Draft202012Validator:
    """Valida cada línea de responses.jsonl contra el mismo esquema."""
    schema = _run_schema()
    definition = {
        "$schema": schema["$schema"],
        "$defs": schema["$defs"],
        "$ref": "#/$defs/record",
    }
    return Draft202012Validator(definition, format_checker=FormatChecker())
