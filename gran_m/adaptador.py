"""Adaptador para el método de la Gran M."""

from core.modelo import Problema, TipoObjetivo, TipoRestriccion
from gran_m.gran_m import ErrorGranM, SolucionadorGranM


class ErrorAdaptadorGranM(Exception):
    """Error al adaptar un problema al método Gran M."""


def validar_compatibilidad_gran_m(problema: Problema) -> None:
    """Valida que el problema sea soportado por la técnica de Gran M."""
    if problema.tipo_objetivo not in (TipoObjetivo.MAXIMIZAR, TipoObjetivo.MINIMIZAR):
        raise ErrorAdaptadorGranM("El objetivo del problema no es soportado.")
    if not problema.restricciones:
        raise ErrorAdaptadorGranM("Debe existir al menos una restricción.")
    if any(restriccion.termino_independiente < 0 for restriccion in problema.restricciones):
        raise ErrorAdaptadorGranM("Las restricciones con RHS negativo deben convertirse previamente.")


def problema_a_solucionador_gran_m(problema: Problema, valor_M: float = 1_000_000.0) -> SolucionadorGranM:
    """Construye un `SolucionadorGranM` a partir de un `Problema` compatible."""
    validar_compatibilidad_gran_m(problema)
    return SolucionadorGranM(problema, valor_M=valor_M)
