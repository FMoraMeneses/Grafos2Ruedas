import unittest
import sys
import os

# Ensure package imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib


class TestExtractorImport(unittest.TestCase):
    def test_import_and_functions(self):
        mod = importlib.import_module('Extractor')
        # verify the functions exist
        self.assertTrue(hasattr(mod, 'extraer_accidentes_a_grafo'))
        self.assertTrue(hasattr(mod, 'guardar_grafo_json'))


if __name__ == '__main__':
    unittest.main()
