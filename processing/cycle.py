import osmnx as ox
import pandas as pd

# u: ID del nodo origen (nodo inicial de la arista en el grafo)
# v: ID del nodo destino (nodo final de la arista en el grafo)
# lat_origen: latitud del nodo origen
# lon_origen: longitud del nodo origen
# lat_destino: latitud del nodo destino
# lon_destino: longitud del nodo destino
# length: longitud de la arista en metros (distancia física del tramo)
# highway: tipo de vía según OpenStreetMap (ej: cycleway, residential, primary, etc.)
# name: nombre de la vía, si está disponible en OSM (puede estar vacío)

# Cargar grafo desde archivo .osm
G = ox.graph_from_xml("map.osm")

# Convertir grafo en GeoDataFrames
nodes, edges = ox.graph_to_gdfs(G)

# Resetear índice para obtener u y v como columnas
edges = edges.reset_index()

# Filtrar solo ciclovías
ciclovias = edges[edges['highway'] == 'cycleway'].copy()

# Agregar coordenadas de nodos de origen (u) y destino (v)
ciclovias = ciclovias.merge(
    nodes[['y', 'x']], left_on='u', right_index=True
).rename(columns={'y':'lat_origen','x':'lon_origen'})

ciclovias = ciclovias.merge(
    nodes[['y', 'x']], left_on='v', right_index=True
).rename(columns={'y':'lat_destino','x':'lon_destino'})

# Seleccionar columnas clave
cols = ['u','v','lat_origen','lon_origen',
        'lat_destino','lon_destino',
        'length','highway']

# Agregar 'name' solo si existe
if 'name' in ciclovias.columns:
    cols.append('name')

ciclovias = ciclovias[cols]

# Guardar CSV
ciclovias.to_csv("ciclovias.csv", index=False)

print("✅ CSV generado: ciclovias.csv")
print(ciclovias.head())
