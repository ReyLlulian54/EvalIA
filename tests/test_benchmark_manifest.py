"""La partición test revisada debe conservar sus bytes normalizados a LF."""

import hashlib
import json
from pathlib import Path

import pytest

from scripts import check_benchmark_v1

ROOT = Path(__file__).resolve().parents[1]


def _digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _reviewed_snapshot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    original = (ROOT / "datasets/benchmark-v1.jsonl").read_text(encoding="utf-8")
    cases = [json.loads(line) for line in original.splitlines()]
    for case in cases:
        case["review_status"] = "reviewed"
    lines = [json.dumps(case, ensure_ascii=False) for case in cases]
    dataset = tmp_path / "benchmark.jsonl"
    content = "\n".join(lines) + "\n"
    dataset.write_text(content, encoding="utf-8", newline="\n")

    manifest = json.loads(
        (ROOT / "datasets/benchmark-v1-manifest.json").read_text(encoding="utf-8")
    )
    test_lines = [line for line, case in zip(lines, cases, strict=True) if case["split"] == "test"]
    manifest.update(
        phase="reviewed",
        sha256_lf=_digest(content),
        test_sha256_lf=_digest("\n".join(test_lines) + "\n"),
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(check_benchmark_v1, "DATASET", dataset)
    monkeypatch.setattr(check_benchmark_v1, "MANIFEST", manifest_path)
    return dataset, manifest_path


def test_reviewed_manifest_accepts_unchanged_test_partition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _reviewed_snapshot(tmp_path, monkeypatch)

    check_benchmark_v1.main()


def test_reviewed_manifest_rejects_test_change_even_with_updated_dataset_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dataset, manifest_path = _reviewed_snapshot(tmp_path, monkeypatch)
    lines = dataset.read_text(encoding="utf-8").splitlines()
    case = json.loads(lines[0])
    assert case["split"] == "test"
    case["text"] += " Nota adicional."
    lines[0] = json.dumps(case, ensure_ascii=False)
    content = "\n".join(lines) + "\n"
    dataset.write_text(content, encoding="utf-8", newline="\n")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sha256_lf"] = _digest(content)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SystemExit, match="la partición test congelada cambió"):
        check_benchmark_v1.main()


def test_reviewed_manifest_requires_test_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, manifest_path = _reviewed_snapshot(tmp_path, monkeypatch)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["test_sha256_lf"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SystemExit, match="manifiesto incompleto"):
        check_benchmark_v1.main()
