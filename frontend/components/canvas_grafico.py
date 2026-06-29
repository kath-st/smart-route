# -*- coding: utf-8 -*-
import sys
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class CanvasGrafico(FigureCanvas):
    """Lienzo para integrar gráficos Matplotlib en la interfaz de PySide6."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#FFFFFF')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#F5F7FA')
        super().__init__(self.fig)
        self.setParent(parent)
        self.configurar_estilos_ejes()

    def configurar_estilos_ejes(self):
        self.axes.tick_params(colors='#111827', labelsize=8)
        self.axes.grid(True, color='#E5E7EB', linestyle='--', alpha=0.7)
        for spine in self.axes.spines.values():
            spine.set_color('#E5E7EB')

    def limpiar_grafico(self):
        self.axes.clear()
        self.configurar_estilos_ejes()
        self.draw()

    def graficar_puntos(self, puntos, ruta=None, mostrar_etiquetas=True):
        self.limpiar_grafico()
        if not puntos:
            return

        xs_alta, ys_alta, ids_alta = [], [], []
        xs_med, ys_med, ids_med = [], [], []
        xs_baja, ys_baja, ids_baja = [], [], []
        
        for p in puntos:
            if p["prioridad"] == "Alta":
                xs_alta.append(p["x"])
                ys_alta.append(p["y"])
                ids_alta.append(p["id"])
            elif p["prioridad"] == "Media":
                xs_med.append(p["x"])
                ys_med.append(p["y"])
                ids_med.append(p["id"])
            else:
                xs_baja.append(p["x"])
                ys_baja.append(p["y"])
                ids_baja.append(p["id"])
                
        if xs_alta:
            self.axes.scatter(xs_alta, ys_alta, color='#EF4444', s=120, edgecolors='#111827', zorder=5, label='Prioridad Alta')
        if xs_med:
            self.axes.scatter(xs_med, ys_med, color='#F59E0B', s=120, edgecolors='#111827', zorder=5, label='Prioridad Media')
        if xs_baja:
            self.axes.scatter(xs_baja, ys_baja, color='#1D4ED8', s=120, edgecolors='#111827', zorder=5, label='Prioridad Baja')

        if puntos:
            p_inicio = puntos[0]
            self.axes.scatter(p_inicio["x"], p_inicio["y"], color="#F59E0B", s=280, marker='*', edgecolors='#111827', zorder=6, label='Punto Inicial/Base')

        if mostrar_etiquetas:
            for p in puntos:
                self.axes.text(p["x"] + 0.8, p["y"] + 0.8, p["id"], color='#111827', fontsize=9, fontweight='semibold')

        if ruta:
            puntos_dict = {p["id"]: p for p in puntos}
            ruta_puntos = [puntos_dict[pid] for pid in ruta if pid in puntos_dict]
            
            if ruta_puntos:
                rx = [p["x"] for p in ruta_puntos]
                ry = [p["y"] for p in ruta_puntos]
                self.axes.plot(rx, ry, color='#22C55E', linestyle='-', linewidth=2, zorder=3, label='Trayectoria')
                
                for i in range(len(ruta_puntos) - 1):
                    p_act = ruta_puntos[i]
                    p_sig = ruta_puntos[i+1]
                    dx = p_sig["x"] - p_act["x"]
                    dy = p_sig["y"] - p_act["y"]
                    self.axes.annotate('', xy=(p_sig["x"] - dx*0.15, p_sig["y"] - dy*0.15), 
                                       xytext=(p_act["x"], p_act["y"]),
                                       arrowprops=dict(arrowstyle="->", color='#22C55E', lw=1.5, ls='-', shrinkA=0, shrinkB=0))

        self.axes.legend(loc='upper right', facecolor='#FFFFFF', edgecolor='#E5E7EB', labelcolor='#111827', fontsize=8)
        self.axes.set_title("Visualización de Puntos y Conexiones de Ruta", color='#111827', fontsize=10, fontweight='bold')
        self.draw()
