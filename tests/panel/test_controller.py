"""Puertas de 7.b contra el motor real con proveedor simulado, sin sockets."""

import json
import os
import shutil
import socket
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from threading import Event, Thread
from types import SimpleNamespace

import httpx
import pytest

from evalia.panel import LocalPanelController, PanelError, RunOptions
from evalia.panel import controller as panel_module
from evalia.providers.base import GenerationResponse, ProviderFailure
from evalia.providers.ollama import OllamaProvider
from evalia.runner import inputs

ROOT = Path(__file__).resolve().parents[2]
DATASET = "benchmark-v1.jsonl"
PROMPT = "extraction-v1.json"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def reject(*args, **kwargs):
        pytest.fail("Las pruebas del panel no deben abrir conexiones de red")

    monkeypatch.setattr(socket.socket, "connect", reject)
    monkeypatch.setattr(socket, "create_connection", reject)


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / "repo"
    (root / "datasets").mkdir(parents=True)
    (root / "prompts").mkdir()
    for name in ("seed.jsonl", DATASET):
        shutil.copyfile(ROOT / "datasets" / name, root / "datasets" / name)
    shutil.copyfile(ROOT / "prompts" / PROMPT, root / "prompts" / PROMPT)
    return root


@pytest.fixture
def fake(monkeypatch, workspace):
    cases = [
        json.loads(line)
        for name in (DATASET, "seed.jsonl")
        for line in (workspace / "datasets" / name).read_text(encoding="utf-8").splitlines()
    ]
    state = SimpleNamespace(
        calls=[],
        tag_calls=0,
        url=None,
        hook=None,
        tag_error=None,
        outcomes={c["id"]: GenerationResponse(json.dumps(c["expected"])) for c in cases},
    )

    class SimulatedOllama:
        provider_id = "ollama"

        def __init__(self, base_url):
            state.url = base_url

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def model_digest(self, model_id):
            state.tag_calls += 1
            if state.tag_error:
                raise state.tag_error
            return "a" * 64

        def generate(self, request):
            state.calls.append(request)
            if state.hook:
                state.hook(request)
            outcome = state.outcomes[request.case_id]
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    monkeypatch.setattr(inputs, "OllamaProvider", SimulatedOllama)
    return state


def prepare(controller, **kwargs):
    return controller.prepare(DATASET, PROMPT, RunOptions(**kwargs))


def test_prepare_is_immutable_local_and_selects_reviewed_cases(workspace, fake):
    controller = LocalPanelController(workspace)
    assert controller.datasets() == (DATASET, "seed.jsonl")
    assert controller.prompts() == (PROMPT,)
    assert controller.runs() == ()
    seed = controller.prepare("seed.jsonl", PROMPT)
    assert len(seed.case_ids) == 9 and "seed-008" not in seed.case_ids
    prepared = prepare(controller)
    assert prepared.case_ids == tuple(f"bench-{i:03}" for i in range(1, 11))
    assert prepared.splits.count("dev") == 8
    assert prepared.splits.count("test") == 2
    assert not (workspace / "runs").exists()
    assert not fake.calls and fake.tag_calls == 0
    with pytest.raises(FrozenInstanceError):
        prepared.options.max_cases = 2
    assert controller.execute(seed).code == "stale_intent"
    assert not fake.calls


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_id", ""),
        ("model_id", " qwen3:8b"),
        ("model_id", "bad\nmodel"),
        ("max_cases", True),
        ("max_cases", 1.5),
        ("max_cases", 0),
        ("max_cases", 101),
        ("max_output_tokens", False),
        ("max_output_tokens", 0),
        ("max_output_tokens", 2049),
        ("max_retries", True),
        ("max_retries", -1),
        ("max_retries", 3),
        ("temperature", True),
        ("temperature", -0.1),
        ("temperature", 2.1),
        ("temperature", float("nan")),
        ("temperature", float("inf")),
        ("timeout_seconds", True),
        ("timeout_seconds", 0),
        ("timeout_seconds", 121),
    ],
)
def test_invalid_options_fail_before_any_effect(field, value, workspace, fake):
    with pytest.raises(PanelError):
        RunOptions(**{field: value})
    assert not fake.calls and not (workspace / "runs").exists()


