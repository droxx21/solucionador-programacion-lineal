import tkinter as tk
from tkinter import messagebox, ttk

from grafico.grafico import crear_grafica
from grafico.modelo import construir_restriccion, parsear_numero, resolver_modelo


class AplicacionProgramacionLineal:
    def __init__(self, root):
        self.root = root
        self.root.title("Programación Lineal - Método Gráfico")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 750)

        self.restricciones = []
        self.canvas_grafica = None

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TFrame", background="#f3f3f3")
        self.style.configure("TLabelframe", background="#f3f3f3", foreground="#1f2937")
        self.style.configure("TLabel", background="#f3f3f3", foreground="#1f2937")
        self.style.configure("TButton", padding=(8, 5))
        self.style.configure("Treeview", rowheight=24)

        self.crear_menu()
        self.crear_estructura_principal()
        self.cargar_ejemplo()

    def crear_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        menu_archivo = tk.Menu(menu_bar, tearoff=0)
        menu_archivo.add_command(label="Nuevo / Limpiar", command=self.limpiar_todo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.destroy)
        menu_bar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ayuda = tk.Menu(menu_bar, tearoff=0)
        menu_ayuda.add_command(label="Acerca del programa", command=self.acerca_del_programa)
        menu_ayuda.add_command(label="Información breve del método", command=self.informacion_metodo)
        menu_bar.add_cascade(label="Ayuda", menu=menu_ayuda)

    def crear_estructura_principal(self):
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=5)
        self.root.grid_rowconfigure(0, weight=1)

        panel_izquierdo = ttk.Frame(self.root, padding=(10, 10, 5, 10))
        panel_izquierdo.grid(row=0, column=0, sticky="nsew")
        panel_izquierdo.grid_columnconfigure(0, weight=1)

        panel_derecho = ttk.Frame(self.root, padding=(5, 10, 10, 10))
        panel_derecho.grid(row=0, column=1, sticky="nsew")
        panel_derecho.grid_columnconfigure(0, weight=1)
        panel_derecho.grid_rowconfigure(0, weight=3)
        panel_derecho.grid_rowconfigure(1, weight=2)

        self.panel_objetivo = ttk.LabelFrame(panel_izquierdo, text="1. Función Objetivo", padding=(8, 6))
        self.panel_objetivo.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.panel_objetivo.grid_columnconfigure(1, weight=1)

        self.panel_restricciones = ttk.LabelFrame(panel_izquierdo, text="2. Restricciones", padding=(8, 6))
        self.panel_restricciones.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.panel_restricciones.grid_columnconfigure(1, weight=1)

        self.panel_controles = ttk.LabelFrame(panel_izquierdo, text="3. Controles", padding=(8, 6))
        self.panel_controles.grid(row=2, column=0, sticky="ew", pady=(0, 8))

        self.panel_grafica = ttk.LabelFrame(panel_derecho, text="4. Gráfica del Modelo", padding=(8, 6))
        self.panel_grafica.grid(row=0, column=0, sticky="nsew")
        self.panel_grafica.grid_columnconfigure(0, weight=1)
        self.panel_grafica.grid_rowconfigure(0, weight=1)

        self.panel_modelo = ttk.LabelFrame(panel_derecho, text="5. Modelo Matemático", padding=(8, 6))
        self.panel_modelo.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.panel_modelo.grid_columnconfigure(0, weight=1)

        panel_bottom = ttk.Frame(panel_derecho)
        panel_bottom.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        panel_bottom.grid_columnconfigure(0, weight=1)
        panel_bottom.grid_columnconfigure(1, weight=1)
        panel_bottom.grid_columnconfigure(2, weight=1)
        panel_bottom.grid_columnconfigure(3, weight=1)

        self.panel_vertices = ttk.LabelFrame(panel_bottom, text="6. Vértices de la Región Factible", padding=(8, 6))
        self.panel_vertices.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.panel_evaluacion = ttk.LabelFrame(panel_bottom, text="7. Evaluación de la Función Objetivo", padding=(8, 6))
        self.panel_evaluacion.grid(row=0, column=1, sticky="nsew", padx=(0, 6))
        self.panel_solucion = ttk.LabelFrame(panel_bottom, text="8. Solución Óptima", padding=(8, 6))
        self.panel_solucion.grid(row=0, column=2, sticky="nsew", padx=(0, 6))

        self.crear_panel_objetivo()
        self.crear_panel_restricciones()
        self.crear_panel_controles()
        self.crear_panel_modelo()
        self.crear_panel_vertices()
        self.crear_panel_evaluacion()
        self.crear_panel_solucion()

    def crear_panel_objetivo(self):
        tk.Label(self.panel_objetivo, text="Tipo:", anchor="w").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(4, 6))
        self.tipo_objetivo = ttk.Combobox(self.panel_objetivo, values=["Maximizar", "Minimizar"], state="readonly", width=14)
        self.tipo_objetivo.grid(row=0, column=1, sticky="ew", pady=(4, 6))
        self.tipo_objetivo.set("Maximizar")

        tk.Label(self.panel_objetivo, text="Coeficiente de X1:", anchor="w").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 6))
        self.coef_x_objetivo = ttk.Entry(self.panel_objetivo, width=18)
        self.coef_x_objetivo.grid(row=1, column=1, sticky="ew", pady=(0, 6))

        tk.Label(self.panel_objetivo, text="Coeficiente de X2:", anchor="w").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(0, 6))
        self.coef_y_objetivo = ttk.Entry(self.panel_objetivo, width=18)
        self.coef_y_objetivo.grid(row=2, column=1, sticky="ew", pady=(0, 6))

    def crear_panel_restricciones(self):
        campos = ttk.Frame(self.panel_restricciones)
        campos.grid(row=0, column=0, columnspan=2, sticky="ew")
        campos.grid_columnconfigure(1, weight=1)

        tk.Label(campos, text="a (X1):", anchor="w").grid(row=0, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
        self.restriccion_a = ttk.Entry(campos, width=14)
        self.restriccion_a.grid(row=0, column=1, sticky="ew", pady=(0, 6))

        tk.Label(campos, text="b (X2):", anchor="w").grid(row=1, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
        self.restriccion_b = ttk.Entry(campos, width=14)
        self.restriccion_b.grid(row=1, column=1, sticky="ew", pady=(0, 6))

        tk.Label(campos, text="Relación:", anchor="w").grid(row=2, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
        self.restriccion_rel = ttk.Combobox(campos, values=["<=", ">=", "="], state="readonly", width=12)
        self.restriccion_rel.grid(row=2, column=1, sticky="ew", pady=(0, 6))
        self.restriccion_rel.set("<=")

        tk.Label(campos, text="c:", anchor="w").grid(row=3, column=0, padx=(0, 6), pady=(0, 6), sticky="w")
        self.restriccion_c = ttk.Entry(campos, width=14)
        self.restriccion_c.grid(row=3, column=1, sticky="ew", pady=(0, 6))

        self.no_negatividad = tk.BooleanVar(value=True)
        self.check_no_neg = ttk.Checkbutton(self.panel_restricciones, text="Agregar restricciones de no negatividad (x >= 0, y >= 0)", variable=self.no_negatividad, onvalue=True, offvalue=False)
        self.check_no_neg.grid(row=1, column=0, sticky="w", pady=(6, 8))

        self.tree_restricciones = ttk.Treeview(self.panel_restricciones, columns=("#", "a", "b", "rel", "c"), show="headings", height=7)
        self.tree_restricciones.heading("#", text="#")
        self.tree_restricciones.heading("a", text="a (X1)")
        self.tree_restricciones.heading("b", text="b (X2)")
        self.tree_restricciones.heading("rel", text="Relación")
        self.tree_restricciones.heading("c", text="c")
        self.tree_restricciones.column("#", width=40, anchor="center")
        self.tree_restricciones.column("a", width=70, anchor="center")
        self.tree_restricciones.column("b", width=70, anchor="center")
        self.tree_restricciones.column("rel", width=80, anchor="center")
        self.tree_restricciones.column("c", width=80, anchor="center")
        self.tree_restricciones.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        botones = ttk.Frame(self.panel_restricciones)
        botones.grid(row=3, column=0, columnspan=2, sticky="ew")
        botones.grid_columnconfigure(0, weight=1)
        botones.grid_columnconfigure(1, weight=1)
        botones.grid_columnconfigure(2, weight=1)

        ttk.Button(botones, text="Agregar", command=self.agregar_restriccion).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(botones, text="Eliminar", command=self.eliminar_restriccion).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_restricciones).grid(row=0, column=2, sticky="ew", padx=(4, 0))

    def crear_panel_controles(self):
        ttk.Button(self.panel_controles, text="Graficar y Resolver", command=self.graficar_y_resolver).pack(fill="x", pady=(0, 8))
        ttk.Button(self.panel_controles, text="Limpiar Todo", command=self.limpiar_todo).pack(fill="x", pady=(0, 8))
        ttk.Button(self.panel_controles, text="Salir", command=self.root.destroy).pack(fill="x")

    def crear_panel_modelo(self):
        self.modelo_text = tk.Text(self.panel_modelo, height=12, width=42, wrap="word", bg="#ffffff", state="disabled")
        self.modelo_text.pack(fill="both", expand=True)

    def crear_panel_vertices(self):
        self.tree_vertices = ttk.Treeview(self.panel_vertices, columns=("vertice", "x", "y"), show="headings", height=7)
        self.tree_vertices.heading("vertice", text="Vértice")
        self.tree_vertices.heading("x", text="x")
        self.tree_vertices.heading("y", text="y")
        self.tree_vertices.column("vertice", width=80, anchor="center")
        self.tree_vertices.column("x", width=90, anchor="center")
        self.tree_vertices.column("y", width=90, anchor="center")
        self.tree_vertices.pack(fill="both", expand=True)

    def crear_panel_evaluacion(self):
        self.tree_evaluacion = ttk.Treeview(self.panel_evaluacion, columns=("vertice", "x", "y", "z"), show="headings", height=7)
        self.tree_evaluacion.heading("vertice", text="Vértice")
        self.tree_evaluacion.heading("x", text="x")
        self.tree_evaluacion.heading("y", text="y")
        self.tree_evaluacion.heading("z", text="Z")
        self.tree_evaluacion.column("vertice", width=80, anchor="center")
        self.tree_evaluacion.column("x", width=80, anchor="center")
        self.tree_evaluacion.column("y", width=80, anchor="center")
        self.tree_evaluacion.column("z", width=90, anchor="center")
        self.tree_evaluacion.pack(fill="both", expand=True)

    def crear_panel_solucion(self):
        self.etiqueta_optimo = ttk.Label(self.panel_solucion, text="Óptimo en el vértice: -\n\nx = -\ny = -\n\nValor óptimo:\nZ = -", justify="left")
        self.etiqueta_optimo.pack(fill="both", expand=True, padx=6, pady=6)

    def agregar_restriccion(self):
        try:
            a = parsear_numero(self.restriccion_a.get())
            b = parsear_numero(self.restriccion_b.get())
            c = parsear_numero(self.restriccion_c.get())
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar valores numéricos válidos o fracciones como 1/2.")
            return

        relacion = self.restriccion_rel.get()
        if relacion not in {"<=", ">=", "="}:
            messagebox.showerror("Error", "Debe seleccionar una relación válida.")
            return

        restriccion = construir_restriccion(a, b, relacion, c)
        self.restricciones.append(restriccion)
        self.actualizar_tabla_restricciones()
        self.restriccion_a.delete(0, "end")
        self.restriccion_b.delete(0, "end")
        self.restriccion_c.delete(0, "end")
        self.restriccion_rel.set("<=")

    def eliminar_restriccion(self):
        seleccion = self.tree_restricciones.selection()
        if not seleccion:
            messagebox.showinfo("Selección", "Seleccione una restricción para eliminar.")
            return

        indice = int(self.tree_restricciones.item(seleccion[0], "values")[0]) - 1
        del self.restricciones[indice]
        self.actualizar_tabla_restricciones()

    def limpiar_restricciones(self):
        self.restricciones.clear()
        self.actualizar_tabla_restricciones()

    def actualizar_tabla_restricciones(self):
        for fila in self.tree_restricciones.get_children():
            self.tree_restricciones.delete(fila)

        for idx, r in enumerate(self.restricciones, start=1):
            self.tree_restricciones.insert("", "end", values=(idx, r["a"], r["b"], r["relation"], r["c"]))

    def _restricciones_para_modelo(self):
        restricciones = list(self.restricciones)
        if self.no_negatividad.get():
            restricciones.extend([
                construir_restriccion(1, 0, ">=", 0),
                construir_restriccion(0, 1, ">=", 0),
            ])
        return restricciones

    def graficar_y_resolver(self):
        coef_x = self.coef_x_objetivo.get().strip()
        coef_y = self.coef_y_objetivo.get().strip()
        if not coef_x or not coef_y:
            messagebox.showerror("Error", "Debe ingresar los coeficientes de la función objetivo.")
            return

        try:
            objetivo = {
                "tipo": self.tipo_objetivo.get(),
                "a": parsear_numero(coef_x),
                "b": parsear_numero(coef_y),
            }
        except ValueError:
            messagebox.showerror("Error", "Los coeficientes de la función objetivo deben ser numéricos o fracciones válidas como 1/2.")
            return

        restricciones_modelo = self._restricciones_para_modelo()
        if not restricciones_modelo:
            messagebox.showerror("Error", "Debe ingresar al menos una restricción.")
            return

        try:
            resultado = resolver_modelo(objetivo, restricciones_modelo, incluir_no_negatividad=False)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.actualizar_modelo(resultado["modelo_texto"])
        self.actualizar_vertices(resultado["vertices"])
        self.actualizar_evaluacion(resultado["evaluaciones"])
        self.actualizar_solucion(resultado["optimo"])

        if self.canvas_grafica is not None:
            self.canvas_grafica.get_tk_widget().destroy()
        self.canvas_grafica = crear_grafica(self.panel_grafica, self._restricciones_para_modelo(), resultado["vertices"], resultado["optimo"])

    def actualizar_modelo(self, texto):
        self.modelo_text.config(state="normal")
        self.modelo_text.delete("1.0", "end")
        self.modelo_text.insert("1.0", texto)
        self.modelo_text.config(state="disabled")

    def actualizar_vertices(self, vertices):
        for fila in self.tree_vertices.get_children():
            self.tree_vertices.delete(fila)

        for idx, (x, y) in enumerate(vertices, start=1):
            self.tree_vertices.insert("", "end", values=(f"V{idx}", f"{x:.2f}", f"{y:.2f}"))

    def actualizar_evaluacion(self, evaluaciones):
        for fila in self.tree_evaluacion.get_children():
            self.tree_evaluacion.delete(fila)

        for item in evaluaciones:
            self.tree_evaluacion.insert("", "end", values=(item["vertice"], f"{item['x']:.2f}", f"{item['y']:.2f}", f"{item['z']:.2f}"))

    def actualizar_solucion(self, optimo):
        self.etiqueta_optimo.config(
            text=(
                f"Óptimo en el vértice: {optimo['vertice']}\n\n"
                f"x = {optimo['x']:.2f}\n"
                f"y = {optimo['y']:.2f}\n\n"
                f"Valor óptimo:\nZ = {optimo['z']:.2f}"
            )
        )

    def limpiar_todo(self):
        self.tipo_objetivo.set("Maximizar")
        self.coef_x_objetivo.delete(0, "end")
        self.coef_y_objetivo.delete(0, "end")
        self.no_negatividad.set(True)
        self.restricciones.clear()
        self.actualizar_tabla_restricciones()
        self.modelo_text.config(state="normal")
        self.modelo_text.delete("1.0", "end")
        self.modelo_text.config(state="disabled")
        for tabla in (self.tree_vertices, self.tree_evaluacion):
            for fila in tabla.get_children():
                tabla.delete(fila)
        self.etiqueta_optimo.config(text="Óptimo en el vértice: -\n\nx = -\ny = -\n\nValor óptimo:\nZ = -")
        if self.canvas_grafica is not None:
            self.canvas_grafica.get_tk_widget().destroy()
            self.canvas_grafica = None

    def acerca_del_programa(self):
        messagebox.showinfo(
            "Acerca del programa",
            "Programación Lineal - Método Gráfico\n\nAplicación académica para resolver problemas de optimización lineal mediante el método gráfico en dos variables.",
        )

    def informacion_metodo(self):
        messagebox.showinfo(
            "Método gráfico",
            "La solución se encuentra en los vértices de la región factible. La función objetivo se evalúa en cada vértice y se selecciona el mejor valor según el criterio de maximización o minimización.",
        )

    def cargar_ejemplo(self):
        self.tipo_objetivo.set("Maximizar")
        self.coef_x_objetivo.insert(0, "40")
        self.coef_y_objetivo.insert(0, "30")
        self.restricciones = [
            construir_restriccion(2, 1, "<=", 40),
            construir_restriccion(1, 2, "<=", 50),
        ]
        self.actualizar_tabla_restricciones()
        self.graficar_y_resolver()


def crear_aplicacion(root):
    return AplicacionProgramacionLineal(root)
