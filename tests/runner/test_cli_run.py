"""Criterios de aceptación de 4.3: CLI, entradas, reintentos e interrupción."""

import hashlib
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from evalia.cli import app
from evalia.providers.base import GenerationRequest, GenerationResponse, ProviderFailure
from evalia.runner.core import run_requests
from evalia.runner.inputs import compose_requests, load_prompt, load_reviewed_cases
from evalia.runner.schema import manifest_validator, record_validator

ROOT = Path(__file__).resolve().parents[2]
CLI = CliRunner()


def _artifacts(path: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in (path / "responses.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    manifest_validator().validate(manifest)
    for record in records:
        record_validator().validate(record)
    return manifest, records


def _command(output: Path, *, max_cases: int = 2) -> list[str]:
    return [
        "run",
        "--dataset",
        str(ROOT / "datasets/seed.jsonl"),
        "--prompt",
        str(ROOT / "prompts/extraction-v1.json"),
        "--fixture",
        str(ROOT / "examples/fixtures/seed-two.json"),
        "--output",
        str(output),
        "--model-id",
        "simulado-v1",
        "--max-cases",
        str(max_cases),
        "--timeout-seconds",
        "7.5",
    ]


def test_cli_completes_offline_run_with_verified_input_hashes(tmp_path: Path) -> None:
    target = tmp_path / "run"
    result = CLI.invoke(app, _command(target))
    assert result.exit_code == 0, result.output

    manifest, records = _artifacts(target)
    assert manifest["status"] == "completed"
    assert manifest["request_count"] == 2
    assert (
        manifest["dataset_sha256"]
        == hashlib.sha256((ROOT / "datasets/seed.jsonl").read_bytes()).hexdigest()
    )
    assert (
        manifest["prompt_sha256"]
        == hashlib.sha256((ROOT / "prompts/extraction-v1.json").read_bytes()).hexdigest()
    )
    assert (
        manifest["fixture_sha256"]
        == hashlib.sha256((ROOT / "examples/fixtures/seed-two.json").read_bytes()).hexdigest()
    )
    assert (manifest["prompt_id"], manifest["prompt_version"]) == ("convocatorias-es", "1.0.0")
    assert manifest["max_retries"] == 0
    assert manifest["timeout_seconds"] == 7.5
    assert [record["case_id"] for record in records] == ["seed-001", "seed-002"]
    assert [record["attempts"] for record in records] == [1, 1]
    assert all(record["status"] == "success" for record in records)
    assert "simuladas" in result.output.lower()


def test_cli_limits_selected_reviewed_cases(tmp_path: Path) -> None:
    target = tmp_path / "one"
    result = CLI.invoke(app, _command(target, max_cases=1))
    assert result.exit_code == 0, result.output
    manifest, records = _artifacts(target)
    assert manifest["request_count"] == 1
    assert [record["case_id"] for record in records] == ["seed-001"]


def test_cli_reports_case_failures_with_nonzero_exit(tmp_path: Path) -> None:
    target = tmp_path / "missing-fixture"
    result = CLI.invoke(app, _command(target, max_cases=3))
    assert result.exit_code == 1
    manifest, records = _artifacts(target)
    assert manifest["status"] == "completed"
    assert manifest["failure_count"] == 1
    assert records[-1]["error_code"] == "fixture_missing"
    assert "1 fallo(s)" in result.output


def test_bad_input_does_not_create_run_directory(tmp_path: Path) -> None:
    dataset = tmp_path / "bad.jsonl"
    dataset.write_text("no es JSON\n", encoding="utf-8")
    target = tmp_path / "run"
    command = _command(target)
    command[command.index("--dataset") + 1] = str(dataset)
    result = CLI.invoke(app, command)
    assert result.exit_code != 0
    assert not target.exists()


def test_prompt_must_have_exactly_one_text_placeholder(tmp_path: Path) -> None:
    prompt = tmp_path / "bad-prompt.json"
    prompt.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "prompt_id": "test-prompt",
                "version": "1.0.0",
                "template": "{{text}} y {{text}}",
            }
        ),
        encoding="utf-8",
    )
    target = tmp_path / "run"
    command = _command(target)
    command[command.index("--prompt") + 1] = str(prompt)
    result = CLI.invoke(app, command)
    assert result.exit_code != 0
    assert not target.exists()


