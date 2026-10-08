"""Carga entradas versionadas y compone solicitudes del recorrido sin red."""

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from importlib import resources
from io import StringIO
from pathlib import Path

from jsonschema import Draft202012Validator

from evalia.providers.base import GenerationRequest, GenerationResponse, ProviderFailure
from evalia.providers.fixture import FixtureProvider
from evalia.providers.ollama import DEFAULT_OLLAMA_URL, OllamaProvider
from evalia.runner.core import RunProvenance, run_requests
from evalia.validation import validate_jsonl_lines


class RunInputError(ValueError):
    """Entrada rechazada antes de crear el directorio de ejecución."""


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    prompt_id: str
    version: str
    template: str = field(repr=False)
    sha256: str


def _schema(name: str) -> dict:
    packaged = resources.files("evalia").joinpath(f"schemas/{name}")
    path = (
        packaged if packaged.is_file() else Path(__file__).resolve().parents[3] / "schemas" / name
    )
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _load_json(path: Path, schema_name: str, label: str) -> tuple[dict, str]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise RunInputError(f"{label}: no se pudo leer el archivo") from error
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RunInputError(f"{label}: JSON UTF-8 inválido") from error
    validator = Draft202012Validator(_schema(schema_name))
    if not validator.is_valid(document):
        raise RunInputError(f"{label}: no cumple el esquema {schema_name}")
    return document, hashlib.sha256(raw).hexdigest()


def load_prompt(path: Path) -> PromptTemplate:
    """Valida la plantilla y conserva el hash de sus bytes exactos."""
    document, sha256 = _load_json(path, "evalia-prompt.schema.json", "Prompt")
    template = document["template"]
    if template.count("{{text}}") != 1:
        raise RunInputError("Prompt: la plantilla requiere exactamente un {{text}}")
    return PromptTemplate(document["prompt_id"], document["version"], template, sha256)


def load_fixture(path: Path) -> tuple[FixtureProvider, str]:
    """Carga respuestas simuladas sin uso, costo ni llamadas de red."""
    document, sha256 = _load_json(path, "evalia-fixture.schema.json", "Fixture")
    outcomes: dict[str, GenerationResponse | ProviderFailure] = {}
    for case_id, outcome in document["outcomes"].items():
        if "raw_text" in outcome:
            outcomes[case_id] = GenerationResponse(raw_text=outcome["raw_text"])
        else:
            outcomes[case_id] = ProviderFailure(
                outcome["error_code"],
                retryable=outcome["retryable"],
                message="Fallo simulado por fixture",
            )
    return FixtureProvider(outcomes), sha256


def load_reviewed_cases(path: Path, max_cases: int) -> tuple[list[dict], str]:
    """Valida el contenido exacto que se ejecutará y selecciona casos revisados."""
    if type(max_cases) is not int or not 1 <= max_cases <= 100:
        raise RunInputError("max_cases debe estar entre 1 y 100")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise RunInputError("Conjunto: no se pudo leer el archivo") from error
    try:
        content = raw.decode("utf-8")
    except UnicodeError as error:
        raise RunInputError("Conjunto: se requiere UTF-8") from error
    lines = list(StringIO(content, newline=None))
    _, issues = validate_jsonl_lines(lines)
    if issues:
        raise RunInputError(
            f"Conjunto inválido: {len(issues)} problema(s); ejecute evalia validate para verlos"
        )
    selected: list[dict] = []
    for line in lines:
        case = json.loads(line)
        if case["review_status"] == "reviewed":
            selected.append(case)
            if len(selected) == max_cases:
                break
    if not selected:
        raise RunInputError("Conjunto: no hay casos revisados para ejecutar")
    return selected, hashlib.sha256(raw).hexdigest()


def compose_requests(
    cases: list[dict],
    prompt: PromptTemplate,
    *,
    model_id: str,
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: float,
) -> list[GenerationRequest]:
    """Inserta cada texto una sola vez, sin interpretar llaves presentes en el caso."""
    return [
        GenerationRequest(
            case_id=case["id"],
            prompt=prompt.template.replace("{{text}}", case["text"]),
            model_id=model_id,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
        )
        for case in cases
    ]


def _source_commit() -> str | None:
    """Solo declara el commit si el paquete viene de un checkout limpio."""
    root = Path(__file__).resolve().parents[3]
    if not (root / ".git").exists():
        return None
    try:
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            capture_output=True,
            text=True,
            timeout=3,
            check=True,
        )
        if status.stdout.strip():
            return None
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return commit if len(commit) == 40 else None


def run_dataset(
    *,
    dataset_path: Path,
    prompt_path: Path,
    fixture_path: Path | None,
    output_dir: Path,
    model_id: str,
    max_cases: int,
    temperature: float,
    max_output_tokens: int,
    timeout_seconds: float,
    max_retries: int,
    provider_kind: str = "fixture",
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> Path:
    """Ejecuta el mismo contrato con fixture o un modelo Ollama local."""
    if provider_kind not in {"fixture", "ollama"}:
        raise RunInputError("Proveedor desconocido; use fixture u ollama")
    if provider_kind == "fixture" and fixture_path is None:
        raise RunInputError("El proveedor fixture requiere --fixture")
    if provider_kind == "ollama" and fixture_path is not None:
        raise RunInputError("El proveedor ollama no acepta --fixture")
    if provider_kind == "ollama" and model_id == "simulado-v1":
        raise RunInputError("Indique --model-id con el nombre exacto del modelo local")
    cases, dataset_sha256 = load_reviewed_cases(dataset_path, max_cases)
    prompt = load_prompt(prompt_path)
    requests = compose_requests(
        cases,
        prompt,
        model_id=model_id,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        timeout_seconds=timeout_seconds,
    )

    def execute(provider, fixture_sha256: str | None, model_digest: str | None) -> Path:
        return run_requests(
            requests,
            provider,
            output_dir,
            provenance=RunProvenance(
                dataset_sha256=dataset_sha256,
                prompt_sha256=prompt.sha256,
                fixture_sha256=fixture_sha256,
                model_digest=model_digest,
                prompt_id=prompt.prompt_id,
                prompt_version=prompt.version,
                source_commit=_source_commit(),
            ),
            max_retries=max_retries,
        )

    if provider_kind == "fixture":
        provider, fixture_sha256 = load_fixture(fixture_path)
        return execute(provider, fixture_sha256, None)
    try:
        local_provider = OllamaProvider(base_url=ollama_url)
    except ValueError as error:
        raise RunInputError(str(error)) from error
    with local_provider as provider:
        model_digest = provider.model_digest(model_id)
        return execute(provider, None, model_digest)
