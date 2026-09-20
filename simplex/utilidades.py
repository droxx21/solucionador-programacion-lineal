"""Utilidades de validacion y presentacion."""

from typing import TYPE_CHECKING, Iterable, List, Optional

from core.numeros import formatear_numero

if TYPE_CHECKING:  # Solo para anotaciones; evita una importacion circular en tiempo de ejecucion.
    from simplex.simplex import Iteracion


def analizar_numero(valor: str, etiqueta: str) -> float:
    texto = valor.strip().replace(",", ".")
    if not texto:
        raise ValueError(f"El campo '{etiqueta}' esta vacio.")
    try:
        return float(texto)
    except ValueError as exc:
        raise ValueError(f"El campo '{etiqueta}' debe ser numerico.") from exc


def expresion(nombres: Iterable[str], valores: Iterable[float]) -> str:
    """Escribe una combinacion lineal, p. ej. `0.5x1 + s1 - 3x2`.

    Omite los terminos nulos y el coeficiente cuando vale +-1.
    """
    partes: List[str] = []
    for nombre, valor in zip(nombres, valores):
        if abs(valor) < 1e-9:
            continue
        magnitud = abs(valor)
        coeficiente = "" if abs(magnitud - 1) < 1e-9 else formatear_numero(magnitud)
        if partes:
            partes.append(f"{'-' if valor < 0 else '+'} {coeficiente}{nombre}")
        else:
            partes.append(f"{'-' if valor < 0 else ''}{coeficiente}{nombre}")
    return " ".join(partes) or "0"


def formatear_razones(razones: Optional[List[Optional[float]]]) -> List[str]:
    """Razones de la prueba del cociente, con '-' donde la fila no participa."""
    return ["-" if razon is None else formatear_numero(razon) for razon in (razones or [])]


def formatear_iteracion(item: "Iteracion") -> str:
    """Texto de una iteracion: tabla y, si hubo pivoteo, el detalle de la operacion.

    Solo presenta datos que `SolucionadorSimplex.resolver()` ya calculo y
    guardo en `Iteracion`; no recalcula nada. La ultima iteracion (la
    optima) no tiene pivote, asi que solo muestra la tabla.
    """
    texto = f"ITERACION {item.numero}\n{item.tabla.to_string()}\n"
    if item.entrante:
        texto += (
            f"{item.explicacion}\n"
            f"Razones: {formatear_razones(item.razones)}\n"
            f"Columna pivote: {item.entrante} | Fila pivote: {item.saliente} | "
            f"Elemento pivote: {formatear_numero(item.elemento_pivote)}\n\n"
        )
    return texto
