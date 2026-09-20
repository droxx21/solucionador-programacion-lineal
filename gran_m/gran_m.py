"""Transformación del problema original para resolverlo con el Simplex existente."""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from core.modelo import Problema, Restriccion, TipoObjetivo, TipoRestriccion
from simplex.simplex import SolucionadorSimplex


class ErrorGranM(Exception):
    """Error comprensible producido al preparar o ejecutar Gran M."""


def _normalizar_restriccion(restriccion: Restriccion) -> Restriccion:
    """Asegura RHS no negativo invirtiendo la desigualdad si hace falta."""
    if restriccion.termino_independiente >= 0:
        return restriccion
    coeficientes = [-coeficiente for coeficiente in restriccion.coeficientes]
    if restriccion.tipo == TipoRestriccion.MENOR_IGUAL:
        nuevo_tipo = TipoRestriccion.MAYOR_IGUAL
    elif restriccion.tipo == TipoRestriccion.MAYOR_IGUAL:
        nuevo_tipo = TipoRestriccion.MENOR_IGUAL
    else:
        nuevo_tipo = TipoRestriccion.IGUAL
    return Restriccion(
        coeficientes=coeficientes,
        tipo=nuevo_tipo,
        termino_independiente=-restriccion.termino_independiente,
        etiqueta=restriccion.etiqueta,
    )


@dataclass
class TransformacionGranM:
    """Crea la versión canónica para reutilizar el Simplex actual."""

    problema: Problema
    valor_M: float = 1000.0
    restricciones: Optional[List[List[float]]] = None
    terminos_independientes: Optional[List[float]] = None
    nombres_variables: Optional[List[str]] = None
    funcion_objetivo: Optional[List[float]] = None
    variables_basicas_iniciales: Optional[List[str]] = None
    artificiales: Optional[List[str]] = None

    def __post_init__(self):
        self._transformar()

    def _transformar(self) -> None:
        if self.valor_M <= 0:
            raise ErrorGranM("La penalización M debe ser positiva.")

        restricciones = [_normalizar_restriccion(r) for r in self.problema.restricciones]
        n = self.problema.num_variables
        num_slacks = sum(1 for r in restricciones if r.tipo == TipoRestriccion.MENOR_IGUAL)
        num_excess = sum(1 for r in restricciones if r.tipo == TipoRestriccion.MAYOR_IGUAL)
        num_artificiales = sum(1 for r in restricciones if r.tipo in (TipoRestriccion.MAYOR_IGUAL, TipoRestriccion.IGUAL))
        total_columnas = n + num_slacks + num_excess + num_artificiales

        filas: List[List[float]] = []
        rhs: List[float] = []
        base: List[str] = []
        slack_names: List[str] = []
        excess_names: List[str] = []
        artificial_names: List[str] = []

        contador_slack = 0
        contador_excess = 0
        contador_artificial = 0

        for restriccion in restricciones:
            fila = [0.0] * total_columnas
            for indice, coeficiente in enumerate(restriccion.coeficientes):
                fila[indice] = coeficiente

            if restriccion.tipo == TipoRestriccion.MENOR_IGUAL:
                nombre = f"s{contador_slack + 1}"
                fila[n + contador_slack] = 1.0
                slack_names.append(nombre)
                base.append(nombre)
                contador_slack += 1
            elif restriccion.tipo == TipoRestriccion.MAYOR_IGUAL:
                exceso = f"e{contador_excess + 1}"
                artificial = f"a{contador_artificial + 1}"
                fila[n + num_slacks + contador_excess] = -1.0
                fila[n + num_slacks + num_excess + contador_artificial] = 1.0
                excess_names.append(exceso)
                artificial_names.append(artificial)
                base.append(artificial)
                contador_excess += 1
                contador_artificial += 1
            elif restriccion.tipo == TipoRestriccion.IGUAL:
                artificial = f"a{contador_artificial + 1}"
                fila[n + num_slacks + num_excess + contador_artificial] = 1.0
                artificial_names.append(artificial)
                base.append(artificial)
                contador_artificial += 1
            else:
                raise ErrorGranM(f"Tipo de restricción no soportado: {restriccion.tipo}")

            filas.append(fila)
            rhs.append(restriccion.termino_independiente)

        nombres_totales = list(self.problema.nombres_variables) + slack_names + excess_names + artificial_names
        objetivo = list(self.problema.coeficientes_objetivo)
        if self.problema.tipo_objetivo == TipoObjetivo.MINIMIZAR:
            objetivo = [-coeficiente for coeficiente in objetivo]
        objetivo.extend([0.0] * (num_slacks + num_excess + num_artificiales))
        for nombre in artificial_names:
            objetivo[nombres_totales.index(nombre)] = -self.valor_M

        self.restricciones = filas
        self.terminos_independientes = rhs
        self.nombres_variables = nombres_totales
        self.funcion_objetivo = objetivo
        self.variables_basicas_iniciales = base
        self.artificiales = artificial_names

    def construir_solucionador(self) -> SolucionadorSimplex:
        if self.restricciones is None or self.terminos_independientes is None:
            raise ErrorGranM("La transformación no está lista para resolver.")
        solucionador = SolucionadorSimplex(
            self.funcion_objetivo,
            self.restricciones,
            self.terminos_independientes,
            self.nombres_variables,
            variables_basicas_iniciales=self.variables_basicas_iniciales,
        )
        for fila, variable in enumerate(solucionador.variables_basicas):
            if variable.startswith("a"):
                indice_columna = solucionador.nombres_columnas.index(variable)
                factor = -solucionador.funcion_objetivo[indice_columna]
                solucionador.tabla[-1] -= factor * solucionador.tabla[fila]
        solucionador.tabla[np.abs(solucionador.tabla) < solucionador.tolerancia] = 0
        solucionador.tabla_inicial = solucionador.tabla.copy()
        return solucionador


class SolucionadorGranM:
    """Resuelve un problema usando Gran M y reutiliza el Simplex existente."""

    def __init__(self, problema: Problema, valor_M: float = 1000.0):
        self.problema = problema
        self.valor_M = float(valor_M)
        self.transformacion = TransformacionGranM(problema, valor_M=self.valor_M)
        self.solucionador = self.transformacion.construir_solucionador()
        self.iteraciones = []
        self.solucion = {}
        self.valor_optimo = 0.0
        self.estado = "no_iniciado"

    def resolver(self, maximo_iteraciones: int = 100):
        self.iteraciones = self.solucionador.resolver(maximo_iteraciones=maximo_iteraciones)
        self.solucion = {
            nombre: float(valor)
            for nombre, valor in self.solucionador.solucion.items()
            if nombre in self.problema.nombres_variables
        }
        self.valor_optimo = float(self.solucionador.valor_optimo)
        if self.problema.tipo_objetivo == TipoObjetivo.MINIMIZAR:
            self.valor_optimo = -self.valor_optimo

        for nombre in self.transformacion.artificiales or []:
            valor = self.solucionador.solucion.get(nombre, 0.0)
            if valor > self.solucionador.tolerancia:
                self.estado = "no_factible"
                return self.iteraciones
        self.estado = self.solucionador.estado
        return self.iteraciones

    def modelo_estandar_texto(self) -> str:
        return self.solucionador.modelo_estandar_texto()


def problema_a_solucionador_gran_m(problema: Problema, valor_M: float = 1000.0) -> SolucionadorGranM:
    """Crea un `SolucionadorGranM` para un problema original."""
    return SolucionadorGranM(problema, valor_M=valor_M)
