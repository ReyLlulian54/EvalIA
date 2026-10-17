"""Command-line entry point for EvalIA."""

import json
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from evalia import __version__
from evalia.providers.base import ProviderFailure
from evalia.providers.ollama import DEFAULT_OLLAMA_URL
from evalia.reports.compare import RunComparisonError, compare_runs, write_comparison
from evalia.reports.score import RunScoreError, score_run, write_score_report
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
    except FileExistsError as error:
        typer.echo("El directorio de salida ya existe; elija una ruta nueva.", err=True)
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


@app.command("score-run")
def score_run_command(
    dataset: Annotated[Path, typer.Option(help="Conjunto JSONL de la corrida.")],
    prompt: Annotated[Path, typer.Option(help="Prompt versionado usado en la corrida.")],
    run_dir: Annotated[Path, typer.Option(help="Directorio privado con manifest y responses.")],
) -> None:
    """Puntúa una corrida 5.3 por dev/test sin ejecutar modelos ni publicar respuestas."""
    try:
        report = score_run(dataset, prompt, run_dir)
        output = write_score_report(run_dir, report)
    except (RunScoreError, RunInputError, FileExistsError, OSError) as error:
        typer.echo(f"Puntuación rechazada: {error}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"Informe privado: {output}. "
        f"dev {report['splits']['dev']['scored_count']}/{report['splits']['dev']['eligible_count']}; "
        f"test {report['splits']['test']['scored_count']}/{report['splits']['test']['eligible_count']}."
    )


@app.command()
def compare(
    dataset: Annotated[Path, typer.Option(help="Conjunto JSONL de ambas corridas.")],
    prompt: Annotated[Path, typer.Option(help="Prompt versionado de ambas corridas.")],
    base_run: Annotated[Path, typer.Option(help="Directorio privado de la corrida base.")],
    candidate_run: Annotated[Path, typer.Option(help="Directorio privado de la candidata.")],
    output: Annotated[Path, typer.Option(help="Archivo JSON privado nuevo; no se sobrescribe.")],
) -> None:
    """Compara informes de corridas reauditoradas sin ejecutar modelos."""
    try:
        report = compare_runs(dataset, prompt, base_run, candidate_run)
        destination = write_comparison(output, report)
    except (RunComparisonError, RunInputError, FileExistsError, OSError) as error:
        typer.echo(f"Comparación rechazada: {error}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(f"Comparación privada: {destination}. Dirección: base a candidata.")
