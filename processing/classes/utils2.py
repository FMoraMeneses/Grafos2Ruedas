import os
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# Resolve path relative to package root: Mapas/DataCiclovias/alturas_santiago.csv
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ALT_PATH = os.path.join(BASE_DIR, 'Mapas', 'DataCiclovias', 'alturas_santiago.csv')
if not os.path.exists(ALT_PATH):
    # Fallback to data/ for backward compatibility
    ALT_PATH = os.path.join(BASE_DIR, '..', 'data', 'alturas_santiago.csv')

# Cargar dataset y preparar árbol
DF = pd.read_csv(ALT_PATH)
COORDS = DF[['lat', 'lon']].values
TREE = cKDTree(COORDS)

# Solo deben pasarle la latitud y la longitud tal y como se muestra en los parametros
def altura_aproximada(lat, lon, k=3):
    """
    Estima la altura (ele) de un punto (lat, lon)
    usando interpolación promedio de los k vecinos más cercanos.
    """
    distancias, indices = TREE.query([lat, lon], k=k)
    alturas = DF.iloc[indices]['ele'].values

    if k == 1:
        return alturas[0]
    else:
        pesos = 1 / (distancias + 1e-8)  # evitar división por cero
        return np.sum(pesos * alturas) / np.sum(pesos)
