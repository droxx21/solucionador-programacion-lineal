"""Implementacion del metodo Simplex para problemas de maximizacion."""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

from core.numeros import formatear_numero
from simplex.utilidades import expresion


class ErrorSimplex(Exception):
    """Error comprensible producido al construir o ejecutar el modelo."""


@dataclass
class Iteracion:
    numero: int
    tabla: pd.DataFrame
    entrante: Optional[str] = None
    saliente: Optional[str] = None
    razones: Optional[List[Optional[float]]] = None
    columna_pivote: Optional[int] = None
    fila_pivote: Optional[int] = None
    elemento_pivote: Optional[float] = None
    explicacion: str = ""


class SolucionadorSimplex:
    """Simplex tabular para maximizacion con restricciones <= y b >= 0."""

    def __init__(self, funcion_objetivo: List[float], restricciones: List[List[float]],
                 terminos_independientes: List[float], nombres_variables: Optional[List[str]] = None):
        self.funcion_objetivo = np.array(funcion_objetivo, dtype=float)
        self.restricciones = np.array(restricciones, dtype=float)
        self.terminos_independientes = np.array(terminos_independientes, dtype=float)
        self.nombres_variables = nombres_variables or [
            f"x{i + 1}" for i in range(len(funcion_objetivo))
        ]
        self.tolerancia = 1e-9
        self.iteraciones: List[Iteracion] = []
        self.estado = "no_iniciado"
        self.solucion = {}
        self.valor_optimo = 0.0

        if self.restricciones.ndim != 2 or len(self.restricciones) == 0:
            raise ErrorSimplex("Debe existir al menos una restriccion.")
        if self.restricciones.shape[1] != len(self.funcion_objetivo):
            raise ErrorSimplex("Las restricciones no coinciden con las variables.")
        if len(self.terminos_independientes) != len(self.restricciones):
            raise ErrorSimplex("Cada restriccion debe tener un termino independiente.")
        if np.any(self.terminos_independientes < -self.tolerancia):
            raise ErrorSimplex(
                "El termino independiente no puede ser negativo para esta version "
                "del metodo Simplex."
            )

        self.nombres_holgura = [f"s{i + 1}" for i in range(len(self.terminos_independientes))]
        self.nombres_columnas = self.nombres_variables + self.nombres_holgura
        self.tabla = np.zeros(
            (len(self.terminos_independientes) + 1, len(self.nombres_columnas) + 1), dtype=float
        )
        self.tabla[:-1, :len(self.nombres_columnas)] = np.hstack(
            (self.restricciones, np.eye(len(self.terminos_independientes)))
        )
        self.tabla[:-1, -1] = self.terminos_independientes
        self.tabla[-1, :len(self.funcion_objetivo)] = -self.funcion_objetivo
        self.variables_basicas = self.nombres_holgura.copy()
        # `self.tabla` se modifica al iterar; se conserva la inicial para poder
        # describir el modelo que realmente se cargo en la tabla.
        self.tabla_inicial = self.tabla.copy()

    def _construir_dataframe(self) -> pd.DataFrame:
        etiquetas = self.variables_basicas + ["Z"]
        return pd.DataFrame(
            np.round(self.tabla, 10),
            index=etiquetas,
            columns=self.nombres_columnas + ["RHS"],
        )

    def modelo_estandar_texto(self) -> str:
        """Modelo con variables de holgura, leido de la tabla inicial.

        Se obtiene de la misma tabla con la que arranca el algoritmo (columnas
        `nombres_columnas`, incluidas las holguras), de modo que no puede
        divergir de lo que Simplex esta usando. La fila Z de la tabla guarda
        los coeficientes de la funcion objetivo con signo cambiado.
        """
        tabla = self.tabla_inicial
        lineas = [f"Max Z = {expresion(self.nombres_columnas, -tabla[-1, :-1])}"]
        for fila in tabla[:-1]:
            lineas.append(
                f"{expresion(self.nombres_columnas, fila[:-1])} = {formatear_numero(fila[-1])}"
            )
        lineas.append(f"{', '.join(self.nombres_columnas)} >= 0")
        return "\n".join(lineas)

    def resolver(self, maximo_iteraciones: int = 100) -> List[Iteracion]:
        """Ejecuta Simplex y conserva la tabla antes y despues de cada pivote."""
        self.iteraciones = [Iteracion(0, self._construir_dataframe(), explicacion="Tabla inicial.")]

        for numero in range(1, maximo_iteraciones + 1):
            fila_objetivo = self.tabla[-1, :-1]
            indice_entrante = int(np.argmin(fila_objetivo))
            if fila_objetivo[indice_entrante] >= -self.tolerancia:
                self.estado = "optimo"
                self._construir_solucion()
                self.iteraciones[-1].explicacion = "Se ha encontrado la solucion optima."
                return self.iteraciones

            columna = self.tabla[:-1, indice_entrante]
            razones: List[Optional[float]] = []
            filas_validas = []
            for fila, coeficiente in enumerate(columna):
                if coeficiente > self.tolerancia:
                    razones.append(float(self.tabla[fila, -1] / coeficiente))
                    filas_validas.append(fila)
                else:
                    razones.append(None)
            if not filas_validas:
                self.estado = "no_acotado"
                raise ErrorSimplex(
                    f"El problema no esta acotado: no hay variable saliente para "
                    f"{self.nombres_columnas[indice_entrante]}."
                )

            fila_saliente = min(filas_validas, key=lambda fila: razones[fila])
            pivote = self.tabla[fila_saliente, indice_entrante]
            if abs(pivote) <= self.tolerancia:
                self.estado = "invalido"
                raise ErrorSimplex("El elemento pivote es cero o invalido.")

            entrante = self.nombres_columnas[indice_entrante]
            saliente = self.variables_basicas[fila_saliente]
            actual = self.iteraciones[-1]
            actual.entrante = entrante
            actual.saliente = saliente
            actual.razones = razones
            actual.columna_pivote = indice_entrante
            actual.fila_pivote = fila_saliente
            actual.elemento_pivote = float(pivote)
            actual.explicacion = (
                f"Entra {entrante}; sale {saliente}. "
                f"Se divide la fila pivote entre {pivote:.6g} y se hacen ceros "
                "en el resto de la columna."
            )

            self.tabla[fila_saliente] /= pivote
            for fila in range(len(self.tabla)):
                if fila != fila_saliente:
                    self.tabla[fila] -= (
                        self.tabla[fila, indice_entrante]
                        * self.tabla[fila_saliente]
                    )
            self.tabla[np.abs(self.tabla) < self.tolerancia] = 0
            self.variables_basicas[fila_saliente] = entrante
            self.iteraciones.append(Iteracion(numero, self._construir_dataframe()))

        self.estado = "limite"
        raise ErrorSimplex("Se alcanzo el limite de iteraciones sin hallar el optimo.")

    def _construir_solucion(self) -> None:
        valores = {nombre: 0.0 for nombre in self.nombres_columnas}
        for fila, variable in enumerate(self.variables_basicas):
            valores[variable] = float(self.tabla[fila, -1])
        self.solucion = {nombre: valores[nombre] for nombre in self.nombres_variables}
        self.valor_optimo = float(self.tabla[-1, -1])
