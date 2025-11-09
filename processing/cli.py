#!/usr/bin/env python3
"""CLI para ejecutar el flujo completo:
leer Excel de accidentes -> calcular indicador -> asignar a nodos -> calcular ruta

Ejemplo:
  PYTHONPATH=. python3 GrafosYDosRuedas/cli.py --accidentes data/os2_sin_2025_08.xlsx \
    --agrupar COMUNA --inicio 1 --objetivo 3 --alg astar --w_dist 1.0 --w_elev 0.01 --w_seg 1.0

    otro ejemplo:

    python .\cli.py --accidentes data/os2_sin_2025_08.xlsx --agrupar COMUNA --inicio 386235 --objetivo 386236 --alg astar --w_dist 1.0 --w_elev 0.01 --w_seg 1.0

"""

import argparse
import json
import os

from classes.grafo import Grafo
from classes import routing
from classes import safety
from classes.utils import guardar_grafo_json
import xml.etree.ElementTree as ET

def construir_grafo_desde_osm():
    """
    Construye un grafo a partir de un archivo .osm (OpenStreetMap XML).

    Parámetros:
        ruta_osm (str): ruta al archivo .osm

    Retorna:
        Grafo: instancia del grafo con los nodos y caminos cargados
    """

    ruta_osm = "data/map_with_elevation.osm" # Reemplazar por otra direccion del .osm al que se quiere armar el grafo

    g = Grafo()

    tree = ET.parse(ruta_osm)
    root = tree.getroot()

    # 1️⃣ Cargar todos los nodos (lat, lon, elevación)
    nodos = {}
    for node in root.findall("node"):
        node_id = int(node.attrib["id"])
        lat = float(node.attrib["lat"])
        lon = float(node.attrib["lon"])
        ele = float(node.attrib.get("ele", 0.0))
        g.agregar_nodo(node_id, lat, lon, ele, 0)  # puedes adaptar 'x' según tu sistema
        nodos[node_id] = (lat, lon, ele)

    # 2️⃣ Cargar las vías (campos)
    for way in root.findall("way"):
        way_id = int(way.attrib["id"])
        refs = [int(nd.attrib["ref"]) for nd in way.findall("nd")]

        # Filtrar solo las vías que sean caminos o ciclovías
        tags = {t.attrib["k"]: t.attrib["v"] for t in way.findall("tag")}
        highway_type = tags.get("highway")
        if not highway_type:
            continue  # ignorar vías que no sean caminos

        # Marcar si es ciclovía
        ciclovia = (highway_type == "cycleway") or (tags.get("bicycle") == "yes")

        # Importancia simple según tipo de camino
        importancia = {
            "motorway": 1,
            "primary": 2,
            "secondary": 3,
            "tertiary": 4,
            "residential": 5,
            "cycleway": 6,
        }.get(highway_type, 10)

        # Crear conexiones entre nodos consecutivos
        # Use a unique id for each segment (way may have many segments).
        # Start an incremental counter for caminos to avoid id collisions.
        id_camino_counter = max(g.caminos.keys(), default=0) + 1
        for i in range(len(refs) - 1):
            n1 = refs[i]
            n2 = refs[i + 1]
            if n1 in nodos and n2 in nodos:
                g.agregar_camino(id_camino_counter, n1, n2, ciclovia=ciclovia, importancia=importancia)
                id_camino_counter += 1

    return g




def main():
    p = argparse.ArgumentParser()
    p.add_argument('--accidentes', help='Ruta al Excel de accidentes', required=True)
    p.add_argument('--agrupar', help='Columna para agrupar (ej: COMUNA, ZONA)', default='COMUNA')
    p.add_argument('--inicio', type=int, help='ID nodo inicio', required=True)
    p.add_argument('--objetivo', type=int, help='ID nodo objetivo', required=True)
    p.add_argument('--alg', choices=['astar', 'dijkstra'], default='astar')
    p.add_argument('--w_dist', type=float, default=1.0)
    p.add_argument('--w_elev', type=float, default=0.0)
    p.add_argument('--w_seg', type=float, default=1.0)
    p.add_argument('--out_dir', default='.')

    args = p.parse_args()

    # construir o cargar grafo
    g = construir_grafo_desde_osm()
    print(f"Grafo construido con {len(g.nodos)} nodos y {len(g.caminos)} caminos.")

    # calcular indicador de seguridad
    print(f'Calculando indicador desde {args.accidentes} agrupando por {args.agrupar}...')
    scores = safety.calcular_indicador_seguridad_desde_excel(args.accidentes, agrupar_por=args.agrupar)
    norm = safety.normalizar_scores(scores)
    print(f'Grupos calculados: {len(norm)}')

    # Nota: este ejemplo espera que los nodos tengan atributo `comuna` o similar.
    # En la práctica debes asignar `nodo.comuna` cuando importes/crees nodos.
    print('Asignando indicador a nodos... (buscando atributo "comuna")')
    routing.asignar_indicador_seguridad(g, norm, nodo_attr='comuna')

    # calcular ruta
    if args.alg == 'astar':
        ruta = routing.a_estrella(g, args.inicio, args.objetivo, w_dist=args.w_dist, w_elev=args.w_elev, w_seg=args.w_seg)
    else:
        _, prev = routing.dijkstra(g, args.inicio, goal_id=args.objetivo, w_dist=args.w_dist, w_elev=args.w_elev, w_seg=args.w_seg)
        ruta = routing.reconstruir_camino(prev, args.inicio, args.objetivo)

    print('Ruta calculada:', ruta)

    os.makedirs(args.out_dir, exist_ok=True)
    ruta_file = os.path.join(args.out_dir, 'ruta_cli.json')
    with open(ruta_file, 'w', encoding='utf-8') as f:
        json.dump({'ruta': ruta}, f, ensure_ascii=False, indent=2)
    print('Ruta guardada en', ruta_file)

    # guardar grafo
    guardar_grafo_json(g, os.path.join(args.out_dir, 'grafo_cli.json'))


if __name__ == '__main__':
    main()
