"""Utilidades de validacion y presentacion."""

from typing import Iterable, List



def analizar_numero(valor: str, etiqueta: str) -> float:
    texto = valor.strip().replace(",", ".")
    if not texto:
        raise ValueError(f"El campo '{etiqueta}' esta vacio.")
    try:
        return float(texto)
    except ValueError as exc:
        raise ValueError(f"El campo '{etiqueta}' debe ser numerico.") from exc



def formatear_numero(valor: float) -> str:
    if abs(valor) < 1e-9:
        valor = 0
    return f"{valor:.6g}"


def expresion(nombres: Iterable[str], valores: Iterable[float]) -> str:
    partes: List[str] = []
    for nombre, valor in zip(nombres, valores):
        if abs(valor) < 1e-9:
            continue
        signo = "+" if valor > 0 and partes else ""
        coeficiente = formatear_numero(abs(valor))
        partes.append(f"{signo}{'-' if valor < 0 else ''}{coeficiente}{nombre}")
    return " ".join(partes) or "0"
