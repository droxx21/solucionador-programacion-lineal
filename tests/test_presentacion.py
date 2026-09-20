"""Pruebas de la presentación de los métodos gráfico y Simplex.

Verifican que la información del proceso (evaluación de vértices, modelo
con holguras y detalle de pivote) se expone correctamente, sin alterar
los resultados matemáticos.
"""

from core.validacion import construir_problema, construir_restriccion
from grafico.adaptador import problema_a_modelo_grafico
from grafico.modelo import resolver_modelo
from grafico.presentacion import filas_evaluacion
from simplex.adaptador import problema_a_solucionador_simplex
from simplex.simplex import SolucionadorSimplex
from simplex.utilidades import expresion, formatear_iteracion, formatear_razones

# Problema del enunciado: Max 15x1 + 10x2 con coeficientes 0.333333, 0.5 y 0.166667.
EJEMPLO_SIMPLEX = ([15, 10], [[0.333333, 0.5], [0.333333, 0.166667]], [100, 80])

MODELO_ESPERADO = (
    "Max Z = 15x1 + 10x2\n"
    "0.333333x1 + 0.5x2 + s1 = 100\n"
    "0.333333x1 + 0.166667x2 + s2 = 80\n"
    "x1, x2, s1, s2 >= 0"
)


# ---------- Simplex: modelo con variables de holgura ----------

def probar_modelo_estandar_ejemplo():
    return SolucionadorSimplex(*EJEMPLO_SIMPLEX).modelo_estandar_texto() == MODELO_ESPERADO


def probar_modelo_estandar_no_cambia_tras_resolver():
    solucionador = SolucionadorSimplex(*EJEMPLO_SIMPLEX)
    antes = solucionador.modelo_estandar_texto()
    solucionador.resolver()
    return solucionador.modelo_estandar_texto() == antes == MODELO_ESPERADO


def probar_modelo_estandar_sigue_las_columnas_reales():
    # 3 variables y 2 restricciones -> holguras s1 y s2, tomadas de la tabla.
    solucionador = SolucionadorSimplex([3, -2, 1], [[1, 1, 1], [2, 0, -1]], [10, 4])
    lineas = solucionador.modelo_estandar_texto().split("\n")
    return lineas == [
        "Max Z = 3x1 - 2x2 + x3",
        "x1 + x2 + x3 + s1 = 10",
        "2x1 - x3 + s2 = 4",
        "x1, x2, x3, s1, s2 >= 0",
    ]


def probar_modelo_estandar_desde_problema_comun():
    # Camino de la Entrada Común: Problema -> adaptador -> solucionador.
    r1 = construir_restriccion(["2", "1"], "<=", "40", 2, etiqueta="R1")
    r2 = construir_restriccion(["1", "2"], "<=", "50", 2, etiqueta="R2")
    problema = construir_problema("Maximizar", ["x1", "x2"], ["40", "30"], [r1, r2])
    texto = problema_a_solucionador_simplex(problema).modelo_estandar_texto()
    return texto == "Max Z = 40x1 + 30x2\n2x1 + x2 + s1 = 40\nx1 + 2x2 + s2 = 50\nx1, x2, s1, s2 >= 0"


def probar_expresion_signos_y_coeficientes_unitarios():
    return (
        expresion(["x1", "x2", "x3"], [-1, 2.5, -1]) == "-x1 + 2.5x2 - x3"
        and expresion(["x1", "x2"], [0, 0]) == "0"
        and expresion(["x1", "x2"], [0, 4]) == "4x2"
    )


# ---------- Simplex: detalle de cada iteración ----------

def probar_detalle_iteracion_ejemplo():
    iteraciones = SolucionadorSimplex(*EJEMPLO_SIMPLEX).resolver()
    lineas = formatear_iteracion(iteraciones[0]).split("\n")
    return (
        lineas[0] == "ITERACION 0"
        and lineas[-5].startswith("Entra x1; sale s2. Se divide la fila pivote entre 0.333333")
        and lineas[-4] == "Razones: ['300', '240']"
        and lineas[-3] == "Columna pivote: x1 | Fila pivote: s2 | Elemento pivote: 0.333333"
    )


def probar_iteracion_optima_sin_detalle_de_pivote():
    iteraciones = SolucionadorSimplex(*EJEMPLO_SIMPLEX).resolver()
    texto = formatear_iteracion(iteraciones[-1])
    return texto.startswith(f"ITERACION {iteraciones[-1].numero}") and "Razones" not in texto and "pivote" not in texto


def probar_razones_marca_filas_sin_razon():
    # Columna de x1 = [1, -1]: la segunda fila no participa en la prueba del cociente.
    iteraciones = SolucionadorSimplex([1, 0], [[1, 1], [-1, 1]], [5, 3]).resolver()
    return formatear_razones(iteraciones[0].razones) == ["5", "-"]


