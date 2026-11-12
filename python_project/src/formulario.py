from .financial_engine import PerfilFinanciero


def construir_perfil(datos):
    return PerfilFinanciero(
        saldo_inicial=float(str(datos["saldo_inicial"]).replace(".", "")),
        ingreso_mensual=float(str(datos["ingreso_mensual"]).replace(".", "")),
        gastos_fijos_mensuales=float(str(datos["gastos_fijos_mensuales"]).replace(".", "")),
        gasto_variable_diario_promedio=float(
            str(datos["gasto_variable_diario_promedio"]).replace(".", "")
        ),
        dias_a_proyectar=int(datos["dias_a_proyectar"]),
    )