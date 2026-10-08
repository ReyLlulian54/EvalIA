"""Motor interno con registros durables por caso y manifiesto atómico."""

import hashlib
import json
import os
import platform
import re
import tempfile
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from evalia import __version__
from evalia.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ModelProvider,
    ProviderFailure,
)
from evalia.runner.schema import manifest_validator, record_validator, run_schema_version

RUN_SCHEMA_VERSION = run_schema_version()
MAX_RETRIES = 2


@dataclass(frozen=True, slots=True)
class RunProvenance:
    """Hashes comprobados por quien compone las solicitudes; None significa desconocido."""

    dataset_sha256: str | None = None
    prompt_sha256: str | None = None
    fixture_sha256: str | None = None
    model_digest: str | None = None
    prompt_id: str | None = None
    prompt_version: str | None = None
    source_commit: str | None = None

    def __post_init__(self) -> None:
        for name in ("dataset_sha256", "prompt_sha256", "fixture_sha256", "model_digest"):
            value = getattr(self, name)
            if value is not None and (
                not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
            ):
                raise ValueError(f"{name} debe ser SHA-256 hexadecimal")
        if self.source_commit is not None and (
            not isinstance(self.source_commit, str)
            or re.fullmatch(r"[0-9a-f]{40}", self.source_commit) is None
        ):
            raise ValueError("source_commit debe ser SHA-1 hexadecimal")
        if (self.prompt_id is None) != (self.prompt_version is None):
            raise ValueError("prompt_id y prompt_version deben conocerse juntos")
        if self.prompt_id is not None and self.prompt_sha256 is None:
            raise ValueError("un prompt versionado requiere prompt_sha256")
        if self.prompt_id is not None and (
            not isinstance(self.prompt_id, str)
            or re.fullmatch(r"[a-z][a-z0-9_-]{2,63}", self.prompt_id) is None
            or not isinstance(self.prompt_version, str)
            or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", self.prompt_version) is None
        ):
            raise ValueError("identidad o versión de prompt inválida")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _cost_text(cost: Decimal | None) -> str | None:
    if cost is None:
        return None
    return "0" if cost == 0 else format(cost, "f")


def _request_data(request: GenerationRequest) -> dict:
    return {
        "case_id": request.case_id,
        "prompt": request.prompt,
        "model_id": request.model_id,
        "temperature": request.temperature,
        "max_output_tokens": request.max_output_tokens,
        "timeout_seconds": request.timeout_seconds,
    }


def _validate_requests(requests: tuple[GenerationRequest, ...]) -> None:
    if not requests:
        raise ValueError("La ejecución requiere al menos una solicitud")
    if any(not isinstance(request, GenerationRequest) for request in requests):
        raise TypeError("Todas las solicitudes deben ser GenerationRequest")
    ids = [request.case_id for request in requests]
    if len(ids) != len(set(ids)):
        raise ValueError("Los case_id de una ejecución deben ser únicos")
    first = requests[0]
    config = (first.model_id, first.temperature, first.max_output_tokens, first.timeout_seconds)
    for request in requests[1:]:
        if (
            request.model_id,
            request.temperature,
            request.max_output_tokens,
            request.timeout_seconds,
        ) != config:
            raise ValueError("Todas las solicitudes deben usar el mismo modelo y límites")


def _manifest(
    requests: tuple[GenerationRequest, ...],
    provider_id: str,
    provenance: RunProvenance,
    max_retries: int,
    retry_delay_seconds: float,
) -> dict:
    first = requests[0]
    timestamp = _now()
    return {
        "schema_version": RUN_SCHEMA_VERSION,
        "run_id": uuid4().hex,
        "created_at": timestamp,
        "updated_at": timestamp,
        "finished_at": None,
        "status": "running",
        "evalia_version": __version__,
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "source_commit": provenance.source_commit,
        "provider_id": provider_id,
        "model_id": first.model_id,
        "model_digest": provenance.model_digest,
        "temperature": first.temperature,
        "max_output_tokens": first.max_output_tokens,
        "timeout_seconds": first.timeout_seconds,
        "max_retries": max_retries,
        "retry_delay_seconds": retry_delay_seconds,
        "requests_sha256": _digest([_request_data(request) for request in requests]),
        "dataset_sha256": provenance.dataset_sha256,
        "prompt_sha256": provenance.prompt_sha256,
        "fixture_sha256": provenance.fixture_sha256,
        "prompt_id": provenance.prompt_id,
        "prompt_version": provenance.prompt_version,
        "request_count": len(requests),
        "recorded_count": 0,
        "success_count": 0,
        "failure_count": 0,
        "last_case_id": None,
    }


