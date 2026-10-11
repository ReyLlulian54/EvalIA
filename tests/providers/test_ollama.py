"""Contrato del adaptador Ollama con transporte HTTP simulado y sin red."""

import json

import httpx
import pytest

from evalia.providers.base import GenerationRequest, ProviderFailure
from evalia.providers.ollama import OllamaProvider


def _request() -> GenerationRequest:
    return GenerationRequest(
        case_id="seed-001",
        prompt="PROMPT_PRIVADO",
        model_id="qwen3:8b",
        temperature=0.0,
        max_output_tokens=128,
        timeout_seconds=7.5,
    )


def test_chat_preserves_raw_text_usage_and_exact_request_options() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "model": "qwen3:8b",
                "message": {"role": "assistant", "content": "{JSON incompleto"},
                "done": True,
                "prompt_eval_count": 0,
                "eval_count": 12,
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as client:
        provider = OllamaProvider(client=client)
        response = provider.generate(_request())

    assert provider.provider_id == "ollama"
    assert response.raw_text == "{JSON incompleto"
    assert response.reported_model_id == "qwen3:8b"
    assert (response.prompt_tokens, response.completion_tokens) == (0, 12)
    assert response.cost_usd is None
    assert len(seen) == 1
    assert seen[0].method == "POST"
    assert str(seen[0].url) == "http://127.0.0.1:11434/api/chat"
    assert json.loads(seen[0].content) == {
        "model": "qwen3:8b",
        "messages": [{"role": "user", "content": "PROMPT_PRIVADO"}],
        "stream": False,
        "think": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_predict": 128},
    }
    assert seen[0].extensions["timeout"]["read"] == 7.5


def test_missing_usage_stays_unknown_and_empty_content_is_preserved() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"model": "qwen3:8b", "message": {"content": ""}, "done": True}
        )

    with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as client:
        response = OllamaProvider(client=client).generate(_request())
    assert response.raw_text == ""
    assert response.prompt_tokens is None
    assert response.completion_tokens is None
    assert response.cost_usd is None


@pytest.mark.parametrize(
    ("status", "code", "retryable"),
    [
        (400, "invalid_request", False),
        (404, "model_not_found", False),
        (429, "rate_limited", True),
        (500, "server_error", True),
        (503, "server_error", True),
    ],
)
def test_http_failures_are_classified_without_server_message(
    status: int, code: str, retryable: bool
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "PRIVATE_TOKEN"})

    with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as client:
        with pytest.raises(ProviderFailure) as failure:
            OllamaProvider(client=client).generate(_request())
    assert (failure.value.code, failure.value.retryable) == (code, retryable)
    assert "PRIVATE_TOKEN" not in str(failure.value)


def test_timeout_is_retryable_without_echoing_prompt() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("PROMPT_PRIVADO")

    with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as client:
        with pytest.raises(ProviderFailure) as failure:
            OllamaProvider(client=client).generate(_request())
    assert failure.value.code == "timeout"
    assert failure.value.retryable is True
    assert "PROMPT_PRIVADO" not in str(failure.value)


@pytest.mark.parametrize(
    "payload",
    [
        {"model": "qwen3:8b", "message": {"content": "{}"}, "done": False},
        {"model": "qwen3:8b", "message": {}, "done": True},
        {"model": "qwen3:8b", "message": {"content": "{}"}, "done": True, "eval_count": -1},
        {"model": "otro:7b", "message": {"content": "{}"}, "done": True},
    ],
)
def test_incomplete_or_invalid_response_is_not_recorded_as_success(payload: dict) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as client:
        with pytest.raises(ProviderFailure) as failure:
            OllamaProvider(client=client).generate(_request())
    assert failure.value.code == "invalid_response"
    assert failure.value.retryable is False


def test_model_digest_requires_exact_local_model_name() -> None:
    digest = "a" * 64

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/tags"
        return httpx.Response(
            200,
            json={"models": [{"name": "qwen3:8b", "digest": digest}, {"name": "otro:7b"}]},
        )

    with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as client:
        provider = OllamaProvider(client=client)
        assert provider.model_digest("qwen3:8b") == digest
        with pytest.raises(ProviderFailure) as failure:
            provider.model_digest("qwen3:7b")
    assert failure.value.code == "model_not_found"


@pytest.mark.parametrize(
    "url",
    [
        "https://api.example.com",
        "http://192.168.1.10:11434",
        "http://0.0.0.0:11434",
        "http://user:pass@127.0.0.1:11434",
        "http://127.0.0.1:11434/other",
    ],
)
def test_provider_rejects_nonlocal_or_ambiguous_endpoints(url: str) -> None:
    with pytest.raises(ValueError):
        OllamaProvider(base_url=url)