def probar_detalle_usa_datos_ya_calculados():
    # El texto debe coincidir con lo que el solucionador guardó en la Iteracion.
    solucionador = SolucionadorSimplex(*EJEMPLO_SIMPLEX)
    for item in solucionador.resolver():
        if not item.entrante:
            continue
        texto = formatear_iteracion(item)
        if f"Columna pivote: {item.entrante} | Fila pivote: {item.saliente}" not in texto:
            return False
        if f"Razones: {formatear_razones(item.razones)}" not in texto:
            return False
    return True


# ---------- Método gráfico: evaluación de vértices ----------

def _resolver_grafico_clasico():
    r1 = construir_restriccion(["2", "1"], "<=", "40", 2, etiqueta="R1")
    r2 = construir_restriccion(["1", "2"], "<=", "50", 2, etiqueta="R2")
    problema = construir_problema("Maximizar", ["x1", "x2"], ["40", "30"], [r1, r2])
    objetivo, restricciones = problema_a_modelo_grafico(problema)
    return resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)


def probar_filas_evaluacion_coordenadas_y_z():
    resultado = _resolver_grafico_clasico()
    filas = filas_evaluacion(resultado["vertices"], resultado["evaluaciones"])
    esperado = {("0", "0", "0"), ("20", "0", "800"), ("10", "20", "1000"), ("0", "25", "750")}
    return len(filas) == 4 and {(x, y, z) for _, x, y, z in filas} == esperado


def probar_filas_evaluacion_incluye_todos_los_vertices():
    resultado = _resolver_grafico_clasico()
    filas = filas_evaluacion(resultado["vertices"], resultado["evaluaciones"])
    return [fila[0] for fila in filas] == [f"V{i}" for i in range(1, len(resultado["vertices"]) + 1)]


def probar_filas_evaluacion_coherentes_con_el_optimo():
    resultado = _resolver_grafico_clasico()
    filas = filas_evaluacion(resultado["vertices"], resultado["evaluaciones"])
    optimo = resultado["optimo"]
    fila_optima = next(fila for fila in filas if fila[0] == optimo["vertice"])
    return float(fila_optima[3]) == optimo["z"] and float(fila_optima[3]) == max(float(f[3]) for f in filas)


def probar_filas_evaluacion_formato_unificado():
    # Vértice (20/3, 20/3) con Z = 40: coordenadas sin redondeo a 4 decimales, en formato de core.numeros.
    objetivo = {"tipo": "Maximizar", "a": 3.0, "b": 3.0}
    restricciones = [
        {"a": 2.0, "b": 1.0, "relation": "<=", "c": 20.0},
        {"a": 1.0, "b": 2.0, "relation": "<=", "c": 20.0},
    ]
    resultado = resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
    filas = filas_evaluacion(resultado["vertices"], resultado["evaluaciones"])
    return any(fila[1:] == ("6.66667", "6.66667", "40") for fila in filas)


if __name__ == "__main__":
    pruebas = [
        ("Prueba 1: modelo con holguras del enunciado", probar_modelo_estandar_ejemplo),
        ("Prueba 2: modelo no cambia tras resolver", probar_modelo_estandar_no_cambia_tras_resolver),
        ("Prueba 3: modelo sigue las columnas reales", probar_modelo_estandar_sigue_las_columnas_reales),
        ("Prueba 4: modelo desde Problema común", probar_modelo_estandar_desde_problema_comun),
        ("Prueba 5: expresión con signos y coeficientes unitarios", probar_expresion_signos_y_coeficientes_unitarios),
        ("Prueba 6: detalle de iteración del enunciado", probar_detalle_iteracion_ejemplo),
        ("Prueba 7: iteración óptima sin detalle de pivote", probar_iteracion_optima_sin_detalle_de_pivote),
        ("Prueba 8: razones marca filas sin razón", probar_razones_marca_filas_sin_razon),
        ("Prueba 9: detalle usa datos ya calculados", probar_detalle_usa_datos_ya_calculados),
        ("Prueba 10: evaluación de vértices (coordenadas y Z)", probar_filas_evaluacion_coordenadas_y_z),
        ("Prueba 11: evaluación incluye todos los vértices", probar_filas_evaluacion_incluye_todos_los_vertices),
        ("Prueba 12: evaluación coherente con el óptimo", probar_filas_evaluacion_coherentes_con_el_optimo),
        ("Prueba 13: evaluación con formato unificado", probar_filas_evaluacion_formato_unificado),
    ]

    for nombre, prueba in pruebas:
        resultado = prueba()
        print(f"{nombre}: {'OK' if resultado else 'FALLA'}")
        if not resultado:
            raise SystemExit(1)

    print("Todas las pruebas pasaron.")
