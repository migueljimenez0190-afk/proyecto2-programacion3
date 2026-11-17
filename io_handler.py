# Título: GraphLab - io_handler.py
# Nombre del autor: Miguel Jimenez
# Fecha: 2026-11-16
# Descripción: Backend de red de transporte del Proyecto 2.
"""Lee y guarda las conexiones del grafo en un archivo CSV."""

import csv
import math
import os
import tempfile
from typing import List

from grafo import Grafo


ENCABEZADOS: List[str] = ["Origen", "Destino", "Peso"]


def validar_datos_conexion(ori: str, des: str, peso: float) -> None:
    """Rechaza nombres vacíos y pesos que Dijkstra no admite."""
    if not ori.strip() or not des.strip():
        raise ValueError("Los nombres de nodos no pueden estar vacíos.")
    if not math.isfinite(peso) or peso < 0:
        raise ValueError("Dijkstra requiere pesos no negativos.")


def _validar_encabezados_csv(ruta: str) -> bool:
    """Comprueba que el archivo contiene exactamente tres encabezados."""
    with open(ruta, mode="r", encoding="utf-8", newline="") as archivo:
        lector = csv.reader(archivo)
        return next(lector, None) == ENCABEZADOS


def guardar_conexion(ruta: str, ori: str, des: str, peso: float) -> None:
    """Valida y añade una conexión sin sobrescribir las existentes."""
    ori = ori.strip()
    des = des.strip()
    validar_datos_conexion(ori, des, peso)

    archivo_con_datos = (
        os.path.isfile(ruta) and os.path.getsize(ruta) > 0
    )
    if archivo_con_datos and not _validar_encabezados_csv(ruta):
        raise ValueError("No se puede escribir: encabezados incorrectos.")

    with open(ruta, mode="a", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        if not archivo_con_datos:
            escritor.writerow(ENCABEZADOS)
        escritor.writerow([ori, des, peso])


def cargar_grafo_desde_csv(ruta: str, avisos=None) -> Grafo:
    """Carga las conexiones válidas y omite filas corruptas del CSV."""
    grafo = Grafo()

    def notificar(mensaje):
        if avisos is None:
            print(mensaje)
        else:
            avisos.append(mensaje)

    try:
        with open(ruta, mode="r", encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames != ENCABEZADOS:
                notificar(f"Encabezados incorrectos en '{ruta}'.")
                return grafo

            for num_linea, fila in enumerate(lector, start=2):
                try:
                    if None in fila or None in fila.values():
                        raise ValueError("Columnas adicionales.")

                    origen = fila["Origen"].strip()
                    destino = fila["Destino"].strip()
                    peso = float(fila["Peso"])
                    validar_datos_conexion(origen, destino, peso)
                    grafo.agregar_arista(origen, destino, peso)
                except KeyError as error:
                    notificar(f"Línea {num_linea}: columna {error} ausente.")
                except (ValueError, TypeError) as error:
                    notificar(f"Línea {num_linea}: datos inválidos: {error}")
    except FileNotFoundError:
        notificar(f"Archivo '{ruta}' no encontrado. Grafo vacío.")

    return grafo


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as carpeta:
        archivo_prueba = os.path.join(carpeta, "nodos.csv")
        guardar_conexion(archivo_prueba, "A", "B", 4.0)
        guardar_conexion(archivo_prueba, "A", "C", 2.0)
        guardar_conexion(archivo_prueba, "B", "C", 1.0)

        grafo_prueba = cargar_grafo_desde_csv(archivo_prueba)
        assert set(grafo_prueba.nodos) == {"A", "B", "C"}
        assert grafo_prueba.dijkstra("A", "C") == (2.0, ["A", "C"])
        assert _validar_encabezados_csv(archivo_prueba)

    print("Pruebas básicas de io_handler.py: correctas")
