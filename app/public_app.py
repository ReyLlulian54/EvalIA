"""Visor público de la comparación aprobada, sin ejecución ni selección de archivos."""

from typing import Any

import streamlit as st

from evalia.reports.public_demo import PublicReportError, load_public_report

SPLIT_LABELS = {"dev": "Desarrollo (dev)", "test": "Prueba (test)"}
FIELD_LABELS = {
    "closing_date": "Fecha de cierre",
    "modality": "Modalidad",
    "skills": "Habilidades",
    "skills_exact": "Habilidades exactas",
    "student_required": "Requisito de estudiante",
}
CATEGORIES = (
    "improvement",
    "regression",
    "correct_tie",
    "incorrect_tie",
    "not_comparable",
)
STATUSES = ("scored", "provider_error", "internal_error", "format_error")


def _display_value(value: Any, *, student: bool = False) -> str:
    if value is None:
        return "Desconocido"
    if student:
        return "Sí" if value is True else "No"
    if isinstance(value, list):
        return ", ".join(value) if value else "Ninguna"
    return str(value)


def _model_header(report: dict[str, Any]) -> None:
    st.title("EvalIA · comparación pública")
    dev_count = report["splits"]["dev"]["selected_count"]
    test_count = report["splits"]["test"]["selected_count"]
    st.caption(
        f"Resultados precomputados de {dev_count + test_count} casos ficticios seleccionados "
        f"({dev_count} dev · {test_count} test). Esta vista no ejecuta modelos."
    )
    provenance = report["provenance"]
    base = provenance["base"]
    candidate = provenance["candidate"]
    st.subheader("Modelos comparados")
    st.write(f"Base: {base['model_id']} · Candidato: {candidate['model_id']}")
    with st.expander("Procedencia y alcance del reporte"):
        st.write(f"Reporte generado: {report['generated_at']}")
        st.write(f"Digest base: {_display_value(base['model_digest'])}")
        st.write(f"Digest candidato: {_display_value(candidate['model_digest'])}")
        st.write(f"Commit base: {_display_value(base['source_commit'])}")
        st.write(f"Commit candidato: {_display_value(candidate['source_commit'])}")
        st.write(f"Hash del conjunto: {provenance['dataset_sha256']}")
    st.info(
        "Alcance: solo casos seleccionados (selected_cases_only). "
        "No se verificaron citas literales de las predicciones (not_observed). "
        "La comparación es descriptiva y no declara un ganador (descriptive_no_winner). "
        "El reporte no incluye textos de convocatoria ni citas de los modelos."
    )


def _summary(report: dict[str, Any]) -> None:
    st.header("Resumen del reporte")
    st.caption(
        "Conteos originales del artefacto; los filtros de abajo no cambian estos denominadores."
    )
    for split in ("dev", "test"):
        summary = report["splits"][split]
        count = summary["selected_count"]
        st.subheader(f"{SPLIT_LABELS[split]} · {count} casos")
        st.caption(f"Cada categoría de campo cuenta casos de este conjunto: denominador {count}.")
        st.dataframe(
            [
                {
                    "Campo": FIELD_LABELS[field],
                    "Mejora": counts["improvement"],
                    "Regresión": counts["regression"],
                    "Empate correcto": counts["correct_tie"],
                    "Empate incorrecto": counts["incorrect_tie"],
                    "No comparable": counts["not_comparable"],
                }
                for field, counts in summary["fields"].items()
            ],
            hide_index=True,
            width="stretch",
        )
        st.caption(f"Estados por modelo; denominador {count} casos por columna.")
        st.dataframe(
            [
                {
                    "Modelo": label,
                    "Evaluados": side["scored_count"],
                    "Error proveedor": side["provider_error_count"],
                    "Error interno": side["internal_error_count"],
                    "Error formato": side["format_error_count"],
                }
                for label, side in (
                    ("Base", summary["base"]),
                    ("Candidato", summary["candidate"]),
                )
            ],
            hide_index=True,
            width="stretch",
        )
        base_elapsed = summary["base"]["elapsed_ms"]
        candidate_elapsed = summary["candidate"]["elapsed_ms"]
        st.caption(
            "Mediana de tiempo informado: "
            f"base {_milliseconds(base_elapsed['median'])} "
            f"({base_elapsed['observations']} observaciones); "
            f"candidato {_milliseconds(candidate_elapsed['median'])} "
            f"({candidate_elapsed['observations']} observaciones)."
        )


def _milliseconds(value: float | None) -> str:
    return "No aplicable" if value is None else f"{value:,.0f} ms"