@pytest.mark.parametrize(
    "name",
    [
        "../benchmark-v1.jsonl",
        "sub/file.jsonl",
        r"sub\file.jsonl",
        "/etc/passwd",
        r"C:\private.jsonl",
        r"\\server\share\file.jsonl",
        "CON.jsonl",
        "file.jsonl:secret",
        "benchmark-v1.jsonl.",
        "benchmark-v1.json",
        "missing.jsonl",
    ],
)
def test_unsafe_or_absent_input_rejected(name, workspace, fake):
    controller = LocalPanelController(workspace)
    old = prepare(controller)
    with pytest.raises(PanelError):
        controller.prepare(name, PROMPT)
    assert controller.execute(old).code == "stale_intent"
    assert fake.tag_calls == 0 and not (workspace / "runs").exists()


@pytest.mark.parametrize("kind", ["invalid_dataset", "no_reviewed", "invalid_prompt"])
def test_invalid_content_rejected_during_prepare(kind, workspace, fake):
    if kind == "invalid_prompt":
        path = workspace / "prompts" / PROMPT
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["template"] = "Sin marcador"
        path.write_text(json.dumps(doc), encoding="utf-8")
    else:
        path = workspace / "datasets" / DATASET
        if kind == "invalid_dataset":
            path.write_text("not json", encoding="utf-8")
        else:
            cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            for case in cases:
                case["review_status"] = "draft"
            path.write_text("\n".join(json.dumps(case) for case in cases) + "\n", encoding="utf-8")
    with pytest.raises(PanelError, match="Revise"):
        prepare(LocalPanelController(workspace))
    assert not fake.calls and not (workspace / "runs").exists()


@pytest.mark.parametrize("which", ["dataset", "prompt"])
def test_changed_bytes_reject_and_consume_intent(which, workspace, fake):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller)
    path = prepared.dataset_path if which == "dataset" else prepared.prompt_path
    path.write_bytes(path.read_bytes() + b"\n")
    assert controller.execute(prepared).code == "inputs_changed"
    assert controller.execute(prepared).code == "stale_intent"
    assert fake.tag_calls == 0 and not (workspace / "runs").exists()


def test_one_dispatch_fixed_url_and_read_without_inference(workspace, fake, monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:9999")
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=3)
    forged = replace(prepared, options=RunOptions(max_cases=100))
    assert controller.execute(forged).code == "stale_intent"
    result = controller.execute(prepared)
    assert result.status == "completed"
    assert result.snapshot.recorded_count == 3
    assert fake.url == "http://127.0.0.1:11434"
    assert [r.case_id for r in fake.calls] == list(prepared.case_ids)
    assert controller.execute(prepared).code == "stale_intent"
    assert LocalPanelController(workspace).execute(prepared).code == "stale_intent"
    assert controller.runs() == (prepared.intent_id,)
    snapshot = controller.read_run(prepared.intent_id)
    assert all("raw_text" not in record for record in snapshot.records)
    assert len(fake.calls) == 3
    raw = controller.read_run(prepared.intent_id, include_raw=True)
    values = [json.loads(r["raw_text"])["student_required"] for r in raw.records]
    assert False in values and None in values
    assert "raw_text" not in repr(raw)
    assert not (prepared.output_dir / "score-report.json").exists()


def test_two_sessions_share_execution_lock_and_busy_intent_is_consumed(workspace, fake):
    first, second = LocalPanelController(workspace), LocalPanelController(workspace)
    a, b = prepare(first, max_cases=1), prepare(second, max_cases=1)
    entered, release = Event(), Event()
    results = []

    def hold(request):
        entered.set()
        assert release.wait(10)

    fake.hook = hold
    worker = Thread(target=lambda: results.append(first.execute(a)))
    worker.start()
    try:
        assert entered.wait(10)
        assert first.execute(a).code == "stale_intent"
        assert second.execute(b).code == "busy"
        assert not b.output_dir.exists()
    finally:
        release.set()
        worker.join(10)
    assert not worker.is_alive() and results[0].status == "completed"
    assert len(fake.calls) == 1
    assert second.execute(b).code == "stale_intent"
    fake.hook = None
    assert second.execute(prepare(second, max_cases=1)).status == "completed"


def test_existing_destination_preserved(workspace, fake):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller)
    prepared.output_dir.mkdir(parents=True)
    sentinel = prepared.output_dir / "user.txt"
    sentinel.write_bytes(b"preserve")
    result = controller.execute(prepared)
    assert result.code == "destination_exists" and result.run_name is None
    assert sentinel.read_bytes() == b"preserve"
    assert not fake.calls and fake.tag_calls == 0


