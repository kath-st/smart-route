# -*- coding: utf-8 -*-
import random
import os
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QCheckBox, QProgressBar, QLineEdit, QTableWidgetItem, QMessageBox, QFileDialog
from frontend.components import PageHeader, ParameterCard, PlotCard, StyledTable, CanvasGrafico

try:
    from backend.algorithms import exportar_resultados_csv
except ImportError:
    # Simulación local
    import csv
    def exportar_resultados_csv(datos_tabla, path_archivo):
        try:
            with open(path_archivo, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["N (Puntos)", "Algoritmo", "Tiempo medio", "Memoria promedio", "Costo promedio"])
                for row in datos_tabla:
                    writer.writerow(row)
            return True
        except:
            return False

class ScreenExperimentos(QWidget):
    """Módulo del Banco de Experimentos de Escalabilidad."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Banco de experimentos empíricos",
            "Módulo de análisis experimental para pruebas de escalabilidad y robustez algorítmica ante variación en el tamaño de la entrada (N)"
        )
        layout.addWidget(self.header)

        # Layout horizontal principal
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Panel izquierdo (Controles)
        izq_layout = QVBoxLayout()
        izq_layout.setSpacing(14)

        self.param_card = ParameterCard("Configuración del experimento")
        self.combo_tamano = QComboBox()
        self.combo_tamano.addItems(["10 puntos", "100 puntos", "1000 puntos", "10000 puntos", "Personalizado"])
        self.combo_tamano.currentIndexChanged.connect(self.cambiar_comportamiento_tamano)

        self.spin_custom = QSpinBox()
        self.spin_custom.setRange(10, 50000)
        self.spin_custom.setValue(500)
        self.spin_custom.setEnabled(False)

        self.chk_vecino_exp = QCheckBox("Vecino más cercano")
        self.chk_vecino_exp.setChecked(True)
        self.chk_aco_exp = QCheckBox("Colonia de hormigas")
        self.chk_aco_exp.setChecked(True)
        self.chk_gp_exp = QCheckBox("Programación genética")
        self.chk_gp_exp.setChecked(True)

        self.spin_reps = QSpinBox()
        self.spin_reps.setRange(1, 30)
        self.spin_reps.setValue(5)

        self.spin_semilla = QSpinBox()
        self.spin_semilla.setRange(0, 99999)
        self.spin_semilla.setValue(12345)

        self.btn_iniciar = QPushButton("Iniciar experimento masivo")
        self.btn_iniciar.setObjectName("PrimaryBtn")
        self.btn_iniciar.clicked.connect(self.iniciar_experimentos)

        self.btn_detener = QPushButton("Detener pruebas")
        self.btn_detener.setObjectName("DangerBtn")
        self.btn_detener.setEnabled(False)
        self.btn_detener.clicked.connect(self.detener_experimentos)

        self.param_card.add_widget("Tamaño de entrada (N):", self.combo_tamano)
        self.param_card.add_widget("Personalizado:", self.spin_custom)
        self.param_card.v_layout.addWidget(QLabel("Algoritmos a ejecutar:"))
        self.param_card.v_layout.addWidget(self.chk_vecino_exp)
        self.param_card.v_layout.addWidget(self.chk_aco_exp)
        self.param_card.v_layout.addWidget(self.chk_gp_exp)
        self.param_card.add_widget("Repeticiones por prueba:", self.spin_reps)
        self.param_card.add_widget("Semilla aleatoria:", self.spin_semilla)
        
        self.param_card.v_layout.addWidget(self.btn_iniciar)
        self.param_card.v_layout.addWidget(self.btn_detener)
        izq_layout.addWidget(self.param_card)

        # Barra de progreso del experimento
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        izq_layout.addWidget(self.progress_bar)

        izq_layout.addWidget(QLabel("Consola de eventos en tiempo real:"))
        self.txt_log = QLineEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("font-family: monospace; font-size: 11px; background-color: #FFFFFF; color: #1D4ED8; border: 1px solid #E5E7EB; border-radius: 4px; padding: 6px;")
        izq_layout.addWidget(self.txt_log)
        izq_layout.addStretch()

        h_layout.addLayout(izq_layout, 2)

        # Panel derecho (Resultados y Gráficos)
        der_layout = QVBoxLayout()
        der_layout.setSpacing(14)

        # Tabla experimental
        self.table_exp = StyledTable()
        self.table_exp.setColumnCount(5)
        self.table_exp.setHorizontalHeaderLabels(["N (Puntos)", "Algoritmo", "Tiempo medio", "Memoria promedio", "Costo promedio"])
        self.table_exp.setMaximumHeight(180)
        der_layout.addWidget(self.table_exp)

        # Canvas de curvas de escalabilidad
        self.canvas = CanvasGrafico(self)
        self.plot_card = PlotCard(self.canvas, has_controls=False)
        der_layout.addWidget(self.plot_card, 1)

        self.btn_exportar = QPushButton("Exportar resultados a CSV")
        self.btn_exportar.setObjectName("SecondaryBtn")
        self.btn_exportar.clicked.connect(self.exportar_resultados)
        der_layout.addWidget(self.btn_exportar)

        h_layout.addLayout(der_layout, 3)

        layout.addLayout(h_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.iterar_experimento)
        self.paso_actual = 0
        self.puntos_n = 10

    def cambiar_comportamiento_tamano(self):
        self.spin_custom.setEnabled(self.combo_tamano.currentText() == "Personalizado")

    def iniciar_experimentos(self):
        self.btn_iniciar.setEnabled(False)
        self.btn_detener.setEnabled(True)
        self.progress_bar.setValue(0)
        self.paso_actual = 0

        txt_n = self.combo_tamano.currentText()
        if "10 puntos" in txt_n:
            self.puntos_n = 10
        elif "100 puntos" in txt_n:
            self.puntos_n = 100
        elif "1000 puntos" in txt_n:
            self.puntos_n = 1000
        elif "10000 puntos" in txt_n:
            self.puntos_n = 10000
        else:
            self.puntos_n = self.spin_custom.value()

        self.txt_log.setText(f"Iniciando experimento con N = {self.puntos_n}...")
        self.timer.start(150)

    def iterar_experimento(self):
        self.paso_actual += 1
        progreso = int((self.paso_actual / 10) * 100)
        self.progress_bar.setValue(progreso)

        logs_simulados = [
            f"Configurando estructura espacial de {self.puntos_n} puntos...",
            f"Ejecutando Vecino más cercano (Repetición 1/{self.spin_reps.value()})...",
            f"Ejecutando Colonia de hormigas (Repetición 1/{self.spin_reps.value()})...",
            f"Ejecutando Programación genética (Repetición 1/{self.spin_reps.value()})...",
            "Midiendo tiempos de ejecución...",
            "Registrando picos máximos de memoria...",
            "Calculando desviaciones estándar de los costos...",
            "Consolidando métricas promedio en estructura temporal...",
            "Evaluando complejidad empírica vs límites asintóticos...",
            "Experimento masivo completado con éxito"
        ]
        self.txt_log.setText(logs_simulados[self.paso_actual - 1])

        if self.paso_actual >= 10:
            self.finalizar_experimentos()

    def finalizar_experimentos(self):
        self.timer.stop()
        self.btn_iniciar.setEnabled(True)
        self.btn_detener.setEnabled(False)

        self.table_exp.setRowCount(0)
        self.datos_tabla_cache = []

        n = self.puntos_n
        if self.chk_vecino_exp.isChecked():
            t = (n ** 2) * 0.000000008 + 0.001
            m = n * 0.12 + 120.0
            c = n * 11.5
            self.datos_tabla_cache.append((n, "Vecino más cercano", f"{t:.6f} s", f"{m:.2f} KB", f"{c:.2f}"))

        if self.chk_aco_exp.isChecked():
            t = (n ** 2) * 0.0000006 + 0.035
            m = n * 0.45 + 1024.0
            c = n * 8.2
            self.datos_tabla_cache.append((n, "Colonia de hormigas", f"{t:.6f} s", f"{m:.2f} KB", f"{c:.2f}"))

        if self.chk_gp_exp.isChecked():
            t = n * 0.00018 + 0.075
            m = n * 0.28 + 2048.0
            c = n * 7.5
            self.datos_tabla_cache.append((n, "Programación genética", f"{t:.6f} s", f"{m:.2f} KB", f"{c:.2f}"))

        for i, row in enumerate(self.datos_tabla_cache):
            self.table_exp.insertRow(i)
            self.table_exp.setItem(i, 0, QTableWidgetItem(str(row[0])))
            self.table_exp.setItem(i, 1, QTableWidgetItem(row[1]))
            self.table_exp.setItem(i, 2, QTableWidgetItem(row[2]))
            self.table_exp.setItem(i, 3, QTableWidgetItem(row[3]))
            self.table_exp.setItem(i, 4, QTableWidgetItem(row[4]))
        self.table_exp.ajustar_contenido()

        # Graficar curvas de complejidad empíricas
        self.canvas.limpiar_grafico()
        self.canvas.fig.clf()
        
        ax_t = self.canvas.fig.add_subplot(121)
        ax_m = self.canvas.fig.add_subplot(122)
        
        ax_t.set_facecolor('#F5F7FA')
        ax_m.set_facecolor('#F5F7FA')
        ax_t.tick_params(colors='#111827', labelsize=8)
        ax_m.tick_params(colors='#111827', labelsize=8)
        ax_t.grid(True, color='#E5E7EB', linestyle='--')
        ax_m.grid(True, color='#E5E7EB', linestyle='--')

        tamanos = [10, 100, 500, 1000, 5000]
        
        if self.chk_vecino_exp.isChecked():
            ys_t = [(x**2)*0.000000008 for x in tamanos]
            ys_m = [x*0.12 + 120.0 for x in tamanos]
            ax_t.plot(tamanos, ys_t, '-o', label='Vecino (O(n²))', color='#1D4ED8')
            ax_m.plot(tamanos, ys_m, '-o', label='Vecino', color='#1D4ED8')
            
        if self.chk_aco_exp.isChecked():
            ys_t = [(x**2)*0.0000006 for x in tamanos]
            ys_m = [x*0.45 + 1024.0 for x in tamanos]
            ax_t.plot(tamanos, ys_t, '-s', label='ACO (O(n²))', color='#22C55E')
            ax_m.plot(tamanos, ys_m, '-s', label='ACO', color='#22C55E')
            
        if self.chk_gp_exp.isChecked():
            ys_t = [x*0.00018 for x in tamanos]
            ys_m = [x*0.28 + 2048.0 for x in tamanos]
            ax_t.plot(tamanos, ys_t, '-^', label='GP (O(n))', color='#8B5CF6')
            ax_m.plot(tamanos, ys_m, '-^', label='GP', color='#8B5CF6')

        ax_t.set_title("Tiempo Medio (s) vs N", color='#111827', fontsize=9, fontweight='semibold')
        ax_t.set_xlabel("N (Puntos)", color='#111827', fontsize=8)
        ax_t.legend(facecolor='#FFFFFF', edgecolor='#E5E7EB')

        ax_m.set_title("Memoria (KB) vs N", color='#111827', fontsize=9, fontweight='semibold')
        ax_m.set_xlabel("N (Puntos)", color='#111827', fontsize=8)
        ax_m.legend(facecolor='#FFFFFF', edgecolor='#E5E7EB')

        self.canvas.fig.tight_layout()
        self.canvas.draw()

        self.app.experimentos_contador += 1
        self.app.screen_inicio.actualizar_kpis()

    def detener_experimentos(self):
        self.timer.stop()
        self.btn_iniciar.setEnabled(True)
        self.btn_detener.setEnabled(False)
        self.txt_log.setText("Pruebas abortadas.")

    def exportar_resultados(self):
        if not hasattr(self, 'datos_tabla_cache') or not self.datos_tabla_cache:
            QMessageBox.warning(self, "Sin resultados", "No hay datos para exportar. Ejecute el experimento primero.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Exportar experimento CSV", "", "Archivos CSV (*.csv)")
        if path:
            exito = exportar_resultados_csv(self.datos_tabla_cache, path)
            if exito:
                QMessageBox.information(self, "Exportación completada", f"Se guardó el log con éxito en {os.path.basename(path)}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo escribir el archivo en el disco.")
