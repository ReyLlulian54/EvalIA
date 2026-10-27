"""Criterios de 6.b con corridas simuladas, sin inferencia ni red."""

import json
from pathlib import Path

import pytest
from jsonschema import ValidationError
from typer.testing import CliRunner

from evalia.cli import app
from evalia.graders.dataset import evaluate_dataset
from evalia.reports.schema import score_report_validator
from evalia.reports.score import RunScoreError, score_run, write_score_report
from evalia.runner.inputs import load_prompt, run_dataset

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts/extraction-v1.json"


def test_scoring_prompt_keeps_frozen_byte_hash() -> None:
    assert (
        load_prompt(PROMPT).sha256
        == "2535a9c5f6ab590ca356647dc342958a5459f3a2685ab67523db55a9ed37c86e"
    )


def _fixture_run(
    tmp_path: Path, overrides: dict[str, object] | None = None, count: int = 3
) -> tuple[Path, Path]:
    source_lines = (ROOT / "datasets/benchmark-v1.jsonl").read_text(encoding="utf-8").splitlines()
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text("\n".join(source_lines[:count]) + "\n", encoding="utf-8", newline="\n")
    cases = [json.loads(line) for line in source_lines[:count]]
    outcomes = {
        case["id"]: {"raw_text": json.dumps(case["expected"], ensure_ascii=False)} for case in cases
    }
    for case_id, outcome in (overrides or {}).items():
        outcomes[case_id] = outcome
    fixture = tmp_path / "fixture.json"
    fixture.write_text(
        json.dumps({"schema_version": "0.1.0", "outcomes": outcomes}, ensure_ascii=False),
        encoding="utf-8",
    )
    run_dir = tmp_path / "run"
    run_dataset(
        dataset_path=dataset,
        prompt_path=PROMPT,
        fixture_path=fixture,
        output_dir=run_dir,
        model_id="simulado-v1",
        max_cases=count,
        temperature=0,
        max_output_tokens=256,
        timeout_seconds=120,
        max_retries=0,
    )
    return dataset, run_dir


def test_private_report_separates_splits_false_null_and_unobserved_evidence(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(tmp_path)

    report = score_run(dataset, PROMPT, run_dir)

    score_report_validator().validate(report)
    assert [(case["case_id"], case["split"]) for case in report["cases"]] == [
        ("bench-001", "test"),
        ("bench-002", "dev"),
        ("bench-003", "dev"),
    ]
    dev = report["splits"]["dev"]
    test = report["splits"]["test"]
    assert (dev["eligible_count"], dev["scored_count"]) == (2, 2)
    assert (test["eligible_count"], test["scored_count"]) == (1, 1)
    assert dev["metrics"]["student_required"]["numerator"] == 2
    assert dev["metrics"]["abstention"]["student_required"] == {
        "numerator": 1,
        "denominator": 1,
        "value": 1.0,
        "failed_case_ids": [],
    }
    assert report["evidence_literal"] == {
        "status": "not_observed",
        "reason": "prompt_did_not_request_evidence",
    }
    assert dev["telemetry"]["cost_usd"] == {"observations": 0, "total": None}
    assert "raw_text" not in json.dumps(report)
    cases = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines()]
    for split in ("dev", "test"):
        selected = [case for case in cases if case["split"] == split]
        baseline = evaluate_dataset(
            selected,
            [
                {
                    "case_id": case["id"],
                    "extraction": case["expected"],
                    "evidence": case["evidence"],
                }
                for case in selected
            ],
        )
        for field in (
            "coverage",
            "closing_date",
            "modality",
            "student_required",
            "skills_exact",
            "skills_precision",
            "skills_recall",
            "skills_f1",
        ):
            assert (
                report["splits"][split]["metrics"][field]["numerator"]
                == baseline.metric(field).ratio.numerator
            )
            assert (
                report["splits"][split]["metrics"][field]["denominator"]
                == baseline.metric(field).ratio.denominator
            )


