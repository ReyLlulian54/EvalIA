"""Command-line entry point for EvalIA."""

import json
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from evalia import __version__
from evalia.providers.base import ProviderFailure
from evalia.providers.ollama import DEFAULT_OLLAMA_URL
from evalia.runner.inputs import RunInputError, run_dataset
from evalia.validation import validate_jsonl

app = typer.Typer(
    help="Herramientas de evaluación reproducible de modelos en español.",
    no_args_is_help=True,
    add_completion=False,
)


class ProviderChoice(StrEnum):
    fixture = "fixture"
    ollama = "ollama"


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
    output: Annotated[Path, typer.Option(help="Directorio nuevo para artefactos privados.")],
    max_cases: Annotated[
        int, typer.Option(min=1, max=100, help="Límite explícito de casos revisados.")
    ],
    provider: Annotated[
        ProviderChoice, typer.Option(help="Proveedor local.")
    ] = ProviderChoice.fixture,
    fixture: Annotated[
        Path | None, typer.Option(help="Respuestas simuladas; obligatorio con fixture.")
    ] = None,
    model_id: Annotated[
        str, typer.Option(help="Nombre exacto del modelo; obligatorio con Ollama.")
    ] = "simulado-v1",
    ollama_url: Annotated[
        str, typer.Option(help="Servidor Ollama en loopback.")
    ] = DEFAULT_OLLAMA_URL,
    temperature: Annotated[float, typer.Option(min=0, max=2)] = 0.0,
    max_output_tokens: Annotated[int, typer.Option(min=1, max=2048)] = 256,
    timeout_seconds: Annotated[float, typer.Option(min=0.01, max=120)] = 30.0,
    max_retries: Annotated[int, typer.Option(min=0, max=2)] = 0,
) -> None:
    """Ejecuta casos revisados con fixture o con Ollama local."""
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
            provider_kind=provider.value,
            ollama_url=ollama_url,
        )
        manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    except RunInputError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error
    except ProviderFailure as error:
        typer.echo(f"Ollama: {error.code}", err=True)
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
        f"Ejecución {provider.value} procesada: "
        f"{manifest['success_count']} éxito(s), {manifest['failure_count']} fallo(s). "
        f"Artefactos: {destination}"
    )
    if manifest["failure_count"]:
        raise typer.Exit(code=1)
