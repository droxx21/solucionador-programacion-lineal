# Solucionador de Programación Lineal

Aplicación para resolver problemas de programación lineal utilizando distintos métodos de solución:

- Método gráfico
- Método Simplex
- Método Gran M

El proyecto está organizado para separar claramente:

- el modelo matemático del problema,
- la validación de entrada,
- la resolución por método,
- y la interfaz de usuario.

## Estructura del proyecto

```text
solucionador-programacion-lineal/
├── core/
│   ├── __init__.py
│   ├── modelo.py
│   ├── numeros.py
│   └── validacion.py
├── grafico/
│   ├── __init__.py
│   ├── adaptador.py
│   ├── grafico.py
│   ├── interfaz.py
│   ├── main.py
│   ├── modelo.py
│   └── presentacion.py
├── simplex/
│   ├── __init__.py
│   ├── adaptador.py
│   ├── interfaz.py
│   ├── main.py
│   ├── simplex.py
│   └── utilidades.py
├── gran_m/
│   ├── __init__.py
│   ├── adaptador.py
│   └── gran_m.py
├── entrada/
│   ├── __init__.py
│   └── interfaz.py
├── tests/
│   ├── __init__.py
│   ├── test_modelo.py
│   ├── test_presentacion.py
│   └── pruebas_grafico.py
├── main.py
├── README.md
└── requirements.txt
```

## Descripción de módulos

### core/

Contiene la representación común del problema original, sin mezclar conceptos de métodos específicos.

- `modelo.py`: define el `Problema`, restricciones y condiciones de variables.
- `validacion.py`: valida entradas del usuario y construye el problema matemático.
- `numeros.py`: parseo, formato y manejo uniforme de números.

### grafico/

Implementa la resolución del método gráfico.

- `adaptador.py`: convierte el problema común al formato requerido por el método gráfico.
- `modelo.py`: lógica del modelo gráfico.
- `presentacion.py`: formato de visualización de resultados.
- `grafico.py`: rendering visual de la región factible.
- `interfaz.py`: formulario del método gráfico.

### simplex/

Implementa la resolución del método Simplex clásico.

- `simplex.py`: motor del algoritmo tabular.
- `adaptador.py`: convierte el problema común a la representación del simplex.
- `utilidades.py`: funciones auxiliares para expresiones y formatos de iteración.
- `interfaz.py`: formulario del método simplex.

### gran_m/

Implementa la técnica de Gran M para problemas que incluyen restricciones `>=` o `=` y minimización.

- `gran_m.py`: transforma el problema original a un formato factible para Simplex con variables artificiales.
- `adaptador.py`: adapta el problema común al solver Gran M.

### entrada/

Módulo de entrada común para construir un problema una sola vez y luego elegir el método de resolución.

### tests/

Pruebas del proyecto para validar:

- la construcción del modelo,
- los adaptadores,
- la salida visual y textual,
- y el comportamiento del solver.

## Cómo ejecutar

Desde la raíz del proyecto:

```bash
python main.py
```

Esto abre el menú principal, desde donde se puede elegir:

- Entrada Común
- Método Gráfico
- Método Simplex

## Uso del método Gran M

El método Gran M puede resolver problemas con:

- maximización,
- minimización,
- restricciones `<=`, `>=` y `=`,
- variables con condición de no negatividad.

La transformación se hace sobre el problema original, sin mutar el modelo compartido.

## Requisitos

El proyecto usa el stack estándar de Python con:

- `numpy`
- `pandas`
- `tkinter`

Si el entorno no tiene dependencias instaladas, puedes instalarlas con:

```bash
pip install numpy pandas
```

## Objetivo del proyecto

El objetivo principal es aprender e implementar varios métodos de resolución de programación lineal manteniendo una arquitectura ordenada, reutilizable y extensible.

## Notas

- El modelo común (`core.modelo.Problema`) permanece independiente del método de solución.
- El método Simplex original sigue funcionando para los casos que soporta.
- Gran M se integra como una extensión del mismo enfoque, reutilizando el motor tabular existente en lugar de duplicar lógica.
