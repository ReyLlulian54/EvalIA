"""Arranque soportado del panel, con configuración local explícita."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Usar el mismo intérprete y fijar opciones por encima del entorno."""
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "app" / "local_app.py"),
            "--server.address=127.0.0.1",
            "--server.port=8501",
            "--server.enableCORS=true",
            "--server.enableXsrfProtection=true",
            "--browser.gatherUsageStats=false",
            "--client.toolbarMode=minimal",
            "--client.showErrorDetails=none",
            "--server.headless=true",
            "--server.fileWatcherType=none",
            "--server.runOnSave=false",
        ],
        cwd=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
