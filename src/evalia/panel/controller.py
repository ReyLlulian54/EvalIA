"""Operaciones explícitas del panel; ninguna depende de eventos de Streamlit."""

import hashlib
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4

from jsonschema import ValidationError

from evalia.panel.paths import PanelPaths
from evalia.panel.types import (
    ExecutionResult,
    ExecutionStatus,
    PanelError,
    PreparedRun,
    RunOptions,
    RunSnapshot,
)
from evalia.providers.base import ProviderFailure
from evalia.providers.ollama import DEFAULT_OLLAMA_URL
from evalia.reports.schema import score_report_validator
from evalia.reports.score import (
    RunScoreError,
    _read_artifact,
    _read_records,
    score_run,
    write_score_report,
)
from evalia.runner.inputs import RunInputError, load_prompt, load_reviewed_cases, run_dataset
from evalia.runner.schema import manifest_validator

# Compartido por todas las sesiones/controladores del mismo proceso.
_EXECUTION_LOCK = Lock()


class LocalPanelController:
    """Una instancia por sesión, conservada entre reruns; al recrearla no hay orden pendiente."""

    def __init__(self, root: Path | None = None) -> None:
        self._paths = PanelPaths(root if root is not None else Path(__file__).resolve().parents[3])
        self._state_lock = Lock()
        self._prepared: PreparedRun | None = None

    def datasets(self) -> tuple[str, ...]:
        return self._catalog("datasets")

    def prompts(self) -> tuple[str, ...]:
        return self._catalog("prompts")

    def _catalog(self, category: str) -> tuple[str, ...]:
        try:
            return self._paths.catalog(category)
        except OSError as error:
            raise PanelError("read_failed", "No se pudo leer el catálogo local.") from error

    def runs(self) -> tuple[str, ...]:
        """Nombres seguros; read_run valida cada artefacto antes de mostrar su contenido."""
        try:
            return self._paths.runs()
        except OSError as error:
            raise PanelError(
                "read_failed", "No se pudo consultar el directorio de corridas."
            ) from error

    def prepare(
        self, dataset_name: str, prompt_name: str, options: RunOptions | None = None
    ) -> PreparedRun:
        """Invalida la preparación anterior; no crea archivos ni contacta proveedores."""
        with self._state_lock:
            self._prepared = None
            options = options if options is not None else RunOptions()
            if type(options) is not RunOptions:
                raise PanelError("invalid_options", "Se requieren opciones de ejecución válidas.")
            try:
                dataset = self._paths.input("datasets", dataset_name)
                prompt_path = self._paths.input("prompts", prompt_name)
                cases, dataset_hash = load_reviewed_cases(dataset, options.max_cases)
                prompt = load_prompt(prompt_path)
                intent = uuid4().hex
                output = self._paths.run(intent, required=False)
                prepared = PreparedRun(
                    intent,
                    dataset_name,
                    prompt_name,
                    dataset,
                    prompt_path,
                    output,
                    dataset_hash,
                    prompt.sha256,
                    prompt.prompt_id,
                    prompt.version,
                    tuple(case["id"] for case in cases),
                    tuple(case["split"] for case in cases),
                    options,
                )
            except (RunInputError, OSError) as error:
                raise PanelError(
                    "invalid_inputs",
                    "Revise el conjunto y el prompt con evalia validate y su esquema.",
                ) from error
            self._prepared = prepared
            return prepared

    def _revalidate(self, prepared: PreparedRun) -> None:
        dataset = self._paths.input("datasets", prepared.dataset_name)
        prompt_path = self._paths.input("prompts", prepared.prompt_name)
        output = self._paths.run(prepared.intent_id, required=False)
        if (
            dataset != prepared.dataset_path
            or prompt_path != prepared.prompt_path
            or output != prepared.output_dir
            or hashlib.sha256(dataset.read_bytes()).hexdigest() != prepared.dataset_sha256
            or hashlib.sha256(prompt_path.read_bytes()).hexdigest() != prepared.prompt_sha256
        ):
            raise PanelError("inputs_changed", "Las entradas cambiaron; prepare otra ejecución.")
        cases, dataset_hash = load_reviewed_cases(dataset, prepared.options.max_cases)
        prompt = load_prompt(prompt_path)
        if (
            dataset != prepared.dataset_path
            or prompt_path != prepared.prompt_path
            or output != prepared.output_dir
            or dataset_hash != prepared.dataset_sha256
            or prompt.sha256 != prepared.prompt_sha256
            or tuple(case["id"] for case in cases) != prepared.case_ids
        ):
            raise PanelError("inputs_changed", "Las entradas cambiaron; prepare otra ejecución.")
        if output.exists():
            raise PanelError("destination_exists", "El destino ya existe; prepare otra ejecución.")

    def execute(self, prepared: PreparedRun) -> ExecutionResult:
        """Consume una intención auténtica una vez, incluso si la operación es rechazada."""
        with self._state_lock:
            if prepared is None or prepared is not self._prepared:
                return ExecutionResult("rejected", "stale_intent", "Prepare una nueva ejecución.")
            self._prepared = None
        if not _EXECUTION_LOCK.acquire(blocking=False):
            return ExecutionResult(
                "rejected", "busy", "Ya hay una ejecución activa; espere y prepare otra."
            )
        started = False
        try:
            self._revalidate(prepared)
            options = prepared.options
            started = True
            run_dataset(
                dataset_path=prepared.dataset_path,
                prompt_path=prepared.prompt_path,
                fixture_path=None,
                output_dir=prepared.output_dir,
                model_id=options.model_id,
                max_cases=options.max_cases,
                temperature=options.temperature,
                max_output_tokens=options.max_output_tokens,
                timeout_seconds=options.timeout_seconds,
                max_retries=options.max_retries,
                provider_kind="ollama",
                ollama_url=DEFAULT_OLLAMA_URL,
            )
            return self._result(prepared, "completed", "completed", "Corrida finalizada.")
        except PanelError as error:
            return ExecutionResult("rejected", error.code, str(error))
        except RunInputError:
            if started:
                return self._rejected_or_partial(
                    prepared, "invalid_inputs", "Revise las entradas y los artefactos disponibles."
                )
            return ExecutionResult(
                "rejected", "invalid_inputs", "Revise las entradas y prepare otra vez."
            )
        except ProviderFailure as error:
            return self._rejected_or_partial(
                prepared,
                error.code,
                "No se pudo verificar Ollama o el modelo. Revise el servidor local y su nombre exacto.",
            )
        except FileExistsError:
            return self._rejected_or_partial(
                prepared,
                "destination_exists",
                "Una escritura encontró un destino existente; revise los artefactos disponibles.",
            )
        except KeyboardInterrupt:
            return self._result(prepared, "interrupted", "interrupted", "Ejecución interrumpida.")
        except Exception:
            if started:
                return self._result(
                    prepared,
                    "failed",
                    "execution_failed",
                    "La ejecución falló; revise sus artefactos.",
                )
            return ExecutionResult(
                "rejected", "preflight_failed", "No se pudieron verificar las entradas."
            )
        finally:
            _EXECUTION_LOCK.release()

    def _rejected_or_partial(
        self, prepared: PreparedRun, code: str, message: str
    ) -> ExecutionResult:
        # El mismo tipo de excepción puede aparecer antes o después de persistir registros.
        try:
            if not self._paths.run(prepared.intent_id, required=False).exists():
                return ExecutionResult("rejected", code, message)
        except (PanelError, OSError):
            return ExecutionResult(
                "failed",
                "artifacts_unreadable",
                "Revise la ruta de los artefactos.",
                prepared.intent_id,
            )
        return self._result(prepared, "failed", code, message)

    def _result(
        self, prepared: PreparedRun, status: ExecutionStatus, code: str, message: str
    ) -> ExecutionResult:
        try:
            path = self._paths.run(prepared.intent_id, required=False)
            if not path.exists():
                return ExecutionResult("failed" if status == "completed" else status, code, message)
            snapshot = self.read_run(prepared.intent_id)
        except (PanelError, OSError):
            return ExecutionResult(
                "failed",
                "artifacts_unreadable",
                "Los artefactos requieren revisión; no se reintentó.",
                prepared.intent_id,
            )
        if status == "completed" and snapshot.manifest["status"] != "completed":
            status, code, message = (
                "failed",
                "unclosed_run",
                "La corrida no tiene un cierre confirmado.",
            )
        elif status == "completed" and snapshot.manifest["failure_count"]:
            code, message = "completed_with_errors", "Corrida finalizada con errores de proveedor."
        return ExecutionResult(status, code, message, prepared.intent_id, snapshot)

    def read_run(self, run_name: str, *, include_raw: bool = False) -> RunSnapshot:
        """Lectura estructural, sin puntuación ni recuperación automática de corridas."""
        try:
            manifest_path = self._paths.artifact(run_name, "manifest.json")
            records_path = self._paths.artifact(run_name, "responses.jsonl", required=False)
            _, manifest = _read_artifact(manifest_path)
            manifest_validator().validate(manifest)
            if records_path.exists():
                _, records = _read_records(records_path)
            elif manifest["status"] != "completed" and manifest["recorded_count"] == 0:
                records = []
            else:
                raise PanelError("invalid_artifacts", "Faltan los registros de la corrida.")
            ids = [record["case_id"] for record in records]
            successes = sum(record["status"] == "success" for record in records)
            if (
                [r["index"] for r in records] != list(range(len(records)))
                or len(set(ids)) != len(ids)
                or len(records) > manifest["request_count"]
            ):
                raise PanelError("invalid_artifacts", "Índices o IDs de la corrida inconsistentes.")
            consistent = (
                manifest["recorded_count"] == len(records)
                and manifest["success_count"] == successes
                and manifest["failure_count"] == len(records) - successes
                and manifest["last_case_id"] == (ids[-1] if ids else None)
            )
            warnings = []
            if manifest["status"] == "completed":
                if not consistent or len(records) != manifest["request_count"]:
                    raise PanelError("invalid_artifacts", "Conteos de la corrida inconsistentes.")
            else:
                if not consistent:
                    warnings.append("manifest_counts_unconfirmed")
                if manifest["status"] == "running":
                    warnings.append("unclosed_run")
            visible = tuple(
                {key: value for key, value in record.items() if include_raw or key != "raw_text"}
                for record in records
            )
            return RunSnapshot(run_name, manifest, visible, tuple(warnings))
        except (RunScoreError, ValidationError, OSError) as error:
            raise PanelError(
                "invalid_artifacts", "No se pudieron validar los artefactos de la corrida."
            ) from error

    def score(self, run_name: str, dataset_name: str, prompt_name: str) -> dict:
        """Acción explícita: audita y crea el informe una vez; nunca genera inferencia."""
        return self._score(run_name, dataset_name, prompt_name, persist=True)

    def read_score(self, run_name: str, dataset_name: str, prompt_name: str) -> dict:
        """Verifica un informe existente contra sus fuentes sin escribir archivos."""
        return self._score(run_name, dataset_name, prompt_name, persist=False)

    def _score(self, run_name: str, dataset_name: str, prompt_name: str, *, persist: bool) -> dict:
        try:
            self.read_run(run_name)
            run_dir = self._paths.run(run_name)
            report_path = self._paths.artifact(run_name, "score-report.json", required=False)
            if not persist and not report_path.exists():
                raise PanelError("score_missing", "Todavía no se ha calculado el informe.")
            dataset = self._paths.input("datasets", dataset_name)
            prompt = self._paths.input("prompts", prompt_name)
            report = score_run(dataset, prompt, run_dir)
            if not report_path.exists():
                if not persist:
                    raise PanelError("score_missing", "El informe ya no está disponible.")
                try:
                    write_score_report(run_dir, report)
                except FileExistsError:
                    pass  # Otra consulta lo creó; se valida abajo, nunca se reemplaza.
            report_path = self._paths.artifact(run_name, "score-report.json")
            _, stored = _read_artifact(report_path)
            score_report_validator().validate(stored)
            expected = {k: v for k, v in report.items() if k != "created_at"}
            actual = {k: v for k, v in stored.items() if k != "created_at"}
            if json.dumps(expected, sort_keys=True) != json.dumps(actual, sort_keys=True):
                raise PanelError(
                    "score_mismatch", "El informe no coincide con la auditoría actual."
                )
            return stored
        except RunScoreError as error:
            known = {
                "La corrida no está completada": "La corrida debe estar completada para puntuar.",
                "El prompt no es el fijado para la puntuación 6.b": "Este prompt no admite puntuación 6.b.",
                "El reporte 6.b solo admite particiones dev y test": "Solo se puntúan casos dev/test; seed no es compatible.",
            }
            raise PanelError(
                "score_unavailable",
                known.get(str(error), "La auditoría rechazó las entradas o la corrida."),
            ) from error
        except (RunInputError, ValidationError, OSError) as error:
            raise PanelError(
                "score_failed", "No se pudo verificar o guardar el informe privado."
            ) from error
