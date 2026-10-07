"""Proveedor simulado determinista para pruebas locales sin red."""

from collections.abc import Mapping

from evalia.providers.base import GenerationRequest, GenerationResponse, ProviderFailure


class FixtureProvider:
    """Devuelve respuestas o fallos definidos explícitamente por case_id."""

    provider_id = "fixture"

    def __init__(self, outcomes: Mapping[str, GenerationResponse | ProviderFailure]) -> None:
        self._outcomes = dict(outcomes)
        for case_id, outcome in self._outcomes.items():
            if not isinstance(case_id, str) or not case_id.strip():
                raise ValueError("Cada fixture requiere un case_id no vacío")
            if not isinstance(outcome, (GenerationResponse, ProviderFailure)):
                raise TypeError("Cada fixture debe ser GenerationResponse o ProviderFailure")

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        outcome = self._outcomes.get(request.case_id)
        if outcome is None:
            raise ProviderFailure(
                "fixture_missing",
                retryable=False,
                message=f"No hay respuesta simulada para {request.case_id}",
            )
        if isinstance(outcome, ProviderFailure):
            raise ProviderFailure(outcome.code, retryable=outcome.retryable, message=str(outcome))
        return outcome
