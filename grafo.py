"""Representa una red de transporte mediante nodos, grafos y Dijkstra."""

import math
from typing import Dict, List, Optional, Set, Tuple


class Nodo:
    """Representa una ubicación y sus conexiones dirigidas con peso."""

    def __init__(self, nombre: str) -> None:
        """Inicializa la identificación y el diccionario de vecinos."""
        self.nombre: str = nombre
        self.vecinos: Dict[str, float] = {}

    def agregar_vecino(self, vecino: str, peso: float) -> None:
        """Agrega un vecino si su peso es finito y no negativo."""
        if not math.isfinite(peso) or peso < 0:
            raise ValueError("Dijkstra requiere pesos no negativos.")
        self.vecinos[vecino] = peso

    def __repr__(self) -> str:
        """Muestra el identificador del nodo."""
        return f"Nodo({self.nombre})"


class Grafo:
    """Almacena los nodos de una red de transporte dirigida."""

    def __init__(self) -> None:
        """Inicializa el conjunto de nodos indexados por nombre."""
        self.nodos: Dict[str, Nodo] = {}

    def obtener_o_crear_nodo(self, nombre: str) -> Nodo:
        """Busca un nodo por su nombre o lo crea si no existe."""
        if nombre not in self.nodos:
            self.nodos[nombre] = Nodo(nombre)
        return self.nodos[nombre]

    def agregar_arista(self, origen: str, destino: str, peso: float) -> None:
        """Añade una arista dirigida sin dejar nodos nuevos si falla."""
        origen_nuevo = origen not in self.nodos
        destino_nuevo = destino not in self.nodos
        n_origen = self.obtener_o_crear_nodo(origen)
        self.obtener_o_crear_nodo(destino)

        try:
            n_origen.agregar_vecino(destino, peso)
        except ValueError:
            if origen_nuevo:
                del self.nodos[origen]
            if destino_nuevo and destino in self.nodos:
                del self.nodos[destino]
            raise

    def dijkstra(self, inicio: str, destino: str) -> Tuple[float, List[str]]:
        """Calcula el camino mínimo y su peso total entre dos nodos."""
        if inicio not in self.nodos or destino not in self.nodos:
            return float("inf"), []

        distancias: Dict[str, float] = {}
        anteriores: Dict[str, Optional[str]] = {}
        visitados: Set[str] = set()

        for nombre in self.nodos:
            distancias[nombre] = float("inf")
            anteriores[nombre] = None

        distancias[inicio] = 0.0

        while len(visitados) < len(self.nodos):
            nodo_actual: Optional[str] = None
            menor_distancia = float("inf")

            for nombre in self.nodos:
                if nombre not in visitados:
                    if distancias[nombre] < menor_distancia:
                        menor_distancia = distancias[nombre]
                        nodo_actual = nombre

            if nodo_actual is None:
                break

            if nodo_actual == destino:
                break

            visitados.add(nodo_actual)

            nodo = self.nodos[nodo_actual]
            for vecino, peso in nodo.vecinos.items():
                nueva_distancia = distancias[nodo_actual] + peso
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    anteriores[vecino] = nodo_actual

        if math.isinf(distancias[destino]):
            return float("inf"), []

        camino: List[str] = []
        actual: Optional[str] = destino

        while actual is not None:
            camino.append(actual)
            actual = anteriores[actual]

        camino.reverse()
        return distancias[destino], camino


if __name__ == "__main__":
    grafo_prueba = Grafo()
    grafo_prueba.agregar_arista("A", "B", 4.0)
    grafo_prueba.agregar_arista("A", "C", 2.0)
    grafo_prueba.agregar_arista("B", "C", 1.0)
    grafo_prueba.agregar_arista("C", "D", 2.0)
    grafo_prueba.agregar_arista("B", "D", 5.0)

    costo, ruta = grafo_prueba.dijkstra("A", "D")
    assert (costo, ruta) == (4.0, ["A", "C", "D"])
    assert grafo_prueba.dijkstra("D", "A") == (float("inf"), [])
    assert grafo_prueba.dijkstra("A", "A") == (0.0, ["A"])

    for invalido in (-3.0, float("nan"), float("inf")):
        try:
            grafo_prueba.agregar_arista("D", "E", invalido)
        except ValueError:
            assert "E" not in grafo_prueba.nodos
        else:
            raise AssertionError("Se aceptó un peso inválido")

    print("Pruebas básicas de grafo.py: correctas")