def _reset_filters() -> None:
    for key, value in (
        ("split_filter", "Todos"),
        ("case_id_filter", ""),
        ("base_status_filter", "Todos"),
        ("candidate_status_filter", "Todos"),
        ("category_filter", "Todas"),
        ("not_comparable_only", False),
    ):
        st.session_state[key] = value
    st.session_state.pop("case_detail", None)


def _filtered_cases(report: dict[str, Any]) -> list[dict[str, Any]]:
    st.header("Explorar casos")
    st.caption("Los controles filtran la vista, nunca los conteos del resumen.")
    split = st.selectbox("Conjunto", ("Todos", "dev", "test"), key="split_filter")
    query = st.text_input("Buscar ID de caso", key="case_id_filter").strip().casefold()
    base_status = st.selectbox("Estado base", ("Todos", *STATUSES), key="base_status_filter")
    candidate_status = st.selectbox(
        "Estado candidato", ("Todos", *STATUSES), key="candidate_status_filter"
    )
    category = st.selectbox(
        "Categoría en cualquier campo", ("Todas", *CATEGORIES), key="category_filter"
    )
    not_comparable = st.checkbox("Solo casos no comparables", key="not_comparable_only")
    st.button("Restablecer filtros", key="reset_filters", on_click=_reset_filters)

    selected = [
        case
        for case in report["cases"]
        if (split == "Todos" or case["split"] == split)
        and query in case["case_id"].casefold()
        and (base_status == "Todos" or case["base"]["status"] == base_status)
        and (candidate_status == "Todos" or case["candidate"]["status"] == candidate_status)
        and (category == "Todas" or category in case["fields"].values())
        and (not not_comparable or "not_comparable" in case["fields"].values())
    ]
    st.caption(f"Mostrando {len(selected)} de {len(report['cases'])} casos del reporte aprobado.")
    if not selected:
        st.info("No hay casos con esos filtros. Use «Restablecer filtros» para volver a verlos.")
        return []
    st.dataframe(
        [
            {
                "Caso": case["case_id"],
                "Conjunto": case["split"],
                "Base": case["base"]["status"],
                "Candidato": case["candidate"]["status"],
                "Campos no comparables": sum(
                    result == "not_comparable" for result in case["fields"].values()
                ),
            }
            for case in selected
        ],
        hide_index=True,
        width="stretch",
    )
    return selected


def _extraction_rows(extraction: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "Campo": FIELD_LABELS[field],
            "Valor": _display_value(value, student=field == "student_required"),
        }
        for field, value in extraction.items()
    ]


def _outcome(label: str, outcome: dict[str, Any]) -> None:
    st.subheader(label)
    st.write(f"Estado: {outcome['status']}")
    st.write(f"Tiempo informado: {_milliseconds(outcome['elapsed_ms'])}")
    if outcome["status"] != "scored":
        st.write(f"Código de error: {outcome['error_code']}")
        st.write("Sin predicción")
        return
    st.dataframe(_extraction_rows(outcome["prediction"]), hide_index=True, width="stretch")


def _case_detail(selected: list[dict[str, Any]]) -> None:
    st.header("Detalle de un caso")
    by_id = {case["case_id"]: case for case in selected}
    if st.session_state.get("case_detail") not in by_id:
        st.session_state["case_detail"] = next(iter(by_id))
    case_id = st.selectbox("Caso visible", tuple(by_id), key="case_detail")
    case = by_id[case_id]
    st.caption(f"{case_id} · {SPLIT_LABELS[case['split']]}")
    st.subheader("Valores esperados")
    st.dataframe(_extraction_rows(case["expected"]), hide_index=True, width="stretch")
    _outcome("Modelo base", case["base"])
    _outcome("Modelo candidato", case["candidate"])
    st.subheader("Categoría de comparación por campo")
    st.dataframe(
        [
            {"Campo": FIELD_LABELS[field], "Categoría": category}
            for field, category in case["fields"].items()
        ],
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Estas categorías describen coincidencias de campos estructurados. "
        "El reporte no contiene citas para comprobar respaldo semántico."
    )


def main() -> None:
    st.set_page_config(page_title="EvalIA · comparación pública", layout="wide")
    try:
        report = load_public_report()
    except PublicReportError:
        st.error(
            "No se puede mostrar el reporte público aprobado. "
            "Compruebe que el artefacto publicado sea la copia verificada del proyecto."
        )
        st.stop()
    _model_header(report)
    _summary(report)
    selected = _filtered_cases(report)
    if selected:
        _case_detail(selected)


if __name__ == "__main__":
    main()
