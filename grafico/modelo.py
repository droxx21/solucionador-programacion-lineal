import math
import re
from typing import Dict, List, Optional, Tuple

import numpy as np


def parsear_numero(valor) -> float:
    if isinstance(valor, (int, float)):
        numero = float(valor)
        if math.isnan(numero):
            raise ValueError("El valor ingresado no es válido.")
        return numero

    texto = str(valor).strip()
    if texto == "":
        raise ValueError("Debe ingresar un valor numérico.")

    if "/" in texto:
        partes = texto.split("/")
        if len(partes) != 2:
            raise ValueError("La fracción ingresada no es válida.")
        numerador = parsear_numero(partes[0])
        denominador = parsear_numero(partes[1])
        if abs(denominador) < 1e-12:
            raise ValueError("No se puede dividir entre cero.")
        return numerador / denominador

    numero = float(texto)
    if math.isnan(numero):
        raise ValueError("El valor ingresado no es válido.")
    return numero


def normalizar_relacion(relacion: str) -> str:
    valor = str(relacion).strip()
    if valor in {"<=", ">=", "="}:
        return valor
    raise ValueError("La relación debe ser <=, >= o =.")


def construir_restriccion(a: float, b: float, relacion: str, c: float) -> Dict[str, float | str]:
    try:
        a_num = parsear_numero(a)
        b_num = parsear_numero(b)
        c_num = parsear_numero(c)
    except ValueError as exc:
        raise ValueError("Los coeficientes y el término independiente deben ser numéricos o fracciones válidas.") from exc

    if math.isnan(a_num) or math.isnan(b_num) or math.isnan(c_num):
        raise ValueError("Los valores ingresados no son válidos.")

    return {
        "a": a_num,
        "b": b_num,
        "relation": normalizar_relacion(relacion),
        "c": c_num,
    }


def calcular_interseccion(restriccion_1: Dict[str, float | str], restriccion_2: Dict[str, float | str], tol: float = 1e-9) -> Optional[Tuple[float, float]]:
    a1 = float(restriccion_1["a"])
    b1 = float(restriccion_1["b"])
    c1 = float(restriccion_1["c"])
    a2 = float(restriccion_2["a"])
    b2 = float(restriccion_2["b"])
    c2 = float(restriccion_2["c"])

    determinante = a1 * b2 - a2 * b1
    if abs(determinante) <= tol:
        return None

    x = (c1 * b2 - c2 * b1) / determinante
    y = (a1 * c2 - a2 * c1) / determinante
    if math.isnan(x) or math.isnan(y):
        return None

    return (float(x), float(y))


def verificar_punto(punto: Tuple[float, float], restricciones: List[Dict[str, float | str]], tol: float = 1e-6) -> bool:
    x, y = punto
    for restriccion in restricciones:
        a = float(restriccion["a"])
        b = float(restriccion["b"])
        c = float(restriccion["c"])
        lhs = a * x + b * y
        relacion = str(restriccion["relation"])

        if relacion == "<=" and lhs > c + tol:
            return False
        if relacion == ">=" and lhs < c - tol:
            return False
        if relacion == "=" and abs(lhs - c) > tol:
            return False

    return True


def obtener_puntos_candidatos(restricciones: List[Dict[str, float | str]], tol: float = 1e-9) -> List[Tuple[float, float]]:
    lineas = list(restricciones)
    lineas.extend([
        {"a": 1.0, "b": 0.0, "c": 0.0, "relation": "="},
        {"a": 0.0, "b": 1.0, "c": 0.0, "relation": "="},
    ])

    candidatos: List[Tuple[float, float]] = []
    for i in range(len(lineas)):
        for j in range(i + 1, len(lineas)):
            punto = calcular_interseccion(lineas[i], lineas[j], tol=tol)
            if punto is None:
                continue
            x, y = punto
            if not math.isfinite(x) or not math.isfinite(y):
                continue
            candidatos.append((float(x), float(y)))

    return candidatos


def normalizar_vertices(vertices: List[Tuple[float, float]], tol: float = 1e-6) -> List[Tuple[float, float]]:
    unicos: List[Tuple[float, float]] = []
    for punto in vertices:
        x, y = punto
        if not math.isfinite(x) or not math.isfinite(y):
            continue
        duplicado = False
        for actual in unicos:
            if abs(actual[0] - x) <= tol and abs(actual[1] - y) <= tol:
                duplicado = True
                break
        if not duplicado:
            unicos.append((float(x), float(y)))
    return unicos


def obtener_vertices(restricciones: List[Dict[str, float | str]], tol: float = 1e-6) -> List[Tuple[float, float]]:
    candidatos = obtener_puntos_candidatos(restricciones)
    factibles = [punto for punto in candidatos if verificar_punto(punto, restricciones, tol=tol)]
    vertices = normalizar_vertices(factibles, tol)
    if not vertices:
        return []

    centro_x = sum(x for x, _ in vertices) / len(vertices)
    centro_y = sum(y for _, y in vertices) / len(vertices)
    ordenados = sorted(vertices, key=lambda punto: math.atan2(punto[1] - centro_y, punto[0] - centro_x))
    return ordenados


