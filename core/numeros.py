"""Parseo y formateo numérico unificado para todo el proyecto.

Este módulo centraliza dos operaciones que antes estaban duplicadas de
forma distinta en `grafico/modelo.py` (con soporte de fracciones) y en
`simplex/utilidades.py` (con soporte de coma decimal): analizar texto
ingresado por el usuario y convertirlo a `float`, y formatear números
para mostrarlos en pantalla.

Soporta:
- Números con punto decimal ("3.5") o coma decimal ("3,5").
- Fracciones simples ("1/2", "-3/4").
"""

import math


def analizar_numero(valor, etiqueta: str = "valor") -> float:
    """Convierte `valor` a `float`, aceptando coma decimal y fracciones.

    `valor` puede ser un `int`/`float` ya numérico, o un texto con
    notación decimal (con punto o coma) o fraccionaria ("1/2").
    `etiqueta` se usa únicamente para identificar el campo en los
    mensajes de error.
    """
    if isinstance(valor, (int, float)):
        numero = float(valor)
        if math.isnan(numero):
            raise ValueError(f"El campo '{etiqueta}' no es válido.")
        return numero

    texto = str(valor).strip()
    if texto == "":
        raise ValueError(f"El campo '{etiqueta}' está vacío.")

    texto_normalizado = texto.replace(",", ".")

    if "/" in texto_normalizado:
        partes = texto_normalizado.split("/")
        if len(partes) != 2:
            raise ValueError(f"El campo '{etiqueta}' tiene una fracción no válida.")
        numerador = analizar_numero(partes[0], etiqueta)
        denominador = analizar_numero(partes[1], etiqueta)
        if abs(denominador) < 1e-12:
            raise ValueError(f"El campo '{etiqueta}' no puede dividir entre cero.")
        return numerador / denominador

    try:
        numero = float(texto_normalizado)
    except ValueError as exc:
        raise ValueError(f"El campo '{etiqueta}' debe ser numérico o una fracción válida.") from exc

    if math.isnan(numero):
        raise ValueError(f"El campo '{etiqueta}' no es válido.")
    return numero


def formatear_numero(valor: float) -> str:
    """Formatea un número para mostrarlo en pantalla."""
    if abs(valor) < 1e-9:
        valor = 0
    return f"{valor:.6g}"
