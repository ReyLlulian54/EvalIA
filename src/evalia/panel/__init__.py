"""API interna del futuro panel web local."""

from evalia.panel.controller import LocalPanelController
from evalia.panel.types import ExecutionResult, PanelError, PreparedRun, RunOptions, RunSnapshot

__all__ = [
    "ExecutionResult",
    "LocalPanelController",
    "PanelError",
    "PreparedRun",
    "RunOptions",
    "RunSnapshot",
]
