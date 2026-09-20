"""Validación de entradas y construcción del modelo común `Problema`.

Este módulo es el único responsable de validar los datos crudos
ingresados por el usuario (texto) y de ensamblarlos en un `Problema`
ya validado. Ni `grafico/` ni `simplex/` necesitan repetir estas
validaciones: reciben siempre un `Problema` consistente.
"""

from typing import List, Optional, Sequence

from core.modelo import CondicionVariable, Problema, Restriccion, TipoObjetivo, TipoRestriccion
from core.numeros import analizar_numero


class ErrorModelo(Exception):
    """Error comprensible al construir o validar un `Problema`."""


_RELACIONES_VALIDAS = {
    "<=": TipoRestriccion.MENOR_IGUAL,
    ">=": TipoRestriccion.MAYOR_IGUAL,
    "=": TipoRestriccion.IGUAL,
}


def validar_numero_variables(cantidad) -> int:
    try:
        numero = int(cantidad)
    except (TypeError, ValueError) as exc:
        raise ErrorModelo("El número de variables debe ser un entero positivo.") from exc
    if numero < 1:
        raise ErrorModelo("El número de variables debe ser un entero positivo.")
    return numero


def validar_tipo_objetivo(valor) -> TipoObjetivo:
    texto = str(valor).strip().capitalize()
    for tipo in TipoObjetivo:
        if tipo.value == texto:
            return tipo
    raise ErrorModelo("El tipo de objetivo debe ser 'Maximizar' o 'Minimizar'.")


def validar_tipo_restriccion(valor) -> TipoRestriccion:
    texto = str(valor).strip()
    if texto not in _RELACIONES_VALIDAS:
        raise ErrorModelo("El tipo de restricción debe ser <=, >= o =.")
    return _RELACIONES_VALIDAS[texto]


def _validar_lista_coeficientes(valores: Sequence, num_variables: int, contexto: str) -> List[float]:
    if len(valores) != num_variables:
        raise ErrorModelo(
            f"{contexto}: se esperaban {num_variables} coeficientes, se recibieron {len(valores)}."
        )
    coeficientes = []
    for indice, valor in enumerate(valores, start=1):
        try:
            coeficientes.append(analizar_numero(valor, f"{contexto}, coeficiente x{indice}"))
        except ValueError as exc:
            raise ErrorModelo(str(exc)) from exc
    return coeficientes


def construir_restriccion(
    coeficientes: Sequence,
    tipo,
    termino_independiente,
    num_variables: int,
    etiqueta: str = "",
) -> Restriccion:
    """Valida y construye una única restricción.

    Pensada para usarse mientras el usuario agrega restricciones una a
    una en el formulario, con validación inmediata de cada fila.
    """
    contexto = etiqueta or "Restricción"
    coeficientes_validados = _validar_lista_coeficientes(coeficientes, num_variables, contexto)
    tipo_validado = validar_tipo_restriccion(tipo)
    try:
        termino = analizar_numero(termino_independiente, f"{contexto}, término independiente")
    except ValueError as exc:
        raise ErrorModelo(str(exc)) from exc
    return Restriccion(
        coeficientes=coeficientes_validados,
        tipo=tipo_validado,
        termino_independiente=termino,
        etiqueta=etiqueta,
    )


def construir_problema(
    tipo_objetivo,
    nombres_variables: Sequence[str],
    coeficientes_objetivo: Sequence,
    restricciones: Sequence[Restriccion],
    condiciones_variables: Optional[Sequence[CondicionVariable]] = None,
) -> Problema:
    """Valida los datos del formulario y ensambla el `Problema` final.

    `restricciones` debe ser una secuencia de `Restriccion` ya
    construidas (típicamente con `construir_restriccion`, una por
    una, a medida que el usuario las agrega).
    """
    tipo_validado = validar_tipo_objetivo(tipo_objetivo)
    num_variables = validar_numero_variables(len(nombres_variables))

    nombres = [str(nombre).strip() for nombre in nombres_variables]
    if any(not nombre for nombre in nombres):
        raise ErrorModelo("Todos los nombres de variables deben especificarse.")
    if len(set(nombres)) != len(nombres):
        raise ErrorModelo("Los nombres de las variables deben ser únicos.")

    coeficientes_obj = _validar_lista_coeficientes(coeficientes_objetivo, num_variables, "Función objetivo")

    if not restricciones:
        raise ErrorModelo("Debe ingresar al menos una restricción.")

    for restriccion in restricciones:
        if len(restriccion.coeficientes) != num_variables:
            raise ErrorModelo(
                "Todas las restricciones deben tener un coeficiente por cada variable."
            )

    if condiciones_variables is None:
        condiciones = [CondicionVariable(variable=nombre, tipo="no_negativa") for nombre in nombres]
    else:
        condiciones = list(condiciones_variables)
        if len(condiciones) != num_variables:
            raise ErrorModelo("Debe existir una condición por cada variable.")

    return Problema(
        tipo_objetivo=tipo_validado,
        nombres_variables=nombres,
        coeficientes_objetivo=coeficientes_obj,
        restricciones=list(restricciones),
        condiciones_variables=condiciones,
    )