def test_composition_inserts_case_text_without_interpreting_its_braces() -> None:
    prompt = load_prompt(ROOT / "prompts/extraction-v1.json")
    text = "Convocatoria {{text}} con dato literal"
    requests = compose_requests(
        [{"id": "case-1", "text": text}],
        prompt,
        model_id="simulado-v1",
        temperature=0.0,
        max_output_tokens=128,
        timeout_seconds=7.5,
    )
    assert len(requests) == 1
    assert requests[0].prompt.endswith(text)
    assert requests[0].timeout_seconds == 7.5


def test_dataset_reader_keeps_unicode_line_separator_inside_text(tmp_path: Path) -> None:
    case = json.loads((ROOT / "datasets/seed.jsonl").read_text(encoding="utf-8").splitlines()[0])
    case["text"] += "\u2028final"
    path = tmp_path / "unicode.jsonl"
    path.write_text(json.dumps(case, ensure_ascii=False) + "\n", encoding="utf-8")
    selected, _ = load_reviewed_cases(path, 1)
    assert selected[0]["text"].endswith("\u2028final")


def _request(case_id: str) -> GenerationRequest:
    return GenerationRequest(case_id, "prompt", "simulado", 0.0, 128, 5.0)


def test_retries_only_typed_transient_failures_and_records_attempts(tmp_path: Path) -> None:
    class ScriptedProvider:
        provider_id = "scripted"

        def __init__(self) -> None:
            self.calls: dict[str, int] = {}

        def generate(self, request: GenerationRequest) -> GenerationResponse:
            count = self.calls.get(request.case_id, 0) + 1
            self.calls[request.case_id] = count
            if request.case_id == "transient" and count == 1:
                raise ProviderFailure("timeout", retryable=True, message="secreto-privado")
            if request.case_id == "permanent":
                raise ProviderFailure("invalid_request", retryable=False, message="no reintentar")
            return GenerationResponse(raw_text="{}")

    provider = ScriptedProvider()
    run_requests(
        [_request("transient"), _request("permanent")],
        provider,
        tmp_path / "retry",
        max_retries=2,
        retry_delay_seconds=0,
    )
    manifest, records = _artifacts(tmp_path / "retry")
    assert manifest["status"] == "completed"
    assert provider.calls == {"transient": 2, "permanent": 1}
    assert [record["attempts"] for record in records] == [2, 1]
    assert [record["status"] for record in records] == ["success", "provider_error"]
    assert "secreto-privado" not in (tmp_path / "retry/responses.jsonl").read_text()


def test_transient_failure_stops_after_bounded_retries(tmp_path: Path) -> None:
    class AlwaysFails:
        provider_id = "scripted"

        def __init__(self) -> None:
            self.calls = 0

        def generate(self, request: GenerationRequest) -> GenerationResponse:
            self.calls += 1
            raise ProviderFailure("timeout", retryable=True, message="temporal")

    provider = AlwaysFails()
    run_requests(
        [_request("case-1")],
        provider,
        tmp_path / "exhausted",
        max_retries=2,
        retry_delay_seconds=0,
    )
    _, records = _artifacts(tmp_path / "exhausted")
    assert provider.calls == 3
    assert records[0]["attempts"] == 3
    assert records[0]["error_code"] == "timeout"


def test_keyboard_interrupt_preserves_previous_case(tmp_path: Path) -> None:
    class InterruptedProvider:
        provider_id = "scripted"

        def generate(self, request: GenerationRequest) -> GenerationResponse:
            if request.case_id == "case-2":
                raise KeyboardInterrupt
            return GenerationResponse(raw_text="primero")

    target = tmp_path / "interrupted"
    with pytest.raises(KeyboardInterrupt):
        run_requests([_request("case-1"), _request("case-2")], InterruptedProvider(), target)
    manifest, records = _artifacts(target)
    assert manifest["status"] == "interrupted"
    assert manifest["recorded_count"] == 1
    assert [record["case_id"] for record in records] == ["case-1"]


def test_cli_does_not_print_unexpected_provider_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(**kwargs):
        raise RuntimeError("SECRETO_DE_PROVEEDOR")

    monkeypatch.setattr("evalia.cli.run_dataset", fail)
    result = CLI.invoke(app, _command(tmp_path / "run"))
    assert result.exit_code != 0
    assert "SECRETO_DE_PROVEEDOR" not in result.output
