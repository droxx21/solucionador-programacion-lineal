"""Módulo de resolución con el método de la Gran M."""

from gran_m.adaptador import ErrorAdaptadorGranM, problema_a_solucionador_gran_m
from gran_m.gran_m import ErrorGranM, SolucionadorGranM

__all__ = [
    "ErrorAdaptadorGranM",
    "ErrorGranM",
    "SolucionadorGranM",
    "problema_a_solucionador_gran_m",
]
