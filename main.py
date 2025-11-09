"""
Ejemplo de uso del sistema de grafos y ruteo.

Comandos útiles:
- Ejecutar tests desde la raíz del repositorio:
  - `PYTHONPATH=. python3 -m unittest discover -s GrafosYDosRuedas/tests -v`
  - o (desde dentro de `GrafosYDosRuedas`): `python3 -m unittest discover -s tests -v`
- Ejecutar este ejemplo:
  - `PYTHONPATH=. python3 GrafosYDosRuedas/main.py`

Este script construye un grafo de ejemplo, calcula rutas con A* y Dijkstra
usando `classes.routing` y guarda la ruta encontrada en `ruta_ejemplo.json`.
"""

from classes.grafo import Grafo
from classes.utils import guardar_grafo_json
try:
  from classes.utils2 import altura_aproximada
except Exception:
  # Fallback simple si no hay pandas/scipy en el entorno
  def altura_aproximada(lat, lon, k=3):
    print('Aviso: paquete para alturas no disponible; usando altura fija 0.0')
    return 0.0
from classes import routing
import json


def guardar_ruta(ruta: list, ruta_archivo: str):
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump({'ruta': ruta}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    g = Grafo()

    # Crear nodos con alturas aproximadas
    g.agregar_nodo(1, -33.45, -70.65, altura_aproximada(-33.45, -70.65), 0.1)
    g.agregar_nodo(2, -33.46, -70.66, altura_aproximada(-33.46, -70.66), 0.05)
    g.agregar_nodo(3, -33.47, -70.67, altura_aproximada(-33.47, -70.67), 0.2)

    # Crear caminos
    g.agregar_camino(101, 1, 2, ciclovia=True, importancia=2)
    g.agregar_camino(102, 2, 3, ciclovia=False, importancia=3)

    # Mostrar info básica
    print(g)
    print(g.nodos[1])
    print(g.caminos[101])

    # Calcular ruta con A* (A-estrella)
    ruta_ast = routing.a_estrella(g, 1, 3, w_dist=1.0, w_elev=0.01, w_seg=10.0)
    print('Ruta A*:', ruta_ast)
    if ruta_ast:
        guardar_ruta(ruta_ast, 'ruta_ejemplo_ast.json')

    # Calcular ruta con Dijkstra
    dist, prev = routing.dijkstra(g, 1, goal_id=3, w_dist=1.0, w_elev=0.01, w_seg=10.0)
    ruta_dijk = routing.reconstruir_camino(prev, 1, 3)
    print('Ruta Dijkstra:', ruta_dijk)
    if ruta_dijk:
        guardar_ruta(ruta_dijk, 'ruta_ejemplo_dijkstra.json')

    # Guardar grafo completo a JSON
    guardar_grafo_json(g, 'grafo.json')
