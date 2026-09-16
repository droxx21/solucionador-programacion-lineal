"""Implementacion del metodo Simplex para problemas de maximizacion."""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd


class SimplexError(Exception):
    """Error comprensible producido al construir o ejecutar el modelo."""


@dataclass
class Iteration:
    number: int
    tableau: pd.DataFrame
    entering: Optional[str] = None
    leaving: Optional[str] = None
    ratios: Optional[List[Optional[float]]] = None
    pivot_column: Optional[int] = None
    pivot_row: Optional[int] = None
    pivot_element: Optional[float] = None
    explanation: str = ""


class SimplexSolver:
    """Simplex tabular para maximizacion con restricciones <= y b >= 0."""

    def __init__(self, objective: List[float], constraints: List[List[float]],
                 rhs: List[float], variable_names: Optional[List[str]] = None):
        self.objective = np.array(objective, dtype=float)
        self.constraints = np.array(constraints, dtype=float)
        self.rhs = np.array(rhs, dtype=float)
        self.variable_names = variable_names or [
            f"x{i + 1}" for i in range(len(objective))
        ]
        self.tolerance = 1e-9
        self.iterations: List[Iteration] = []
        self.status = "not_started"
        self.solution = {}
        self.optimal_value = 0.0

        if self.constraints.ndim != 2 or len(self.constraints) == 0:
            raise SimplexError("Debe existir al menos una restriccion.")
        if self.constraints.shape[1] != len(self.objective):
            raise SimplexError("Las restricciones no coinciden con las variables.")
        if len(self.rhs) != len(self.constraints):
            raise SimplexError("Cada restriccion debe tener un termino independiente.")
        if np.any(self.rhs < -self.tolerance):
            raise SimplexError(
                "El termino independiente no puede ser negativo para esta version "
                "del metodo Simplex."
            )

        self.slack_names = [f"s{i + 1}" for i in range(len(self.rhs))]
        self.column_names = self.variable_names + self.slack_names
        self.tableau = np.zeros(
            (len(self.rhs) + 1, len(self.column_names) + 1), dtype=float
        )
        self.tableau[:-1, :len(self.column_names)] = np.hstack(
            (self.constraints, np.eye(len(self.rhs)))
        )
        self.tableau[:-1, -1] = self.rhs
        self.tableau[-1, :len(self.objective)] = -self.objective
        self.basic_variables = self.slack_names.copy()

    def _dataframe(self) -> pd.DataFrame:
        labels = self.basic_variables + ["Z"]
        return pd.DataFrame(
            np.round(self.tableau, 10),
            index=labels,
            columns=self.column_names + ["RHS"],
        )

    def solve(self, max_iterations: int = 100) -> List[Iteration]:
        """Ejecuta Simplex y conserva la tabla antes y despues de cada pivote."""
        self.iterations = [Iteration(0, self._dataframe(), explanation="Tabla inicial.")]

        for number in range(1, max_iterations + 1):
            objective_row = self.tableau[-1, :-1]
            entering_index = int(np.argmin(objective_row))
            if objective_row[entering_index] >= -self.tolerance:
                self.status = "optimal"
                self._build_solution()
                self.iterations[-1].explanation = "Se ha encontrado la solucion optima."
                return self.iterations

            column = self.tableau[:-1, entering_index]
            ratios: List[Optional[float]] = []
            valid_rows = []
            for row, coefficient in enumerate(column):
                if coefficient > self.tolerance:
                    ratios.append(float(self.tableau[row, -1] / coefficient))
                    valid_rows.append(row)
                else:
                    ratios.append(None)
            if not valid_rows:
                self.status = "unbounded"
                raise SimplexError(
                    f"El problema no esta acotado: no hay variable saliente para "
                    f"{self.column_names[entering_index]}."
                )

            leaving_row = min(valid_rows, key=lambda row: ratios[row])
            pivot = self.tableau[leaving_row, entering_index]
            if abs(pivot) <= self.tolerance:
                self.status = "invalid"
                raise SimplexError("El elemento pivote es cero o invalido.")

            entering = self.column_names[entering_index]
            leaving = self.basic_variables[leaving_row]
            current = self.iterations[-1]
            current.entering = entering
            current.leaving = leaving
            current.ratios = ratios
            current.pivot_column = entering_index
            current.pivot_row = leaving_row
            current.pivot_element = float(pivot)
            current.explanation = (
                f"Entra {entering}; sale {leaving}. "
                f"Se divide la fila pivote entre {pivot:.6g} y se hacen ceros "
                "en el resto de la columna."
            )

            self.tableau[leaving_row] /= pivot
            for row in range(len(self.tableau)):
                if row != leaving_row:
                    self.tableau[row] -= (
                        self.tableau[row, entering_index]
                        * self.tableau[leaving_row]
                    )
            self.tableau[np.abs(self.tableau) < self.tolerance] = 0
            self.basic_variables[leaving_row] = entering
            self.iterations.append(Iteration(number, self._dataframe()))

        self.status = "limit"
        raise SimplexError("Se alcanzo el limite de iteraciones sin hallar el optimo.")

    def _build_solution(self) -> None:
        values = {name: 0.0 for name in self.column_names}
        for row, variable in enumerate(self.basic_variables):
            values[variable] = float(self.tableau[row, -1])
        self.solution = {name: values[name] for name in self.variable_names}
        self.optimal_value = float(self.tableau[-1, -1])
