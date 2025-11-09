import unittest
import sys
import os
import tempfile
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except Exception:
    PANDAS_AVAILABLE = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from classes import safety


class TestSafetyIndicator(unittest.TestCase):
    def setUp(self):
        # Crear un DataFrame con algunas de las filas de ejemplo
        rows = [
            {'ID':45697, 'COMUNA':'INDEPENDENCIA', 'FALLECIDO':0, 'GRAVE':0, 'M/GRAVE':0, 'LEVE':0},
            {'ID':47048, 'COMUNA':'VITACURA', 'FALLECIDO':0, 'GRAVE':0, 'M/GRAVE':0, 'LEVE':0},
            {'ID':45049, 'COMUNA':'RENCA', 'FALLECIDO':1, 'GRAVE':0, 'M/GRAVE':0, 'LEVE':7},
            {'ID':45365, 'COMUNA':'QUEMCHI', 'FALLECIDO':0, 'GRAVE':1, 'M/GRAVE':0, 'LEVE':1},
        ]
        if PANDAS_AVAILABLE:
            self.df = pd.DataFrame(rows)
        else:
            self.df = None

    def test_calculo_indicador(self):
        if not PANDAS_AVAILABLE:
            self.skipTest('pandas no disponible: test de safety saltado')

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            path = tmp.name
        try:
            self.df.to_excel(path, index=False)
            scores = safety.calcular_indicador_seguridad_desde_excel(path, agrupar_por='COMUNA')
            self.assertIn('RENCA', scores)
            self.assertIn('VITACURA', scores)
            norm = safety.normalizar_scores(scores)
            # valores normalizados entre 0 y 1
            for v in norm.values():
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.0)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
