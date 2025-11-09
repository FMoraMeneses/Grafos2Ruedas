import json
from .grafo import Grafo

def guardar_grafo_json(grafo: Grafo, ruta_archivo: str):
    data = {"nodos": [], "caminos": []}

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


