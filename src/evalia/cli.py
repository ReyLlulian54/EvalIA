"""Command-line entry point for EvalIA."""

import json
from pathlib import Path
from typing import Annotated

import typer

from evalia import __version__
from evalia.runner.inputs import RunInputError, run_dataset
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
    """Comprueba la estructura JSONL y la coherencia mecánica de los casos."""
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

    typer.echo(f"Validación mecánica correcta: {count} casos.")


@app.command()
def run(
    dataset: Annotated[Path, typer.Option(help="Conjunto JSONL validado.")],
    prompt: Annotated[Path, typer.Option(help="Plantilla JSON versionada.")],
    fixture: Annotated[Path, typer.Option(help="Respuestas simuladas en JSON; no usa red.")],
    output: Annotated[Path, typer.Option(help="Directorio nuevo para artefactos privados.")],
    max_cases: Annotated[
        int, typer.Option(min=1, max=100, help="Límite explícito de casos revisados.")
    ],
    model_id: Annotated[
        str, typer.Option(help="Identificador del modelo simulado.")
    ] = "simulado-v1",
    temperature: Annotated[float, typer.Option(min=0, max=2)] = 0.0,
    max_output_tokens: Annotated[int, typer.Option(min=1, max=2048)] = 256,
    timeout_seconds: Annotated[float, typer.Option(min=0.01, max=120)] = 30.0,
    max_retries: Annotated[int, typer.Option(min=0, max=2)] = 0,
) -> None:
    """Ejecuta un recorrido local con respuestas simuladas, sin modelos reales."""
    try:
        destination = run_dataset(
            dataset_path=dataset,
            prompt_path=prompt,
            fixture_path=fixture,
            output_dir=output,
            model_id=model_id,
            max_cases=max_cases,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    except RunInputError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error
    except KeyboardInterrupt as error:
        typer.echo(
            "Ejecución interrumpida; revise el manifiesto y las respuestas guardadas.", err=True
        )
        raise typer.Exit(code=130) from error
    except Exception as error:
        typer.echo("Ejecución fallida; revise el manifiesto y las respuestas guardadas.", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        "Ejecución con respuestas simuladas procesada: "
        f"{manifest['success_count']} éxito(s), {manifest['failure_count']} fallo(s). "
        f"Artefactos: {destination}"
    )
    if manifest["failure_count"]:
        raise typer.Exit(code=1)
