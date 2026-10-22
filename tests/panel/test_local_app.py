"""Interacciones 7.c con controlador/motor reales y transporte simulado sin red."""

import json
import shutil
import socket
from pathlib import Path
from threading import local
from types import SimpleNamespace

import pytest

import evalia.panel
from evalia.panel import LocalPanelController
from evalia.providers.base import GenerationResponse, ProviderFailure
from evalia.runner import inputs

pytest.importorskip("streamlit", reason="Las pruebas de la interfaz requieren el extra panel")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app" / "local_app.py"
DATASET = "benchmark-v1.jsonl"
PROMPT = "extraction-v1.json"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    original_connect = socket.socket.connect
    original_pair = socket.socketpair
    context = local()

    def pair(*args, **kwargs):
        # asyncio crea su canal interno con socketpair; Windows lo emula en loopback.
        # La excepción solo vive durante esa llamada y en su hilo, nunca en la app.
        context.creating_pair = True
        try:
            return original_pair(*args, **kwargs)
        finally:
            context.creating_pair = False

    def guarded_connect(sock, address):
        if getattr(context, "creating_pair", False) and address[0] in {"127.0.0.1", "::1"}:
            return original_connect(sock, address)
        reject()

    def reject(*args, **kwargs):
        pytest.fail("Las interacciones del panel no deben abrir conexiones de red")

    monkeypatch.setattr(socket, "socketpair", pair)
    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket, "create_connection", reject)


