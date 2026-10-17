"""Puertas de 6.d con permisos de prueba, sin publicación ni llamadas a modelos."""

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError
from typer.testing import CliRunner

from evalia.cli import app
from evalia.reports.compare import compare_runs, write_comparison
from evalia.reports.export_public import (
    PublicExportError,
    export_public_candidate,
    write_public_candidate,
)
from evalia.reports.schema import public_report_validator
from evalia.reports.score import score_run, write_score_report
from evalia.runner.inputs import run_dataset

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts/extraction-v1.json"


def _sources(
    tmp_path: Path, *, disallow_second: bool = False
) -> tuple[Path, Path, Path, Path, Path]:
    lines = (ROOT / "datasets/benchmark-v1.jsonl").read_text(encoding="utf-8").splitlines()[:3]
    cases = [json.loads(line) for line in lines]
    if disallow_second:
        cases[1]["redistribution_allowed"] = False
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    base_outcomes = {case["id"]: {"raw_text": json.dumps(case["expected"])} for case in cases}
    candidate_outcomes = dict(base_outcomes)
    candidate_outcomes["bench-002"] = {"raw_text": "PRIVATE_RAW_SENTINEL"}
    candidate_outcomes["bench-003"] = {
        "raw_text": json.dumps(dict(cases[2]["expected"], student_required=False))
    }
    runs = []
    for name, outcomes in (("base", base_outcomes), ("candidate", candidate_outcomes)):
        fixture = tmp_path / f"{name}-fixture.json"
        fixture.write_text(json.dumps({"schema_version": "0.1.0", "outcomes": outcomes}))
        run_dir = tmp_path / name
        run_dataset(
            dataset_path=dataset,
            prompt_path=PROMPT,
            fixture_path=fixture,
            output_dir=run_dir,
            model_id=f"{name}-v1",
            max_cases=3,
            temperature=0,
            max_output_tokens=256,
            timeout_seconds=120,
            max_retries=0,
        )
        write_score_report(run_dir, score_run(dataset, PROMPT, run_dir))
        runs.append(run_dir)
    comparison = tmp_path / "comparison.json"
    write_comparison(comparison, compare_runs(dataset, PROMPT, *runs))
    approval = tmp_path / "approval.json"
    approval.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
                "comparison_sha256": hashlib.sha256(comparison.read_bytes()).hexdigest(),
                "reviewed_at": "2026-10-16T12:00:00Z",
                "reviewer": "fixture-test",
                "cases": [
                    {
                        "case_id": case["id"],
                        "source_license": case["source_license"],
                        "basis": "original_created_for_project",
                        "evidence_reference": "PRIVATE_APPROVAL_SENTINEL",
                    }
                    for case in cases
                ],
            }
        ),
        encoding="utf-8",
    )
    return dataset, *runs, comparison, approval


def test_allowlisted_candidate_preserves_null_false_and_recalculates_subset(tmp_path: Path) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path)
    review = json.loads(approval.read_text(encoding="utf-8"))
    review["cases"] = [review["cases"][0], review["cases"][2]]
    approval.write_text(json.dumps(review), encoding="utf-8")

    report = export_public_candidate(dataset, PROMPT, base, candidate, comparison, approval)

    public_report_validator().validate(report)
    assert report["publication_review"] == "pending_artifact_review"
    assert [case["case_id"] for case in report["cases"]] == ["bench-001", "bench-003"]
    dev = report["splits"]["dev"]
    assert (dev["selected_count"], report["splits"]["test"]["selected_count"]) == (1, 1)
    assert dev["fields"]["student_required"]["regression"] == 1
    assert report["cases"][1]["expected"]["student_required"] is None
    assert report["cases"][1]["candidate"]["prediction"]["student_required"] is False
    encoded = json.dumps(report)
    for forbidden in (
        "PRIVATE_RAW_SENTINEL",
        "PRIVATE_APPROVAL_SENTINEL",
        "raw_text",
        "source_url",
        "evidence_reference",
        "prompt_template",
        "manifest.json",
        str(tmp_path),
    ):
        assert forbidden not in encoded
    output = tmp_path / "candidate-public.json"
    write_public_candidate(output, report)
    assert json.loads(output.read_text(encoding="utf-8")) == report
    with pytest.raises(FileExistsError):
        write_public_candidate(output, report)
    with pytest.raises(PublicExportError, match="ruta privada"):
        write_public_candidate(ROOT / "docs" / "forbidden-export.json", report)
    report["cases"][0]["raw_text"] = "secret"
    with pytest.raises(ValidationError):
        public_report_validator().validate(report)


