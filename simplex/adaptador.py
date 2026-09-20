"""Adaptador entre el modelo común (`core.modelo.Problema`) y el
`SolucionadorSimplex`.

Por ahora el método Simplex tabular (`simplex/simplex.py`) solo
resuelve problemas de maximización con restricciones `<=` y términos
independientes no negativos. Los casos de minimización o de
restricciones `>=`/`=` requieren la técnica de la Gran M, que se
implementará más adelante dentro de este mismo paquete (`simplex/`),
sin que `core.modelo` necesite cambiar.
"""

from core.modelo import Problema, TipoObjetivo, TipoRestriccion
from simplex.simplex import SolucionadorSimplex


class ErrorAdaptadorSimplex(Exception):
    """Error al adaptar un `Problema` para la versión actual del método Simplex."""


def validar_compatibilidad_simplex(problema: Problema) -> None:
    if problema.tipo_objetivo != TipoObjetivo.MAXIMIZAR:
        raise ErrorAdaptadorSimplex(
            "Esta versión del método Simplex solo resuelve problemas de "
            "maximización. La minimización requiere la técnica de la Gran M, "
            "aún no disponible."
        )

    restricciones_no_soportadas = [
        restriccion
        for restriccion in problema.restricciones
        if restriccion.tipo != TipoRestriccion.MENOR_IGUAL
    ]
    if restricciones_no_soportadas:
        raise ErrorAdaptadorSimplex(
            "Esta versión del método Simplex solo admite restricciones <=. "
            "Las restricciones >= o = requieren la técnica de la Gran M, "
            "aún no disponible."
        )

    if any(restriccion.termino_independiente < 0 for restriccion in problema.restricciones):
        raise ErrorAdaptadorSimplex(
            "Los términos independientes deben ser no negativos para esta "
            "versión del método Simplex."
        )


def problema_a_solucionador_simplex(problema: Problema) -> SolucionadorSimplex:
    """Construye un `SolucionadorSimplex` a partir de un `Problema` compatible."""
    validar_compatibilidad_simplex(problema)

    restricciones = [list(restriccion.coeficientes) for restriccion in problema.restricciones]
    terminos_independientes = [
        restriccion.termino_independiente for restriccion in problema.restricciones
    ]

    return SolucionadorSimplex(
        list(problema.coeficientes_objetivo),
        restricciones,
        terminos_independientes,
        list(problema.nombres_variables),
    )
