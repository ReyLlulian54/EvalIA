"""Recorrido visible del visor público con el reporte aprobado, sin inferencia."""

from pathlib import Path

import pytest

from evalia.reports import public_demo

pytest.importorskip("streamlit", reason="AppTest requiere el extra panel")
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app/public_app.py"


def open_app() -> AppTest:
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    return app


def visible_text(app: AppTest) -> str:
    kinds = ("title", "header", "subheader", "markdown", "caption", "info", "warning", "error")
    return "\n".join(str(element.value) for kind in kinds for element in app.get(kind))


def test_initial_view_keeps_split_denominators_and_limitations() -> None:
    app = open_app()
    text = visible_text(app)

    assert "EvalIA · comparación pública" in text
    assert "Desarrollo (dev) · 27 casos" in text
    assert "Prueba (test) · 9 casos" in text
    assert "selected_cases_only" in text
    assert "not_observed" in text
    assert "descriptive_no_winner" in text
    assert "Mostrando 36 de 36" in text
    assert not app.error


def test_filters_find_error_case_without_changing_summary() -> None:
    app = open_app()
    app.selectbox(key="split_filter").set_value("test").run()
    app.text_input(key="case_id_filter").input("bench-001").run()
    app.selectbox(key="base_status_filter").set_value("format_error").run()
    app.selectbox(key="candidate_status_filter").set_value("format_error").run()
    app.selectbox(key="category_filter").set_value("not_comparable").run()
    app.checkbox(key="not_comparable_only").check().run()
    text = visible_text(app)

    assert not app.exception
    assert "Mostrando 1 de 36" in text
    assert app.selectbox(key="case_detail").value == "bench-001"
    assert text.count("Sin predicción") == 2
    assert "noncanonical_skill" in text
    assert "Desarrollo (dev) · 27 casos" in text
    assert "Prueba (test) · 9 casos" in text


def test_empty_filter_can_be_reset() -> None:
    app = open_app()
    app.text_input(key="case_id_filter").input("no-existe").run()

    assert "No hay casos con esos filtros" in visible_text(app)
    assert "Mostrando 0 de 36" in visible_text(app)
    assert all(widget.key != "case_detail" for widget in app.selectbox)

    app.button(key="reset_filters").click().run()
    assert not app.exception
    assert "Mostrando 36 de 36" in visible_text(app)
    assert app.text_input(key="case_id_filter").value == ""


def test_detail_distinguishes_unknown_from_explicit_no() -> None:
    app = open_app()
    app.selectbox(key="case_detail").set_value("bench-008").run()
    assert not app.exception

    values = [
        frame.value.loc[frame.value["Campo"] == "Requisito de estudiante", "Valor"].iloc[0]
        for frame in app.dataframe
        if "Campo" in frame.value.columns
        and "Valor" in frame.value.columns
        and "Requisito de estudiante" in frame.value["Campo"].values
    ]
    assert values == ["Desconocido", "Desconocido", "No"]


def test_modified_artifact_blocks_every_data_widget(monkeypatch) -> None:
    monkeypatch.setattr(public_demo, "APPROVED_SHA256", "0" * 64)
    app = open_app()

    assert "No se puede mostrar el reporte público aprobado" in visible_text(app)
    assert len(app.dataframe) == 0
    assert len(app.selectbox) == 0
    assert len(app.text_input) == 0