def test_format_error_has_no_prediction(tmp_path: Path) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path)
    report = export_public_candidate(dataset, PROMPT, base, candidate, comparison, approval)
    second = report["cases"][1]
    assert second["candidate"]["status"] == "format_error"
    assert second["candidate"]["error_code"] == "invalid_json"
    assert second["candidate"]["prediction"] is None
    assert report["splits"]["dev"]["candidate"]["format_error_count"] == 1


def test_empty_selected_split_has_zero_counts_and_null_median(tmp_path: Path) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path)
    review = json.loads(approval.read_text(encoding="utf-8"))
    review["cases"] = review["cases"][:1]
    approval.write_text(json.dumps(review), encoding="utf-8")
    report = export_public_candidate(dataset, PROMPT, base, candidate, comparison, approval)
    dev = report["splits"]["dev"]
    assert dev["selected_count"] == 0
    assert dev["base"]["elapsed_ms"] == {"observations": 0, "median": None}
    assert all(count == 0 for counts in dev["fields"].values() for count in counts.values())


def test_rejects_case_without_redistribution_permission(tmp_path: Path) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path, disallow_second=True)
    with pytest.raises(PublicExportError, match="sin autorización"):
        export_public_candidate(dataset, PROMPT, base, candidate, comparison, approval)


@pytest.mark.parametrize("change", ["wrong_hash", "wrong_license", "duplicate_id", "extra_field"])
def test_rejects_invalid_permission_review(tmp_path: Path, change: str) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path)
    review = json.loads(approval.read_text(encoding="utf-8"))
    if change == "wrong_hash":
        review["comparison_sha256"] = "0" * 64
    elif change == "wrong_license":
        review["cases"][0]["source_license"] = "other"
    elif change == "duplicate_id":
        review["cases"].append({**review["cases"][0], "evidence_reference": "second"})
    else:
        review["private_note"] = "not allowed"
    approval.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(PublicExportError):
        export_public_candidate(dataset, PROMPT, base, candidate, comparison, approval)


def test_rejects_tampered_comparison(tmp_path: Path) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path)
    report = json.loads(comparison.read_text(encoding="utf-8"))
    report["cases"][0]["fields"]["modality"] = "regression"
    comparison.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(PublicExportError, match="desactualizada o alterada"):
        export_public_candidate(dataset, PROMPT, base, candidate, comparison, approval)


def test_cli_requires_permission_review_before_writing(tmp_path: Path) -> None:
    dataset, base, candidate, comparison, approval = _sources(tmp_path)
    output = tmp_path / "candidate.json"
    args = [
        "export-public",
        "--dataset",
        str(dataset),
        "--prompt",
        str(PROMPT),
        "--base-run",
        str(base),
        "--candidate-run",
        str(candidate),
        "--comparison",
        str(comparison),
        "--approval",
        str(approval),
        "--output",
        str(output),
    ]
    runner = CliRunner()
    assert runner.invoke(app, args).exit_code == 0
    assert output.exists()
    approval.unlink()
    missing_output = tmp_path / "must-not-write.json"
    assert runner.invoke(app, [*args[:-1], str(missing_output)]).exit_code == 2
    assert not missing_output.exists()
