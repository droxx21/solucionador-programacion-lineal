import math

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