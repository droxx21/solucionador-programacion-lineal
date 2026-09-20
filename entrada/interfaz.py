"""Formulario común de entrada para problemas de Programación Lineal.

Este módulo construye un `core.modelo.Problema` a partir de los datos
ingresados por el usuario, de forma totalmente independiente del
método de solución: no arma tablas Simplex ni realiza cálculos del
método gráfico. Según el método elegido, delega la resolución al
adaptador correspondiente (`grafico.adaptador` o `simplex.adaptador`).
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

from core.modelo import Problema
from core.numeros import formatear_numero
from core.validacion import ErrorModelo, construir_problema, construir_restriccion
from grafico.adaptador import (
    LIMITE_VARIABLES_GRAFICO,
    ErrorAdaptadorGrafico,
    problema_a_modelo_grafico,
)
from grafico.grafico import crear_grafica
from grafico.modelo import resolver_modelo
from grafico.presentacion import filas_evaluacion
from gran_m.adaptador import ErrorAdaptadorGranM, problema_a_solucionador_gran_m
from gran_m.gran_m import ErrorGranM
from simplex.adaptador import ErrorAdaptadorSimplex, problema_a_solucionador_simplex
from simplex.simplex import ErrorSimplex
from simplex.utilidades import formatear_iteracion


class AplicacionEntradaComun(ttk.Frame):
    """Formulario común: objetivo, variables, restricciones y método."""

    def __init__(self, master):
        super().__init__(master, padding=10)
        self.pack(fill="both", expand=True)

        self.num_variables = tk.IntVar(value=2)
        self.entradas_coeficientes_objetivo: List[ttk.Entry] = []
        self.entradas_coeficientes_restriccion: List[ttk.Entry] = []
        self.restricciones_agregadas = []

        self._construir_panel_objetivo()
        self._construir_panel_restricciones()
        self._construir_panel_condiciones()
        self._construir_panel_metodo()

        self._generar_campos_variables()

    # ---------- Construcción de paneles ----------

    def _construir_panel_objetivo(self):
        panel = ttk.LabelFrame(self, text="1. Función objetivo y número de variables", padding=8)
        panel.pack(fill="x", pady=(0, 8))

        fila_superior = ttk.Frame(panel)
        fila_superior.pack(fill="x")

        ttk.Label(fila_superior, text="Tipo:").pack(side="left", padx=(0, 6))
        self.tipo_objetivo = ttk.Combobox(
            fila_superior, values=["Maximizar", "Minimizar"], state="readonly", width=14
        )
        self.tipo_objetivo.set("Maximizar")
        self.tipo_objetivo.pack(side="left", padx=(0, 20))

        ttk.Label(fila_superior, text="Número de variables:").pack(side="left", padx=(0, 6))
        ttk.Spinbox(
            fila_superior, from_=1, to=10, textvariable=self.num_variables, width=5,
            command=self._generar_campos_variables,
        ).pack(side="left")

        self.panel_coeficientes = ttk.Frame(panel)
        self.panel_coeficientes.pack(fill="x", pady=(10, 0))

    def _construir_panel_restricciones(self):
        panel = ttk.LabelFrame(self, text="2. Restricciones", padding=8)
        panel.pack(fill="x", pady=(0, 8))

        fila_entrada = ttk.Frame(panel)
        fila_entrada.pack(fill="x")

        self.panel_coeficientes_restriccion = ttk.Frame(fila_entrada)
        self.panel_coeficientes_restriccion.pack(side="left")

        ttk.Label(fila_entrada, text="  Relación:").pack(side="left", padx=(6, 4))
        self.relacion_restriccion = ttk.Combobox(
            fila_entrada, values=["<=", ">=", "="], state="readonly", width=4
        )
        self.relacion_restriccion.set("<=")
        self.relacion_restriccion.pack(side="left")

        ttk.Label(fila_entrada, text="  c:").pack(side="left", padx=(6, 4))
        self.termino_restriccion = ttk.Entry(fila_entrada, width=8)
        self.termino_restriccion.pack(side="left")

        ttk.Button(fila_entrada, text="Agregar", command=self._agregar_restriccion).pack(
            side="left", padx=(10, 0)
        )

        self.tree_restricciones = ttk.Treeview(
            panel, columns=("num", "restriccion"), show="headings", height=6
        )
        self.tree_restricciones.heading("num", text="#")
        self.tree_restricciones.heading("restriccion", text="Restricción")
        self.tree_restricciones.column("num", width=40, anchor="center")
        self.tree_restricciones.column("restriccion", width=420, anchor="w")
        self.tree_restricciones.pack(fill="x", pady=(8, 4))

        botones = ttk.Frame(panel)
        botones.pack(fill="x")
        ttk.Button(botones, text="Eliminar seleccionada", command=self._eliminar_restriccion).pack(
            side="left"
        )
        ttk.Button(botones, text="Limpiar restricciones", command=self._limpiar_restricciones).pack(
            side="left", padx=(6, 0)
        )

    def _construir_panel_condiciones(self):
        panel = ttk.LabelFrame(self, text="3. Condiciones de las variables", padding=8)
        panel.pack(fill="x", pady=(0, 8))
        ttk.Label(
            panel,
            text="Se asume la condición estándar x_i >= 0 para todas las variables.",
        ).pack(anchor="w")

    def _construir_panel_metodo(self):
        panel = ttk.LabelFrame(self, text="4. Método de solución", padding=8)
        panel.pack(fill="x", pady=(0, 8))

        self.metodo = tk.StringVar(value="grafico")

        self.radio_grafico = ttk.Radiobutton(
            panel, text="Método Gráfico", value="grafico", variable=self.metodo
        )
        self.radio_grafico.pack(anchor="w")
        self.etiqueta_aviso_grafico = ttk.Label(
            panel, text="", foreground="#b45309", wraplength=480, justify="left"
        )
        self.etiqueta_aviso_grafico.pack(anchor="w", padx=(20, 0))

        ttk.Radiobutton(panel, text="Método Simplex", value="simplex", variable=self.metodo).pack(
            anchor="w", pady=(6, 0)
        )
        ttk.Radiobutton(panel, text="Método Gran M", value="gran_m", variable=self.metodo).pack(
            anchor="w", pady=(6, 0)
        )

        ttk.Button(panel, text="Resolver", command=self._resolver).pack(anchor="e", pady=(10, 0))

    # ---------- Regeneración dinámica según el número de variables ----------

    def _generar_campos_variables(self):
        try:
            n = max(1, int(self.num_variables.get()))
        except (tk.TclError, ValueError):
            n = 1

        for widget in self.panel_coeficientes.winfo_children():
            widget.destroy()
        self.entradas_coeficientes_objetivo = []

        ttk.Label(self.panel_coeficientes, text="Z =").grid(row=0, column=0, padx=(0, 6))
        for i in range(n):
            entrada = ttk.Entry(self.panel_coeficientes, width=8)
            entrada.grid(row=0, column=2 * i + 1, padx=(0, 2))
            texto = f"x{i + 1}" + (" +" if i < n - 1 else "")
            ttk.Label(self.panel_coeficientes, text=texto).grid(row=0, column=2 * i + 2, padx=(0, 6))
            self.entradas_coeficientes_objetivo.append(entrada)

        for widget in self.panel_coeficientes_restriccion.winfo_children():
            widget.destroy()
        self.entradas_coeficientes_restriccion = []
        for i in range(n):
            entrada = ttk.Entry(self.panel_coeficientes_restriccion, width=6)
            entrada.grid(row=0, column=2 * i, padx=(0, 2))
            ttk.Label(self.panel_coeficientes_restriccion, text=f"x{i + 1}").grid(
                row=0, column=2 * i + 1, padx=(0, 6)
            )
            self.entradas_coeficientes_restriccion.append(entrada)

        # Cambiar la dimensión invalida las restricciones ya agregadas.
        self.restricciones_agregadas = []
        self._actualizar_tabla_restricciones()
        self._actualizar_estado_metodo_grafico()

    def _actualizar_estado_metodo_grafico(self):
        n = len(self.entradas_coeficientes_objetivo)
        if n == LIMITE_VARIABLES_GRAFICO:
            self.radio_grafico.state(["!disabled"])
            self.etiqueta_aviso_grafico.config(text="")
        else:
            self.radio_grafico.state(["disabled"])
            self.etiqueta_aviso_grafico.config(
                text=(
                    "El método gráfico solo está disponible para problemas de "
                    f"{LIMITE_VARIABLES_GRAFICO} variables (actualmente hay {n}). "
                    "Seleccione el método Simplex."
                )
            )
            if self.metodo.get() == "grafico":
                self.metodo.set("simplex")

    # ---------- Restricciones ----------

    def _formatear_restriccion(self, restriccion, nombres_variables) -> str:
        terminos = []
        for coeficiente, nombre in zip(restriccion.coeficientes, nombres_variables):
            if abs(coeficiente) < 1e-9:
                continue
            signo = "+" if coeficiente > 0 and terminos else ""
            terminos.append(f"{signo}{formatear_numero(coeficiente)}{nombre}")
        lado_izquierdo = " ".join(terminos) or "0"
        return f"{lado_izquierdo} {restriccion.tipo.value} {formatear_numero(restriccion.termino_independiente)}"

    def _agregar_restriccion(self):
        coeficientes_texto = [entrada.get() for entrada in self.entradas_coeficientes_restriccion]
        relacion = self.relacion_restriccion.get()
        termino_texto = self.termino_restriccion.get()
        num_variables = len(self.entradas_coeficientes_objetivo)

        try:
            restriccion = construir_restriccion(
                coeficientes_texto,
                relacion,
                termino_texto,
                num_variables,
                etiqueta=f"R{len(self.restricciones_agregadas) + 1}",
            )
        except ErrorModelo as exc:
            messagebox.showerror("Restricción inválida", str(exc))
            return

        self.restricciones_agregadas.append(restriccion)
        self._actualizar_tabla_restricciones()

        for entrada in self.entradas_coeficientes_restriccion:
            entrada.delete(0, "end")
        self.termino_restriccion.delete(0, "end")
        self.relacion_restriccion.set("<=")

    def _actualizar_tabla_restricciones(self):
        for fila in self.tree_restricciones.get_children():
            self.tree_restricciones.delete(fila)
        nombres = [f"x{i + 1}" for i in range(len(self.entradas_coeficientes_objetivo))]
        for idx, restriccion in enumerate(self.restricciones_agregadas, start=1):
            texto = self._formatear_restriccion(restriccion, nombres)
            self.tree_restricciones.insert("", "end", values=(idx, texto))

    def _eliminar_restriccion(self):
        seleccion = self.tree_restricciones.selection()
        if not seleccion:
            messagebox.showinfo("Selección", "Seleccione una restricción para eliminar.")
            return
        indice = int(self.tree_restricciones.item(seleccion[0], "values")[0]) - 1
        del self.restricciones_agregadas[indice]
        self._actualizar_tabla_restricciones()

    def _limpiar_restricciones(self):
        self.restricciones_agregadas = []
        self._actualizar_tabla_restricciones()

    # ---------- Resolución ----------

    def _resolver(self):
        n = len(self.entradas_coeficientes_objetivo)
        nombres_variables = [f"x{i + 1}" for i in range(n)]
        coeficientes_objetivo_texto = [entrada.get() for entrada in self.entradas_coeficientes_objetivo]

        try:
            problema = construir_problema(
                self.tipo_objetivo.get(),
                nombres_variables,
                coeficientes_objetivo_texto,
                self.restricciones_agregadas,
            )
        except ErrorModelo as exc:
            messagebox.showerror("Datos inválidos", str(exc))
            return

        if self.metodo.get() == "grafico":
            self._resolver_con_grafico(problema)
        elif self.metodo.get() == "gran_m":
            self._resolver_con_gran_m(problema)
        else:
            self._resolver_con_simplex(problema)

    def _resolver_con_grafico(self, problema: Problema):
        try:
            objetivo, restricciones = problema_a_modelo_grafico(problema)
            resultado = resolver_modelo(objetivo, restricciones, incluir_no_negatividad=True)
        except (ErrorAdaptadorGrafico, ValueError) as exc:
            messagebox.showerror("No se puede resolver", str(exc))
            return

        ventana = tk.Toplevel(self)
        ventana.title("Resultado - Método Gráfico")
        ventana.geometry("900x900")

        # El resumen y la tabla se empaquetan primero, abajo, para que la gráfica
        # (que se expande) nunca los desplace fuera de la ventana.
        panel_texto = ttk.Frame(ventana)
        panel_texto.pack(side="bottom", fill="x", padx=8, pady=(0, 8))

        panel_evaluacion = ttk.LabelFrame(
            ventana, text="Evaluación de la función objetivo en los vértices", padding=6
        )
        panel_evaluacion.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        self._crear_tabla_evaluacion(panel_evaluacion, problema.nombres_variables, resultado)

        panel_grafica = ttk.Frame(ventana)
        panel_grafica.pack(fill="both", expand=True, padx=8, pady=8)
        crear_grafica(panel_grafica, restricciones, resultado["vertices"], resultado["optimo"])

        optimo = resultado["optimo"]
        texto = (
            f"Óptimo en {optimo['vertice']}: x1 = {formatear_numero(optimo['x'])}, "
            f"x2 = {formatear_numero(optimo['y'])}, Z = {formatear_numero(optimo['z'])}"
        )
        ttk.Label(panel_texto, text=texto, font=("TkDefaultFont", 11, "bold")).pack(anchor="w")

    def _crear_tabla_evaluacion(self, padre, nombres_variables, resultado):
        """Tabla con las coordenadas de cada vértice y el valor de Z en él."""
        filas = filas_evaluacion(resultado["vertices"], resultado["evaluaciones"])
        filas_visibles = 8

        tabla = ttk.Treeview(
            padre,
            columns=("vertice", "x", "y", "z"),
            show="headings",
            height=min(max(len(filas), 1), filas_visibles),
        )
        encabezados = ("Vértice", *nombres_variables, "Z")
        for columna, encabezado in zip(("vertice", "x", "y", "z"), encabezados):
            tabla.heading(columna, text=encabezado)
            tabla.column(columna, width=120, anchor="center")
        for fila in filas:
            tabla.insert("", "end", values=fila)

        tabla.pack(side="left", fill="x", expand=True)
        if len(filas) > filas_visibles:
            barra = ttk.Scrollbar(padre, orient="vertical", command=tabla.yview)
            tabla.configure(yscrollcommand=barra.set)
            barra.pack(side="right", fill="y")

    def _resolver_con_simplex(self, problema: Problema):
        try:
            solucionador = problema_a_solucionador_simplex(problema)
            iteraciones = solucionador.resolver()
        except (ErrorAdaptadorSimplex, ErrorSimplex) as exc:
            messagebox.showerror("No se puede resolver", str(exc))
            return

        ventana = tk.Toplevel(self)
        ventana.title("Resultado - Método Simplex")
        ventana.geometry("850x650")

        texto_salida = tk.Text(ventana, wrap="none", font=("Courier New", 9))
        texto_salida.pack(fill="both", expand=True, padx=8, pady=8)

        texto_salida.insert(
            "end", f"Modelo con variables de holgura:\n{solucionador.modelo_estandar_texto()}\n\n"
        )
        for item in iteraciones:
            texto_salida.insert("end", formatear_iteracion(item))

        texto_salida.insert("end", "\nSolución óptima:\n")
        for nombre, valor in solucionador.solucion.items():
            texto_salida.insert("end", f"{nombre} = {formatear_numero(valor)}\n")
        texto_salida.insert("end", f"Z = {formatear_numero(solucionador.valor_optimo)}\n")

        texto_salida.config(state="disabled")

    def _resolver_con_gran_m(self, problema: Problema):
        try:
            solucionador = problema_a_solucionador_gran_m(problema)
            iteraciones = solucionador.resolver()
        except (ErrorAdaptadorGranM, ErrorGranM, ErrorSimplex) as exc:
            messagebox.showerror("No se puede resolver", str(exc))
            return

        ventana = tk.Toplevel(self)
        ventana.title("Resultado - Método Gran M")
        ventana.geometry("850x650")

        texto_salida = tk.Text(ventana, wrap="none", font=("Courier New", 9))
        texto_salida.pack(fill="both", expand=True, padx=8, pady=8)

        texto_salida.insert("end", f"Modelo transformado con Gran M:\n{solucionador.modelo_estandar_texto()}\n\n")
        for item in iteraciones:
            texto_salida.insert("end", formatear_iteracion(item))

        texto_salida.insert("end", "\nSolución óptima:\n")
        for nombre, valor in solucionador.solucion.items():
            texto_salida.insert("end", f"{nombre} = {formatear_numero(valor)}\n")
        texto_salida.insert("end", f"Z = {formatear_numero(solucionador.valor_optimo)}\n")
        texto_salida.config(state="disabled")


def crear_aplicacion(root):
    return AplicacionEntradaComun(root)