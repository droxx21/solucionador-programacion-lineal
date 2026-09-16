"""Interfaz grafica de la practica Simplex."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

from simplex.simplex import SimplexError, SimplexSolver
from simplex.utils import expression, format_number, parse_number


class SimplexApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Practica 3 - Metodo Simplex")
        self.geometry("1100x750")
        self.minsize(850, 600)
        self.objective_entries: List[tk.Entry] = []
        self.constraint_entries: List[List[tk.Entry]] = []
        self.rhs_entries: List[tk.Entry] = []
        self.operator_boxes: List[ttk.Combobox] = []
        self.variable_count = tk.IntVar(value=2)
        self.constraint_count = tk.IntVar(value=2)
        self.model_frame = None
        self.standard_text = None
        self.output_text = None
        self.solution_text = None
        self._build()

    def _build(self):
        controls = ttk.LabelFrame(self, text="Datos del problema", padding=8)
        controls.pack(fill="x", padx=10, pady=8)
        ttk.Label(controls, text="Variables:").grid(row=0, column=0)
        ttk.Spinbox(controls, from_=1, to=12, textvariable=self.variable_count,
                    width=6).grid(row=0, column=1, padx=5)
        ttk.Label(controls, text="Restricciones:").grid(row=0, column=2)
        ttk.Spinbox(controls, from_=1, to=12, textvariable=self.constraint_count,
                    width=6).grid(row=0, column=3, padx=5)
        ttk.Button(controls, text="Generar modelo", command=self.generate_model).grid(
            row=0, column=4, padx=8
        )
        ttk.Button(controls, text="Resolver", command=self.solve).grid(row=0, column=5)
        ttk.Button(controls, text="Limpiar datos", command=self.clear_model).grid(
            row=0, column=6, padx=8
        )
        ttk.Button(controls, text="Reiniciar", command=self.reset).grid(row=0, column=7)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 10))
        self.content = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda _: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        ))
        self.generate_model()

    def generate_model(self):
        try:
            n, m = int(self.variable_count.get()), int(self.constraint_count.get())
            if n < 1 or m < 1:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Datos invalidos", "Variables y restricciones deben ser enteros positivos.")
            return
        if self.model_frame:
            self.model_frame.destroy()
        self.objective_entries, self.constraint_entries, self.rhs_entries = [], [], []
        self.operator_boxes = []
        self.model_frame = ttk.Frame(self.content)
        self.model_frame.pack(fill="x", pady=5)
        objective_box = ttk.LabelFrame(self.model_frame, text="Funcion objetivo (Maximizar Z)", padding=8)
        objective_box.pack(fill="x", pady=4)
        for col in range(n):
            ttk.Label(objective_box, text=f"x{col + 1}").grid(row=0, column=2 * col)
            entry = ttk.Entry(objective_box, width=9)
            entry.grid(row=0, column=2 * col + 1, padx=(2, 8))
            self.objective_entries.append(entry)
        constraints_box = ttk.LabelFrame(self.model_frame, text="Restricciones (solo <=)", padding=8)
        constraints_box.pack(fill="x", pady=4)
        for row in range(m):
            entries = []
            for col in range(n):
                entry = ttk.Entry(constraints_box, width=9)
                entry.grid(row=row, column=2 * col, padx=(2, 4))
                entries.append(entry)
                ttk.Label(constraints_box, text=f"x{col + 1}").grid(row=row, column=2 * col + 1)
            box = ttk.Combobox(constraints_box, values=["<="], state="readonly", width=4)
            box.set("<=")
            box.grid(row=row, column=2 * n, padx=8)
            rhs = ttk.Entry(constraints_box, width=9)
            rhs.grid(row=row, column=2 * n + 1)
            self.constraint_entries.append(entries)
            self.operator_boxes.append(box)
            self.rhs_entries.append(rhs)
        standard_box = ttk.LabelFrame(self.content, text="Forma estandar", padding=8)
        standard_box.pack(fill="x", pady=4)
        self.standard_text = tk.Text(standard_box, height=5, wrap="word")
        self.standard_text.pack(fill="x")
        output_box = ttk.LabelFrame(self.content, text="Iteraciones Simplex", padding=8)
        output_box.pack(fill="both", expand=True, pady=4)
        self.output_text = tk.Text(output_box, height=25, wrap="none", font=("Courier New", 9))
        self.output_text.pack(fill="both", expand=True)
        solution_box = ttk.LabelFrame(self.content, text="Solucion optima", padding=8)
        solution_box.pack(fill="x", pady=4)
        self.solution_text = tk.Text(solution_box, height=5, wrap="word")
        self.solution_text.pack(fill="x")

    def _read_model(self):
        n = int(self.variable_count.get())
        objective = [parse_number(e.get(), f"coeficiente de x{i + 1}") for i, e in enumerate(self.objective_entries)]
        constraints = []
        rhs = []
        for row, entries in enumerate(self.constraint_entries):
            constraints.append([parse_number(e.get(), f"restriccion {row + 1}, x{i + 1}") for i, e in enumerate(entries)])
            rhs.append(parse_number(self.rhs_entries[row].get(), f"termino independiente {row + 1}"))
            if self.operator_boxes[row].get() != "<=":
                raise ValueError("Esta practica solo admite restricciones <=.")
        return n, objective, constraints, rhs

    def solve(self):
        try:
            n, objective, constraints, rhs = self._read_model()
            solver = SimplexSolver(objective, constraints, rhs, [f"x{i + 1}" for i in range(n)])
            self.standard_text.delete("1.0", "end")
            self.standard_text.insert("end", f"Max Z = {expression(solver.variable_names, objective)}\n")
            for i, (coefficients, value) in enumerate(zip(constraints, rhs), 1):
                self.standard_text.insert("end", f"{expression(solver.variable_names, coefficients)} + s{i} = {format_number(value)}\n")
            self.standard_text.insert("end", "Todas las variables son no negativas.\n")
            iterations = solver.solve()
            self.output_text.delete("1.0", "end")
            for item in iterations:
                self.output_text.insert("end", f"ITERACION {item.number}\n{item.tableau.to_string()}\n")
                if item.entering:
                    shown_ratios = ["-" if r is None else format_number(r) for r in item.ratios]
                    self.output_text.insert("end", f"{item.explanation}\nRazones: {shown_ratios}\n")
                    self.output_text.insert("end", f"Columna pivote: {item.entering} | Fila pivote: {item.leaving} | Elemento pivote: {format_number(item.pivot_element)}\n\n")
            self.solution_text.delete("1.0", "end")
            self.solution_text.insert("end", "Se ha encontrado la solucion optima.\n")
            self.solution_text.insert("end", "\n".join(f"{name} = {format_number(value)}" for name, value in solver.solution.items()))
            self.solution_text.insert("end", f"\nZ = {format_number(solver.optimal_value)}")
        except (ValueError, SimplexError) as exc:
            messagebox.showerror("No se puede resolver", str(exc))

    def clear_model(self):
        for entry in self.objective_entries + self.rhs_entries:
            entry.delete(0, "end")
        for row in self.constraint_entries:
            for entry in row:
                entry.delete(0, "end")
        for widget in (self.standard_text, self.output_text, self.solution_text):
            widget.delete("1.0", "end")

    def reset(self):
        self.variable_count.set(2)
        self.constraint_count.set(2)
        self.generate_model()


if __name__ == "__main__":
    SimplexApp().mainloop()
