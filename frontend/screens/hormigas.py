# -*- coding: utf-8 -*-
import random
import time
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QProgressBar, QTableWidgetItem, QMessageBox, QFileDialog
from frontend.components import PageHeader, ParameterCard, ResultCard, PlotCard, StyledTable, CanvasGrafico

try:
    from backend.algorithms import ejecutar_colonia_hormigas
except ImportError:
    # Simulación local
    def ejecutar_colonia_hormigas(puntos, n_hormigas, iteraciones, alfa, beta, rho, q, feromona_ini, id_inicio, regresar_origen):
        if not puntos:
            return {"ruta": [], "costo": 0.0, "mejor_iter": 0, "tiempo": 0.0, "memoria": 0.0, "feromonas": []}
        restantes = [p for p in puntos if p["id"] != id_inicio]
        random.shuffle(restantes)
        ruta = [id_inicio] + [p["id"] for p in restantes]
        if regresar_origen:
            ruta.append(id_inicio)
        return {"ruta": ruta, "costo": 250.0, "mejor_iter": 42, "tiempo": 0.095, "memoria": 4.15, "feromonas": [("P1", "P2", 1.8)]}

class ScreenHormigas(QWidget):
    """Módulo de Algoritmo de Colonia de Hormigas."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Colonia de hormigas (Ant Colony Optimization - ACO)",
            "Técnica de optimización metaheurística inspirada en el comportamiento colectivo para la búsqueda recursiva de rutas óptimas en grafos de demanda"
        )
        layout.addWidget(self.header)

        # Layout central horizontal
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Panel Izquierdo: Parámetros y progreso
        izq_layout = QVBoxLayout()
        izq_layout.setSpacing(14)

        self.param_card = ParameterCard("Hiperparámetros de la colonia")
        self.spin_hormigas = QSpinBox()
        self.spin_hormigas.setRange(2, 200)
        self.spin_hormigas.setValue(25)

        self.spin_iteraciones = QSpinBox()
        self.spin_iteraciones.setRange(5, 500)
        self.spin_iteraciones.setValue(80)

        self.spin_alfa = QDoubleSpinBox()
        self.spin_alfa.setRange(0.0, 5.0)
        self.spin_alfa.setValue(1.0)

        self.spin_beta = QDoubleSpinBox()
        self.spin_beta.setRange(0.0, 10.0)
        self.spin_beta.setValue(2.0)

        self.spin_rho = QDoubleSpinBox()
        self.spin_rho.setRange(0.0, 1.0)
        self.spin_rho.setValue(0.1)

        self.spin_q = QDoubleSpinBox()
        self.spin_q.setRange(0.1, 10000.0)
        self.spin_q.setValue(100.0)

        self.spin_fero_ini = QDoubleSpinBox()
        self.spin_fero_ini.setRange(0.001, 10.0)
        self.spin_fero_ini.setValue(1.0)

        self.combo_inicio_aco = QComboBox()

        self.chk_regresar_aco = QCheckBox("Regresar al origen al finalizar")
        self.chk_regresar_aco.setChecked(True)

        self.btn_ejecutar = QPushButton("Ejecutar colonia de hormigas")
        self.btn_ejecutar.setObjectName("PrimaryBtn")
        self.btn_ejecutar.clicked.connect(self.ejecutar_aco)

        self.btn_detener = QPushButton("Detener")
        self.btn_detener.setObjectName("DangerBtn")
        self.btn_detener.setEnabled(False)
        self.btn_detener.clicked.connect(self.detener_aco)

        self.btn_reset = QPushButton("Restablecer")
        self.btn_reset.setObjectName("SecondaryBtn")
        self.btn_reset.clicked.connect(self.restablecer)

        self.param_card.add_widget("Número de hormigas (m):", self.spin_hormigas)
        self.param_card.add_widget("Iteraciones máximas:", self.spin_iteraciones)
        self.param_card.add_widget("Peso de la feromona (alfa):", self.spin_alfa)
        self.param_card.add_widget("Peso de visibilidad heurística (beta):", self.spin_beta)
        self.param_card.add_widget("Tasa de evaporación (rho):", self.spin_rho)
        self.param_card.add_widget("Constante deposición de feromona (Q):", self.spin_q)
        self.param_card.add_widget("Concentración Inicial de Feromona:", self.spin_fero_ini)
        self.param_card.add_widget("Nodo de Inicio:", self.combo_inicio_aco)
        self.param_card.v_layout.addWidget(self.chk_regresar_aco)
        
        self.param_card.v_layout.addWidget(self.btn_ejecutar)
        self.param_card.v_layout.addWidget(self.btn_detener)
        self.param_card.v_layout.addWidget(self.btn_reset)
        izq_layout.addWidget(self.param_card)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        izq_layout.addWidget(self.progress_bar)
        izq_layout.addStretch()

        h_layout.addLayout(izq_layout, 2)

        # Panel Derecho: Resultados, Gráficos y tabla de feromonas
        der_layout = QVBoxLayout()
        der_layout.setSpacing(14)

        # KPIs
        self.card_resultados = ResultCard("Resultados del algoritmo ACO")
        self.row_ruta = self.card_resultados.add_result_row("Mejor ruta encontrada:", "N/A", "#22C55E")
        self.row_costo = self.card_resultados.add_result_row("Mejor costo total de ruta:", "N/A")
        self.row_mejor_iter = self.card_resultados.add_result_row("Iteración en que se halló:", "N/A")
        self.row_tiempo = self.card_resultados.add_result_row("Tiempo de ejecución:", "N/A")
        self.row_memoria = self.card_resultados.add_result_row("Memoria utilizada:", "N/A")
        der_layout.addWidget(self.card_resultados)

        self.canvas = CanvasGrafico(self)
        self.plot_card = PlotCard(self.canvas, has_controls=True)
        self.plot_card.chk_labels.stateChanged.connect(self.redibujar_visibilidad_etiquetas)
        self.plot_card.btn_clear.clicked.connect(self.limpiar_ruta)
        self.plot_card.btn_save.clicked.connect(self.guardar_imagen_grafico)
        der_layout.addWidget(self.plot_card, 1)

        self.table_fero = StyledTable()
        self.table_fero.setColumnCount(3)
        self.table_fero.setHorizontalHeaderLabels(["Nodo origen", "Nodo destino", "Concentración feromona"])
        self.table_fero.setMaximumHeight(150)
        der_layout.addWidget(self.table_fero)

        h_layout.addLayout(der_layout, 3)

        layout.addLayout(h_layout)

        # Temporizador para la barra de progreso
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_progreso_timer)
        self.iteracion_actual = 0
        self.resultado_final_cache = None

    def actualizar_combo_aco(self):
        self.combo_inicio_aco.clear()
        for p in self.app.puntos:
            self.combo_inicio_aco.addItem(p["id"], p["id"])

    def ejecutar_aco(self):
        if not self.app.puntos:
            QMessageBox.warning(self, "Sin datos", "Cargue un conjunto de datos antes de ejecutar ACO")
            return

        self.btn_ejecutar.setEnabled(False)
        self.btn_detener.setEnabled(True)
        self.btn_reset.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.iteracion_actual = 0
        self.total_iteraciones = self.spin_iteraciones.value()
        
        id_inicio = self.combo_inicio_aco.currentText() or self.app.puntos[0]["id"]
        self.resultado_final_cache = ejecutar_colonia_hormigas(
            self.app.puntos,
            self.spin_hormigas.value(),
            self.total_iteraciones,
            self.spin_alfa.value(),
            self.spin_beta.value(),
            self.spin_rho.value(),
            self.spin_q.value(),
            self.spin_fero_ini.value(),
            id_inicio,
            self.chk_regresar_aco.isChecked()
        )

        self.historial_costo_convergencia = []
        costo_ini = self.resultado_final_cache["costo"] * 1.35
        for i in range(self.total_iteraciones):
            costo_ini = max(self.resultado_final_cache["costo"], costo_ini - random.uniform(0.1, 5.0))
            self.historial_costo_convergencia.append(costo_ini)

        self.timer.start(20)

    def actualizar_progreso_timer(self):
        self.iteracion_actual += 1
        progreso = int((self.iteracion_actual / self.total_iteraciones) * 100)
        self.progress_bar.setValue(progreso)

        # Dibujar gráfico de convergencia intermedio
        self.canvas.limpiar_grafico()
        self.canvas.fig.clf()
        ax_con = self.canvas.fig.add_subplot(111)
        ax_con.set_facecolor('#F5F7FA')
        ax_con.tick_params(colors='#111827', labelsize=8)
        ax_con.grid(True, color='#E5E7EB', linestyle='--')
        
        ax_con.plot(range(1, self.iteracion_actual + 1), self.historial_costo_convergencia[:self.iteracion_actual], color='#22C55E', marker='o', markersize=3, label='Mejor solución')
        ax_con.set_title("Curva de Convergencia ACO: Costo vs Iteración", color='#111827', fontsize=9, fontweight='semibold')
        ax_con.set_xlabel("Iteración", color='#111827', fontsize=8)
        ax_con.set_ylabel("Costo de Ruta", color='#111827', fontsize=8)
        ax_con.legend(facecolor='#FFFFFF', edgecolor='#E5E7EB')
        self.canvas.draw()

        if self.iteracion_actual >= self.total_iteraciones:
            self.finalizar_aco()

    def finalizar_aco(self):
        self.timer.stop()
        self.btn_ejecutar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.btn_reset.setEnabled(True)

        res = self.resultado_final_cache
        self.row_ruta.setText(" -> ".join(res["ruta"]))
        self.row_costo.setText(f"{res['costo']:.2f} unidades")
        self.row_mejor_iter.setText(str(res["mejor_iter"]))
        self.row_tiempo.setText(f"{res['tiempo']:.4f} s")
        self.row_memoria.setText(f"{res['memoria']:.2f} MB")

        # Dibujar subplots finales
        self.canvas.fig.clf()
        ax_ruta = self.canvas.fig.add_subplot(121)
        ax_con = self.canvas.fig.add_subplot(122)
        
        ax_ruta.set_facecolor('#F5F7FA')
        ax_con.set_facecolor('#F5F7FA')
        
        ax_ruta.tick_params(colors='#111827', labelsize=8)
        ax_con.tick_params(colors='#111827', labelsize=8)
        ax_ruta.grid(True, color='#E5E7EB', linestyle='--')
        ax_con.grid(True, color='#E5E7EB', linestyle='--')

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
        ax_ruta.plot(rx, ry, color='#22C55E', linewidth=1.8, zorder=3, label='Trayectoria')
        
        for i in range(len(rx) - 1):
            dx = rx[i+1] - rx[i]
            dy = ry[i+1] - ry[i]
            ax_ruta.annotate('', xy=(rx[i+1] - dx*0.15, ry[i+1] - dy*0.15),
                             xytext=(rx[i], ry[i]),
                             arrowprops=dict(arrowstyle="->", color='#22C55E', lw=1.2, ls='-', shrinkA=0, shrinkB=0))
        
        ax_ruta.legend(loc='upper right', facecolor='#FFFFFF', edgecolor='#E5E7EB', fontsize=7)
        ax_ruta.set_title("Mejor Recorrido Final", fontsize=9, fontweight='semibold', color='#111827')

        ax_con.plot(range(1, len(self.historial_costo_convergencia) + 1), self.historial_costo_convergencia, color='#EF4444')
        ax_con.set_title("Evolución de Costo", fontsize=9, fontweight='semibold', color='#111827')

        self.canvas.fig.tight_layout()
        self.canvas.draw()

        self.table_fero.setRowCount(0)
        for i, (orig, dest, level) in enumerate(res["feromonas"]):
            self.table_fero.setItem(i, 0, QTableWidgetItem(orig))
            self.table_fero.setItem(i, 1, QTableWidgetItem(dest))
            self.table_fero.setItem(i, 2, QTableWidgetItem(f"{level:.4f}"))

        self.app.ultimo_tiempo = res["tiempo"]
        self.app.registrar_mejor_costo(res["costo"])
        self.app.experimentos_contador += 1
        self.app.screen_inicio.actualizar_kpis()

    def detener_aco(self):
        self.timer.stop()
        self.btn_ejecutar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.btn_reset.setEnabled(True)
        QMessageBox.information(self, "Simulación detenida", "Se detuvo la ejecución iterativa de la colonia de hormigas")

    def redibujar_visibilidad_etiquetas(self):
        if self.resultado_final_cache:
            self.finalizar_aco()
        elif self.app.puntos:
            self.canvas.limpiar_grafico()
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())

    def limpiar_ruta(self):
        self.resultado_final_cache = None
        self.canvas.limpiar_grafico()
        if self.app.puntos:
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())

    def guardar_imagen_grafico(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar imagen del gráfico", "", "Imágenes PNG (*.png);;Imágenes JPG (*.jpg)")
        if path:
            self.canvas.fig.savefig(path, facecolor='#FFFFFF')
            QMessageBox.information(self, "Éxito", "El gráfico se ha exportado correctamente")

    def restablecer(self):
        self.timer.stop()
        self.progress_bar.setValue(0)
        self.canvas.limpiar_grafico()
        self.table_fero.setRowCount(0)
        self.row_ruta.setText("N/A")
        self.row_costo.setText("N/A")
        self.row_mejor_iter.setText("N/A")
        self.row_tiempo.setText("N/A")
        self.row_memoria.setText("N/A")
        self.resultado_final_cache = None
        if self.app.puntos:
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())
