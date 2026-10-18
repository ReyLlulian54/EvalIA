"""Contrato Python del panel local, independiente de Streamlit."""

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ExecutionStatus = Literal["rejected", "completed", "failed", "interrupted"]


class PanelError(ValueError):
    """Error seguro para presentar: código estable y mensaje sin datos crudos."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class RunOptions:
    model_id: str = "qwen3:8b"
    max_cases: int = 10
    temperature: float = 0.0
    max_output_tokens: int = 256
    timeout_seconds: float = 120.0
    max_retries: int = 0

    def __post_init__(self) -> None:
        if (
            not isinstance(self.model_id, str)
            or not self.model_id.strip()
            or self.model_id != self.model_id.strip()
            or any(ord(c) < 32 for c in self.model_id)
        ):
            raise PanelError("invalid_model", "Indique el nombre exacto del modelo local.")
        for name, lower, upper in (
            ("max_cases", 1, 100),
            ("max_output_tokens", 1, 2048),
            ("max_retries", 0, 2),
        ):
            value = getattr(self, name)
            if type(value) is not int or not lower <= value <= upper:
                raise PanelError("invalid_options", f"{name}: entero entre {lower} y {upper}.")
        for name, lower, upper in (("temperature", 0, 2), ("timeout_seconds", 0.01, 120)):
            value = getattr(self, name)
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or not lower <= value <= upper
            ):
                raise PanelError("invalid_options", f"{name}: número entre {lower} y {upper}.")


@dataclass(frozen=True, slots=True)
class PreparedRun:
    intent_id: str
    dataset_name: str
    prompt_name: str
    dataset_path: Path = field(repr=False)
    prompt_path: Path = field(repr=False)
    output_dir: Path = field(repr=False)
    dataset_sha256: str
    prompt_sha256: str
    prompt_id: str
    prompt_version: str
    case_ids: tuple[str, ...]
    splits: tuple[str, ...]
    options: RunOptions


@dataclass(frozen=True, slots=True)
class RunSnapshot:
    """Datos de los esquemas existentes; sin raw_text salvo petición explícita."""

    run_name: str
    manifest: dict = field(repr=False)
    records: tuple[dict, ...] = field(repr=False)
    warnings: tuple[str, ...] = ()

    @property
    def recorded_count(self) -> int:
        return len(self.records)


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    status: ExecutionStatus
    code: str
    message: str
    run_name: str | None = None
    snapshot: RunSnapshot | None = field(default=None, repr=False)