def test_permission_error_before_execution_is_sanitized(workspace, fake, monkeypatch):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller)
    read_bytes = Path.read_bytes

    def denied(path):
        if path == prepared.dataset_path:
            raise PermissionError("secret/private/path")
        return read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", denied)
    result = controller.execute(prepared)
    assert result.status == "rejected" and "secret" not in repr(result)
    assert not fake.calls and not prepared.output_dir.exists()


@pytest.mark.parametrize("code", ["connection_error", "model_not_found", "invalid_response"])
def test_preflight_failures_create_no_run_and_allow_explicit_new_preparation(code, workspace, fake):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    fake.tag_error = ProviderFailure(code, retryable=False, message="private body")
    result = controller.execute(prepared)
    assert result.status == "rejected" and result.code == code
    assert "private" not in repr(result)
    assert not fake.calls and not prepared.output_dir.exists()
    assert controller.execute(prepared).code == "stale_intent"
    fake.tag_error = None
    assert controller.execute(prepare(controller, max_cases=1)).status == "completed"


def test_real_adapter_rejects_invalid_digest_without_chat(workspace, monkeypatch):
    paths = []

    def respond(request):
        paths.append(request.url.path)
        return httpx.Response(200, json={"models": [{"name": "qwen3:8b", "digest": "bad"}]})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        monkeypatch.setattr(
            inputs, "OllamaProvider", lambda base_url: OllamaProvider(base_url, client=client)
        )
        controller = LocalPanelController(workspace)
        prepared = prepare(controller)
        assert controller.execute(prepared).code == "invalid_response"
    assert paths == ["/api/tags"] and not prepared.output_dir.exists()


@pytest.mark.parametrize(
    "failure,status,count",
    [
        (RuntimeError("private exception"), "failed", 2),
        (inputs.RunInputError("private exception"), "failed", 2),
        (FileExistsError("private exception"), "failed", 2),
        (KeyboardInterrupt(), "interrupted", 1),
        (ProviderFailure("timeout", retryable=True, message="private"), "completed", 3),
    ],
)
def test_failures_preserve_partial_artifacts_and_do_not_repeat(
    failure, status, count, workspace, fake
):
    fake.outcomes["bench-002"] = failure
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=3)
    result = controller.execute(prepared)
    assert result.status == status
    assert result.snapshot.manifest["status"] == status
    assert result.snapshot.recorded_count == count
    assert "private" not in repr(result)
    before = (prepared.output_dir / "responses.jsonl").read_bytes()
    assert controller.execute(prepared).code == "stale_intent"
    assert (prepared.output_dir / "responses.jsonl").read_bytes() == before
    if status == "completed":
        assert result.code == "completed_with_errors"
        assert result.snapshot.manifest["failure_count"] == 1


def test_only_explicit_provider_retries_are_used(workspace, fake):
    def transient(request):
        if len(fake.calls) == 1:
            raise ProviderFailure("timeout", retryable=True, message="simulated")

    fake.hook = transient
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=2, max_retries=1)
    result = controller.execute(prepared)
    assert result.status == "completed"
    assert [r["attempts"] for r in result.snapshot.records] == [2, 1]
    assert len(fake.calls) == 3


def test_unclosed_run_is_read_without_changing_status_or_inference(workspace, fake):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    controller.execute(prepared)
    manifest_path = prepared.output_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        status="running", finished_at=None, recorded_count=0, success_count=0, last_case_id=None
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    before = manifest_path.read_bytes()
    snapshot = LocalPanelController(workspace).read_run(prepared.intent_id)
    assert snapshot.warnings == ("manifest_counts_unconfirmed", "unclosed_run")
    assert snapshot.recorded_count == 1
    assert manifest_path.read_bytes() == before and len(fake.calls) == 1


def test_scoring_is_explicit_audited_and_never_overwrites(workspace, fake):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=3)
    controller.execute(prepared)
    report_path = prepared.output_dir / "score-report.json"
    with pytest.raises(PanelError) as error:
        controller.read_score(prepared.intent_id, DATASET, PROMPT)
    assert error.value.code == "score_missing" and not report_path.exists()
    report = controller.score(prepared.intent_id, DATASET, PROMPT)
    assert report["splits"]["dev"]["scored_count"] == 2
    assert report["splits"]["test"]["scored_count"] == 1
    assert report["splits"]["dev"]["telemetry"]["cost_usd"]["total"] is None
    assert report["evidence_literal"]["status"] == "not_observed"
    report["created_at"] = "2020-01-01T00:00:00Z"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    before = report_path.read_bytes()
    assert controller.score(prepared.intent_id, DATASET, PROMPT) == report
    assert controller.read_score(prepared.intent_id, DATASET, PROMPT) == report
    assert report_path.read_bytes() == before and len(fake.calls) == 3


