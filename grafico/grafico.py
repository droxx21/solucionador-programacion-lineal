import math
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def ordenar_vertices(vertices: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    if not vertices:
        return []
    centro_x = sum(x for x, _ in vertices) / len(vertices)
    centro_y = sum(y for _, y in vertices) / len(vertices)
    return sorted(vertices, key=lambda punto: math.atan2(punto[1] - centro_y, punto[0] - centro_x))


def construir_ejes(ax, vertices: List[Tuple[float, float]], margen: float = 0.2) -> None:
    if not vertices:
        return

    xs = [p[0] for p in vertices]
    ys = [p[1] for p in vertices]
    xmin = min(0.0, min(xs))
    xmax = max(0.0, max(xs))
    ymin = min(0.0, min(ys))
    ymax = max(0.0, max(ys))
    ancho = max(1.0, xmax - xmin)
    alto = max(1.0, ymax - ymin)

    ax.set_xlim(xmin - ancho * margen, xmax + ancho * margen)
    ax.set_ylim(ymin - alto * margen, ymax + alto * margen)

    ax.axhline(0, color="#4b5563", linewidth=1)
    ax.axvline(0, color="#4b5563", linewidth=1)
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.5)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Región factible y solución óptima")


def graficar_restricciones(ax, restricciones: List[Dict[str, float | str]], vertices: List[Tuple[float, float]]) -> None:
    if not restricciones:
        return

    xs = [p[0] for p in vertices] if vertices else [0.0]
    ys = [p[1] for p in vertices] if vertices else [0.0]
    xmin = min(0.0, min(xs)) if xs else -10
    xmax = max(0.0, max(xs)) if xs else 10
    ymin = min(0.0, min(ys)) if ys else -10
    ymax = max(0.0, max(ys)) if ys else 10
    x_min = xmin - 1
    x_max = xmax + 1
    y_min = ymin - 1
    y_max = ymax + 1

    colores = ["#4f6d7a", "#7a8f9d", "#617b8d", "#9aa9b5", "#708090", "#445c71"]
    for idx, restriccion in enumerate(restricciones):
        a = float(restriccion["a"])
        b = float(restriccion["b"])
        c = float(restriccion["c"])
        x_values = [x_min, x_max]

        if abs(b) > 1e-9:
            y_values = [(c - a * x) / b for x in x_values]
            ax.plot(x_values, y_values, color=colores[idx % len(colores)], linewidth=1.8, label=f"R{idx + 1}")
        else:
            x_val = c / a if abs(a) > 1e-9 else 0.0
            ax.axvline(x=x_val, color=colores[idx % len(colores)], linewidth=1.8, label=f"R{idx + 1}")

    if vertices:
        polygon = ordenar_vertices(vertices)
        xs_poly = [p[0] for p in polygon]
        ys_poly = [p[1] for p in polygon]
        ax.fill(xs_poly + [polygon[0][0]], ys_poly + [polygon[0][1]], color="#dfe7ed", alpha=0.7, zorder=1)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)


def graficar_vertices(ax, vertices: List[Tuple[float, float]]) -> None:
    if not vertices:
        return
    xs = [p[0] for p in vertices]
    ys = [p[1] for p in vertices]
    ax.scatter(xs, ys, color="#1f2937", s=40, zorder=3)
    for idx, (x, y) in enumerate(vertices, start=1):
        ax.annotate(f"V{idx}", (x, y), textcoords="offset points", xytext=(6, 4), fontsize=8, color="#1f2937")


def graficar_optimo(ax, punto_optimo: Dict[str, float | str]) -> None:
    if not punto_optimo:
        return
    x = float(punto_optimo["x"])
    y = float(punto_optimo["y"])
    ax.scatter([x], [y], color="#3b82f6", s=110, marker="*", edgecolor="#1f2937", linewidth=1.2, zorder=4, label="Óptimo")
    ax.annotate("Óptimo", (x, y), textcoords="offset points", xytext=(8, 8), fontsize=9, color="#1f2937")


def crear_grafica(frame, restricciones: List[Dict[str, float | str]], vertices: List[Tuple[float, float]], punto_optimo: Dict[str, float | str] | None = None) -> FigureCanvasTkAgg:
    for widget in frame.winfo_children():
        widget.destroy()

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_facecolor("#f5f5f5")
    fig.patch.set_facecolor("#f5f5f5")
    ax.set_axisbelow(True)

    graficar_restricciones(ax, restricciones, vertices)
    graficar_vertices(ax, vertices)
    graficar_optimo(ax, punto_optimo or {})
    construir_ejes(ax, vertices)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    return canvas
