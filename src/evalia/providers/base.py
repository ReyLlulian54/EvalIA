"""Contrato Python compartido por el motor y sus adaptadores."""

import math
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol


def _nonblank(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} debe ser texto no vacío")


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Solicitud de un caso con prompt ya compuesto y límites explícitos."""

    case_id: str
    prompt: str = field(repr=False)
    model_id: str
    temperature: float
    max_output_tokens: int
    timeout_seconds: float

    def __post_init__(self) -> None:
        _nonblank(self.case_id, "case_id")
        _nonblank(self.prompt, "prompt")
        _nonblank(self.model_id, "model_id")
        if (
            isinstance(self.temperature, bool)
            or not isinstance(self.temperature, (int, float))
            or not math.isfinite(self.temperature)
            or self.temperature < 0
        ):
            raise ValueError("temperature debe ser finita y no negativa")
        if (
            isinstance(self.max_output_tokens, bool)
            or not isinstance(self.max_output_tokens, int)
            or self.max_output_tokens <= 0
        ):
            raise ValueError("max_output_tokens debe ser un entero positivo")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not math.isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds debe ser finito y positivo")


@dataclass(frozen=True, slots=True)
class GenerationResponse:
    """Salida cruda; los datos de uso siguen desconocidos si no se informan."""

    raw_text: str = field(repr=False)
    reported_model_id: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cost_usd: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.raw_text, str):
            raise ValueError("raw_text debe ser texto, incluso si está vacío")
        if self.reported_model_id is not None:
            _nonblank(self.reported_model_id, "reported_model_id")
        for name in ("prompt_tokens", "completion_tokens"):
            value = getattr(self, name)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                raise ValueError(f"{name} debe ser un entero no negativo o None")
        if self.cost_usd is not None and (
            not isinstance(self.cost_usd, Decimal)
            or not self.cost_usd.is_finite()
            or self.cost_usd < 0
        ):
            raise ValueError("cost_usd debe ser Decimal finito no negativo o None")


class ProviderFailure(Exception):
    """Fallo tipado; el motor decidirá después si corresponde reintentar."""

    def __init__(self, code: str, *, retryable: bool, message: str) -> None:
        if not isinstance(code, str) or re.fullmatch(r"[a-z][a-z0-9_]{0,63}", code) is None:
            raise ValueError("code debe ser un identificador estable en minúsculas")
        _nonblank(message, "message")
        if not isinstance(retryable, bool):
            raise ValueError("retryable debe ser booleano")
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ModelProvider(Protocol):
    """Interfaz única que usará el motor para cualquier proveedor."""

    @property
    def provider_id(self) -> str: ...

    def generate(self, request: GenerationRequest) -> GenerationResponse: ...
