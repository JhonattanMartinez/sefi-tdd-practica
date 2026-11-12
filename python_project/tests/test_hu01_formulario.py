import os
import sys
import unittest

# Agrega python_project/ al buscador de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.financial_engine import PerfilFinanciero
from src.formulario import construir_perfil


class TestHU01ConstruirPerfil(unittest.TestCase):
    """HU-01: el formulario de cinco campos alimenta al motor financiero."""

    def test_construye_perfil_con_los_cinco_campos(self):
        # CA1/CA2: los cinco campos del formulario llegan al motor
        datos = {
            "saldo_inicial": "500000",
            "ingreso_mensual": "0",
            "gastos_fijos_mensuales": "300000",
            "gasto_variable_diario_promedio": "15000",
            "dias_a_proyectar": "30",
        }
        perfil = construir_perfil(datos)

        self.assertIsInstance(perfil, PerfilFinanciero)
        self.assertEqual(perfil.saldo_inicial, 500000.0)
        self.assertEqual(perfil.gasto_variable_diario_promedio, 15000.0)
        self.assertEqual(perfil.dias_a_proyectar, 30)

    def test_conserva_valor_numerico_sin_separador_de_miles(self):
        # CA3: el campo muestra 1.500.000 pero el cálculo usa 1500000
        datos = {
            "saldo_inicial": "1.500.000",
            "ingreso_mensual": "3.000.000",
            "gastos_fijos_mensuales": "1.800.000",
            "gasto_variable_diario_promedio": "40.000",
            "dias_a_proyectar": "60",
        }
        perfil = construir_perfil(datos)

        self.assertEqual(perfil.saldo_inicial, 1500000.0)
        self.assertEqual(perfil.ingreso_mensual, 3000000.0)
        self.assertEqual(perfil.gastos_fijos_mensuales, 1800000.0)


if __name__ == "__main__":
    unittest.main()