"""Lectura cerrada del único reporte aprobado para la demo pública."""

import hashlib
import json
import stat
from pathlib import Path
from typing import Any, cast

from jsonschema.exceptions import SchemaError, ValidationError

from evalia.reports.schema import public_report_validator

REPO_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_REPORT_PATH = REPO_ROOT / "examples/results/benchmark-v1-qwen3-vs-qwen25.json"
APPROVED_SHA256 = "7071ee504391a38c9866342481ff5124bdd75199c74189b17e024baf32f22565"


class PublicReportError(Exception):
    """Error seguro para mostrar al visitante sin revelar datos del sistema de archivos."""


def load_public_report() -> dict[str, Any]:
    """Devuelve el reporte fijo solo si ruta, bytes y contrato siguen aprobados."""
    path = PUBLIC_REPORT_PATH
    expected_path = REPO_ROOT / "examples/results/benchmark-v1-qwen3-vs-qwen25.json"
    if path != expected_path:
        raise PublicReportError("El reporte público aprobado no superó la verificación.")

    try:
        # Resolver toda la ruta impide que un enlace o junction la redirija.
        if path.resolve(strict=True) != path or not stat.S_ISREG(path.stat().st_mode):
            raise PublicReportError("El reporte público aprobado no superó la verificación.")
        raw = path.read_bytes()
    except (OSError, RuntimeError) as error:
        raise PublicReportError("El reporte público aprobado no está disponible.") from error

    if hashlib.sha256(raw).hexdigest() != APPROVED_SHA256:
        raise PublicReportError("El reporte público aprobado no superó la verificación.")

    try:
        report = json.loads(raw.decode("utf-8"))
        public_report_validator().validate(report)
    except (OSError, UnicodeError, json.JSONDecodeError, ValidationError, SchemaError) as error:
        raise PublicReportError("El reporte público aprobado no superó la verificación.") from error

    if report["publication_review"] != "approved_for_publication":
        raise PublicReportError("El reporte público aprobado no está autorizado para mostrarse.")
    return cast(dict[str, Any], report)