def test_explicit_false_does_not_count_as_abstention(tmp_path: Path) -> None:
    source_lines = (ROOT / "datasets/benchmark-v1.jsonl").read_text(encoding="utf-8").splitlines()
    expected = json.loads(source_lines[2])["expected"]
    expected["student_required"] = False
    dataset, run_dir = _fixture_run(tmp_path, {"bench-003": {"raw_text": json.dumps(expected)}})

    dev = score_run(dataset, PROMPT, run_dir)["splits"]["dev"]

    assert dev["metrics"]["student_required"]["numerator"] == 1
    assert dev["metrics"]["abstention"]["student_required"] == {
        "numerator": 0,
        "denominator": 1,
        "value": 0.0,
        "failed_case_ids": ["bench-003"],
    }


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        ("{", "invalid_json"),
        ('{"closing_date":null,"closing_date":null}', "duplicate_key"),
        ('{"closing_date":NaN}', "nonstandard_constant"),
        (
            '{"closing_date":null,"modality":null,"skills":[],"student_required":null,"extra":1}',
            "invalid_extraction",
        ),
        (
            '{"closing_date":null,"modality":null,"skills":[],"student_required":"false"}',
            "invalid_extraction",
        ),
        (
            '{"closing_date":null,"modality":null,"skills":["Python 3"],"student_required":null}',
            "noncanonical_skill",
        ),
    ],
)
def test_format_failures_reduce_coverage_not_content_denominators(
    tmp_path: Path, raw: str, code: str
) -> None:
    dataset, run_dir = _fixture_run(tmp_path, {"bench-002": {"raw_text": raw}})

    report = score_run(dataset, PROMPT, run_dir)
    dev = report["splits"]["dev"]

    assert report["cases"][1]["outcome"] == "format_error"
    assert report["cases"][1]["error_code"] == code
    assert dev["format_error_count"] == 1
    assert dev["metrics"]["coverage"]["denominator"] == 2
    assert dev["metrics"]["coverage"]["numerator"] == 1
    assert dev["metrics"]["closing_date"]["denominator"] == 1
    assert report["splits"]["test"]["metrics"]["coverage"]["numerator"] == 1


def test_provider_error_is_kept_separate_from_format_error(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(
        tmp_path,
        {"bench-002": {"error_code": "fixture_failure", "retryable": False}},
    )

    report = score_run(dataset, PROMPT, run_dir)

    assert report["cases"][1]["outcome"] == "provider_error"
    assert report["cases"][1]["error_code"] == "fixture_failure"
    assert report["splits"]["dev"]["provider_error_count"] == 1
    assert report["splits"]["dev"]["format_error_count"] == 0


def test_zero_content_denominator_is_null_not_perfect(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(
        tmp_path,
        {"bench-002": {"raw_text": "{"}, "bench-003": {"raw_text": "{"}},
    )

    dev = score_run(dataset, PROMPT, run_dir)["splits"]["dev"]

    assert dev["metrics"]["coverage"]["value"] == 0
    assert dev["metrics"]["closing_date"] == {
        "numerator": 0,
        "denominator": 0,
        "value": None,
        "failed_case_ids": [],
    }
    assert dev["metrics"]["skills_precision"]["value"] is None


def test_empty_split_has_no_applicable_coverage(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(tmp_path, count=1)

    dev = score_run(dataset, PROMPT, run_dir)["splits"]["dev"]

    assert dev["eligible_count"] == 0
    assert dev["metrics"]["coverage"]["value"] is None
    assert dev["telemetry"]["elapsed_ms"] == {"observations": 0, "median": None}


def test_preflight_rejects_changed_provenance_before_scoring(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(tmp_path)
    manifest_path = run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["prompt_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RunScoreError, match="hashes"):
        score_run(dataset, PROMPT, run_dir)
    assert not (run_dir / "score-report.json").exists()


def test_preflight_rejects_changed_record_order_before_scoring(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(tmp_path)
    responses = run_dir / "responses.jsonl"
    lines = responses.read_text(encoding="utf-8").splitlines()
    lines[0], lines[1] = lines[1], lines[0]
    responses.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(RunScoreError, match="orden"):
        score_run(dataset, PROMPT, run_dir)


def test_report_contract_and_exclusive_private_write(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(tmp_path)
    report = score_run(dataset, PROMPT, run_dir)
    output = write_score_report(run_dir, report)
    assert output == run_dir / "score-report.json"
    assert (
        json.loads(output.read_text(encoding="utf-8"))["run"]["run_id"] == report["run"]["run_id"]
    )
    with pytest.raises(FileExistsError):
        write_score_report(run_dir, report)
    report["splits"]["dev"]["metrics"]["coverage"]["extra"] = True
    with pytest.raises(ValidationError):
        score_report_validator().validate(report)


def test_cli_score_run_writes_once_without_network(tmp_path: Path) -> None:
    dataset, run_dir = _fixture_run(tmp_path)
    command = [
        "score-run",
        "--dataset",
        str(dataset),
        "--prompt",
        str(PROMPT),
        "--run-dir",
        str(run_dir),
    ]

    first = CliRunner().invoke(app, command)
    second = CliRunner().invoke(app, command)

    assert first.exit_code == 0, first.output
    assert "dev 2/2" in first.output and "test 1/1" in first.output
    assert second.exit_code == 2
    assert (run_dir / "score-report.json").exists()
