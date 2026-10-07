"""Criterios de aceptación del motor incremental, con proveedor sin red."""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from jsonschema import ValidationError

from evalia.providers.base import GenerationRequest, GenerationResponse, ProviderFailure
from evalia.providers.fixture import FixtureProvider
from evalia.runner.core import run_requests
from evalia.runner.schema import manifest_validator, record_validator, run_schema_version


def request(case_id: str, *, model_id: str = "modelo-prueba") -> GenerationRequest:
    return GenerationRequest(
        case_id=case_id,
        prompt=f"PROMPT_PRIVADO_{case_id}",
        model_id=model_id,
        temperature=0.0,
        max_output_tokens=128,
        timeout_seconds=10.0,
    )


def artifacts(path: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in (path / "responses.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    manifest_validator().validate(manifest)
    for record in records:
        record_validator().validate(record)
    return manifest, records


def test_successes_are_written_incrementally_under_one_manifest(tmp_path: Path) -> None:
    target = tmp_path / "run-1"
    provider = FixtureProvider(
        {
            "case-1": GenerationResponse(raw_text="{JSON incompleto"),
            "case-2": GenerationResponse(
                raw_text="{}",
                reported_model_id="modelo-reportado",
                prompt_tokens=0,
                completion_tokens=4,
                cost_usd=Decimal("0.000001"),
            ),
        }
    )
    assert run_requests([request("case-1"), request("case-2")], provider, target) == target

    manifest, records = artifacts(target)
    assert manifest["status"] == "completed"
    assert manifest["schema_version"] == run_schema_version()
    assert (manifest["request_count"], manifest["recorded_count"]) == (2, 2)
    assert (manifest["success_count"], manifest["failure_count"]) == (2, 0)
    assert manifest["provider_id"] == "fixture"
    assert manifest["model_id"] == "modelo-prueba"
    assert manifest["dataset_sha256"] is None
    assert manifest["prompt_sha256"] is None
    assert manifest["source_commit"] is None
    assert len(manifest["requests_sha256"]) == 64
    assert [record["index"] for record in records] == [0, 1]
    assert records[0]["raw_text"] == "{JSON incompleto"
    assert records[0]["prompt_tokens"] is None
    assert records[1]["cost_usd"] == "0.000001"
    assert records[1]["reported_model_id"] == "modelo-reportado"
    assert "PROMPT_PRIVADO" not in (target / "manifest.json").read_text(encoding="utf-8")
    assert "PROMPT_PRIVADO" not in (target / "responses.jsonl").read_text(encoding="utf-8")

    invalid = dict(records[0], error_code="should_not_exist")
    with pytest.raises(ValidationError):
        record_validator().validate(invalid)
    invalid_manifest = dict(manifest, finished_at=None)
    with pytest.raises(ValidationError):
        manifest_validator().validate(invalid_manifest)


def test_negative_zero_cost_is_serialized_as_zero(tmp_path: Path) -> None:
    target = tmp_path / "costo-cero"
    provider = FixtureProvider(
        {"case-1": GenerationResponse(raw_text="{}", cost_usd=Decimal("-0"))}
    )
    run_requests([request("case-1")], provider, target)
    _, records = artifacts(target)
    assert records[0]["cost_usd"] == "0"


def test_provider_failure_is_recorded_without_message_and_run_continues(tmp_path: Path) -> None:
    target = tmp_path / "run-2"
    provider = FixtureProvider(
        {
            "case-1": ProviderFailure(
                "temporary", retryable=True, message="SECRETO_EN_MENSAJE_DEL_PROVEEDOR"
            ),
            "case-2": GenerationResponse(raw_text="{}"),
        }
    )
    run_requests([request("case-1"), request("case-2")], provider, target)

    manifest, records = artifacts(target)
    assert manifest["status"] == "completed"
    assert (manifest["success_count"], manifest["failure_count"]) == (1, 1)
    assert records[0]["status"] == "provider_error"
    assert records[0]["error_code"] == "temporary"
    assert records[0]["retryable"] is True
    assert records[0]["raw_text"] is None
    assert records[1]["status"] == "success"
    assert "SECRETO_EN_MENSAJE" not in (target / "responses.jsonl").read_text(encoding="utf-8")


def test_write_failure_preserves_durable_previous_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import evalia.runner.core as runner

    target = tmp_path / "run-3"
    provider = FixtureProvider(
        {
            "case-1": GenerationResponse(raw_text="primera respuesta"),
            "case-2": GenerationResponse(raw_text="segunda respuesta"),
        }
    )
    original_append = runner._append_record
    calls = 0

    def fail_on_second(stream, record):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("disco simulado lleno")
        original_append(stream, record)

    monkeypatch.setattr(runner, "_append_record", fail_on_second)
    with pytest.raises(OSError, match="disco simulado lleno"):
        run_requests([request("case-1"), request("case-2")], provider, target)

    manifest, records = artifacts(target)
    assert manifest["status"] == "failed"
    assert (manifest["recorded_count"], manifest["success_count"]) == (1, 1)
    assert manifest["last_case_id"] == "case-1"
    assert [record["raw_text"] for record in records] == ["primera respuesta"]


def test_partial_line_is_truncated_when_append_fails(tmp_path: Path) -> None:
    import evalia.runner.core as runner

    source = tmp_path / "fuente"
    run_requests(
        [request("case-1")],
        FixtureProvider({"case-1": GenerationResponse(raw_text="{}")}),
        source,
    )
    _, records = artifacts(source)

    class ShortWrite:
        def __init__(self, stream):
            self.stream = stream

        def write(self, payload: bytes) -> int:
            return self.stream.write(payload[:5])

        def __getattr__(self, name):
            return getattr(self.stream, name)

    target = tmp_path / "parcial.jsonl"
    with target.open("wb") as stream:
        with pytest.raises(OSError, match="Escritura parcial"):
            runner._append_record(ShortWrite(stream), records[0])
    assert target.read_bytes() == b""


def test_unexpected_provider_error_is_generic_in_artifact(tmp_path: Path) -> None:
    class BrokenProvider:
        provider_id = "broken"

        def generate(self, item: GenerationRequest) -> GenerationResponse:
            if item.case_id == "case-2":
                raise RuntimeError("CLAVE_PRIVADA_EN_EXCEPCION")
            return GenerationResponse(raw_text="primera")

    target = tmp_path / "run-4"
    with pytest.raises(RuntimeError, match="CLAVE_PRIVADA"):
        run_requests([request("case-1"), request("case-2")], BrokenProvider(), target)
    manifest, records = artifacts(target)
    assert manifest["status"] == "failed"
    assert [record["status"] for record in records] == ["success", "internal_error"]
    assert records[1]["error_code"] == "unexpected_provider_error"
    assert records[1]["retryable"] is False
    assert "CLAVE_PRIVADA" not in (target / "responses.jsonl").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "requests",
    [
        [],
        [request("case-1"), request("case-1")],
        [request("case-1"), request("case-2", model_id="otro-modelo")],
    ],
)
def test_invalid_batch_is_rejected_before_creating_files(
    tmp_path: Path, requests: list[GenerationRequest]
) -> None:
    target = tmp_path / "sin-crear"
    with pytest.raises(ValueError):
        run_requests(requests, FixtureProvider({}), target)
    assert not target.exists()


def test_existing_directory_is_not_overwritten(tmp_path: Path) -> None:
    target = tmp_path / "existente"
    target.mkdir()
    sentinel = target / "archivo-del-usuario.txt"
    sentinel.write_text("conservar", encoding="utf-8")
    with pytest.raises(FileExistsError):
        run_requests([request("case-1")], FixtureProvider({}), target)
    assert sentinel.read_text(encoding="utf-8") == "conservar"
