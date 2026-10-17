"""Puertas de 6.c con dos corridas simuladas y sin llamadas a modelos."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from evalia.cli import app
from evalia.reports.compare import RunComparisonError, compare_runs, write_comparison
from evalia.reports.schema import comparison_validator
from evalia.reports.score import score_run, write_score_report
from evalia.runner.inputs import run_dataset

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts/extraction-v1.json"


def _pair(
    tmp_path: Path, candidate_options: dict[str, int | float] | None = None
) -> tuple[Path, Path, Path]:
    lines = (ROOT / "datasets/benchmark-v1.jsonl").read_text(encoding="utf-8").splitlines()[:6]
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    cases = [json.loads(line) for line in lines]
    base = {case["id"]: {"raw_text": json.dumps(case["expected"])} for case in cases}
    candidate = {case["id"]: {"raw_text": json.dumps(case["expected"])} for case in cases}
    # bench-002: mejora de modalidad; bench-003: regresión false frente a null.
    wrong_modality = dict(cases[1]["expected"], modality="remota")
    base["bench-002"] = {"raw_text": json.dumps(wrong_modality)}
    wrong_student = dict(cases[2]["expected"], student_required=False)
    candidate["bench-003"] = {"raw_text": json.dumps(wrong_student)}
    # bench-004: ambos erran fecha con valores distintos; bench-005: formato inválido.
    base["bench-004"] = {
        "raw_text": json.dumps(dict(cases[3]["expected"], closing_date="2028-01-01"))
    }
    candidate["bench-004"] = {
        "raw_text": json.dumps(dict(cases[3]["expected"], closing_date="2029-01-01"))
    }
    candidate["bench-005"] = {"raw_text": "{mal json"}
    candidate["bench-006"] = {"error_code": "fixture_failure", "retryable": False}
    directories = []
    for name, outcomes in (("base", base), ("candidate", candidate)):
        fixture = tmp_path / f"{name}.json"
        fixture.write_text(json.dumps({"schema_version": "0.1.0", "outcomes": outcomes}))
        directory = tmp_path / name
        options = candidate_options if name == "candidate" and candidate_options else {}
        run_dataset(
            dataset_path=dataset,
            prompt_path=PROMPT,
            fixture_path=fixture,
            output_dir=directory,
            model_id=f"{name}-v1",
            max_cases=6,
            temperature=options.get("temperature", 0),
            max_output_tokens=options.get("max_output_tokens", 256),
            timeout_seconds=options.get("timeout_seconds", 120),
            max_retries=options.get("max_retries", 0),
        )
        write_score_report(directory, score_run(dataset, PROMPT, directory))
        directories.append(directory)
    return dataset, *directories


def test_paired_categories_and_private_contract(tmp_path: Path) -> None:
    dataset, base, candidate = _pair(tmp_path)
    report = compare_runs(dataset, PROMPT, base, candidate)
    comparison_validator().validate(report)
    cases = {case["case_id"]: case for case in report["cases"]}
    assert cases["bench-001"]["fields"]["closing_date"] == "correct_tie"
    assert cases["bench-002"]["fields"]["modality"] == "improvement"
    assert cases["bench-003"]["fields"]["student_required"] == "regression"
    assert cases["bench-004"]["fields"]["closing_date"] == "incorrect_tie"
    assert set(cases["bench-005"]["fields"].values()) == {"not_comparable"}
    assert set(cases["bench-006"]["fields"].values()) == {"not_comparable"}
    assert cases["bench-005"]["candidate_outcome"] == {
        "status": "format_error",
        "error_code": "invalid_json",
    }
    dev = report["splits"]["dev"]
    assert dev["eligible_count"] == 5
    assert dev["coverage"]["candidate"]["format_error_count"] == 1
    assert dev["coverage"]["candidate"]["provider_error_count"] == 1
    assert dev["fields"]["closing_date"]["incorrect_tie"]["case_ids"] == ["bench-004"]
    assert dev["fields"]["modality"]["improvement"]["count"] == 1
    for split in ("dev", "test"):
        for field in ("closing_date", "modality", "student_required", "skills_exact"):
            assert (
                sum(x["count"] for x in report["splits"][split]["fields"][field].values())
                == (report["splits"][split]["eligible_count"])
            )
    assert report["evidence_literal"]["status"] == "not_observed"
    assert report["splits"]["dev"]["telemetry"]["base"]["cost_usd"]["total"] is None
    assert all(word not in json.dumps(report) for word in ("raw_text", "2028-01-01"))
    output = tmp_path / "comparison.json"
    write_comparison(output, report)
    with pytest.raises(FileExistsError):
        write_comparison(output, report)


def test_rejects_changed_score_report_and_source_record(tmp_path: Path) -> None:
    dataset, base, candidate = _pair(tmp_path)
    path = base / "score-report.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["cases"][0]["field_correct"]["modality"] = False
    path.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(RunComparisonError, match="desactualizado o alterado"):
        compare_runs(dataset, PROMPT, base, candidate)


def test_rejects_changed_raw_records(tmp_path: Path) -> None:
    dataset, base, candidate = _pair(tmp_path)
    records = candidate / "responses.jsonl"
    records.write_bytes(records.read_bytes() + b"\n")
    with pytest.raises(RunComparisonError):
        compare_runs(dataset, PROMPT, base, candidate)


@pytest.mark.parametrize(
    ("key", "value"),
    [("temperature", 0.5), ("max_output_tokens", 128), ("timeout_seconds", 60), ("max_retries", 1)],
)
def test_rejects_incompatible_configuration(tmp_path: Path, key: str, value: int | float) -> None:
    dataset, base, candidate = _pair(tmp_path, {key: value})
    with pytest.raises(RunComparisonError, match=key):
        compare_runs(dataset, PROMPT, base, candidate)


def test_cli_writes_once_and_rejects_reversed_missing_input(tmp_path: Path) -> None:
    dataset, base, candidate = _pair(tmp_path)
    output = tmp_path / "private.json"
    args = [
        "compare",
        "--dataset",
        str(dataset),
        "--prompt",
        str(PROMPT),
        "--base-run",
        str(base),
        "--candidate-run",
        str(candidate),
        "--output",
        str(output),
    ]
    runner = CliRunner()
    assert runner.invoke(app, args).exit_code == 0
    assert runner.invoke(app, args).exit_code == 2
    assert (
        runner.invoke(app, [*args[:-1], str(tmp_path / "missing" / "private.json")]).exit_code == 2
    )
