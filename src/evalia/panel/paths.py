"""Catálogos y contención de rutas antes de cualquier lectura o escritura."""

import ntpath
import re
from pathlib import Path, PureWindowsPath

from evalia.panel.types import PanelError

_is_reserved = getattr(ntpath, "isreserved", lambda value: PureWindowsPath(value).is_reserved())


def _name(value: str) -> None:
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", value) is None
        or value.endswith(".")
        or _is_reserved(value)
    ):
        raise PanelError("invalid_path", "Seleccione un nombre del catálogo local permitido.")


def _resolve(path: Path, *, strict: bool = False) -> Path:
    try:
        return path.resolve(strict=strict)
    except (OSError, RuntimeError, ValueError) as error:
        raise PanelError("invalid_path", "No se pudo resolver la ruta local permitida.") from error


class PanelPaths:
    """La raíz es configuración confiable del proceso, nunca entrada del navegador."""

    def __init__(self, root: Path) -> None:
        self.root = _resolve(root, strict=True)

    def directory(self, *parts: str, required: bool = True) -> Path:
        current = self.root
        for part in parts:
            current = current / part
            # También rechaza raíces redirigidas a otro lugar dentro del checkout.
            if _resolve(current) != current:
                raise PanelError("invalid_path", "El directorio permitido está redirigido.")
            if current.exists() and not current.is_dir():
                raise PanelError("invalid_path", "Se esperaba un directorio local.")
            if required and not current.is_dir():
                raise PanelError("missing_directory", "Falta un directorio del proyecto.")
        return current

    def input(self, category: str, name: str) -> Path:
        suffix = {"datasets": ".jsonl", "prompts": ".json"}[category]
        _name(name)
        if not name.endswith(suffix):
            raise PanelError("invalid_path", "El archivo no pertenece al catálogo seleccionado.")
        directory = self.directory(category)
        path = _resolve(directory / name, strict=True)
        if path.parent != directory or not path.is_file():
            raise PanelError("invalid_path", "El archivo sale del directorio permitido.")
        return path

    def catalog(self, category: str) -> tuple[str, ...]:
        directory = self.directory(category)
        names = []
        for path in directory.iterdir():
            try:
                self.input(category, path.name)
            except PanelError:
                continue
            names.append(path.name)
        return tuple(sorted(names))

    def run(self, name: str, *, required: bool = True) -> Path:
        if not isinstance(name, str) or re.fullmatch(r"[a-f0-9]{32}", name) is None:
            raise PanelError("invalid_path", "Seleccione una corrida del panel.")
        return self.directory("runs", "panel", name, required=required)

    def artifact(self, run_name: str, filename: str, *, required: bool = True) -> Path:
        if filename not in {"manifest.json", "responses.jsonl", "score-report.json"}:
            raise PanelError("invalid_path", "Artefacto no admitido.")
        directory = self.run(run_name)
        path = directory / filename
        resolved = _resolve(path, strict=required)
        if resolved.parent != directory:
            raise PanelError("invalid_path", "El artefacto sale de la corrida seleccionada.")
        if resolved.exists() and not resolved.is_file():
            raise PanelError("invalid_path", "Se esperaba un archivo de artefacto.")
        return resolved

    def runs(self) -> tuple[str, ...]:
        directory = self.directory("runs", "panel", required=False)
        if not directory.exists():
            return ()
        names = []
        for path in directory.iterdir():
            try:
                self.run(path.name)
            except PanelError:
                continue
            names.append(path.name)
        return tuple(sorted(names))
