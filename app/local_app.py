"""Panel local: los efectos requieren acciones explícitas de la persona usuaria."""

from collections import Counter
from dataclasses import asdict
from pathlib import Path

import streamlit as st

from evalia.panel import LocalPanelController, PanelError, PreparedRun, RunOptions, RunSnapshot

ROOT = Path(__file__).resolve().parents[1]
METRIC_LABELS = {
    "coverage": "Cobertura",
    "closing_date": "Fecha de cierre",
    "modality": "Modalidad",
    "student_required": "Requisito de estudiante",
    "skills_exact": "Habilidades: coincidencia exacta",
    "skills_precision": "Habilidades: precisión",
    "skills_recall": "Habilidades: cobertura",
    "skills_f1": "Habilidades: F1",
}
RECORD_LABELS = {
    "success": "Respuesta recibida",
    "provider_error": "Error de proveedor",
    "internal_error": "Error interno",
}


def _error(error: Exception) -> None:
    if isinstance(error, PanelError):
        st.error(f"{error.code}: {error}")
    else:
        st.error("No se pudo completar la operación. Revise las entradas y artefactos locales.")


def _reported(value: object) -> str:
    return "No informado" if value is None else str(value)


def _reset_query() -> None:
    st.session_state.show_raw = False
    st.session_state.score_scope = None


def _prepare(controller: LocalPanelController, datasets: tuple, prompts: tuple) -> None:
    st.header("1. Configurar")
    st.caption(
        "Ollama local · http://127.0.0.1:11434. El panel no inicia Ollama ni descarga modelos."
    )
    if not datasets or not prompts:
        st.warning("Agregue un conjunto JSONL y un prompt JSON válidos a datasets/ y prompts/.")
        return
    with st.form("configuration"):
        left, right = st.columns(2)
        dataset = left.selectbox("Conjunto", datasets, key="dataset_name")
        prompt = right.selectbox("Prompt", prompts, key="prompt_name")
        model = left.text_input("Nombre exacto del modelo", "qwen3:8b", key="model_id")
        limit = right.number_input("Máximo de casos", 1, 100, 10, key="max_cases")
        with st.expander("Opciones de generación"):
            first, second = st.columns(2)
            temperature = first.number_input(
                "Temperatura", 0.0, 2.0, 0.0, step=0.1, key="temperature"
            )
            tokens = second.number_input(
                "Máximo de tokens de salida", 1, 2048, 256, key="max_output_tokens"
            )
            timeout = first.number_input(
                "Espera de I/O (segundos)", 0.01, 120.0, 120.0, key="timeout_seconds"
            )
            retries = second.number_input("Reintentos por caso", 0, 2, 0, key="max_retries")
            st.caption("La espera de I/O no es una duración máxima de la evaluación completa.")
        st.caption(
            "Los textos se envían a su Ollama local. Los artefactos y respuestas permanecen "
            "en runs/panel/, excluido de Git. Preparar solo valida; no genera respuestas."
        )
        submitted = st.form_submit_button("Preparar ejecución", key="prepare_run")
    if submitted:
        # Invalidar también la vista si RunOptions falla antes de llamar a prepare.
        st.session_state.prepared_run = None
        st.session_state.last_prepared = None
        st.session_state.execution_result = None
        st.session_state.execution_state = "Rechazada"
        st.session_state.prepare_error = None
        try:
            options = RunOptions(model, limit, temperature, tokens, timeout, retries)
            prepared = controller.prepare(dataset, prompt, options)
        except Exception as error:
            st.session_state.prepare_error = (
                (error.code, str(error)) if isinstance(error, PanelError) else None
            )
            if not isinstance(error, PanelError):
                st.session_state.prepare_error = (
                    "prepare_failed",
                    "No se pudo preparar la corrida.",
                )
        else:
            st.session_state.prepared_run = prepared
            st.session_state.last_prepared = prepared
            st.session_state.execution_state = "Preparada"


