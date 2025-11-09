"""
Procesador mejorado para archivo map_clean.osm que conecta nodos basándose en las ways OSM
"""

import xml.etree.ElementTree as ET
from processing.classes.grafo import Grafo
from processing.classes.nodo import Nodo
from processing.classes.camino import Camino
from processing.classes.routing import distancia_haversine

class OSMProcessor:
    def __init__(self):
        self.grafo = Grafo()
        self.ways_data = {}  # Almacenar información de las ways
        
    def procesar_osm(self, ruta_osm):
        """Procesar archivo OSM usando las ways para conexiones reales"""
        print(f"📁 Procesando {ruta_osm}...")
        
        try:
            tree = ET.parse(ruta_osm)
            root = tree.getroot()
            
            # Contadores
            nodos_procesados = 0
            caminos_creados = 0
            
            # Primera pasada: extraer todos los nodos
            nodos_osm = {}
            for node in root.findall("node"):
                node_id = int(node.attrib["id"])
                lat = float(node.attrib["lat"])
                lon = float(node.attrib["lon"])
                
                # Determinar tipo y probabilidad de accidente basado en tags
                prob_accidente = self._calcular_probabilidad_seguridad(node)
                altura = self._estimar_altura(lat, lon)
                
                # Agregar al grafo
                self.grafo.agregar_nodo(node_id, lat, lon, altura, prob_accidente)
                nodos_osm[node_id] = {
                    'lat': lat, 
                    'lon': lon,
                    'prob_accidente': prob_accidente,
                    'altura': altura
                }
                nodos_procesados += 1
            
            print(f"📊 Nodos extraídos: {nodos_procesados}")
            
            # Segunda pasada: procesar ways para conexiones reales
            caminos_creados = self._procesar_ways(root, nodos_osm)
            
            # Tercera pasada: conectar nodos cercanos que no estén en ways
            conexiones_extra = self._conectar_nodos_cercanos(nodos_osm)
            caminos_creados += conexiones_extra
            
            print(f"✅ OSM procesado: {nodos_procesados} nodos, {caminos_creados} caminos")
            return self.grafo
            
        except Exception as e:
            print(f"❌ Error procesando OSM: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _procesar_ways(self, root, nodos_osm):
        """Procesar las ways OSM para crear conexiones reales entre nodos"""
        print("🛣️ Procesando ways OSM...")
        caminos_creados = 0
        
        for way in root.findall("way"):
            way_id = way.attrib["id"]
            nodes_in_way = []
            
            # Recoger todos los nodos de esta way
            for nd in way.findall("nd"):
                node_ref = int(nd.attrib["ref"])
                if node_ref in nodos_osm:
                    nodes_in_way.append(node_ref)
            
            # Si la way tiene menos de 2 nodos, saltar
            if len(nodes_in_way) < 2:
                continue
            
            # Determinar propiedades de la way basadas en tags
            es_ciclovia, importancia = self._analizar_tags_way(way)
            
            # Crear conexiones entre nodos consecutivos en la way
            for i in range(len(nodes_in_way) - 1):
                node1 = nodes_in_way[i]
                node2 = nodes_in_way[i + 1]
                
                # Verificar si ya existe esta conexión
                if self._conexion_existe(node1, node2):
                    continue
                
                # Calcular distancia real
                nodo1_data = nodos_osm[node1]
                nodo2_data = nodos_osm[node2]
                distancia = distancia_haversine(
                    nodo1_data['lat'], nodo1_data['lon'],
                    nodo2_data['lat'], nodo2_data['lon']
                )
                
                # Crear camino con peso basado en distancia y seguridad
                peso = distancia * (1 + nodo1_data['prob_accidente'] + nodo2_data['prob_accidente'])
                
                camino_id = len(self.grafo.caminos) + 1
                self.grafo.agregar_camino(camino_id, node1, node2, es_ciclovia, peso)
                caminos_creados += 1
        
        print(f"   📍 Conexiones desde ways: {caminos_creados}")
        return caminos_creados
    
    def _analizar_tags_way(self, way):
        """Analizar tags de una way para determinar si es ciclovía y su importancia"""
        es_ciclovia = False
        importancia = 1
        
        for tag in way.findall("tag"):
            k = tag.attrib['k']
            v = tag.attrib['v']
            
            # Detectar ciclovías
            if k == 'highway' and v == 'cycleway':
                es_ciclovia = True
                importancia = 2
            elif k == 'bicycle' and v in ['yes', 'designated']:
                es_ciclovia = True
                importancia = 2
            elif k == 'cycleway':
                es_ciclovia = True
                importancia = 2
            
            # Ajustar importancia basado en tipo de vía
            if k == 'highway':
                if v in ['motorway', 'trunk']:
                    importancia = 3  # Menos seguro para ciclistas
                elif v in ['primary', 'secondary']:
                    importancia = 2
                elif v in ['residential', 'tertiary']:
                    importancia = 1  # Más seguro
        
        return es_ciclovia, importancia
    
    def _conectar_nodos_cercanos(self, nodos_osm):
        """Conectar nodos cercanos que no estén conectados por ways"""
        print("🔗 Conectando nodos cercanos adicionales...")
        caminos_creados = 0
        nodos_list = list(nodos_osm.keys())
        
        # Limitar para rendimiento
        max_nodos = min(100, len(nodos_list))
        
        for i in range(max_nodos):
            node1_id = nodos_list[i]
            node1_data = nodos_osm[node1_id]
            
            for j in range(i + 1, min(i + 30, len(nodos_list))):
                node2_id = nodos_list[j]
                node2_data = nodos_osm[node2_id]
                
                distancia = distancia_haversine(
                    node1_data['lat'], node1_data['lon'],
                    node2_data['lat'], node2_data['lon']
                )
                
                # Conectar solo nodos muy cercanos (menos de 100m) y que no estén ya conectados
                if distancia < 100 and not self._conexion_existe(node1_id, node2_id):
                    es_ciclovia = False  # Asumir que no es ciclovía por defecto
                    peso = distancia * (1 + node1_data['prob_accidente'] + node2_data['prob_accidente'])
                    
                    camino_id = len(self.grafo.caminos) + 1
                    self.grafo.agregar_camino(camino_id, node1_id, node2_id, es_ciclovia, peso)
                    caminos_creados += 1
        
        print(f"   📍 Conexiones cercanas adicionales: {caminos_creados}")
        return caminos_creados
    
    def _conexion_existe(self, node1_id, node2_id):
        """Verificar si ya existe una conexión entre dos nodos"""
        for camino in self.grafo.caminos.values():
            nodos_camino = [camino.nodos[0].id, camino.nodos[1].id]
            if node1_id in nodos_camino and node2_id in nodos_camino:
                return True
        return False
    
    def _calcular_probabilidad_seguridad(self, node):
        """Calcular probabilidad de accidente basado en tags OSM"""
        tags = {tag.attrib['k']: tag.attrib['v'] for tag in node.findall("tag")}
        
        # Basado en tipo de elemento OSM
        if 'highway' in tags:
            highway_type = tags['highway']
            if highway_type == 'traffic_signals':
                return 0.2  # Semáforos: más seguro
            elif highway_type == 'crossing':
                return 0.3  # Cruces: seguridad media
            elif highway_type in ['stop', 'give_way']:
                return 0.4  # Señales de pare/ceda
        
        # Si es estación de metro, más seguro
        if 'railway' in tags and tags['railway'] == 'station':
            return 0.1
        
        return 0.5  # Valor por defecto
    
    def _estimar_altura(self, lat, lon):
        """Estimar altura basada en coordenadas (puedes mejorar esto con datos reales)"""
        # Estimación simple basada en la latitud (puedes reemplazar con datos CSV)
        altura_base = 570  # Altura base de Santiago
        variacion = (lat + 33.45) * 1000  # Variación basada en latitud
        return altura_base + variacion

# Función de conveniencia
def cargar_grafo_desde_osm(ruta_osm="data/generados/map_clean.osm"):
    """Cargar grafo desde OSM en una sola función"""
    processor = OSMProcessor()
    return processor.procesar_osm(ruta_osm)