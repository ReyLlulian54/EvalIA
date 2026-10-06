from typer.testing import CliRunner

from evalia import __version__
from evalia.cli import app

runner = CliRunner()


def test_help_lists_available_command() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "version" in result.output


def test_version_reports_installed_package_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"EvalIA {__version__}"


def test_unknown_command_is_rejected() -> None:
    result = runner.invoke(app, ["evaluate"])

    assert result.exit_code != 0
    assert "evaluate" in result.output
