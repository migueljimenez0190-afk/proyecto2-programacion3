# Título: Pruebas de GraphLab
# Nombre del autor: Miguel Jimenez
# Fecha: 2026-11-16
# Descripción: Verifica carga única, persistencia, rutas y errores.
"""Pruebas integradas con archivos temporales y Streamlit AppTest."""

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

import io_handler
from grafo import Grafo


APP = Path(__file__).with_name("app.py")


@pytest.fixture
def entorno(tmp_path):
    """Copia la vista para que ninguna prueba modifique el CSV original."""
    vista = tmp_path / "app.py"
    vista.write_text(APP.read_text(encoding="utf-8"), encoding="utf-8")
    csv = tmp_path / "nodos.csv"
    csv.write_text("Origen,Destino,Peso\nA,B,4\nA,C,2\nC,D,2\n",
                   encoding="utf-8")
    return vista, csv


def test_carga_unica_y_ruta(entorno):
    vista, _ = entorno
    with patch.object(io_handler, "cargar_grafo_desde_csv",
                      wraps=io_handler.cargar_grafo_desde_csv) as cargar:
        app = AppTest.from_file(str(vista)).run()
        app.text_input(key="ruta_origen").set_value("A")
        app.text_input(key="ruta_destino").set_value("D")
        app.button(key="calcular").click().run()
        assert app.metric[0].value == "4"
        assert app.success[0].value == "A → C → D"
        app.run()
        assert cargar.call_count == 1
        assert not app.exception


def guardar(app, peso="3"):
    """Completa el formulario y envía sus datos."""
    app.text_input(key="registro_origen").set_value("D")
    app.text_input(key="registro_destino").set_value("E")
    app.text_input(key="registro_peso").set_value(peso)
    app.button[1].click().run()


def test_registro_ram_y_disco(entorno):
    vista, csv = entorno
    app = AppTest.from_file(str(vista)).run()
    guardar(app)
    assert app.session_state.grafo.dijkstra("A", "E")[0] == 7
    assert "D,E,3.0" in csv.read_text()
    assert len(app.dataframe[0].value) == 4
    otra = AppTest.from_file(str(vista)).run()
    assert otra.session_state.grafo.dijkstra("A", "E")[0] == 7
    assert not app.exception


@pytest.mark.parametrize("peso", ["-1", "nan", "inf", "abc", ""])
def test_peso_invalido(entorno, peso):
    vista, csv = entorno
    original = csv.read_bytes()
    app = AppTest.from_file(str(vista)).run()
    guardar(app, peso)
    assert app.error
    assert csv.read_bytes() == original
    assert "E" not in app.session_state.grafo.nodos
    assert not app.exception


def test_permiso_escritura(entorno):
    vista, csv = entorno
    app = AppTest.from_file(str(vista)).run()
    original = csv.read_bytes()
    with patch.object(io_handler, "guardar_conexion",
                      side_effect=PermissionError("Acceso denegado")):
        guardar(app)
    assert app.error
    assert "E" not in app.session_state.grafo.nodos
    assert csv.read_bytes() == original
    assert not app.exception


@pytest.mark.parametrize("origen,destino,tipo", [
    ("", "D", "error"), ("X", "D", "warning"),
    ("D", "A", "warning"), ("A", "A", "metric"),
])
def test_consultas(entorno, origen, destino, tipo):
    vista, _ = entorno
    app = AppTest.from_file(str(vista)).run()
    app.text_input(key="ruta_origen").set_value(origen)
    app.text_input(key="ruta_destino").set_value(destino)
    app.button(key="calcular").click().run()
    assert len(getattr(app, tipo)) > 0
    assert not app.exception


def test_csv_inexistente_y_filas_corruptas(entorno):
    vista, csv = entorno
    csv.unlink()
    app = AppTest.from_file(str(vista)).run()
    assert app.warning
    guardar(app)
    assert csv.exists()
    csv.write_text("Origen,Destino,Peso\nA,B,2\nC\nD,E,-1\n",
                   encoding="utf-8")
    app = AppTest.from_file(str(vista)).run()
    assert len(app.warning) == 2
    assert len(app.dataframe[0].value) == 1
    assert not app.exception


def test_backend():
    grafo = Grafo()
    grafo.agregar_arista("A", "B", 0)
    assert grafo.dijkstra("A", "B") == (0, ["A", "B"])
    with pytest.raises(ValueError):
        grafo.agregar_arista("B", "C", -1)
    assert "C" not in grafo.nodos


def test_fallo_lectura_no_reintenta(entorno):
    vista, _ = entorno
    with patch.object(io_handler, "cargar_grafo_desde_csv",
                      side_effect=PermissionError("Acceso denegado")) as leer:
        app = AppTest.from_file(str(vista)).run()
        app.run()
        guardar(app)
        assert leer.call_count == 1
        assert app.warning and app.error
        assert not app.session_state.grafo.nodos
        assert not app.exception


def test_duplicado_y_guardado_sin_recarga(entorno):
    vista, csv = entorno
    with patch.object(io_handler, "cargar_grafo_desde_csv",
                      wraps=io_handler.cargar_grafo_desde_csv) as leer:
        app = AppTest.from_file(str(vista)).run()
        guardar(app, "0")
        guardar(app, "5")
        assert leer.call_count == 1
        assert app.session_state.grafo.dijkstra("D", "E")[0] == 5
        assert len(app.dataframe[0].value) == 4
        assert "D,E,0.0" in csv.read_text()
        assert "D,E,5.0" in csv.read_text()
        assert not app.exception
