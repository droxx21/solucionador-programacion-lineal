"""Presentacion de los resultados del metodo grafico.

Convierte lo que devuelve `grafico.modelo.resolver_modelo` en filas de
texto listas para mostrar, con el formato numerico unificado del
proyecto. No calcula nada: solo da formato.
"""

from typing import Dict, List, Sequence, Tuple

from core.numeros import formatear_numero


def filas_evaluacion(
    vertices: Sequence[Tuple[float, float]], evaluaciones: Sequence[Dict[str, float]]
) -> List[Tuple[str, str, str, str]]:
    """Filas (vertice, x, y, Z) con la funcion objetivo evaluada en cada vertice.

    `evaluaciones` sigue el mismo orden que `vertices` (asi lo genera
    `evaluar_funcion`). Las coordenadas se toman de `vertices`, sin
    redondear, para coincidir con las del optimo; Z es el valor que ya
    calculo el solucionador.
    """
    return [
        (
            str(evaluacion["vertice"]),
            formatear_numero(x),
            formatear_numero(y),
            formatear_numero(evaluacion["z"]),
        )
        for (x, y), evaluacion in zip(vertices, evaluaciones)
    ]