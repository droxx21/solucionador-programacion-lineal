from core.modelo import TipoObjetivo
from core.numeros import analizar_numero
from core.validacion import ErrorModelo, construir_problema, construir_restriccion
from grafico.adaptador import ErrorAdaptadorGrafico, problema_a_modelo_grafico
from simplex.adaptador import ErrorAdaptadorSimplex, problema_a_solucionador_simplex


def probar_analizar_numero_decimal_y_coma():
    return abs(analizar_numero("3.5", "x") - 3.5) < 1e-9 and abs(analizar_numero("3,5", "x") - 3.5) < 1e-9


def probar_analizar_numero_fraccion():
    return abs(analizar_numero("1/2", "x") - 0.5) < 1e-9


def probar_analizar_numero_invalido():
    try:
        analizar_numero("abc", "x")
        return False
    except ValueError:
        return True


def probar_construir_problema_valido():
    r1 = construir_restriccion(["2", "1"], "<=", "40", 2, etiqueta="R1")
    r2 = construir_restriccion(["1", "2"], "<=", "50", 2, etiqueta="R2")
    problema = construir_problema("Maximizar", ["x1", "x2"], ["40", "30"], [r1, r2])
    return (
        problema.tipo_objetivo == TipoObjetivo.MAXIMIZAR
        and problema.num_variables == 2
        and len(problema.restricciones) == 2
        and len(problema.condiciones_variables) == 2
    )


def probar_construir_problema_sin_restricciones():
    try:
        construir_problema("Maximizar", ["x1", "x2"], ["40", "30"], [])
        return False
    except ErrorModelo:
        return True


def probar_construir_problema_dimension_incorrecta():
    try:
        construir_problema("Maximizar", ["x1", "x2"], ["40"], [])
        return False
    except ErrorModelo:
        return True


def probar_adaptador_grafico():
    r1 = construir_restriccion(["2", "1"], "<=", "40", 2, etiqueta="R1")
    r2 = construir_restriccion(["1", "2"], "<=", "50", 2, etiqueta="R2")
    problema = construir_problema("Maximizar", ["x1", "x2"], ["40", "30"], [r1, r2])
    objetivo, restricciones = problema_a_modelo_grafico(problema)
    return objetivo["a"] == 40.0 and objetivo["b"] == 30.0 and len(restricciones) == 2


def probar_adaptador_grafico_rechaza_mas_de_dos_variables():
    r1 = construir_restriccion(["1", "1", "1"], "<=", "10", 3, etiqueta="R1")
    problema = construir_problema("Maximizar", ["x1", "x2", "x3"], ["1", "1", "1"], [r1])
    try:
        problema_a_modelo_grafico(problema)
        return False
    except ErrorAdaptadorGrafico:
        return True


def probar_adaptador_simplex_resuelve_maximizacion():
    r1 = construir_restriccion(["2", "1"], "<=", "40", 2, etiqueta="R1")
    r2 = construir_restriccion(["1", "2"], "<=", "50", 2, etiqueta="R2")
    problema = construir_problema("Maximizar", ["x1", "x2"], ["40", "30"], [r1, r2])
    solucionador = problema_a_solucionador_simplex(problema)
    solucionador.resolver()
    return abs(solucionador.valor_optimo - 1000.0) <= 1e-6


def probar_adaptador_simplex_rechaza_minimizacion():
    r1 = construir_restriccion(["1", "1"], "<=", "10", 2, etiqueta="R1")
    problema = construir_problema("Minimizar", ["x1", "x2"], ["1", "1"], [r1])
    try:
        problema_a_solucionador_simplex(problema)
        return False
    except ErrorAdaptadorSimplex:
        return True


def probar_adaptador_simplex_rechaza_restriccion_mayor_igual():
    r1 = construir_restriccion(["1", "1"], ">=", "10", 2, etiqueta="R1")
    problema = construir_problema("Maximizar", ["x1", "x2"], ["1", "1"], [r1])
    try:
        problema_a_solucionador_simplex(problema)
        return False
    except ErrorAdaptadorSimplex:
        return True


if __name__ == "__main__":
    pruebas = [
        ("Prueba 1: analizar_numero decimal y coma", probar_analizar_numero_decimal_y_coma),
        ("Prueba 2: analizar_numero fracción", probar_analizar_numero_fraccion),
        ("Prueba 3: analizar_numero inválido", probar_analizar_numero_invalido),
        ("Prueba 4: construir_problema válido", probar_construir_problema_valido),
        ("Prueba 5: construir_problema sin restricciones", probar_construir_problema_sin_restricciones),
        ("Prueba 6: construir_problema dimensión incorrecta", probar_construir_problema_dimension_incorrecta),
        ("Prueba 7: adaptador gráfico", probar_adaptador_grafico),
        ("Prueba 8: adaptador gráfico rechaza >2 variables", probar_adaptador_grafico_rechaza_mas_de_dos_variables),
        ("Prueba 9: adaptador simplex resuelve maximización", probar_adaptador_simplex_resuelve_maximizacion),
        ("Prueba 10: adaptador simplex rechaza minimización", probar_adaptador_simplex_rechaza_minimizacion),
        ("Prueba 11: adaptador simplex rechaza restricción >=", probar_adaptador_simplex_rechaza_restriccion_mayor_igual),
    ]

    for nombre, prueba in pruebas:
        resultado = prueba()
        print(f"{nombre}: {'OK' if resultado else 'FALLA'}")
        if not resultado:
            raise SystemExit(1)

    print("Todas las pruebas pasaron.")
