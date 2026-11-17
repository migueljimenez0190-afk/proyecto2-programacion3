# Título: GraphLab - main.py
# Nombre del autor: Miguel Jimenez
# Fecha: 2026-11-16
# Descripción: Backend de red de transporte del Proyecto 2.
"""
Módulo principal interactivo para la red de transporte.
Permite registrar conexiones, persistirlas en CSV y consultar
rutas óptimas mediante Dijkstra.
"""

import math
from io_handler import guardar_conexion, cargar_grafo_desde_csv

ARCHIVO_CSV: str = "nodos.csv"


def solicitar_nodo(mensaje: str) -> str:
    """
    Solicita el nombre de un nodo al usuario mediante consola.
    Garantiza que la entrada no esté vacía.
    """
    while True:
        try:
            nombre: str = input(mensaje).strip()
            if not nombre:
                raise ValueError("El nombre no puede estar vacío.")
        except ValueError as error:
            print(f"Error: {error}")
        else:
            return nombre


def solicitar_peso() -> float:
    """
    Solicita y valida el peso de una arista mediante consola.
    Rechaza valores no numéricos, vacíos, negativos, NaN o inf.
    """
    while True:
        try:
            entrada: str = input("Peso: ").strip()
            if not entrada:
                raise ValueError("El peso no puede estar vacío.")
            peso: float = float(entrada)
            if not math.isfinite(peso) or peso < 0:
                raise ValueError("El peso debe ser finito y no negativo.")
        except ValueError as error:
            print(f"Error: {error}. Ingresa un número válido.")
        else:
            return peso


def agregar_conexion_interactiva() -> None:
    """Captura origen, destino y peso, y los guarda en el CSV."""
    print("\n--- Registrar Nueva Conexión ---")
    origen: str = solicitar_nodo("Nodo origen: ")
    destino: str = solicitar_nodo("Nodo destino: ")
    peso: float = solicitar_peso()

    try:
        guardar_conexion(ARCHIVO_CSV, origen, destino, peso)
    except ValueError as error:
        print(f"Error al guardar la conexión: {error}")
    except OSError as error:
        print(f"Error de sistema al acceder al archivo: {error}")
    else:
        print("Conexión guardada correctamente.")


def consultar_ruta_interactiva() -> None:
    """Carga el grafo desde el CSV y calcula la ruta más corta."""
    print("\n--- Consultar Ruta Más Corta ---")
    grafo = cargar_grafo_desde_csv(ARCHIVO_CSV)

    if not grafo.nodos:
        print("El grafo está vacío o no se pudo cargar el archivo.")
        return

    inicio: str = solicitar_nodo("Nodo origen: ")
    destino: str = solicitar_nodo("Nodo destino: ")

    costo, ruta = grafo.dijkstra(inicio, destino)

    if costo == float('inf') or not ruta:
        print(f"No existe una ruta disponible de '{inicio}' a '{destino}'.")
    else:
        camino_str: str = " -> ".join(ruta)
        print(f"\nRuta óptima: {camino_str}")
        print(f"Costo total: {costo}")


def mostrar_conexiones_interactivas() -> None:
    """Carga y muestra todas las conexiones registradas en el grafo."""
    print("\n--- Conexiones de la Red ---")
    grafo = cargar_grafo_desde_csv(ARCHIVO_CSV)

    if not grafo.nodos:
        print("No hay conexiones registradas en la red.")
        return

    for nombre, nodo_obj in grafo.nodos.items():
        conexiones = [
            f"{vecino} (peso: {peso})"
            for vecino, peso in nodo_obj.vecinos.items()
        ]
        if conexiones:
            detalles: str = ", ".join(conexiones)
            print(f"  {nombre} -> {detalles}")
        else:
            print(f"  {nombre} (Sin conexiones salientes)")


def mostrar_menu() -> None:
    """Imprime las opciones del menú principal."""
    print("\n=== RED DE TRANSPORTE ===")
    print("1. Agregar conexión")
    print("2. Consultar ruta más corta")
    print("3. Mostrar conexiones")
    print("4. Salir")


def main() -> None:
    """Función principal del programa."""
    while True:
        mostrar_menu()
        try:
            opcion: str = input("\nSelecciona una opción: ").strip()
            if opcion == "1":
                agregar_conexion_interactiva()
            elif opcion == "2":
                consultar_ruta_interactiva()
            elif opcion == "3":
                mostrar_conexiones_interactivas()
            elif opcion == "4":
                print("Saliendo del programa...")
                break
            else:
                raise ValueError("Opción inválida. Elige del 1 al 4.")
        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
