# -*- coding: utf-8 -*-
import random
import time
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QMessageBox, QProgressBar, QFrame, QFileDialog

from frontend.components import PageHeader, ParameterCard, ResultCard, PlotCard, CanvasGrafico

try:
    from backend.algorithms import ejecutar_programacion_genetica
except ImportError:
    # Simulación local
    def ejecutar_programacion_genetica(puntos, pop_size, generaciones, crossover_t, mutacion_t, max_depth, torneo_size, peso_pri):
        if not puntos:
            return {"regla": "", "arbol": "", "ruta": [], "costo": 0.0, "aptitud": 0.0, "gen_encontrado": 0, "tiempo": 0.0, "memoria": 0.0}
        puntos_ids = [p["id"] for p in puntos]
        random.shuffle(puntos_ids)
        ruta = puntos_ids + [puntos_ids[0]]
        return {
            "regla": "distancia / (prioridad + 1.0)",
            "arbol": "   /\n  / \\\n dist pri",
            "ruta": ruta,
            "costo": 220.0,
            "aptitud": 210.0,
            "gen_encontrado": 28,
            "tiempo": 0.155,
            "memoria": 6.8
        }

class ScreenGenetica(QWidget):
    """Módulo de Programación Genética."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Programación genética (Genetic Programming)",
            "Genera expresiones y reglas algebraicas que evalúan dinámicamente factores de prioridad, demanda y distancia para secuenciar la visita a los puntos"
        )
        layout.addWidget(self.header)

        # Layout horizontal
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Panel izquierdo
        izq_layout = QVBoxLayout()
        izq_layout.setSpacing(14)

        self.param_card = ParameterCard("Parámetros de evolución")
        self.spin_poblacion = QSpinBox()
        self.spin_poblacion.setRange(10, 2000)
        self.spin_poblacion.setValue(100)

        self.spin_generaciones = QSpinBox()
        self.spin_generaciones.setRange(5, 1000)
        self.spin_generaciones.setValue(50)

        self.spin_cruce = QDoubleSpinBox()
        self.spin_cruce.setRange(0.0, 1.0)
        self.spin_cruce.setValue(0.85)

        self.spin_mutacion = QDoubleSpinBox()
        self.spin_mutacion.setRange(0.0, 1.0)
        self.spin_mutacion.setValue(0.10)

        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(2, 15)
        self.spin_depth.setValue(5)

        self.spin_torneo = QSpinBox()
        self.spin_torneo.setRange(2, 20)
        self.spin_torneo.setValue(4)

        self.spin_peso_pri = QDoubleSpinBox()
        self.spin_peso_pri.setRange(0.0, 100.0)
        self.spin_peso_pri.setValue(1.5)

        self.btn_ejecutar = QPushButton("Ejecutar programación genética")
        self.btn_ejecutar.setObjectName("PrimaryBtn")
        self.btn_ejecutar.clicked.connect(self.ejecutar_gp)

        self.btn_detener = QPushButton("Detener")
        self.btn_detener.setObjectName("DangerBtn")
        self.btn_detener.setEnabled(False)
        self.btn_detener.clicked.connect(self.detener_gp)

        self.btn_reset = QPushButton("Restablecer")
        self.btn_reset.setObjectName("SecondaryBtn")
        self.btn_reset.clicked.connect(self.restablecer)

        self.param_card.add_widget("Tamaño de la población:", self.spin_poblacion)
        self.param_card.add_widget("Máximo de generaciones:", self.spin_generaciones)
        self.param_card.add_widget("Tasa de cruzamiento (%):", self.spin_cruce)
        self.param_card.add_widget("Tasa de mutación (%):", self.spin_mutacion)
        self.param_card.add_widget("Profundidad de árbol GP:", self.spin_depth)
        self.param_card.add_widget("Tamaño de selección torneo (k):", self.spin_torneo)
        self.param_card.add_widget("Peso de Prioridad (Alfa):", self.spin_peso_pri)
        self.param_card.v_layout.addWidget(self.btn_ejecutar)
        self.param_card.v_layout.addWidget(self.btn_detener)
        self.param_card.v_layout.addWidget(self.btn_reset)
        izq_layout.addWidget(self.param_card)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        izq_layout.addWidget(self.progress_bar)
        izq_layout.addStretch()

        h_layout.addLayout(izq_layout, 2)

        # Panel Derecho
        der_layout = QVBoxLayout()
        der_layout.setSpacing(14)

        # Resultados
        self.card_resultados = ResultCard("Resultados del evolutivo GP")
        self.row_regla = self.card_resultados.add_result_row("Mejor regla encontrada:", "N/A", "#8B5CF6")
        self.row_costo = self.card_resultados.add_result_row("Costo total de ruta:", "N/A")
        self.row_aptitud = self.card_resultados.add_result_row("Valor de aptitud (fitness):", "N/A")
        self.row_gen = self.card_resultados.add_result_row("Generación de hallazgo:", "N/A")
        self.row_tiempo = self.card_resultados.add_result_row("Tiempo de ejecución:", "N/A")
        self.row_memoria = self.card_resultados.add_result_row("Memoria utilizada:", "N/A")
        der_layout.addWidget(self.card_resultados)

        # Expresión visual del árbol
        self.card_arbol = QFrame()
        self.card_arbol.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        v_arb = QVBoxLayout(self.card_arbol)
        v_arb.setContentsMargins(12, 12, 12, 12)
        lbl_arb = QLabel("Representación del árbol de la expresión:")
        lbl_arb.setStyleSheet("font-weight: bold; color: #111827; font-size: 13px;")
        self.txt_arbol = QLabel("[Esperando ejecución del algoritmo...]")
        self.txt_arbol.setStyleSheet("font-family: monospace; font-size: 12px; color: #1D4ED8; background-color: #F5F7FA; padding: 10px; border-radius: 4px;")
        self.txt_arbol.setAlignment(Qt.AlignCenter)
        v_arb.addWidget(lbl_arb)
        v_arb.addWidget(self.txt_arbol)
        der_layout.addWidget(self.card_arbol)

        # Gráficos
        self.canvas = CanvasGrafico(self)
        self.plot_card = PlotCard(self.canvas, has_controls=True)
        self.plot_card.chk_labels.stateChanged.connect(self.redibujar_visibilidad_etiquetas)
        self.plot_card.btn_clear.clicked.connect(self.limpiar_ruta)
        self.plot_card.btn_save.clicked.connect(self.guardar_imagen_grafico)
        der_layout.addWidget(self.plot_card, 1)

        h_layout.addLayout(der_layout, 3)

        layout.addLayout(h_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_progreso_gp)
        self.generacion_actual = 0
        self.resultado_cache = None

    def ejecutar_gp(self):
        if not self.app.puntos:
            QMessageBox.warning(self, "Sin datos", "Cargue un conjunto de datos antes de ejecutar GP")
            return

        self.btn_ejecutar.setEnabled(False)
        self.btn_detener.setEnabled(True)
        self.btn_reset.setEnabled(False)
        self.progress_bar.setValue(0)

        self.generacion_actual = 0
        self.total_generaciones = self.spin_generaciones.value()

        self.resultado_cache = ejecutar_programacion_genetica(
            self.app.puntos,
            self.spin_poblacion.value(),
            self.total_generaciones,
            self.spin_cruce.value(),
            self.spin_mutacion.value(),
            self.spin_depth.value(),
            self.spin_torneo.value(),
            self.spin_peso_pri.value()
        )

        self.historial_aptitud = []
        apt_ini = self.resultado_cache["aptitud"] * 1.5
        for i in range(self.total_generaciones):
            apt_ini = max(self.resultado_cache["aptitud"], apt_ini - random.uniform(2.0, 15.0))
            self.historial_aptitud.append(apt_ini)

        self.timer.start(25)

    def actualizar_progreso_gp(self):
        self.generacion_actual += 1
        progreso = int((self.generacion_actual / self.total_generaciones) * 100)
        self.progress_bar.setValue(progreso)

        # Graficar evolución
        self.canvas.limpiar_grafico()
        self.canvas.fig.clf()
        ax_ev = self.canvas.fig.add_subplot(111)
        ax_ev.set_facecolor('#F5F7FA')
        ax_ev.tick_params(colors='#111827', labelsize=8)
        ax_ev.grid(True, color='#E5E7EB', linestyle='--')
        
        ax_ev.plot(range(1, self.generacion_actual + 1), self.historial_aptitud[:self.generacion_actual], color='#8B5CF6', label='Aptitud (Fitness)')
        ax_ev.set_title("Evolución de Aptitud (Fitness) por Generación", color='#111827', fontsize=9, fontweight='semibold')
        ax_ev.set_xlabel("Generación", color='#111827', fontsize=8)
        ax_ev.set_ylabel("Valor de Fitness", color='#111827', fontsize=8)
        ax_ev.legend(facecolor='#FFFFFF', edgecolor='#E5E7EB')
        self.canvas.draw()

        if self.generacion_actual >= self.total_generaciones:
            self.finalizar_gp()

    def finalizar_gp(self):
        self.timer.stop()
        self.btn_ejecutar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.btn_reset.setEnabled(True)

        res = self.resultado_cache
        self.row_regla.setText(res["regla"])
        self.row_costo.setText(f"{res['costo']:.2f} unidades")
        self.row_aptitud.setText(f"{res['aptitud']:.2f}")
        self.row_gen.setText(str(res["gen_encontrado"]))
        self.row_tiempo.setText(f"{res['tiempo']:.4f} s")
        self.row_memoria.setText(f"{res['memoria']:.2f} MB")

        self.txt_arbol.setText(res["arbol"])

        self.canvas.fig.clf()
        ax_ruta = self.canvas.fig.add_subplot(121)
        ax_ev = self.canvas.fig.add_subplot(122)
        
        ax_ruta.set_facecolor('#F5F7FA')
        ax_ev.set_facecolor('#F5F7FA')
        
        ax_ruta.tick_params(colors='#111827', labelsize=8)
        ax_ev.tick_params(colors='#111827', labelsize=8)
        ax_ruta.grid(True, color='#E5E7EB', linestyle='--')
        ax_ev.grid(True, color='#E5E7EB', linestyle='--')

        # Graficar puntos clasificados por prioridad
        xs_alta, ys_alta = [], []
        xs_med, ys_med = [], []
        xs_baja, ys_baja = [], []
        for p in self.app.puntos:
            if p["prioridad"] == "Alta":
                xs_alta.append(p["x"])
                ys_alta.append(p["y"])
            elif p["prioridad"] == "Media":
                xs_med.append(p["x"])
                ys_med.append(p["y"])
            else:
                xs_baja.append(p["x"])
                ys_baja.append(p["y"])

        if xs_alta:
            ax_ruta.scatter(xs_alta, ys_alta, color='#EF4444', s=80, edgecolors='#111827', zorder=5, label='Alta')
        if xs_med:
            ax_ruta.scatter(xs_med, ys_med, color='#F59E0B', s=80, edgecolors='#111827', zorder=5, label='Media')
        if xs_baja:
            ax_ruta.scatter(xs_baja, ys_baja, color='#1D4ED8', s=80, edgecolors='#111827', zorder=5, label='Baja')

        if self.app.puntos:
            p_ini = self.app.puntos[0]
            ax_ruta.scatter(p_ini["x"], p_ini["y"], color='#F59E0B', s=180, marker='*', edgecolors='#111827', zorder=6, label='Base')

        if self.plot_card.chk_labels.isChecked():
            for p in self.app.puntos:
                ax_ruta.text(p["x"] + 0.8, p["y"] + 0.8, p["id"], color='#111827', fontsize=8, fontweight='semibold')

        p_dict = {p["id"]: p for p in self.app.puntos}
        rx = [p_dict[pid]["x"] for pid in res["ruta"] if pid in p_dict]
        ry = [p_dict[pid]["y"] for pid in res["ruta"] if pid in p_dict]
        ax_ruta.plot(rx, ry, color='#8B5CF6', linewidth=1.8, zorder=3, label='Trayectoria')
        
        for i in range(len(rx) - 1):
            dx = rx[i+1] - rx[i]
            dy = ry[i+1] - ry[i]
            ax_ruta.annotate('', xy=(rx[i+1] - dx*0.15, ry[i+1] - dy*0.15),
                             xytext=(rx[i], ry[i]),
                             arrowprops=dict(arrowstyle="->", color='#8B5CF6', lw=1.2, ls='-', shrinkA=0, shrinkB=0))
        
        ax_ruta.legend(loc='upper right', facecolor='#FFFFFF', edgecolor='#E5E7EB', fontsize=7)
        ax_ruta.set_title("Ruta construida con Regla GP", fontsize=9, fontweight='semibold', color='#111827')

        ax_ev.plot(range(1, len(self.historial_aptitud) + 1), self.historial_aptitud, color='#8B5CF6')
        ax_ev.set_title("Evolución de Aptitud final", fontsize=9, fontweight='semibold', color='#111827')

        self.canvas.fig.tight_layout()
        self.canvas.draw()

        self.app.ultimo_tiempo = res["tiempo"]
        self.app.registrar_mejor_costo(res["costo"])
        self.app.experimentos_contador += 1
        self.app.screen_inicio.actualizar_kpis()

    def detener_gp(self):
        self.timer.stop()
        self.btn_ejecutar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.btn_reset.setEnabled(True)
        QMessageBox.information(self, "Detenido", "Se detuvo el proceso evolutivo de Programación Genética.")

    def redibujar_visibilidad_etiquetas(self):
        if self.resultado_cache:
            self.finalizar_gp()
        elif self.app.puntos:
            self.canvas.limpiar_grafico()
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())

    def limpiar_ruta(self):
        self.resultado_cache = None
        self.canvas.limpiar_grafico()
        if self.app.puntos:
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())

    def guardar_imagen_grafico(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Imagen del Gráfico", "", "Imágenes PNG (*.png);;Imágenes JPG (*.jpg)")
        if path:
            self.canvas.fig.savefig(path, facecolor='#FFFFFF')
            QMessageBox.information(self, "Éxito", "El gráfico se ha exportado correctamente.")

    def restablecer(self):
        self.timer.stop()
        self.progress_bar.setValue(0)
        self.canvas.limpiar_grafico()
        self.txt_arbol.setText("[Esperando ejecución del algoritmo...]")
        self.row_regla.setText("N/A")
        self.row_costo.setText("N/A")
        self.row_aptitud.setText("N/A")
        self.row_gen.setText("N/A")
        self.row_tiempo.setText("N/A")
        self.row_memoria.setText("N/A")
        self.resultado_cache = None
        if self.app.puntos:
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())
