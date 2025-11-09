from typing import Dict
from .nodo import Nodo
from .camino import Camino

class Grafo:
    def __init__(self):
        self.nodos: Dict[int, Nodo] = {}
        self.caminos: Dict[int, Camino] = {}

    def agregar_nodo(self, id_nodo: int, lat: float, lon: float, alt: float = 0.0, prob_acc: float = 0.0) -> Nodo:
        if id_nodo not in self.nodos:
            self.nodos[id_nodo] = Nodo(id_nodo, lat, lon, alt, prob_acc)
        return self.nodos[id_nodo]

    def agregar_camino(self, id_camino: int, id_nodo_a: int, id_nodo_b: int, ciclovia: bool = False, importancia: int = 1) -> Camino:
        if id_camino not in self.caminos:
            nodo_a = self.nodos[id_nodo_a]
            nodo_b = self.nodos[id_nodo_b]
            self.caminos[id_camino] = Camino(id_camino, nodo_a, nodo_b, ciclovia, importancia)
        return self.caminos[id_camino]

    def __repr__(self):
        return f"Grafo(nodos={len(self.nodos)}, caminos={len(self.caminos)})"
