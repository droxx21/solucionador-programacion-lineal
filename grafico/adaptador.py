"""Adaptador entre el modelo común (`core.modelo.Problema`) y el
formato interno que espera `grafico.modelo` (diccionarios de objetivo
y restricciones).

Este módulo solo traduce estructuras de datos; no contiene lógica de
resolución del método gráfico, que sigue viviendo íntegramente en
`grafico/modelo.py`.
"""

from typing import Dict, List, Tuple

from core.modelo import Problema

LIMITE_VARIABLES_GRAFICO = 2


class ErrorAdaptadorGrafico(Exception):
    """Error al adaptar un `Problema` para el método gráfico."""


def validar_compatibilidad_grafico(problema: Problema) -> None:
    if problema.num_variables != LIMITE_VARIABLES_GRAFICO:
        raise ErrorAdaptadorGrafico(
            "El método gráfico solo admite problemas con exactamente "
            f"{LIMITE_VARIABLES_GRAFICO} variables (el problema actual tiene "
            f"{problema.num_variables})."
        )


def problema_a_modelo_grafico(problema: Problema) -> Tuple[Dict, List[Dict]]:
    """Convierte un `Problema` en (objetivo, restricciones) para `grafico.modelo`."""
    validar_compatibilidad_grafico(problema)

    objetivo = {
        "tipo": problema.tipo_objetivo.value,
        "a": problema.coeficientes_objetivo[0],
        "b": problema.coeficientes_objetivo[1],
    }

    restricciones = [
        {
            "a": restriccion.coeficientes[0],
            "b": restriccion.coeficientes[1],
            "relation": restriccion.tipo.value,
            "c": restriccion.termino_independiente,
        }
        for restriccion in problema.restricciones
    ]

    return objetivo, restricciones
