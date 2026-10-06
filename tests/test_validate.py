"""Comportamiento público de la validación estructural JSONL."""

import copy
import json
from pathlib import Path

from typer.testing import CliRunner

from evalia.cli import app

ROOT = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()


def write_case(path: Path, case: dict) -> None:
    path.write_text(json.dumps(case, ensure_ascii=False) + "\n", encoding="utf-8")


def seed_case() -> dict:
    return json.loads((ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines()[0])


def test_seed_passes_structural_validation() -> None:
    result = RUNNER.invoke(app, ["validate", str(ROOT / "datasets/seed.jsonl")])

    assert result.exit_code == 0
    assert "10 casos" in result.output


def test_reports_json_error_on_the_actual_line(tmp_path: Path) -> None:
    path = tmp_path / "broken.jsonl"
    path.write_text(json.dumps(seed_case(), ensure_ascii=False) + "\n{\n", encoding="utf-8")

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code != 0
    assert "línea 2" in result.output
    assert "JSON" in result.output


def test_reports_case_and_field_for_invalid_date(tmp_path: Path) -> None:
    case = seed_case()
    case["expected"]["closing_date"] = "15-11"
    path = tmp_path / "without-year.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code != 0
    assert "línea 1" in result.output
    assert case["id"] in result.output
    assert "expected.closing_date" in result.output


def test_rejects_unknown_modality(tmp_path: Path) -> None:
    case = seed_case()
    case["expected"]["modality"] = "virtual"
    path = tmp_path / "unknown.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code != 0
    assert "expected.modality" in result.output


def test_false_is_a_valid_explicit_negative_not_null(tmp_path: Path) -> None:
    original = seed_case()
    case = copy.deepcopy(original)
    case["text"] = "No se requiere ser estudiante."
    case["expected"]["student_required"] = False
    case["evidence"]["student_required"] = {
        "quote": case["text"], "start": 0, "end": len(case["text"])
    }
    path = tmp_path / "false.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 0

    case["evidence"]["student_required"] = None
    write_case(path, case)
    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code != 0
    assert "evidence.student_required" in result.output


def test_empty_file_is_not_a_dataset(tmp_path: Path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code != 0
    assert "vacío" in result.output


def test_non_utf8_file_reports_a_read_error(tmp_path: Path) -> None:
    path = tmp_path / "invalid-encoding.jsonl"
    path.write_bytes(b"\xff\n")

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 2
    assert "No se pudo leer" in result.output
