from typing import Dict, Optional
import json

# Usar las implementaciones canónicas en `classes/` para evitar duplicación
from classes.grafo import Grafo
from classes.nodo import Nodo
from classes.camino import Camino


def extraer_accidentes_a_grafo(ruta_excel: str, grafo: Grafo):
    """
    Lee el archivo Excel de accidentes y agrega caminos al grafo solo para filas con dos calles.
    """
    # importar pandas localmente para evitar dependencia en tiempo de import
    import pandas as pd
    df = pd.read_excel(ruta_excel)
    id_nodo = max(grafo.nodos.keys(), default=0) + 1
    id_camino = max(grafo.caminos.keys(), default=0) + 1
    nombre_a_id = {}  # Mapea nombre de calle a id de nodo

    for _, row in df.iterrows():
        calle_1 = str(row.get('CALLE_1', '')).strip()
        calle_2 = str(row.get('CALLE_2', '')).strip()
        # Omitir filas sin dos calles válidas
        if not calle_1 or not calle_2 or calle_2 == '-' or calle_1 == '-':
            continue

        # Asignar id único a cada calle
        for calle in [calle_1, calle_2]:
            if calle not in nombre_a_id:
                nombre_a_id[calle] = id_nodo
                grafo.agregar_nodo(id_nodo, 0.0, 0.0)  # Sin lat/lon por ahora
                id_nodo += 1

        id_a = nombre_a_id[calle_1]
        id_b = nombre_a_id[calle_2]
        # Evitar caminos duplicados
        if not any(
            (camino.nodos[0].id == id_a and camino.nodos[1].id == id_b) or
            (camino.nodos[0].id == id_b and camino.nodos[1].id == id_a)
            for camino in grafo.caminos.values()
        ):
            grafo.agregar_camino(id_camino, id_a, id_b)
            id_camino += 1


def guardar_grafo_json(grafo: Grafo, ruta_archivo: str):
    """
    Guarda el grafo en un archivo JSON con toda la información de nodos y caminos.
    """
    data = {
        "nodos": [],
        "caminos": []
    }

    # Guardar nodos
    for nodo in grafo.nodos.values():
        data["nodos"].append({
            "id": nodo.id,
            "latitud": nodo.latitud,
            "longitud": nodo.longitud,
            "altura": nodo.altura,
            "prob_accidente": nodo.prob_accidente,
            "vecinos": [v.id for v in nodo.vecinos],
            "caminos": [c.id for c in nodo.caminos]
        })

    # Guardar caminos
    for camino in grafo.caminos.values():
        data["caminos"].append({
            "id": camino.id,
            "nodos": [camino.nodos[0].id, camino.nodos[1].id],
            "ciclovia": camino.ciclovia,
            "importancia": camino.importancia,
            "vecinos": [c.id for c in camino.vecinos]
        })

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Grafo guardado en {ruta_archivo}")


if __name__ == "__main__":
    g = Grafo()

    # Crear nodos de ejemplo
    g.agregar_nodo(1, -33.45, -70.65, 600, 0.1)
    g.agregar_nodo(2, -33.46, -70.66, 605, 0.05)
    g.agregar_nodo(3, -33.47, -70.67, 610, 0.2)

    # Crear caminos de ejemplo
    g.agregar_camino(101, 1, 2, ciclovia=True, importancia=2)
    g.agregar_camino(102, 2, 3, ciclovia=False, importancia=3)

    # Mostrar grafo
    print(g)
    print(g.nodos[1])
    print(g.caminos[101])