"""El lanzador fija protecciones incluso con configuración externa insegura."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_launcher_pins_local_server_and_preserves_exit_code(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "panel_launcher", ROOT / "scripts/run_local_panel.py"
    )
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    monkeypatch.setenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    monkeypatch.setenv("STREAMLIT_SERVER_ENABLE_CORS", "false")
    calls = []

    def launch(command, *, cwd):
        calls.append((command, cwd))
        return 7

    monkeypatch.setattr(launcher.subprocess, "call", launch)
    assert launcher.main() == 7
    command, cwd = calls[0]
    assert cwd == ROOT
    assert command[:5] == [sys.executable, "-m", "streamlit", "run", str(ROOT / "app/local_app.py")]
    assert "--server.address=127.0.0.1" in command
    assert "--server.port=8501" in command
    assert "--server.enableCORS=true" in command
    assert "--server.enableXsrfProtection=true" in command
    assert "--browser.gatherUsageStats=false" in command
    assert "--client.toolbarMode=minimal" in command
    assert "--client.showErrorDetails=none" in command
    assert "--server.fileWatcherType=none" in command
    assert "--server.runOnSave=false" in command