def evaluar_funcion(vertices: List[Tuple[float, float]], objetivo: Dict[str, float | str]) -> List[Dict[str, float]]:
    resultados: List[Dict[str, float]] = []
    coef_x = parsear_numero(objetivo["a"])
    coef_y = parsear_numero(objetivo["b"])
    for idx, (x, y) in enumerate(vertices, start=1):
        z = coef_x * x + coef_y * y
        resultados.append({
            "vertice": f"V{idx}",
            "x": round(float(x), 4),
            "y": round(float(y), 4),
            "z": round(float(z), 4),
        })
    return resultados


def encontrar_optimo(vertices: List[Tuple[float, float]], objetivo: Dict[str, float | str], tipo: str) -> Dict[str, float | str]:
    evaluaciones = evaluar_funcion(vertices, objetivo)
    if not evaluaciones:
        raise ValueError("No existen vértices para evaluar.")

    criterio = max if str(tipo).lower() == "maximizar" else min
    mejor = criterio(evaluaciones, key=lambda item: item["z"])
    x, y = vertices[[item["vertice"] for item in evaluaciones].index(mejor["vertice"]) ]

    return {
        "vertice": mejor["vertice"],
        "x": float(x),
        "y": float(y),
        "z": float(mejor["z"]),
        "tipo": tipo,
    }


def construir_modelo_texto(objetivo: Dict[str, float | str], restricciones: List[Dict[str, float | str]], incluir_no_negatividad: bool = True) -> str:
    tipo = str(objetivo["tipo"]).capitalize()
    a = parsear_numero(objetivo["a"])
    b = parsear_numero(objetivo["b"])
    lineas = [f"{tipo}:\nZ = {a}x + {b}y\n\nSujeto a:\n"]

    for idx, restriccion in enumerate(restricciones, start=1):
        rel = str(restriccion["relation"])
        a_i = float(restriccion["a"])
        b_i = float(restriccion["b"])
        c_i = float(restriccion["c"])
        lineas.append(f"{idx}. {a_i}x + {b_i}y {rel} {c_i}\n")

    if incluir_no_negatividad:
        lineas.append("x >= 0\n")
        lineas.append("y >= 0\n")

    return "".join(lineas)


def resolver_modelo(objetivo: Dict[str, float | str], restricciones: List[Dict[str, float | str]], incluir_no_negatividad: bool = True) -> Dict[str, object]:
    if not restricciones:
        raise ValueError("Debe ingresar al menos una restricción.")

    modelo_restricciones = list(restricciones)
    if incluir_no_negatividad:
        modelo_restricciones.extend([
            {"a": 1.0, "b": 0.0, "c": 0.0, "relation": ">="},
            {"a": 0.0, "b": 1.0, "c": 0.0, "relation": ">="},
        ])

    vertices = obtener_vertices(modelo_restricciones)
    if not vertices:
        raise ValueError("No existe una región factible con las restricciones ingresadas.")

    evaluaciones = evaluar_funcion(vertices, objetivo)
    optimo = encontrar_optimo(vertices, objetivo, str(objetivo["tipo"]))

    return {
        "vertices": vertices,
        "evaluaciones": evaluaciones,
        "optimo": optimo,
        "modelo_texto": construir_modelo_texto(objetivo, restricciones, incluir_no_negatividad),
    }


def probar_maximizacion() -> bool:
    objetivo = {"tipo": "Maximizar", "a": 40.0, "b": 30.0}
    restricciones = [
        construir_restriccion(2, 1, "<=", 40),
        construir_restriccion(1, 2, "<=", 50),
    ]
    resultado = resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
    optimo = resultado["optimo"]
    return abs(optimo["x"] - 10.0) <= 1e-6 and abs(optimo["y"] - 20.0) <= 1e-6 and abs(optimo["z"] - 1000.0) <= 1e-6


def probar_minimizacion() -> bool:
    objetivo = {"tipo": "Minimizar", "a": 3.0, "b": 5.0}
    restricciones = [
        construir_restriccion(1, 1, ">=", 10),
        construir_restriccion(2, 1, ">=", 14),
        construir_restriccion(0, 1, ">=", 4),
    ]
    resultado = resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
    optimo = resultado["optimo"]
    return abs(optimo["x"] - 6.0) <= 1e-6 and abs(optimo["y"] - 4.0) <= 1e-6 and abs(optimo["z"] - 38.0) <= 1e-6


def probar_tres_restricciones() -> bool:
    objetivo = {"tipo": "Maximizar", "a": 20.0, "b": 15.0}
    restricciones = [
        construir_restriccion(2, 1, "<=", 80),
        construir_restriccion(1, 2, "<=", 60),
        construir_restriccion(1, 0, "<=", 30),
    ]
    resultado = resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
    return len(resultado["vertices"]) >= 4 and resultado["optimo"]["z"] > 0


def probar_region_no_factible() -> bool:
    objetivo = {"tipo": "Maximizar", "a": 3.0, "b": 2.0}
    restricciones = [
        construir_restriccion(1, 1, "<=", 5),
        construir_restriccion(1, 1, ">=", 8),
    ]
    try:
        resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
        return False
    except ValueError:
        return True


def probar_fracciones() -> bool:
    objetivo = {"tipo": "Maximizar", "a": "1/2", "b": "1/2"}
    restricciones = [
        construir_restriccion("1/2", "0", "<=", "2"),
        construir_restriccion("0", "1/2", "<=", "2"),
    ]
    resultado = resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
    optimo = resultado["optimo"]
    return abs(optimo["x"] - 4.0) <= 1e-6 and abs(optimo["y"] - 4.0) <= 1e-6 and abs(optimo["z"] - 4.0) <= 1e-6