def _write_manifest(path: Path, manifest: dict) -> None:
    manifest_validator().validate(manifest)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix="manifest-",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _append_record(stream, record: dict) -> None:
    record_validator().validate(record)
    payload = (_json(record) + "\n").encode("utf-8")
    position = stream.tell()
    try:
        written = stream.write(payload)
        if written != len(payload):
            raise OSError("Escritura parcial de responses.jsonl")
        stream.flush()
        os.fsync(stream.fileno())
    except BaseException as error:
        try:
            stream.seek(position)
            stream.truncate()
            stream.flush()
            os.fsync(stream.fileno())
        except OSError as rollback_error:
            error.add_note(
                f"No se pudo truncar el registro parcial: {type(rollback_error).__name__}"
            )
        raise


def _record_base(index: int, request: GenerationRequest, elapsed_ms: float, attempts: int) -> dict:
    return {
        "schema_version": RUN_SCHEMA_VERSION,
        "index": index,
        "case_id": request.case_id,
        "request_sha256": _digest(_request_data(request)),
        "recorded_at": _now(),
        "attempts": attempts,
        "elapsed_ms": elapsed_ms,
        "raw_text": None,
        "reported_model_id": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "cost_usd": None,
        "error_code": None,
        "retryable": None,
    }


def _persist(stream, path: Path, manifest: dict, record: dict) -> None:
    _append_record(stream, record)
    manifest["recorded_count"] += 1
    manifest["last_case_id"] = record["case_id"]
    if record["status"] == "success":
        manifest["success_count"] += 1
    else:
        manifest["failure_count"] += 1
    manifest["updated_at"] = _now()
    _write_manifest(path, manifest)


def run_requests(
    requests: Iterable[GenerationRequest],
    provider: ModelProvider,
    output_dir: Path,
    *,
    provenance: RunProvenance | None = None,
    max_retries: int = 0,
    retry_delay_seconds: float = 0.1,
) -> Path:
    """Ejecuta cada caso con reintentos acotados y persiste su resultado."""
    if type(max_retries) is not int or not 0 <= max_retries <= MAX_RETRIES:
        raise ValueError(f"max_retries debe estar entre 0 y {MAX_RETRIES}")
    if (
        isinstance(retry_delay_seconds, bool)
        or not isinstance(retry_delay_seconds, (int, float))
        or not 0 <= retry_delay_seconds <= 5
    ):
        raise ValueError("retry_delay_seconds debe estar entre 0 y 5")
    if provenance is not None and not isinstance(provenance, RunProvenance):
        raise TypeError("provenance debe ser RunProvenance")
    batch = tuple(requests)
    _validate_requests(batch)
    provider_id = provider.provider_id
    if not isinstance(provider_id, str) or not provider_id.strip():
        raise ValueError("provider_id debe ser texto no vacío")
    manifest = _manifest(
        batch, provider_id, provenance or RunProvenance(), max_retries, retry_delay_seconds
    )
    manifest_path = output_dir / "manifest.json"
    output_dir.mkdir(parents=True, exist_ok=False)
    _write_manifest(manifest_path, manifest)

    try:
        with (output_dir / "responses.jsonl").open("xb") as stream:
            for index, request in enumerate(batch):
                started = time.perf_counter()
                attempts = 0
                try:
                    while True:
                        attempts += 1
                        try:
                            response = provider.generate(request)
                            if not isinstance(response, GenerationResponse):
                                raise TypeError("El proveedor devolvió una respuesta inválida")
                            break
                        except ProviderFailure as failure:
                            if not failure.retryable or attempts > max_retries:
                                raise
                            time.sleep(retry_delay_seconds * attempts)
                except ProviderFailure as error:
                    elapsed = max(0.0, (time.perf_counter() - started) * 1000)
                    record = _record_base(index, request, elapsed, attempts)
                    record.update(
                        status="provider_error", error_code=error.code, retryable=error.retryable
                    )
                except Exception:
                    elapsed = max(0.0, (time.perf_counter() - started) * 1000)
                    record = _record_base(index, request, elapsed, attempts)
                    record.update(
                        status="internal_error",
                        error_code="unexpected_provider_error",
                        retryable=False,
                    )
                    _persist(stream, manifest_path, manifest, record)
                    raise
                else:
                    elapsed = max(0.0, (time.perf_counter() - started) * 1000)
                    record = _record_base(index, request, elapsed, attempts)
                    record.update(
                        status="success",
                        raw_text=response.raw_text,
                        reported_model_id=response.reported_model_id,
                        prompt_tokens=response.prompt_tokens,
                        completion_tokens=response.completion_tokens,
                        cost_usd=_cost_text(response.cost_usd),
                    )
                _persist(stream, manifest_path, manifest, record)
    except BaseException as error:
        manifest["status"] = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        manifest["finished_at"] = _now()
        manifest["updated_at"] = manifest["finished_at"]
        try:
            _write_manifest(manifest_path, manifest)
        except OSError as manifest_error:
            error.add_note(f"No se pudo actualizar manifest.json: {type(manifest_error).__name__}")
        raise

    manifest["status"] = "completed"
    manifest["finished_at"] = _now()
    manifest["updated_at"] = manifest["finished_at"]
    _write_manifest(manifest_path, manifest)
    return output_dir