@pytest.mark.parametrize("kind", ["seed", "prompt", "incomplete"])
def test_incompatible_scoring_preserves_run(kind, workspace, fake):
    controller = LocalPanelController(workspace)
    dataset_name = "seed.jsonl" if kind == "seed" else DATASET
    if kind == "prompt":
        path = workspace / "prompts" / PROMPT
        path.write_bytes(path.read_bytes() + b"\n")
    if kind == "incomplete":
        fake.outcomes["bench-002"] = KeyboardInterrupt()
    prepared = controller.prepare(dataset_name, PROMPT, RunOptions(max_cases=3))
    controller.execute(prepared)
    before = (prepared.output_dir / "responses.jsonl").read_bytes()
    call_count = len(fake.calls)
    with pytest.raises(PanelError) as error:
        controller.score(prepared.intent_id, dataset_name, PROMPT)
    assert error.value.code == "score_unavailable"
    assert not (prepared.output_dir / "score-report.json").exists()
    assert (prepared.output_dir / "responses.jsonl").read_bytes() == before
    assert len(fake.calls) == call_count


@pytest.mark.parametrize("kind", ["score", "record", "counts", "duplicate_json"])
def test_tampered_artifacts_fail_closed(kind, workspace, fake):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    controller.execute(prepared)
    controller.score(prepared.intent_id, DATASET, PROMPT)
    if kind == "score":
        path = prepared.output_dir / "score-report.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["cases"][0]["field_correct"]["student_required"] = False
        path.write_text(json.dumps(document), encoding="utf-8")
    elif kind == "record":
        path = prepared.output_dir / "responses.jsonl"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["request_sha256"] = "0" * 64
        path.write_text(json.dumps(document) + "\n", encoding="utf-8")
    else:
        path = prepared.output_dir / "manifest.json"
        document = json.loads(path.read_text(encoding="utf-8"))
        document["success_count"] = 0
        text = json.dumps(document)
        if kind == "duplicate_json":
            text = '{"status":"completed",' + text[1:]
        path.write_text(text, encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(PanelError):
        controller.read_score(prepared.intent_id, DATASET, PROMPT)
    assert path.read_bytes() == before and len(fake.calls) == 1


def directory_link(link, target):
    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)


@pytest.mark.parametrize("category", ["datasets", "prompts", "runs", "panel", "run"])
def test_real_directory_redirection_is_rejected_before_io(category, workspace, fake, tmp_path):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    outside = tmp_path / "repo-outside"
    outside.mkdir()
    marker = outside / "keep.txt"
    marker.write_bytes(b"untouched")
    if category in {"datasets", "prompts"}:
        link = workspace / category
        link.rename(workspace / (category + "-backup"))
    elif category == "runs":
        link = workspace / "runs"
    elif category == "panel":
        (workspace / "runs").mkdir()
        link = workspace / "runs" / "panel"
    else:
        prepared.output_dir.parent.mkdir(parents=True)
        link = prepared.output_dir
    directory_link(link, outside)
    result = controller.execute(prepared)
    assert result.status == "rejected" and result.code == "invalid_path"
    assert fake.tag_calls == 0 and not fake.calls
    assert list(outside.iterdir()) == [marker]
    assert marker.read_bytes() == b"untouched"


