"""Command-line entry point for EvalIA."""

from pathlib import Path

import typer

from evalia import __version__
from evalia.validation import validate_jsonl

app = typer.Typer(
    help="Herramientas de evaluación reproducible de modelos en español.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Agrupa los comandos de EvalIA."""


@app.command()
def version() -> None:
    """Muestra la versión instalada de EvalIA."""
    typer.echo(f"EvalIA {__version__}")


@app.command()
def validate(path: Path) -> None:
    """Comprueba la estructura JSONL con el contrato de casos 0.1.0."""
    try:
        count, issues = validate_jsonl(path)
    except (OSError, UnicodeError) as error:
        typer.echo(f"No se pudo leer {path}: {error}", err=True)
        raise typer.Exit(code=2) from error

    if issues:
        for issue in issues:
            typer.echo(issue, err=True)
        typer.echo(f"Validación fallida: {len(issues)} error(es) en {count} caso(s).", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Estructura válida: {count} casos.")