@pytest.fixture
def environment(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    (root / "datasets").mkdir(parents=True)
    (root / "prompts").mkdir()
    for name in (DATASET, "seed.jsonl"):
        shutil.copyfile(ROOT / "datasets" / name, root / "datasets" / name)
    shutil.copyfile(ROOT / "prompts" / PROMPT, root / "prompts" / PROMPT)
    cases = [
        json.loads(line)
        for name in (DATASET, "seed.jsonl")
        for line in (root / "datasets" / name).read_text(encoding="utf-8").splitlines()
    ]
    state = SimpleNamespace(
        root=root,
        calls=[],
        tag_calls=0,
        tag_error=None,
        executions=0,
        controllers=[],
        outcomes={case["id"]: GenerationResponse(json.dumps(case["expected"])) for case in cases},
    )

    class SimulatedOllama:
        provider_id = "ollama"

        def __init__(self, base_url):
            assert base_url == "http://127.0.0.1:11434"

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
            outcome = state.outcomes[request.case_id]
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

    class ObservedController(LocalPanelController):
        def __init__(self, *args, **kwargs):
            super().__init__(root)
            state.controllers.append(self)

        def execute(self, prepared):
            state.executions += 1
            return super().execute(prepared)

    monkeypatch.setattr(inputs, "OllamaProvider", SimulatedOllama)
    monkeypatch.setattr(evalia.panel, "LocalPanelController", ObservedController)
    return state


def open_app():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    return app


def prepare(app, *, dataset=DATASET, count=3):
    app.selectbox(key="dataset_name").select(dataset)
    app.selectbox(key="prompt_name").select(PROMPT)
    app.number_input(key="max_cases").set_value(count)
    app.button(key="prepare_run").click().run()
    assert not app.exception
    return app.session_state["prepared_run"]


def execute(app):
    app.button(key="execute_run").click().run()
    assert not app.exception
    result = app.session_state["execution_result"]
    if result.run_name and app.selectbox(key="run_name").value is None:
        app.selectbox(key="run_name").select(result.run_name).run()
        assert not app.exception
    return result


def score_inputs(app, dataset=DATASET):
    app.selectbox(key="score_dataset_name").select(dataset)
    app.selectbox(key="score_prompt_name").select(PROMPT).run()
    assert not app.exception


def visible_text(app):
    kinds = ("markdown", "text", "caption", "info", "warning", "error", "success", "code")
    values = [str(element.value) for kind in kinds for element in app.get(kind)]
    values.extend(frame.value.to_string() for frame in app.dataframe)
    values.extend(frame.value.to_string() for frame in app.table)
    return "\n".join(values)


@pytest.mark.parametrize("dataset,expected", [(DATASET, 10), ("seed.jsonl", 9)])
def test_preparation_and_widget_reruns_never_infer(environment, dataset, expected):
    app = open_app()
    app.text_input(key="model_id").set_value("qwen3:8b").run()
    prepared = prepare(app, dataset=dataset, count=10)
    assert len(prepared.case_ids) == expected
    assert all(case_id in visible_text(app) for case_id in prepared.case_ids)
    app.run()
    assert not app.exception
    assert environment.executions == environment.tag_calls == 0
    assert environment.calls == []
    assert not (environment.root / "runs").exists()


def test_execute_consumes_intent_once_across_filters_reruns_and_new_session(environment):
    app = open_app()
    prepared = prepare(app)
    result = execute(app)
    assert result.status == "completed"
    assert environment.executions == environment.tag_calls == 1
    assert len(environment.calls) == 3
    original = (prepared.output_dir / "responses.jsonl").read_bytes()
    app.run()
    assert app.session_state["prepared_run"] is None
    assert all(button.disabled for button in app.button if button.key == "execute_run")
    for option in app.selectbox(key="status_filter").options:
        app.selectbox(key="status_filter").select(option).run()
        assert not app.exception
    fresh = open_app()
    assert fresh.session_state["prepared_run"] is None
    assert environment.executions == environment.tag_calls == 1
    assert len(environment.calls) == 3
    assert (prepared.output_dir / "responses.jsonl").read_bytes() == original
    assert len(tuple((environment.root / "runs" / "panel").iterdir())) == 1


@pytest.mark.parametrize("code", ["connection_error", "model_not_found", "invalid_response"])
def test_preflight_failure_is_safe_and_requires_new_preparation(environment, code):
    app = open_app()
    prepared = prepare(app, count=1)
    environment.tag_error = ProviderFailure(code, retryable=False, message="SECRET_HTTP_BODY")
    result = execute(app)
    assert result.status == "rejected" and result.code == code
    assert "SECRET_HTTP_BODY" not in visible_text(app)
    assert app.error
    assert not prepared.output_dir.exists()
    app.run()
    assert environment.executions == environment.tag_calls == 1
    assert environment.calls == []
    environment.tag_error = None
    prepare(app, count=1)
    assert execute(app).status == "completed"
    assert len(environment.calls) == 1


def test_changed_input_after_preparing_rejects_without_model_request(environment):
    app = open_app()
    prepared = prepare(app, count=1)
    path = environment.root / "datasets" / DATASET
    path.write_bytes(path.read_bytes() + b"\n")
    result = execute(app)
    assert result.status == "rejected"
    assert environment.tag_calls == 0 and environment.calls == []
    assert not prepared.output_dir.exists()
    assert app.error and not app.exception


def test_unprepared_widget_changes_do_not_change_execution_selection(environment):
    app = open_app()
    prepared = prepare(app, count=1)
    app.number_input(key="max_cases").set_value(3)
    app.text_input(key="model_id").set_value("unprepared-model")
    app.run()
    assert app.session_state["prepared_run"] == prepared
    result = execute(app)
    assert result.status == "completed"
    assert len(environment.calls) == 1
    assert result.snapshot.manifest["model_id"] == "qwen3:8b"


def test_invalid_preparation_clears_previous_intent(environment):
    app = open_app()
    prepare(app, count=1)
    app.text_input(key="model_id").set_value("")
    app.button(key="prepare_run").click().run()
    assert not app.exception and app.error
    assert app.session_state["prepared_run"] is None
    assert environment.executions == environment.tag_calls == 0
    assert environment.calls == []


def test_scoring_is_explicit_read_does_not_create_or_overwrite_report(environment):
    app = open_app()
    prepared = prepare(app, count=3)
    execute(app)
    report_path = prepared.output_dir / "score-report.json"
    assert not report_path.exists()
    score_inputs(app)
    app.button(key="read_score").click().run()
    assert not app.exception and not report_path.exists()
    app.button(key="calculate_score").click().run()
    assert not app.exception and report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["splits"]["dev"]["scored_count"] == 2
    assert report["splits"]["test"]["scored_count"] == 1
    assert report["evidence_literal"]["status"] == "not_observed"
    assert "not_observed" in visible_text(app)
    assert "No informado" in visible_text(app)
    before = report_path.read_bytes()
    app.button(key="read_score").click().run()
    app.run()
    assert not app.exception
    assert report_path.read_bytes() == before
    assert environment.executions == 1 and len(environment.calls) == 3


def test_empty_split_displays_zero_denominator_as_not_applicable(environment):
    app = open_app()
    prepare(app, count=1)
    execute(app)
    score_inputs(app)
    app.button(key="calculate_score").click().run()
    assert not app.exception
    text = visible_text(app)
    assert "No aplicable" in text
    assert environment.executions == 1 and len(environment.calls) == 1


def test_tampered_score_is_hidden_on_rerun_without_rewrite(environment):
    app = open_app()
    prepared = prepare(app, count=1)
    execute(app)
    score_inputs(app)
    app.button(key="calculate_score").click().run()
    report_path = prepared.output_dir / "score-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["cases"][0]["field_correct"]["student_required"] = False
    report_path.write_text(json.dumps(report), encoding="utf-8")
    before = report_path.read_bytes()
    app.run()
    assert not app.exception and app.error
    assert "not_observed" not in visible_text(app)
    assert report_path.read_bytes() == before
    assert environment.executions == 1 and len(environment.calls) == 1


def test_incompatible_scoring_preserves_artifacts_and_does_not_infer(environment):
    app = open_app()
    prepared = prepare(app, dataset="seed.jsonl", count=1)
    execute(app)
    score_inputs(app, "seed.jsonl")
    before = (prepared.output_dir / "responses.jsonl").read_bytes()
    app.button(key="calculate_score").click().run()
    assert not app.exception
    assert app.error or app.warning
    assert not (prepared.output_dir / "score-report.json").exists()
    assert (prepared.output_dir / "responses.jsonl").read_bytes() == before
    assert environment.executions == 1 and len(environment.calls) == 1


def test_raw_response_is_opt_in_and_rendered_only_as_literal_code(environment):
    raw = '<script>alert("PRIVATE_RAW_SENTINEL")</script>'
    environment.outcomes["bench-001"] = GenerationResponse(raw)
    app = open_app()
    prepare(app, count=1)
    execute(app)
    assert "PRIVATE_RAW_SENTINEL" not in visible_text(app)
    app.checkbox(key="show_raw").check().run()
    assert not app.exception
    assert any(raw in element.value for element in app.code)
    assert all("PRIVATE_RAW_SENTINEL" not in element.value for element in app.markdown)
    app.checkbox(key="show_raw").uncheck().run()
    assert "PRIVATE_RAW_SENTINEL" not in visible_text(app)
    assert environment.executions == 1 and len(environment.calls) == 1


def test_null_and_false_remain_distinct_in_raw_and_visible_explanation(environment):
    app = open_app()
    prepare(app, count=3)
    execute(app)
    app.checkbox(key="show_raw").check().run()
    assert not app.exception
    text = visible_text(app)
    assert "false = No" in text and "null = Desconocido" in text
    assert any('"student_required": false' in code.value for code in app.code)
    assert any('"student_required": null' in code.value for code in app.code)
    assert environment.executions == 1 and len(environment.calls) == 3


def test_selecting_another_run_resets_raw_opt_in(environment):
    raw = "PRIVATE_RAW_SECOND_RUN"
    app = open_app()
    first = prepare(app, count=1)
    execute(app)
    environment.outcomes["bench-001"] = GenerationResponse(raw)
    second = prepare(app, count=1)
    execute(app)
    app.selectbox(key="run_name").select(first.intent_id).run()
    app.checkbox(key="show_raw").check().run()
    app.selectbox(key="run_name").select(second.intent_id).run()
    assert not app.exception
    assert app.checkbox(key="show_raw").value is False
    assert raw not in visible_text(app)
    assert environment.executions == 2 and len(environment.calls) == 2


def test_new_session_shows_unclosed_run_without_resuming_or_mutating(environment):
    app = open_app()
    prepared = prepare(app, count=1)
    execute(app)
    path = prepared.output_dir / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.update(
        status="running", finished_at=None, recorded_count=0, success_count=0, last_case_id=None
    )
    path.write_text(json.dumps(manifest), encoding="utf-8")
    before = path.read_bytes()
    fresh = open_app()
    fresh.selectbox(key="run_name").select(prepared.intent_id).run()
    assert not fresh.exception
    assert "Sin cierre confirmado" in visible_text(fresh)
    assert fresh.session_state["prepared_run"] is None
    assert path.read_bytes() == before
    assert environment.executions == 1 and len(environment.calls) == 1


@pytest.mark.parametrize(
    "failure,status,count",
    [
        (RuntimeError("SECRET_INTERNAL_EXCEPTION"), "failed", 2),
        (KeyboardInterrupt(), "interrupted", 1),
        (ProviderFailure("timeout", retryable=True, message="SECRET_HTTP_BODY"), "completed", 3),
    ],
)
def test_partial_and_provider_failures_are_preserved_without_automatic_retry(
    environment, failure, status, count
):
    environment.outcomes["bench-002"] = failure
    app = open_app()
    prepared = prepare(app, count=3)
    result = execute(app)
    assert result.status == status and result.snapshot.recorded_count == count
    assert "SECRET_" not in visible_text(app)
    assert app.error or app.warning
    before = (prepared.output_dir / "responses.jsonl").read_bytes()
    calls = len(environment.calls)
    app.run()
    assert not app.exception
    assert environment.executions == 1 and len(environment.calls) == calls
    assert (prepared.output_dir / "responses.jsonl").read_bytes() == before
