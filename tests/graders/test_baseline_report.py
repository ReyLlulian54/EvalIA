"""Integridad del reporte versionado y su límite de publicación."""

import json
import shutil
from pathlib import Path

import pytest

from scripts.generate_seed_baseline import OUTPUT, ROOT, build_report, serialize_report


def test_committed_seed_report_matches_current_code_and_dataset() -> None:
    report = build_report()
    assert (ROOT / OUTPUT).read_text(encoding="utf-8") == serialize_report(report)
    assert report["evaluation_scope"] == "development_smoke_not_held_out"
    assert report["inputs"]["dataset_sha256"] == (
        "5fd3ffb891ccdca1b7cdf4642af2dc7b547438eda8d3e4766e0af5a26e3ea78e"
    )
    assert report["format_errors"] == []
    assert report["scored_case_ids"] == (
        "seed-001",
        "seed-002",
        "seed-003",
        "seed-004",
        "seed-005",
        "seed-006",
        "seed-007",
        "seed-009",
        "seed-010",
    )


def test_public_report_rejects_nonredistributable_case(tmp_path: Path) -> None:
    for relative in (
        "datasets/seed.jsonl",
        "src/evalia/graders/baseline.py",
        "schemas/evalia-case.schema.json",
        "src/evalia/vocabularies/skills-v1.json",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    dataset = tmp_path / "datasets/seed.jsonl"
    cases = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines()]
    cases[0]["redistribution_allowed"] = False
    dataset.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="permiso de redistribución"):
        build_report(tmp_path)
