"""Comportamiento público de la validación mecánica JSONL."""

import copy
import json
from pathlib import Path

from typer.testing import CliRunner

from evalia.cli import app

ROOT = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()


def write_case(path: Path, case: dict) -> None:
    path.write_text(json.dumps(case, ensure_ascii=False) + "\n", encoding="utf-8")


def write_cases(path: Path, cases: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases),
        encoding="utf-8",
    )


def seed_case() -> dict:
    return json.loads((ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines()[0])


def test_seed_passes_mechanical_validation() -> None:
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
    case = json.loads((ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines()[2])
    assert case["expected"]["student_required"] is False
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


def test_rejects_repeated_id_with_both_line_numbers(tmp_path: Path) -> None:
    first = seed_case()
    second = copy.deepcopy(first)
    second["text"] += " Texto adicional."
    path = tmp_path / "duplicate-id.jsonl"
    write_cases(path, [first, second])

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "línea 2 (caso seed-001): id" in result.output
    assert "línea 1" in result.output


def test_rejects_repeated_text_with_distinct_ids(tmp_path: Path) -> None:
    first = seed_case()
    second = copy.deepcopy(first)
    second["id"] = "fixture-002"
    path = tmp_path / "duplicate-text.jsonl"
    write_cases(path, [first, second])

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "línea 2 (caso fixture-002): text" in result.output
    assert "línea 1" in result.output


def test_rejects_whitespace_only_text(tmp_path: Path) -> None:
    case = seed_case()
    case["text"] = " \n "
    case["expected"] = {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    }
    case["evidence"] = {
        "closing_date": None,
        "modality": None,
        "skills": [],
        "student_required": None,
    }
    path = tmp_path / "blank-text.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "línea 1 (caso seed-001): text" in result.output
    assert "solo espacios" in result.output


def test_rejects_scalar_span_outside_text(tmp_path: Path) -> None:
    case = seed_case()
    case["evidence"]["closing_date"]["end"] = len(case["text"]) + 1
    path = tmp_path / "outside-text.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "línea 1 (caso seed-001): evidence.closing_date" in result.output
    assert "rango inválido" in result.output


def test_rejects_quote_not_matching_its_unicode_span(tmp_path: Path) -> None:
    case = json.loads((ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines()[5])
    case["evidence"]["modality"]["quote"] = "Modalidad: remota."
    path = tmp_path / "wrong-quote.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "línea 1 (caso seed-006): evidence.modality" in result.output
    assert "cita no coincide" in result.output


def test_rejects_missing_skill_evidence(tmp_path: Path) -> None:
    case = seed_case()
    case["evidence"]["skills"].pop()
    path = tmp_path / "missing-skill.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "línea 1 (caso seed-001): evidence.skills" in result.output
    assert "SQL" in result.output


def test_rejects_duplicate_skill_evidence(tmp_path: Path) -> None:
    case = seed_case()
    case["evidence"]["skills"][1]["skill"] = "Python"
    path = tmp_path / "duplicate-skill.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "evidence.skills" in result.output
    assert "SQL" in result.output
    assert "Python" in result.output


def test_rejects_skill_quote_with_reversed_span(tmp_path: Path) -> None:
    case = seed_case()
    case["evidence"]["skills"][0]["start"] = case["evidence"]["skills"][0]["end"]
    path = tmp_path / "reversed-skill.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "evidence.skills.0" in result.output
    assert "rango inválido" in result.output


def test_rejects_skill_alias_in_reference_values(tmp_path: Path) -> None:
    case = seed_case()
    case["expected"]["skills"][0] = "Python 3"
    case["evidence"]["skills"][0]["skill"] = "Python 3"
    path = tmp_path / "noncanonical-skill.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "expected.skills.0" in result.output
    assert "Python" in result.output


def test_rejects_whitespace_only_skill_without_crashing(tmp_path: Path) -> None:
    case = seed_case()
    case["expected"]["skills"][0] = " "
    case["evidence"]["skills"][0]["skill"] = " "
    path = tmp_path / "empty-skill.jsonl"
    write_case(path, case)

    result = RUNNER.invoke(app, ["validate", str(path)])

    assert result.exit_code == 1
    assert "expected.skills.0: habilidad vacía" in result.output