def test_real_input_directory_alias_is_excluded_from_catalog(workspace, fake, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    directory_link(workspace / "datasets" / "alias.jsonl", outside)
    controller = LocalPanelController(workspace)
    assert "alias.jsonl" not in controller.datasets()
    with pytest.raises(PanelError):
        controller.prepare("alias.jsonl", PROMPT)
    assert fake.tag_calls == 0


@pytest.mark.parametrize("filename", ["manifest.json", "responses.jsonl", "score-report.json"])
def test_artifact_resolution_escape_is_rejected_before_content_read(
    filename, workspace, fake, tmp_path, monkeypatch
):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    controller.execute(prepared)
    outside = tmp_path / "outside-secret.json"
    outside.write_text("private", encoding="utf-8")
    selected = prepared.output_dir / filename
    resolve = Path.resolve
    read_bytes = Path.read_bytes

    def redirected(path, *args, **kwargs):
        if path == selected:
            return outside
        return resolve(path, *args, **kwargs)

    def guarded_read(path):
        if path == outside or path == selected:
            pytest.fail("No debe leer contenido de una ruta rechazada")
        return read_bytes(path)

    monkeypatch.setattr(Path, "resolve", redirected)
    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    with pytest.raises(PanelError) as error:
        controller.score(prepared.intent_id, DATASET, PROMPT)
    assert error.value.code == "invalid_path" and len(fake.calls) == 1


def test_real_file_symlink_escape_is_rejected(workspace, fake, tmp_path):
    outside = tmp_path / "secret.jsonl"
    outside.write_text("private", encoding="utf-8")
    link = workspace / "datasets" / "linked.jsonl"
    try:
        link.symlink_to(outside)
    except OSError as error:
        if os.name == "nt" and error.winerror == 1314:
            pytest.skip("Windows requiere privilegio para crear symlinks de archivo")
        raise
    controller = LocalPanelController(workspace)
    assert "linked.jsonl" not in controller.datasets()
    with pytest.raises(PanelError) as error:
        controller.prepare("linked.jsonl", PROMPT)
    assert error.value.code == "invalid_path" and not fake.calls


def test_input_resolution_escape_and_loop_rejected_before_read(
    workspace, fake, tmp_path, monkeypatch
):
    source = workspace / "datasets" / DATASET
    outside = tmp_path / "outside.jsonl"
    outside.write_text("private", encoding="utf-8")
    resolve = Path.resolve

    def redirected(path, *args, **kwargs):
        if path == source:
            return outside
        return resolve(path, *args, **kwargs)

    controller = LocalPanelController(workspace)
    monkeypatch.setattr(Path, "resolve", redirected)
    with pytest.raises(PanelError) as error:
        prepare(controller)
    assert error.value.code == "invalid_path" and not fake.calls

    def loop(path, *args, **kwargs):
        if path == source:
            raise RuntimeError("Symlink loop private path")
        return resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", loop)
    with pytest.raises(PanelError) as error:
        prepare(controller)
    assert "private" not in str(error.value)


def test_root_alias_within_checkout_rejected(workspace, fake):
    original = workspace / "datasets"
    backup = workspace / "datasets-backup"
    original.rename(backup)
    directory_link(original, backup)
    with pytest.raises(PanelError) as error:
        prepare(LocalPanelController(workspace))
    assert error.value.code == "invalid_path" and not fake.calls


def test_run_directory_redirected_after_execution_is_not_read(workspace, fake, tmp_path):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    controller.execute(prepared)
    target = tmp_path / "private-run"
    prepared.output_dir.rename(target)
    directory_link(prepared.output_dir, target)
    assert prepared.intent_id not in controller.runs()
    with pytest.raises(PanelError) as error:
        controller.read_run(prepared.intent_id)
    assert error.value.code == "invalid_path" and len(fake.calls) == 1


def test_missing_records_on_empty_interrupted_run_remains_consultable(workspace, fake):
    fake.tag_error = KeyboardInterrupt()
    controller = LocalPanelController(workspace)
    prepared = prepare(controller)
    result = controller.execute(prepared)
    assert result.status == "interrupted" and result.run_name is None
    fake.tag_error = None
    fake.outcomes["bench-001"] = KeyboardInterrupt()
    prepared = prepare(controller)
    result = controller.execute(prepared)
    assert result.status == "interrupted" and result.snapshot.recorded_count == 0
    (prepared.output_dir / "responses.jsonl").unlink()
    assert controller.read_run(prepared.intent_id).recorded_count == 0


def test_write_permission_failure_preserves_manifest(workspace, fake, monkeypatch):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller)
    original = Path.open

    def denied(path, *args, **kwargs):
        if path == prepared.output_dir / "responses.jsonl":
            raise PermissionError("private path")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied)
    result = controller.execute(prepared)
    assert result.status == "failed"
    assert (prepared.output_dir / "manifest.json").is_file()
    assert "private" not in repr(result) and not fake.calls


def test_read_score_never_recreates_a_report_removed_during_audit(workspace, fake, monkeypatch):
    controller = LocalPanelController(workspace)
    prepared = prepare(controller, max_cases=1)
    controller.execute(prepared)
    controller.score(prepared.intent_id, DATASET, PROMPT)
    report_path = prepared.output_dir / "score-report.json"
    original = panel_module.score_run

    def audit_and_remove(*args):
        report = original(*args)
        report_path.unlink()
        return report

    monkeypatch.setattr(panel_module, "score_run", audit_and_remove)
    with pytest.raises(PanelError) as error:
        controller.read_score(prepared.intent_id, DATASET, PROMPT)
    assert error.value.code == "score_missing" and not report_path.exists()
    assert len(fake.calls) == 1
