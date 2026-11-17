# Título: GraphLab - Proyecto 3
# Nombre del autor: Miguel Jimenez
# Fecha: 2026-11-16
# Descripción: Interfaz Streamlit para la red dirigida del Proyecto 2.
"""Presenta el calculador, el registro y la red almacenada en RAM."""

import csv
from pathlib import Path

import graphviz
import pandas as pd
import streamlit as st

from grafo import Grafo
from io_handler import cargar_grafo_desde_csv, guardar_conexion


ARCHIVO_CSV = Path(__file__).with_name("nodos.csv")


def inicializar_sesion():
    """Intenta cargar el CSV una sola vez, incluso si la lectura falla."""
    if "grafo" not in st.session_state:
        st.session_state.grafo = Grafo()
        st.session_state.avisos = []
        try:
            st.session_state.grafo = cargar_grafo_desde_csv(
                str(ARCHIVO_CSV), avisos=st.session_state.avisos
            )
        except (OSError, UnicodeError, csv.Error) as error:
            st.session_state.avisos.append(f"No se pudo cargar: {error}")
            st.session_state.bloqueo_escritura = True


def calcular_ruta(grafo):
    """Valida los nodos y muestra el resultado del motor existente."""
    st.subheader("Ruta óptima")
    st.caption("Calcula el menor costo entre dos puntos de la red.")
    izquierda, derecha = st.columns(2)
    origen = izquierda.text_input("Nodo origen", key="ruta_origen")
    destino = derecha.text_input("Nodo destino", key="ruta_destino")
    if st.button("Calcular ruta", type="primary", key="calcular"):
        try:
            origen, destino = origen.strip(), destino.strip()
            if not origen or not destino:
                raise ValueError("Ingresa origen y destino.")
            if origen not in grafo.nodos or destino not in grafo.nodos:
                raise KeyError("Origen y destino deben existir en la red.")
            costo, ruta = grafo.dijkstra(origen, destino)
        except ValueError as error:
            st.error(str(error))
        except KeyError as error:
            st.warning(error.args[0])
        else:
            if not ruta:
                st.warning("No existe una ruta dirigida entre estos nodos.")
            else:
                st.metric("Costo mínimo", f"{costo:g}")
                st.success(" → ".join(ruta))


def registrar_conexion(grafo):
    """Persiste primero y actualiza RAM solo después de guardar."""
    st.subheader("Nueva conexión")
    st.caption("Registra un tramo dirigido con peso finito no negativo.")
    with st.form("registro", clear_on_submit=False):
        origen = st.text_input("Origen", key="registro_origen")
        destino = st.text_input("Destino", key="registro_destino")
        entrada = st.text_input("Peso", key="registro_peso")
        enviar = st.form_submit_button("Guardar conexión")
    if enviar:
        if st.session_state.get("bloqueo_escritura", False):
            st.error("Corrige el archivo y abre otra sesión para guardar.")
            return
        try:
            peso = float(entrada)
            origen, destino = origen.strip(), destino.strip()
            guardar_conexion(str(ARCHIVO_CSV), origen, destino, peso)
        except ValueError as error:
            st.error(f"Datos inválidos: {error}")
        except (OSError, UnicodeError, csv.Error) as error:
            st.error(f"No se pudo guardar la conexión: {error}")
        else:
            grafo.agregar_arista(origen, destino, peso)
            st.success("Conexión guardada. La red ya está actualizada.")


def mostrar_red(grafo):
    """Deriva la tabla y la visualización de RAM, sin releer el CSV."""
    st.subheader("Red actual")
    st.caption("Conexiones dirigidas · el último peso registrado prevalece.")
    filas = [
        {"Origen": origen, "Destino": destino, "Peso": peso}
        for origen, nodo in grafo.nodos.items()
        for destino, peso in nodo.vecinos.items()
    ]
    st.dataframe(pd.DataFrame(filas, columns=["Origen", "Destino", "Peso"]),
                 hide_index=True, width="stretch")
    if not filas:
        st.warning("La red está vacía. Registra la primera conexión.")
        return
    red = graphviz.Digraph()
    red.attr(bgcolor="transparent", rankdir="LR")
    red.attr("node", shape="circle", style="filled", color="#99f6e4",
             fillcolor="#153b4d", fontcolor="#ffffff", fontname="Arial")
    red.attr("edge", color="#5eead4", fontcolor="#e2e8f0")
    identificadores = {nombre: str(i) for i, nombre in enumerate(grafo.nodos)}
    for nombre, identificador in identificadores.items():
        red.node(identificador, label=graphviz.escape(nombre))
    for fila in filas:
        red.edge(identificadores[fila["Origen"]],
                 identificadores[fila["Destino"]], label=f'{fila["Peso"]:g}')
    st.graphviz_chart(red, width="stretch")


def main():
    """Organiza las tres operaciones requeridas en pestañas."""
    st.set_page_config(page_title="GraphLab · Proyecto 3", page_icon="◈",
                       layout="wide")
    st.markdown("""
    <style>
    .stApp {background: radial-gradient(at 5% 5%, #164e63, transparent 55%),
        radial-gradient(at 95% 95%, #312e81, transparent 55%), #0b1120;
        color: #f1f5f9;}
    [data-testid="stHeader"] {background: transparent;}
    .block-container {max-width: 1120px; padding-top: 3rem;}
    [data-testid="stForm"], [data-testid="stMetric"] {
        background: rgba(255,255,255,.06); backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,.18); border-radius: 18px;
        padding: 1.25rem;}
    h1 {letter-spacing: -.045em;}
    [data-testid="stCaptionContainer"] {color: #cbd5e1;}
    </style>
    """, unsafe_allow_html=True)
    st.title("GraphLab")
    st.caption("PROYECTO 3 · PROGRAMACIÓN III · RED DE TRANSPORTE")
    inicializar_sesion()
    for aviso in st.session_state.avisos:
        st.warning(aviso)
    calculador, registro, visor = st.tabs(
        ["Dijkstra", "Registro", "Red actual"]
    )
    grafo = st.session_state.grafo
    with calculador:
        calcular_ruta(grafo)
    with registro:
        registrar_conexion(grafo)
    with visor:
        mostrar_red(grafo)


if __name__ == "__main__":
    main()
