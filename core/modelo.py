"""Modelo común de un problema de Programación Lineal.

Este módulo representa únicamente el problema matemático original:
tipo de objetivo, función objetivo, restricciones y condiciones de las
variables.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TipoObjetivo(str, Enum):
    """Tipo de optimización del problema."""
    MAXIMIZAR = "Maximizar"
    MINIMIZAR = "Minimizar"


class TipoRestriccion(str, Enum):
    """Tipo de relación de una restricción"""

    MENOR_IGUAL = "<="
    MAYOR_IGUAL = ">="
    IGUAL = "="


@dataclass
class CondicionVariable:
    """Condición sobre una variable del problema (p. ej. x >= 0)."""

    variable: str
    tipo: str = "no_negativa"


@dataclass
class Restriccion:
    """Una restricción lineal: coeficientes * variables {relación} término."""

    coeficientes: List[float]
    tipo: TipoRestriccion
    termino_independiente: float
    etiqueta: str = ""


@dataclass
class Problema:
    """Representación completa de un problema de Programación Lineal."""

    tipo_objetivo: TipoObjetivo
    nombres_variables: List[str]
    coeficientes_objetivo: List[float]
    restricciones: List[Restriccion]
    condiciones_variables: List[CondicionVariable] = field(default_factory=list)

    @property
    def num_variables(self) -> int:
        return len(self.nombres_variables)