"""Interfaz grafica de la practica Simplex."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

from simplex.simplex import ErrorSimplex, SolucionadorSimplex
from simplex.utilidades import analizar_numero, expresion, formatear_numero


class AplicacionSimplex(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Practica 3 - Metodo Simplex")
        self.geometry("1100x750")
        self.minsize(850, 600)
        self.entradas_objetivo: List[tk.Entry] = []
        self.entradas_restricciones: List[List[tk.Entry]] = []
        self.entradas_terminos_independientes: List[tk.Entry] = []
        self.cajas_operador: List[ttk.Combobox] = []
        self.cantidad_variables = tk.IntVar(value=2)
        self.cantidad_restricciones = tk.IntVar(value=2)
        self.marco_modelo = None
        self.texto_forma_estandar = None
        self.texto_salida = None
        self.texto_solucion = None
        self._construir()

    def _construir(self):
        controles = ttk.LabelFrame(self, text="Datos del problema", padding=8)
        controles.pack(fill="x", padx=10, pady=8)
        ttk.Label(controles, text="Variables:").grid(row=0, column=0)
        ttk.Spinbox(controles, from_=1, to=12, textvariable=self.cantidad_variables,
                    width=6).grid(row=0, column=1, padx=5)
        ttk.Label(controles, text="Restricciones:").grid(row=0, column=2)
        ttk.Spinbox(controles, from_=1, to=12, textvariable=self.cantidad_restricciones,
                    width=6).grid(row=0, column=3, padx=5)
        ttk.Button(controles, text="Generar modelo", command=self.generar_modelo).grid(
            row=0, column=4, padx=8
        )
        ttk.Button(controles, text="Resolver", command=self.resolver).grid(row=0, column=5)
        ttk.Button(controles, text="Limpiar datos", command=self.limpiar_modelo).grid(
            row=0, column=6, padx=8
        )
        ttk.Button(controles, text="Reiniciar", command=self.reiniciar).grid(row=0, column=7)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        barra_desplazamiento = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barra_desplazamiento.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        barra_desplazamiento.pack(side="right", fill="y", padx=(0, 10))
        self.contenido = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.contenido, anchor="nw")
        self.contenido.bind("<Configure>", lambda _: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))
        self.generar_modelo()

    def generar_modelo(self):
        try:
            num_variables, num_restricciones = int(self.cantidad_variables.get()), int(self.cantidad_restricciones.get())
            if num_variables < 1 or num_restricciones < 1:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Datos invalidos", "Variables y restricciones deben ser enteros positivos.")
            return
        if self.marco_modelo:
            self.marco_modelo.destroy()
        self.entradas_objetivo, self.entradas_restricciones, self.entradas_terminos_independientes = [], [], []
        self.cajas_operador = []
        self.marco_modelo = ttk.Frame(self.contenido)
        self.marco_modelo.pack(fill="x", pady=5)
        caja_objetivo = ttk.LabelFrame(self.marco_modelo, text="Funcion objetivo (Maximizar Z)", padding=8)
        caja_objetivo.pack(fill="x", pady=4)
        for columna in range(num_variables):
            ttk.Label(caja_objetivo, text=f"x{columna + 1}").grid(row=0, column=2 * columna)
            entrada = ttk.Entry(caja_objetivo, width=9)
            entrada.grid(row=0, column=2 * columna + 1, padx=(2, 8))
            self.entradas_objetivo.append(entrada)
        caja_restricciones = ttk.LabelFrame(self.marco_modelo, text="Restricciones (solo <=)", padding=8)
        caja_restricciones.pack(fill="x", pady=4)
        for fila in range(num_restricciones):
            entradas = []
            for columna in range(num_variables):
                entrada = ttk.Entry(caja_restricciones, width=9)
                entrada.grid(row=fila, column=2 * columna, padx=(2, 4))
                entradas.append(entrada)
                ttk.Label(caja_restricciones, text=f"x{columna + 1}").grid(row=fila, column=2 * columna + 1)
            caja_operador = ttk.Combobox(caja_restricciones, values=["<="], state="readonly", width=4)
            caja_operador.set("<=")
            caja_operador.grid(row=fila, column=2 * num_variables, padx=8)
            entrada_termino = ttk.Entry(caja_restricciones, width=9)
            entrada_termino.grid(row=fila, column=2 * num_variables + 1)
            self.entradas_restricciones.append(entradas)
            self.cajas_operador.append(caja_operador)
            self.entradas_terminos_independientes.append(entrada_termino)
        caja_forma_estandar = ttk.LabelFrame(self.contenido, text="Forma estandar", padding=8)
        caja_forma_estandar.pack(fill="x", pady=4)
        self.texto_forma_estandar = tk.Text(caja_forma_estandar, height=5, wrap="word")
        self.texto_forma_estandar.pack(fill="x")
        caja_salida = ttk.LabelFrame(self.contenido, text="Iteraciones Simplex", padding=8)
        caja_salida.pack(fill="both", expand=True, pady=4)
        self.texto_salida = tk.Text(caja_salida, height=25, wrap="none", font=("Courier New", 9))
        self.texto_salida.pack(fill="both", expand=True)
        caja_solucion = ttk.LabelFrame(self.contenido, text="Solucion optima", padding=8)
        caja_solucion.pack(fill="x", pady=4)
        self.texto_solucion = tk.Text(caja_solucion, height=5, wrap="word")
        self.texto_solucion.pack(fill="x")

    def _leer_modelo(self):
        num_variables = int(self.cantidad_variables.get())
        funcion_objetivo = [analizar_numero(entrada.get(), f"coeficiente de x{i + 1}") for i, entrada in enumerate(self.entradas_objetivo)]
        restricciones = []
        terminos_independientes = []
        for fila, entradas in enumerate(self.entradas_restricciones):
            restricciones.append([analizar_numero(entrada.get(), f"restriccion {fila + 1}, x{i + 1}") for i, entrada in enumerate(entradas)])
            terminos_independientes.append(analizar_numero(self.entradas_terminos_independientes[fila].get(), f"termino independiente {fila + 1}"))
            if self.cajas_operador[fila].get() != "<=":
                raise ValueError("Esta practica solo admite restricciones <=.")
        return num_variables, funcion_objetivo, restricciones, terminos_independientes

    def resolver(self):
        try:
            num_variables, funcion_objetivo, restricciones, terminos_independientes = self._leer_modelo()
            solucionador = SolucionadorSimplex(funcion_objetivo, restricciones, terminos_independientes, [f"x{i + 1}" for i in range(num_variables)])
            self.texto_forma_estandar.delete("1.0", "end")
            self.texto_forma_estandar.insert("end", f"Max Z = {expresion(solucionador.nombres_variables, funcion_objetivo)}\n")
            for i, (coeficientes, valor) in enumerate(zip(restricciones, terminos_independientes), 1):
                self.texto_forma_estandar.insert("end", f"{expresion(solucionador.nombres_variables, coeficientes)} + s{i} = {formatear_numero(valor)}\n")
            self.texto_forma_estandar.insert("end", "Todas las variables son no negativas.\n")
            iteraciones = solucionador.resolver()
            self.texto_salida.delete("1.0", "end")
            for item in iteraciones:
                self.texto_salida.insert("end", f"ITERACION {item.numero}\n{item.tabla.to_string()}\n")
                if item.entrante:
                    razones_mostradas = ["-" if r is None else formatear_numero(r) for r in item.razones]
                    self.texto_salida.insert("end", f"{item.explicacion}\nRazones: {razones_mostradas}\n")
                    self.texto_salida.insert("end", f"Columna pivote: {item.entrante} | Fila pivote: {item.saliente} | Elemento pivote: {formatear_numero(item.elemento_pivote)}\n\n")
            self.texto_solucion.delete("1.0", "end")
            self.texto_solucion.insert("end", "Se ha encontrado la solucion optima.\n")
            self.texto_solucion.insert("end", "\n".join(f"{nombre} = {formatear_numero(valor)}" for nombre, valor in solucionador.solucion.items()))
            self.texto_solucion.insert("end", f"\nZ = {formatear_numero(solucionador.valor_optimo)}")
        except (ValueError, ErrorSimplex) as exc:
            messagebox.showerror("No se puede resolver", str(exc))

    def limpiar_modelo(self):
        for entrada in self.entradas_objetivo + self.entradas_terminos_independientes:
            entrada.delete(0, "end")
        for fila in self.entradas_restricciones:
            for entrada in fila:
                entrada.delete(0, "end")
        for widget in (self.texto_forma_estandar, self.texto_salida, self.texto_solucion):
            widget.delete("1.0", "end")

    def reiniciar(self):
        self.cantidad_variables.set(2)
        self.cantidad_restricciones.set(2)
        self.generar_modelo()


if __name__ == "__main__":
    AplicacionSimplex().mainloop()
