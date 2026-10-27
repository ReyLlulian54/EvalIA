"""El punto de entrada público se mantiene aislado de ejecución y datos privados."""

import ast
import builtins
import importlib
import io
import os
import socket
from pathlib import Path

import pytest

pytest.importorskip("streamlit", reason="AppTest requiere el extra panel")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app/public_app.py"
READER = ROOT / "src/evalia/reports/public_demo.py"
SCHEMA = ROOT / "src/evalia/reports/schema.py"
FORBIDDEN = (
    "evalia.panel",
    "evalia.runner",
    "evalia.providers",
    "evalia.cli",
    "evalia.reports.export_public",
)


def _forbidden_import(name: str) -> bool:
    return any(name == prefix or name.startswith(f"{prefix}.") for prefix in FORBIDDEN)


def _private_repository_path(value: object) -> bool:
    try:
        path = Path(value)
    except (TypeError, ValueError):
        return False
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        relative = path.resolve(strict=False).relative_to(ROOT)
    except (OSError, RuntimeError, ValueError):
        return False
    return bool(relative.parts) and relative.parts[0] in {"runs", "work"}


def test_public_import_graph_has_no_execution_modules() -> None:
    """Bloquea una dependencia futura aunque no se active en la vista inicial."""
    imported = set()
    for path, package in ((APP, None), (READER, "evalia.reports"), (SCHEMA, "evalia.reports")):
        source = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(source):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level:
                    assert package is not None
                    module = importlib.util.resolve_name(f"{'.' * node.level}{module}", package)
                if module:
                    imported.add(module)
                    imported.update(f"{module}.{alias.name}" for alias in node.names)

    assert not {name for name in imported if _forbidden_import(name)}


def test_public_app_runs_and_filters_without_private_io_or_network(monkeypatch) -> None:
    """Ejecuta la vista y un rerun con puertas de red, imports y archivos cerradas."""
    violations: list[str] = []
    original_import = builtins.__import__
    original_import_module = importlib.import_module
    original_open = builtins.open
    original_path_open = Path.open
    original_io_open = io.open
    original_os_open = os.open
    original_connect = socket.socket.connect
    original_socketpair = socket.socketpair
    inside_socketpair = False

    def checked_import(name, *args, **kwargs):
        module_globals = args[0] if len(args) > 0 else kwargs.get("globals")
        fromlist = args[2] if len(args) > 2 else kwargs.get("fromlist", ())
        level = args[3] if len(args) > 3 else kwargs.get("level", 0)
        resolved = name
        if level and module_globals and module_globals.get("__package__"):
            resolved = importlib.util.resolve_name(
                f"{'.' * level}{name}", module_globals["__package__"]
            )
        candidates = (resolved, *(f"{resolved}.{item}" for item in fromlist or ()))
        forbidden = next((item for item in candidates if _forbidden_import(item)), None)
        if forbidden:
            violations.append(f"import {forbidden}")
            raise AssertionError(f"Importación prohibida: {forbidden}")
        return original_import(name, *args, **kwargs)

    def checked_import_module(name, *args, **kwargs):
        package = args[0] if args else kwargs.get("package")
        resolved = importlib.util.resolve_name(name, package) if name.startswith(".") else name
        if _forbidden_import(resolved):
            violations.append(f"importlib {resolved}")
            raise AssertionError(f"Importación prohibida: {resolved}")
        return original_import_module(name, *args, **kwargs)

    def checked_open(file, *args, **kwargs):
        if _private_repository_path(file):
            violations.append(f"open {file}")
            raise AssertionError("Lectura privada prohibida")
        return original_open(file, *args, **kwargs)

    def checked_path_open(path, *args, **kwargs):
        if _private_repository_path(path):
            violations.append(f"Path.open {path}")
            raise AssertionError("Lectura privada prohibida")
        return original_path_open(path, *args, **kwargs)

    def checked_io_open(file, *args, **kwargs):
        if _private_repository_path(file):
            violations.append(f"io.open {file}")
            raise AssertionError("Lectura privada prohibida")
        return original_io_open(file, *args, **kwargs)

    def checked_os_open(file, *args, **kwargs):
        if _private_repository_path(file):
            violations.append(f"os.open {file}")
            raise AssertionError("Lectura privada prohibida")
        return original_os_open(file, *args, **kwargs)

    def blocked_connect(_socket, address):
        if inside_socketpair:
            return original_connect(_socket, address)
        violations.append(f"socket.connect {address}")
        raise AssertionError("Conexión de red prohibida")

    def blocked_connect_ex(_socket, address):
        violations.append(f"socket.connect_ex {address}")
        raise AssertionError("Conexión de red prohibida")

    def checked_socketpair(*args, **kwargs):
        nonlocal inside_socketpair
        inside_socketpair = True
        try:
            return original_socketpair(*args, **kwargs)
        finally:
            inside_socketpair = False

    monkeypatch.setattr(builtins, "__import__", checked_import)
    monkeypatch.setattr(importlib, "import_module", checked_import_module)
    monkeypatch.setattr(builtins, "open", checked_open)
    monkeypatch.setattr(Path, "open", checked_path_open)
    monkeypatch.setattr(io, "open", checked_io_open)
    monkeypatch.setattr(os, "open", checked_os_open)
    monkeypatch.setattr(socket.socket, "connect", blocked_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked_connect_ex)
    monkeypatch.setattr(socket, "socketpair", checked_socketpair)

    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    assert "Mostrando 36 de 36" in "\n".join(item.value for item in app.caption)

    app.selectbox(key="split_filter").set_value("test").run()
    app.text_input(key="case_id_filter").input("bench-001").run()
    assert not app.exception
    assert app.selectbox(key="case_detail").value == "bench-001"
    assert not violations
