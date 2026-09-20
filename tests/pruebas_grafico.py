from grafico.modelo import (
    probar_fracciones,
    probar_maximizacion,
    probar_minimizacion,
    probar_region_no_factible,
    probar_tres_restricciones,
)


if __name__ == "__main__":
    pruebas = [
        ("Prueba 1: Maximización", probar_maximizacion),
        ("Prueba 2: Minimización", probar_minimizacion),
        ("Prueba 3: Tres restricciones", probar_tres_restricciones),
        ("Prueba 4: Región no factible", probar_region_no_factible),
        ("Prueba 5: Fracciones", probar_fracciones),
    ]

    for nombre, prueba in pruebas:
        resultado = prueba()
        print(f"{nombre}: {'OK' if resultado else 'FALLA'}")
        if not resultado:
            raise SystemExit(1)

    print("Todas las pruebas pasaron.")
