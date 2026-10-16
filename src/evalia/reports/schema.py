"""Validador del contrato autoritativo del puntaje privado."""

import json
from functools import cache
from importlib import resources
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


@cache
def score_report_validator() -> Draft202012Validator:
    packaged = resources.files("evalia").joinpath("schemas/evalia-score-report.schema.json")
    path = (
        packaged
        if packaged.is_file()
        else Path(__file__).resolve().parents[3] / "schemas/evalia-score-report.schema.json"
    )
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def score_report_schema_version() -> str:
    return score_report_validator().schema["properties"]["schema_version"]["const"]