def _prepared_summary(prepared: PreparedRun) -> None:
    st.text(f"Modelo: {prepared.options.model_id}")
    st.text(f"Conjunto: {prepared.dataset_name} · Prompt: {prepared.prompt_name}")
    st.text(f"Prompt: {prepared.prompt_id} · Versión: {prepared.prompt_version}")
    st.metric("Casos seleccionados", len(prepared.case_ids))
    st.table(
        [
            {"Partición": split, "Casos": count}
            for split, count in sorted(Counter(prepared.splits).items())
        ]
    )
    with st.expander("IDs, parámetros y procedencia de la selección"):
        st.code("\n".join(prepared.case_ids), language=None)
        st.json(asdict(prepared.options))
        st.text(f"SHA-256 conjunto: {prepared.dataset_sha256}")
        st.text(f"SHA-256 prompt: {prepared.prompt_sha256}")
    st.text(f"Destino privado: runs/panel/{prepared.intent_id}/")
    st.caption(
        "Este resumen fija lo que se enviará. Los cambios del formulario solo se aplican "
        "cuando vuelve a preparar. Cada preparación se puede ejecutar una sola vez."
    )


def _execute(controller: LocalPanelController) -> None:
    st.header("2. Revisar y ejecutar")
    if st.session_state.last_prepared is not None:
        _prepared_summary(st.session_state.last_prepared)
    status = st.empty()
    status.info(f"Estado: {st.session_state.execution_state}")
    if st.session_state.prepare_error:
        code, message = st.session_state.prepare_error
        st.error(f"{code}: {message}")
    action = st.empty()
    clicked = action.button(
        "Ejecutar",
        key="execute_run",
        type="primary",
        disabled=st.session_state.prepared_run is None,
    )
    if clicked and st.session_state.prepared_run is not None:
        prepared = st.session_state.prepared_run
        # Consumir antes del efecto: ningún rerun reconstruye ni reenvía esta orden.
        st.session_state.prepared_run = None
        st.session_state.execution_state = "En ejecución"
        action.empty()
        action.button("En ejecución", key="execution_busy", disabled=True)
        status.info("Estado: En ejecución. Espere a que termine la solicitud local.")
        try:
            result = controller.execute(prepared)
        except Exception:
            st.session_state.execution_state = "Fallida"
            st.session_state.execution_result = None
            st.error("La ejecución falló. Consulte los artefactos; prepare de nuevo para repetir.")
        else:
            st.session_state.execution_result = result
            st.session_state.execution_state = {
                "completed": "Finalizada",
                "rejected": "Rechazada",
                "failed": "Fallida",
                "interrupted": "Interrumpida",
            }[result.status]
        status.info(f"Estado: {st.session_state.execution_state}")
        action.empty()
        action.button("Preparación consumida", key="execution_consumed", disabled=True)
    result = st.session_state.execution_result
    if result is not None:
        message = f"{result.code}: {result.message}"
        if result.status == "completed" and result.code == "completed":
            st.success(message)
        elif result.status == "completed" or result.status == "interrupted":
            st.warning(message)
        else:
            st.error(message)
        if result.run_name is not None:
            st.text(f"Artefactos conservados: runs/panel/{result.run_name}/")
        st.caption("Para repetir deliberadamente, prepare una ejecución nueva.")


