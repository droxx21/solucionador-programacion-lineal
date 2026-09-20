import tkinter as tk

from entrada.interfaz import crear_aplicacion


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Programación Lineal - Entrada Común")
    root.geometry("900x800")
    root.minsize(800, 700)
    crear_aplicacion(root)
    root.mainloop()
