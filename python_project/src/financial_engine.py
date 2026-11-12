"""
financial_engine.py
--------------------
Motor de Cálculo Financiero y Evaluación de Viabilidad — Proyecto SEFI-Personal
"¿En cuánto me quedo sin plata?"

Este módulo es TOTALMENTE INDEPENDIENTE Y DESACOPLADO de cualquier interfaz de
usuario o capa de persistencia (requisito de la Etapa 1). Contiene dos bloques
funcionales:

1. Proyección de saldo personal (núcleo del producto): a partir de un saldo
   inicial, ingresos y gastos (fijos + variables), proyecta día a día el saldo
   disponible y determina el "día de quiebre" (el día en que el saldo se
   vuelve negativo).
2. Motor de evaluación financiera VAN/TIR (requisito técnico obligatorio del
   entregable): permite evaluar la viabilidad de una decisión financiera
   puntual del usuario (p. ej. tomar un préstamo, comprar a cuotas o hacer una
   inversión) usando Valor Actual Neto (VAN) y Tasa Interna de Retorno (TIR),
   calculada esta última mediante el método numérico de Bisección.

Autoras/autor: Isabella Gómez Quiroz, Susana Sánchez Jaramillo, Jonathan Martínez Bedoya
Asignatura: Gestión Ágil de Proyectos — TdeA
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence


# ---------------------------------------------------------------------------
# Excepciones del dominio
# ---------------------------------------------------------------------------

class FlujoInvalidoError(ValueError):
    """Se lanza cuando la lista de flujos de caja es nula, vacía o inválida."""


class NoConvergenciaError(RuntimeError):
    """Se lanza cuando el método numérico de la TIR no converge dentro del
    número máximo de iteraciones permitido."""


# ---------------------------------------------------------------------------
# BLOQUE 1 — Proyección de saldo personal ("¿En cuánto me quedo sin plata?")
# ---------------------------------------------------------------------------

@dataclass
class PerfilFinanciero:
    """Datos de entrada que el usuario ingresa en la web.

    Attributes:
        saldo_inicial: Dinero disponible hoy (día 0).
        ingreso_mensual: Ingreso fijo que se recibe cada 30 días (mesada,
            salario de medio tiempo, etc.).
        gastos_fijos_mensuales: Suma de gastos fijos que se cobran una vez al
            mes (arriendo, servicios, suscripciones).
        gasto_variable_diario_promedio: Promedio de "gasto hormiga" u otros
            gastos variables que se producen todos los días (comida,
            transporte).
        dias_a_proyectar: Horizonte de la simulación en días.
    """

    saldo_inicial: float
    ingreso_mensual: float
    gastos_fijos_mensuales: float
    gasto_variable_diario_promedio: float
    dias_a_proyectar: int = 90

    def __post_init__(self) -> None:
        if self.dias_a_proyectar <= 0:
            raise FlujoInvalidoError("dias_a_proyectar debe ser mayor que 0.")
        if self.gasto_variable_diario_promedio < 0:
            raise FlujoInvalidoError("El gasto variable diario no puede ser negativo.")


@dataclass
class ResultadoProyeccion:
    """Salida de la proyección, lista para graficar (saldo vs. día)."""

    saldos_diarios: List[float]
    dia_quiebre: Optional[int]  # None si el saldo nunca llega a 0 en el horizonte
    saldo_final: float = field(init=False)

    def __post_init__(self) -> None:
        self.saldo_final = self.saldos_diarios[-1]


def proyectar_saldo(perfil: PerfilFinanciero) -> ResultadoProyeccion:
    """Proyecta el saldo día a día y detecta el día en que el usuario
    "se queda sin plata" (saldo < 0 por primera vez).

    Regla de negocio:
    - El ingreso mensual se acredita cada 30 días (día 30, 60, 90, ...).
    - Los gastos fijos mensuales se prorratean y se descuentan cada día.
    - El gasto variable diario promedio se descuenta todos los días.

    Args:
        perfil: Datos de entrada del usuario.

    Returns:
        ResultadoProyeccion con la serie diaria de saldo y el día de quiebre.

    Raises:
        FlujoInvalidoError: si el perfil es None.
    """
    if perfil is None:
        raise FlujoInvalidoError("El perfil financiero no puede ser nulo.")

    saldo = perfil.saldo_inicial
    saldos_diarios: List[float] = []
    dia_quiebre: Optional[int] = None
    gasto_fijo_diario_equivalente = perfil.gastos_fijos_mensuales / 30.0

    for dia in range(1, perfil.dias_a_proyectar + 1):
        if dia % 30 == 0:
            saldo += perfil.ingreso_mensual
        saldo -= gasto_fijo_diario_equivalente
        saldo -= perfil.gasto_variable_diario_promedio
        saldos_diarios.append(round(saldo, 2))
        if dia_quiebre is None and saldo < 0:
            dia_quiebre = dia

    return ResultadoProyeccion(saldos_diarios=saldos_diarios, dia_quiebre=dia_quiebre)


def simular_reduccion_gasto_hormiga(
    perfil: PerfilFinanciero, porcentaje_reduccion: float = 0.20
) -> ResultadoProyeccion:
    """Simula el efecto de reducir el gasto variable diario (gasto hormiga)
    un porcentaje dado. Sirve para validar la hipótesis de investigación:
    "Visualizar los gastos reduce el gasto hormiga en un 20%".

    Args:
        perfil: Perfil financiero original.
        porcentaje_reduccion: Fracción de reducción del gasto variable diario
            (0.20 = 20%).

    Returns:
        ResultadoProyeccion con el nuevo escenario, para comparar contra la
        escenario base.
    """
    if not 0 <= porcentaje_reduccion <= 1:
        raise FlujoInvalidoError("porcentaje_reduccion debe estar entre 0 y 1.")

    perfil_optimizado = PerfilFinanciero(
        saldo_inicial=perfil.saldo_inicial,
        ingreso_mensual=perfil.ingreso_mensual,
        gastos_fijos_mensuales=perfil.gastos_fijos_mensuales,
        gasto_variable_diario_promedio=perfil.gasto_variable_diario_promedio
        * (1 - porcentaje_reduccion),
        dias_a_proyectar=perfil.dias_a_proyectar,
    )
    return proyectar_saldo(perfil_optimizado)


# ---------------------------------------------------------------------------
# BLOQUE 2 — Motor VAN / TIR (requisito técnico obligatorio del entregable)
# ---------------------------------------------------------------------------

def calcular_van(tasa_descuento: float, flujos_de_caja: Sequence[float]) -> float:
    """Calcula el Valor Actual Neto (VAN) de una serie de flujos de caja.

    flujos_de_caja[0] se interpreta como la inversión inicial (I_0), que debe
    ir en t=0 y típicamente es negativa; flujos_de_caja[1:] son los flujos de
    los periodos 1..n.

    Args:
        tasa_descuento: Tasa de descuento/oportunidad por periodo, en
            decimales (ej. 0.08 para 8%).
        flujos_de_caja: Lista ordenada [FC_0, FC_1, ..., FC_n].

    Returns:
        El VAN como número flotante.

    Raises:
        FlujoInvalidoError: si la lista de flujos es nula o está vacía.
    """
    return round(_van_sin_redondeo(tasa_descuento, flujos_de_caja), 2)


def _van_sin_redondeo(tasa_descuento: float, flujos_de_caja: Sequence[float]) -> float:
    """Cálculo interno del VAN sin redondeo, usado por el método numérico de
    la TIR para evitar que el redondeo a 2 decimales del VAN "de reporte"
    introduzca error en la búsqueda de raíces."""
    if not flujos_de_caja:
        raise FlujoInvalidoError("La lista de flujos de caja no puede estar vacía.")
    van = 0.0
    for periodo, flujo in enumerate(flujos_de_caja):
        van += flujo / ((1 + tasa_descuento) ** periodo)
    return van


def calcular_tir(
    flujos_de_caja: Sequence[float],
    epsilon: float = 1e-6,
    max_iteraciones: int = 1000,
    limite_inferior: float = -0.9999,
    limite_superior: float = 10.0,
) -> float:
    """Calcula la Tasa Interna de Retorno (TIR) mediante el método numérico
    de Bisección, dado que no existe un despeje algebraico directo para
    polinomios de grado > 4 (teorema de Abel-Ruffini).

    La TIR es la tasa `r` tal que VAN(r) = 0.

    Args:
        flujos_de_caja: Lista ordenada [FC_0, FC_1, ..., FC_n]. FC_0 debe ser
            negativo (inversión) y debe existir al menos un flujo positivo,
            de lo contrario no hay cambio de signo y no existe una TIR real.
        epsilon: Tolerancia de error para el criterio de parada (por defecto
            1e-6).
        max_iteraciones: Número máximo de iteraciones permitidas.
        limite_inferior: Cota inferior del intervalo de búsqueda de la tasa.
        limite_superior: Cota superior del intervalo de búsqueda de la tasa.

    Returns:
        La TIR estimada, como decimal (ej. 0.15 = 15%).

    Raises:
        FlujoInvalidoError: si los flujos son nulos/vacíos o no hay cambio de
            signo.
        NoConvergenciaError: si el método no converge dentro de
            max_iteraciones.
    """
    if not flujos_de_caja or len(flujos_de_caja) < 2:
        raise FlujoInvalidoError(
            "Se requieren al menos dos flujos de caja (inversión inicial y un retorno)."
        )

    van_bajo = _van_sin_redondeo(limite_inferior, flujos_de_caja)
    van_alto = _van_sin_redondeo(limite_superior, flujos_de_caja)

    if van_bajo * van_alto > 0:
        raise FlujoInvalidoError(
            "No hay cambio de signo en el intervalo de búsqueda: no existe "
            "una TIR real con estos flujos (revise que haya al menos un "
            "flujo negativo y uno positivo)."
        )

    a, b = limite_inferior, limite_superior
    for _ in range(1, max_iteraciones + 1):
        punto_medio = (a + b) / 2
        van_medio = _van_sin_redondeo(punto_medio, flujos_de_caja)

        if abs(van_medio) < epsilon or (b - a) / 2 < epsilon:
            return round(punto_medio, 6)

        if _van_sin_redondeo(a, flujos_de_caja) * van_medio < 0:
            b = punto_medio
        else:
            a = punto_medio

    raise NoConvergenciaError(
        f"La TIR no convergió después de {max_iteraciones} iteraciones "
        f"con tolerancia epsilon={epsilon}."
    )


# ---------------------------------------------------------------------------
# BLOQUE 3 — Motor de Decisión y Diagnóstico Integrado
# ---------------------------------------------------------------------------

class EvaluacionVAN(str, Enum):
    VIABLE = "Viable"
    INDIFERENTE = "Indiferente"
    NO_VIABLE = "No viable"


class EvaluacionTIR(str, Enum):
    ACEPTABLE = "Aceptable"
    INSUFICIENTE = "Insuficiente"


@dataclass
class DictamenFinanciero:
    van: float
    tir: Optional[float]
    tasa_referencia: float
    evaluacion_van: EvaluacionVAN
    evaluacion_tir: Optional[EvaluacionTIR]
    recomendacion: str


def evaluar_viabilidad(
    flujos_de_caja: Sequence[float], tasa_descuento: float
) -> DictamenFinanciero:
    """Motor de decisión: consolida VAN y TIR en un único dictamen de
    viabilidad con una recomendación para el usuario/cliente.

    Reglas:
    VAN > 0 -> Viable | VAN = 0 -> Indiferente | VAN < 0 -> No viable
    TIR > r -> Aceptable | TIR <= r -> Insuficiente

    Args:
        flujos_de_caja: [FC_0, FC_1, ..., FC_n].
        tasa_descuento: Tasa de descuento/oportunidad de referencia (r).

    Returns:
        Un DictamenFinanciero con ambos indicadores y una recomendación.
    """
    van = calcular_van(tasa_descuento, flujos_de_caja)

    if van > 0:
        evaluacion_van = EvaluacionVAN.VIABLE
    elif van == 0:
        evaluacion_van = EvaluacionVAN.INDIFERENTE
    else:
        evaluacion_van = EvaluacionVAN.NO_VIABLE

    tir: Optional[float] = None
    evaluacion_tir: Optional[EvaluacionTIR] = None
    try:
        tir = calcular_tir(flujos_de_caja)
        evaluacion_tir = (
            EvaluacionTIR.ACEPTABLE if tir > tasa_descuento else EvaluacionTIR.INSUFICIENTE
        )
    except (FlujoInvalidoError, NoConvergenciaError):
        tir = None
        evaluacion_tir = None

    if evaluacion_van == EvaluacionVAN.VIABLE and evaluacion_tir == EvaluacionTIR.ACEPTABLE:
        recomendacion = (
            "La decisión financiera es recomendable: genera valor por "
            "encima de la tasa de oportunidad exigida."
        )
    elif evaluacion_van == EvaluacionVAN.NO_VIABLE:
        recomendacion = (
            "No se recomienda tomar esta decisión: destruye valor respecto "
            "a la tasa de oportunidad."
        )
    else:
        recomendacion = (
            "Resultado mixto o en el límite: se recomienda analizar el "
            "riesgo y sensibilizar los supuestos antes de decidir."
        )

    return DictamenFinanciero(
        van=van,
        tir=tir,
        tasa_referencia=tasa_descuento,
        evaluacion_van=evaluacion_van,
        evaluacion_tir=evaluacion_tir,
        recomendacion=recomendacion,
    )