def _snapshot(snapshot: RunSnapshot) -> None:
    manifest = snapshot.manifest
    labels = {
        "completed": "Finalizada",
        "running": "Sin cierre confirmado",
        "failed": "Fallida",
        "interrupted": "Interrumpida",
    }
    st.text(f"Estado persistido: {labels[manifest['status']]} ({manifest['status']})")
    st.text(f"Modelo solicitado: {manifest['model_id']}")
    for warning in snapshot.warnings:
        st.warning(
            {
                "unclosed_run": "Sin cierre confirmado: no se reanuda ni modifica esta corrida.",
                "manifest_counts_unconfirmed": (
                    "Los conteos del manifiesto no están confirmados. Se muestran los registros leídos."
                ),
            }[warning]
        )
    columns = st.columns(4)
    columns[0].metric("Casos previstos", manifest["request_count"])
    columns[1].metric("Registros leídos", snapshot.recorded_count)
    successes = sum(row["status"] == "success" for row in snapshot.records)
    columns[2].metric("Respuestas recibidas", successes)
    columns[3].metric("Errores registrados", snapshot.recorded_count - successes)
    st.caption(
        "Una respuesta recibida acredita éxito del proveedor; no acredita contenido correcto."
    )
    with st.expander("Procedencia y manifiesto"):
        st.text(f"Commit de origen: {_reported(manifest['source_commit'])}")
        st.text(f"Digest del modelo: {_reported(manifest['model_digest'])}")
        st.json(manifest)


def _records(controller: LocalPanelController, snapshot: RunSnapshot) -> None:
    selected = st.selectbox(
        "Filtrar registros",
        ("Todos", *RECORD_LABELS),
        format_func=lambda value: RECORD_LABELS.get(value, value),
        key="status_filter",
    )
    records = [r for r in snapshot.records if selected == "Todos" or r["status"] == selected]
    st.table(
        [
            {
                "Caso": row["case_id"],
                "Estado": RECORD_LABELS[row["status"]],
                "Código de error": _reported(row["error_code"]),
                "Intentos": row["attempts"],
                "Tiempo (ms)": row["elapsed_ms"],
                "Tokens entrada": _reported(row["prompt_tokens"]),
                "Tokens salida": _reported(row["completion_tokens"]),
                "Costo USD": _reported(row["cost_usd"]),
            }
            for row in records
        ]
    )
    st.caption(
        "En las extracciones: true = Sí; false = No; null = Desconocido. "
        "Una ausencia no equivale a una negativa."
    )
    if st.checkbox("Mostrar respuestas crudas privadas como texto literal", key="show_raw"):
        try:
            raw_snapshot = controller.read_run(snapshot.run_name, include_raw=True)
        except Exception as error:
            _error(error)
        else:
            visible_ids = {row["case_id"] for row in records}
            for row in raw_snapshot.records:
                if row["case_id"] in visible_ids:
                    st.text(f"Caso: {row['case_id']}")
                    st.code(_reported(row["raw_text"]), language=None)


def _metric_rows(metrics: dict) -> list[dict]:
    rows = []
    ratios = [(METRIC_LABELS[name], metrics[name]) for name in METRIC_LABELS]
    ratios += [
        (f"Abstención: {METRIC_LABELS[name]}", ratio)
        for name, ratio in metrics["abstention"].items()
    ]
    for label, ratio in ratios:
        rows.append(
            {
                "Métrica": label,
                "Numerador": ratio["numerator"],
                "Denominador": ratio["denominator"],
                "Valor": "No aplicable" if ratio["value"] is None else f"{ratio['value']:.2%}",
                "Casos fallidos": ", ".join(ratio["failed_case_ids"]) or "Ninguno",
            }
        )
    return rows


def _report(report: dict) -> None:
    st.success("Informe auditado contra la corrida y las fuentes seleccionadas.")
    st.info(
        "Evidencia literal: not_observed. El prompt no solicitó citas; "
        "no se observó evidencia ni se verificó respaldo semántico."
    )
    for split in ("dev", "test"):
        data = report["splits"][split]
        st.subheader(f"Partición {split}")
        st.text(
            f"Elegibles: {data['eligible_count']} · Puntuados: {data['scored_count']} · "
            f"Errores de proveedor: {data['provider_error_count']} · "
            f"Internos: {data['internal_error_count']} · Formato: {data['format_error_count']}"
        )
        st.table(_metric_rows(data["metrics"]))
        st.text(
            f"Habilidades: TP={data['skills_counts']['tp']}, "
            f"FP={data['skills_counts']['fp']}, FN={data['skills_counts']['fn']}"
        )
        telemetry = data["telemetry"]
        st.table(
            [
                {
                    "Medida": label,
                    "Valor": _reported(telemetry[name][field]),
                    "Observaciones": telemetry[name]["observations"],
                }
                for name, label, field in (
                    ("elapsed_ms", "Mediana de tiempo (ms)", "median"),
                    ("prompt_tokens", "Tokens de entrada", "total"),
                    ("completion_tokens", "Tokens de salida", "total"),
                    ("cost_usd", "Costo USD", "total"),
                )
            ]
        )
    st.caption("Los tiempos describen esta máquina y esta corrida. No hay nota compuesta.")
    with st.expander("Resultados por caso y procedencia del informe"):
        st.json(report["cases"])
        st.json(report["run"])


