"""Adaptador HTTP local para la API de chat de Ollama."""

import re
from types import TracebackType

import httpx

from evalia.providers.base import GenerationRequest, GenerationResponse, ProviderFailure

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def _local_base_url(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("La URL de Ollama debe ser texto")
    try:
        url = httpx.URL(value)
    except (httpx.InvalidURL, ValueError) as error:
        raise ValueError("URL de Ollama inválida") from error
    if (
        url.scheme != "http"
        or url.host not in {"127.0.0.1", "localhost", "::1"}
        or url.username
        or url.password
        or url.path not in {"", "/"}
        or url.query
        or url.fragment
    ):
        raise ValueError("Ollama solo acepta una URL HTTP local sin credenciales ni ruta")
    return str(url).rstrip("/")


def _failure(code: str, retryable: bool) -> ProviderFailure:
    return ProviderFailure(code, retryable=retryable, message=f"Ollama: {code}")


def _count(payload: dict, field: str) -> int | None:
    value = payload.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _failure("invalid_response", False)
    return value


class OllamaProvider:
    """Envía solicitudes solo al loopback; conserva el contenido y uso informados."""

    provider_id = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_URL,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = _local_base_url(base_url)
        self._client = client or httpx.Client(trust_env=False)
        self._owns_client = client is None

    def __enter__(self) -> "OllamaProvider":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._owns_client:
            self._client.close()

    def _request(
        self, method: str, path: str, *, timeout_seconds: float, payload: dict | None = None
    ) -> dict:
        timeout = httpx.Timeout(
            connect=min(timeout_seconds, 5.0),
            read=timeout_seconds,
            write=min(timeout_seconds, 5.0),
            pool=min(timeout_seconds, 5.0),
        )
        try:
            response = self._client.request(
                method, f"{self._base_url}{path}", json=payload, timeout=timeout
            )
        except httpx.TimeoutException as error:
            raise _failure("timeout", True) from error
        except (httpx.ConnectError, httpx.NetworkError) as error:
            raise _failure("connection_error", True) from error
        except httpx.HTTPError as error:
            raise _failure("transport_error", False) from error

        status = response.status_code
        if status != 200:
            if status == 400:
                raise _failure("invalid_request", False)
            if status == 404:
                raise _failure("model_not_found", False)
            if status == 429:
                raise _failure("rate_limited", True)
            if status == 408 or status >= 500:
                raise _failure("server_error", True)
            raise _failure("http_client_error", False)
        try:
            body = response.json()
        except ValueError as error:
            raise _failure("invalid_response", False) from error
        if not isinstance(body, dict):
            raise _failure("invalid_response", False)
        return body

    def model_digest(self, model_id: str) -> str:
        """Comprueba que el nombre exacto existe y devuelve su digest local."""
        body = self._request("GET", "/api/tags", timeout_seconds=5.0)
        models = body.get("models")
        if not isinstance(models, list):
            raise _failure("invalid_response", False)
        for model in models:
            if isinstance(model, dict) and model.get("name") == model_id:
                digest = model.get("digest")
                if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                    raise _failure("invalid_response", False)
                return digest
        raise _failure("model_not_found", False)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Aplica el tiempo de espera a I/O y devuelve la respuesta original."""
        body = self._request(
            "POST",
            "/api/chat",
            timeout_seconds=request.timeout_seconds,
            payload={
                "model": request.model_id,
                "messages": [{"role": "user", "content": request.prompt}],
                "stream": False,
                "think": False,
                "format": "json",
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_output_tokens,
                },
            },
        )
        message = body.get("message")
        reported_model = body.get("model")
        if (
            body.get("done") is not True
            or not isinstance(message, dict)
            or not isinstance(message.get("content"), str)
            or not isinstance(reported_model, str)
            or not reported_model.strip()
            or reported_model != request.model_id
        ):
            raise _failure("invalid_response", False)
        return GenerationResponse(
            raw_text=message["content"],
            reported_model_id=reported_model,
            prompt_tokens=_count(body, "prompt_eval_count"),
            completion_tokens=_count(body, "eval_count"),
            cost_usd=None,
        )
