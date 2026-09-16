"""Punto de entrada único de la aplicación de Programación Lineal.

Etapa 1 de la integración: este main.py todavía no fusiona ambas
interfaces gráficas en una sola ventana (eso requiere adaptar
SimplexApp para que deje de heredar de tk.Tk, lo cual se abordará en
una etapa posterior). Por ahora ofrece un menú de selección que lanza
cada método en su propia ventana, sin modificar su lógica ni su
comportamiento actual.
"""

import tkinter as tk
from tkinter import ttk


def abrir_metodo_grafico():
    """Lanza el módulo del método gráfico en su propia ventana."""
    from grafico.interfaz import crear_aplicacion

    ventana = tk.Toplevel()
    crear_aplicacion(ventana)


def abrir_metodo_simplex():
    """Lanza el módulo del método simplex en su propia ventana."""
    from simplex.interfaz import SimplexApp

    SimplexApp().mainloop()


def crear_menu_principal():
    root = tk.Tk()
    root.title("Programación Lineal - Menú Principal")
    root.geometry("420x220")
    root.minsize(380, 200)

    contenedor = ttk.Frame(root, padding=20)
    contenedor.pack(fill="both", expand=True)

    ttk.Label(
        contenedor,
        text="Seleccione el método a utilizar:",
        font=("TkDefaultFont", 12),
    ).pack(pady=(0, 20))

    ttk.Button(
        contenedor,
        text="Método Gráfico",
        command=abrir_metodo_grafico,
    ).pack(fill="x", pady=6)

    ttk.Button(
        contenedor,
        text="Método Simplex",
        command=abrir_metodo_simplex,
    ).pack(fill="x", pady=6)

    ttk.Button(
        contenedor,
        text="Salir",
        command=root.destroy,
    ).pack(fill="x", pady=(20, 0))

    return root


if __name__ == "__main__":
    root = crear_menu_principal()
    root.mainloop()