def _score(
    controller: LocalPanelController, run_name: str, datasets: tuple, prompts: tuple
) -> None:
    st.subheader("Métricas")
    st.caption(
        "Seleccione las fuentes originales para auditar sus hashes. Calcular crea el informe "
        "privado si falta; consultar uno existente no escribe. Ninguna acción ejecuta un modelo. "
        "La puntuación admite el prompt congelado de 6.b y particiones dev/test."
    )
    left, right = st.columns(2)
    dataset = left.selectbox(
        "Conjunto original para puntuación",
        datasets,
        index=None,
        key="score_dataset_name",
        placeholder="Seleccione una opción",
    )
    prompt = right.selectbox(
        "Prompt original para puntuación",
        prompts,
        index=None,
        key="score_prompt_name",
        placeholder="Seleccione una opción",
    )
    disabled = dataset is None or prompt is None
    calculate = left.button("Calcular métricas", key="calculate_score", disabled=disabled)
    read = right.button("Consultar informe existente", key="read_score", disabled=disabled)
    scope = (run_name, dataset, prompt)
    if st.session_state.score_scope != scope:
        st.session_state.score_scope = None
    if calculate or read or st.session_state.score_scope == scope:
        try:
            report = controller.score(*scope) if calculate else controller.read_score(*scope)
        except Exception as error:
            st.session_state.score_scope = None
            st.warning("Puntuación no disponible para estas entradas.")
            _error(error)
        else:
            st.session_state.score_scope = scope
            _report(report)


def main() -> None:
    st.set_page_config(page_title="EvalIA · Panel local", layout="wide")
    st.title("EvalIA · Panel local")
    st.caption("Prepare, ejecute una vez y consulte resultados privados en su equipo.")
    defaults = {
        "prepared_run": None,
        "last_prepared": None,
        "execution_result": None,
        "execution_state": "Sin preparar",
        "prepare_error": None,
        "score_scope": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "panel_controller" not in st.session_state:
        st.session_state.panel_controller = LocalPanelController(ROOT)
    controller = st.session_state.panel_controller
    try:
        datasets, prompts = controller.datasets(), controller.prompts()
    except Exception as error:
        _error(error)
        datasets, prompts = (), ()
    _prepare(controller, datasets, prompts)
    _execute(controller)
    st.divider()
    st.header("3. Consultar resultados")
    st.caption("Seleccionar corridas o filtros no genera inferencias ni reintentos.")
    try:
        runs = controller.runs()
    except Exception as error:
        _error(error)
        return
    if not runs:
        st.info("Todavía no hay corridas del panel para consultar.")
        return
    run_name = st.selectbox(
        "Corrida",
        runs,
        index=None,
        key="run_name",
        on_change=_reset_query,
        placeholder="Seleccione una corrida",
    )
    if run_name is None:
        return
    try:
        snapshot = controller.read_run(run_name)
    except Exception as error:
        st.session_state.score_scope = None
        _error(error)
        return
    _snapshot(snapshot)
    _records(controller, snapshot)
    _score(controller, run_name, datasets, prompts)


if __name__ == "__main__":
    main()
