"""Contrato compartido y proveedor simulado, sin red ni resultados de modelos."""

from decimal import Decimal

import pytest

from evalia.providers.base import (
    GenerationRequest,
    GenerationResponse,
    ModelProvider,
    ProviderFailure,
)
from evalia.providers.fixture import FixtureProvider


def request(case_id: str = "seed-001") -> GenerationRequest:
    return GenerationRequest(
        case_id=case_id,
        prompt="Extrae los campos de este texto privado",
        model_id="modelo-de-prueba",
        temperature=0.0,
        max_output_tokens=256,
        timeout_seconds=15.0,
    )


def test_request_has_explicit_limits_and_hides_prompt_in_repr() -> None:
    item = request()
    assert item.case_id == "seed-001"
    assert item.temperature == 0.0
    assert item.max_output_tokens == 256
    assert item.timeout_seconds == 15.0
    assert "texto privado" not in repr(item)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"case_id": ""}, "case_id"),
        ({"prompt": "   "}, "prompt"),
        ({"model_id": ""}, "model_id"),
        ({"temperature": -0.1}, "temperature"),
        ({"max_output_tokens": True}, "max_output_tokens"),
        ({"timeout_seconds": 0}, "timeout_seconds"),
    ],
)
def test_request_rejects_invalid_configuration(change: dict, message: str) -> None:
    values = {
        "case_id": "seed-001",
        "prompt": "Texto de prueba",
        "model_id": "modelo-de-prueba",
        "temperature": 0.0,
        "max_output_tokens": 256,
        "timeout_seconds": 15.0,
    }
    values.update(change)
    with pytest.raises(ValueError, match=message):
        GenerationRequest(**values)


def test_response_preserves_raw_output_and_unknown_usage() -> None:
    item = GenerationResponse(raw_text="{JSON incompleto")
    assert item.raw_text == "{JSON incompleto"
    assert item.reported_model_id is None
    assert item.prompt_tokens is None
    assert item.completion_tokens is None
    assert item.cost_usd is None
    assert "JSON incompleto" not in repr(item)


def test_reported_usage_is_explicit_and_nonnegative() -> None:
    item = GenerationResponse(
        raw_text="{}",
        reported_model_id="modelo-real-reportado",
        prompt_tokens=0,
        completion_tokens=12,
        cost_usd=Decimal("0.0012"),
    )
    assert item.completion_tokens == 12
    assert item.cost_usd == Decimal("0.0012")
    with pytest.raises(ValueError, match="prompt_tokens"):
        GenerationResponse(raw_text="{}", prompt_tokens=-1)
    with pytest.raises(ValueError, match="cost_usd"):
        GenerationResponse(raw_text="{}", cost_usd=Decimal("NaN"))


def test_fixture_provider_returns_only_supplied_response() -> None:
    expected = GenerationResponse(raw_text='{"closing_date": null}')
    provider: ModelProvider = FixtureProvider({"seed-001": expected})
    assert provider.provider_id == "fixture"
    assert provider.generate(request()) is expected
    assert provider.generate(request()).prompt_tokens is None


def test_fixture_provider_surfaces_typed_failure_and_missing_fixture() -> None:
    temporary = ProviderFailure("temporary", retryable=True, message="Fallo simulado")
    provider = FixtureProvider({"seed-001": temporary})
    with pytest.raises(ProviderFailure) as caught:
        provider.generate(request())
    assert caught.value.code == "temporary"
    assert caught.value.retryable is True
    with pytest.raises(ProviderFailure) as repeated:
        provider.generate(request())
    assert repeated.value is not caught.value

    with pytest.raises(ProviderFailure) as missing:
        provider.generate(request("seed-999"))
    assert missing.value.code == "fixture_missing"
    assert missing.value.retryable is False


def test_failure_code_cannot_be_a_raw_provider_message() -> None:
    with pytest.raises(ValueError, match="code"):
        ProviderFailure("token=PRIVATE", retryable=False, message="fallo")
