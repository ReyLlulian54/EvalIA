"""Regression checks for the selected public report, without private run files."""

import hashlib
import json
from pathlib import Path

from evalia.reports.schema import public_report_validator

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "examples/results/benchmark-v1-qwen3-vs-qwen25.json"


def test_selected_report_has_only_reviewed_structured_cases() -> None:
    assert hashlib.sha256(ARTIFACT.read_bytes()).hexdigest() == (
        "7071ee504391a38c9866342481ff5124bdd75199c74189b17e024baf32f22565"
    )
    report = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    public_report_validator().validate(report)
    assert report["schema_version"] == "0.1.1"
    assert report["publication_review"] == "approved_for_publication"

    cases = [
        json.loads(line)
        for line in (ROOT / "datasets/benchmark-v1.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(report["cases"]) == len(cases) == 36
    assert [row["case_id"] for row in report["cases"]] == [case["id"] for case in cases]
    assert (
        report["splits"]["dev"]["selected_count"],
        report["splits"]["test"]["selected_count"],
    ) == (27, 9)
    for public, source in zip(report["cases"], cases, strict=True):
        assert source["review_status"] == "reviewed"
        assert source["redistribution_allowed"] is True
        assert public["split"] == source["split"]
        assert public["expected"] == source["expected"]

    by_id = {row["case_id"]: row for row in report["cases"]}
    assert by_id["bench-008"]["expected"]["student_required"] is None
    assert by_id["bench-008"]["base"]["prediction"]["student_required"] is None
    assert by_id["bench-008"]["candidate"]["prediction"]["student_required"] is False
    assert by_id["bench-001"]["base"]["status"] == "format_error"
    assert by_id["bench-001"]["base"]["prediction"] is None

    serialized = ARTIFACT.read_text(encoding="utf-8")
    for forbidden in (
        "raw_text",
        "source_url",
        "source_license",
        "evidence_reference",
        "reviewer",
        "request_sha256",
        "prompt_template",
    ):
        assert forbidden not in serialized
    for case in cases:
        assert case["text"] not in serialized
