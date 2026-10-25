"""El visor solo admite el artefacto fijado y revisado para publicación."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from evalia.reports import public_demo

ROOT = Path(__file__).resolve().parents[2]
APPROVED = ROOT / "examples/results/benchmark-v1-qwen3-vs-qwen25.json"


@pytest.fixture
def copied_report(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    report_path = root / "examples/results/benchmark-v1-qwen3-vs-qwen25.json"
    report_path.parent.mkdir(parents=True)
    shutil.copyfile(APPROVED, report_path)
    monkeypatch.setattr(public_demo, "REPO_ROOT", root)
    monkeypatch.setattr(public_demo, "PUBLIC_REPORT_PATH", report_path)
    return root, report_path


def test_loads_only_the_pinned_valid_report() -> None:
    report = public_demo.load_public_report()

    assert report["schema_version"] == "0.1.1"
    assert report["publication_review"] == "approved_for_publication"
    assert len(report["cases"]) == 36
    assert report["splits"]["dev"]["selected_count"] == 27
    assert report["splits"]["test"]["selected_count"] == 9


def test_rejects_missing_selected_report_without_private_fallback(copied_report) -> None:
    root, report_path = copied_report
    report_path.unlink()
    private = root / "runs" / "fake.json"
    private.parent.mkdir()
    shutil.copyfile(APPROVED, private)

    with pytest.raises(public_demo.PublicReportError):
        public_demo.load_public_report()


def test_rejects_changed_bytes_even_if_json_is_valid(copied_report) -> None:
    _, report_path = copied_report
    report_path.write_bytes(report_path.read_bytes() + b"\n")

    with pytest.raises(public_demo.PublicReportError):
        public_demo.load_public_report()


@pytest.mark.parametrize(
    "content",
    [
        b"{broken json",
        json.dumps({"schema_version": "0.1.1"}).encode("utf-8"),
        json.dumps(
            {
                **json.loads(APPROVED.read_text(encoding="utf-8")),
                "publication_review": "pending_artifact_review",
            }
        ).encode("utf-8"),
        json.dumps(
            {
                **json.loads(APPROVED.read_text(encoding="utf-8")),
                "schema_version": "0.1.0",
            }
        ).encode("utf-8"),
    ],
    ids=["json_invalido", "esquema_invalido", "revision_pendiente", "version_anterior"],
)
def test_rejects_invalid_or_unapproved_content_after_integrity_check(
    copied_report, monkeypatch, content: bytes
) -> None:
    _, report_path = copied_report
    report_path.write_bytes(content)
    monkeypatch.setattr(public_demo, "APPROVED_SHA256", hashlib.sha256(content).hexdigest())

    with pytest.raises(public_demo.PublicReportError):
        public_demo.load_public_report()


def test_rejects_report_path_outside_repository(copied_report, monkeypatch, tmp_path) -> None:
    _, _ = copied_report
    outside = tmp_path / "other.json"
    shutil.copyfile(APPROVED, outside)
    monkeypatch.setattr(public_demo, "PUBLIC_REPORT_PATH", outside)

    with pytest.raises(public_demo.PublicReportError):
        public_demo.load_public_report()


def test_rejects_alternate_report_inside_repository(copied_report, monkeypatch) -> None:
    root, _ = copied_report
    alternate = root / "examples/results/alternate.json"
    shutil.copyfile(APPROVED, alternate)
    monkeypatch.setattr(public_demo, "PUBLIC_REPORT_PATH", alternate)

    with pytest.raises(public_demo.PublicReportError):
        public_demo.load_public_report()


def test_rejects_symlink_to_selected_report(copied_report) -> None:
    _, report_path = copied_report
    target = report_path.with_name("target.json")
    report_path.rename(target)
    try:
        report_path.symlink_to(target)
    except (NotImplementedError, OSError):
        pytest.skip("El entorno no permite crear enlaces simbólicos")

    with pytest.raises(public_demo.PublicReportError):
        public_demo.load_public_report()
