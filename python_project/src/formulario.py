"""formulario.py - HU-01: convierte los datos del formulario web en un
PerfilFinanciero que entiende el motor (financial_engine.py)."""

from typing import Any, Mapping

from .financial_engine import PerfilFinanciero

# Campos de dinero del formulario (en COP, pueden venir con separador de miles)
CAMPOS_MONTO = (
    "saldo_inicial",
    "ingreso_mensual",
    "gastos_fijos_mensuales",
    "gasto_variable_diario_promedio",
)


def limpiar_monto(valor: Any) -> float:
    """Quita el separador de miles: '1.500.000' -> 1500000.0 (COP sin decimales)."""
    return float(str(valor).replace(".", ""))


def construir_perfil(datos: Mapping[str, Any]) -> PerfilFinanciero:
    """Crea el PerfilFinanciero a partir de los cinco campos del formulario."""
    montos = {campo: limpiar_monto(datos[campo]) for campo in CAMPOS_MONTO}
    return PerfilFinanciero(**montos, dias_a_proyectar=int(datos["dias_a_proyectar"]))