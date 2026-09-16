"""Utilidades de validacion y presentacion."""

from typing import Iterable, List


def parse_number(value: str, label: str) -> float:
    text = value.strip().replace(",", ".")
    if not text:
        raise ValueError(f"El campo '{label}' esta vacio.")
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"El campo '{label}' debe ser numerico.") from exc


def format_number(value: float) -> str:
    if abs(value) < 1e-9:
        value = 0
    return f"{value:.6g}"


def expression(names: Iterable[str], values: Iterable[float]) -> str:
    parts: List[str] = []
    for name, value in zip(names, values):
        if abs(value) < 1e-9:
            continue
        sign = "+" if value > 0 and parts else ""
        coefficient = format_number(abs(value))
        parts.append(f"{sign}{'-' if value < 0 else ''}{coefficient}{name}")
    return " ".join(parts) or "0"
