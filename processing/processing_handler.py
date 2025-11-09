"""
Manejador de routing que conecta la interfaz con los algoritmos reales
"""

from processing.classes import routing

class RoutingHandler:
    def __init__(self, grafo):
        self.grafo = grafo
    
    def calcular_ruta(self, origen, destino, estrategia, algoritmo):
        """Calcular ruta usando los algoritmos reales"""
        try:
            origen = int(origen)
            destino = int(destino)
            
            if origen not in self.grafo.nodos or destino not in self.grafo.nodos:
                return None, "Nodos no encontrados"
            
            # Configurar pesos según estrategia
            if estrategia == "corta":
                # Usar distancias como peso
                ruta, costo = routing.dijkstra(self.grafo, origen, destino)
            elif estrategia == "segura":
                # Usar probabilidad de accidente como peso
                ruta, costo = self._dijkstra_seguridad(origen, destino)
            elif estrategia == "balanceada":
                # Combinación de distancia y seguridad
                ruta, costo = self._dijkstra_balanceado(origen, destino)
            else:
                return None, "Estrategia no válida"
            
            return ruta, f"Ruta calculada: {len(ruta)} nodos, costo: {costo:.2f}"
            
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def _dijkstra_seguridad(self, origen, destino):
        """Dijkstra que prioriza seguridad sobre distancia"""
        # Implementar usando probabilidades de accidente como pesos
        pass
    
    def _dijkstra_balanceado(self, origen, destino):
        """Dijkstra que balancea distancia y seguridad"""
        pass