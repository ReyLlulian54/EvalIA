"""Command-line entry point for EvalIA."""

import typer

from evalia import __version__

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
