# Grafos2Ruedas
Proyecto de Mapa Interactivo para el curso de Grafos y Algoritmos

# Sistema de Routing para Ciclovías de Santiago

Sistema interactivo para cálculo de rutas óptimas en ciclovías usando teoría de grafos.

## Estructura

sistema-ciclovias/
├── data/ # Datos de entrada y salida
├── processing/ # Scripts de procesamiento
├── tests/ # Tests
└── mapa_interactivo.py # Interfaz principal

Herramientas del profe:
- Sistemas de Información Geográfica (Geographical Information Systems, GIS):
https://guides.library.columbia.edu/geotools/Python
- Transporte Terrestre:
https://www.openstreetmap.org/
https://project-osrm.org/
- Transporte Terrestre Público:
https://www.dtpm.cl/index.php/sistema-transporte-publico-santiago/datos-y-servicios
https://gtfs.org/
https://www.opentripplanner.org/

## Objetivo de archivos en `/classes`

**nodo.py**
Objetivo: Define nodo de grafo.
Input: id, lat, lon, alt, prob_accidente
Output: Nodo con vecinos y caminos

**camino.py**
Objetivo: Define conexión entre nodos.
Input: id, nodo_a, nodo_b, ciclovia, importancia (importanacia es para penalizar o favorecer rutas solo segun la seguridad de la comunas)
Output: Camino enlazando nodos

**grafo.py**
Objetivo: Gestiona nodos y caminos.
Input: nodos y caminos
Output: Grafo completo

**safety.py**
Objetivo: Calcula indicador de seguridad.
Input: ruta Excel, agrupación
Output: Diccionario {grupo: score}

**routing.py**
Objetivo: Algoritmos de ruteo (Dijkstra, A*).
Input: grafo, nodos, pesos
Output: Camino óptimo (lista de nodos)

**utils.py**
Objetivo: Guardar grafo en JSON.
Input: grafo, ruta archivo
Output: Archivo JSON

**utils2.py**
Objetivo: Estimar altura por coordenadas.
Input: latitud, longitud
Output: Altura estimada