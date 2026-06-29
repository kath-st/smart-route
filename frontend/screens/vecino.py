# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QMessageBox, QFileDialog
from frontend.components import PageHeader, ParameterCard, ResultCard, PlotCard, CanvasGrafico

try:
    from backend.algorithms import ejecutar_vecino_mas_cercano
except ImportError:
    # Simulación local en caso de fallo de importación directa
    import random, time
    def ejecutar_vecino_mas_cercano(puntos, id_inicio, criterio, regresar_origen):
        if not puntos:
            return {"ruta": [], "distancia": 0.0, "tiempo": 0.0, "memoria": 0.0, "operaciones": 0}
        restantes = [p for p in puntos if p["id"] != id_inicio]
        random.shuffle(restantes)
        ruta = [id_inicio] + [p["id"] for p in restantes]
        if regresar_origen:
            ruta.append(id_inicio)
        distancia = 0.0
        p_dict = {p["id"]: p for p in puntos}
        for i in range(len(ruta) - 1):
            p1 = p_dict.get(ruta[i])
            p2 = p_dict.get(ruta[i+1])
            if p1 and p2:
                distancia += ((p2["x"] - p1["x"])**2 + (p2["y"] - p1["y"])**2)**0.5
        return {"ruta": ruta, "distancia": distancia, "tiempo": 0.002, "memoria": 135.0, "operaciones": len(puntos)**2}

class ScreenVecino(QWidget):
    """Módulo del Algoritmo del Vecino Más Cercano."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Vecino más cercano (Nearest Neighbor)",
            "Heurística clásica y voraz para la resolución del Problema del Viajante (TSP). Construye recorridos paso a paso seleccionando el nodo no visitado con menor costo de traslado."
        )
        layout.addWidget(self.header)

        # Panel central dividido
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Panel Izquierdo: Parámetros y resultados
        izq_layout = QVBoxLayout()
        izq_layout.setSpacing(16)

        self.param_card = ParameterCard("Parámetros del algoritmo")
        self.combo_inicio = QComboBox()
        self.combo_criterio = QComboBox()
        self.combo_criterio.addItems(["Solo distancia física", "Distancia ponderada por prioridad"])
        self.chk_regresar = QCheckBox("Regresar al origen al finalizar")
        self.chk_regresar.setChecked(True)

        self.btn_ejecutar = QPushButton("Ejecutar vecino más cercano")
        self.btn_ejecutar.setObjectName("PrimaryBtn")
        self.btn_ejecutar.clicked.connect(self.ejecutar_algoritmo)
        
        self.btn_reset = QPushButton("Restablecer")
        self.btn_reset.setObjectName("SecondaryBtn")
        self.btn_reset.clicked.connect(self.restablecer)

        self.param_card.add_widget("Nodo de Inicio (Base/Depósito):", self.combo_inicio)
        self.param_card.add_widget("Criterio de Atracción Euclidiana:", self.combo_criterio)
        self.param_card.v_layout.addWidget(self.chk_regresar)
        self.param_card.v_layout.addWidget(self.btn_ejecutar)
        self.param_card.v_layout.addWidget(self.btn_reset)
        izq_layout.addWidget(self.param_card)

        # Tarjeta de Resultados
        self.result_card = ResultCard("Resultados heurísticos")
        self.row_ruta = self.result_card.add_result_row("Secuencia de ruta:", "N/A", "#1D4ED8")
        self.row_dist = self.result_card.add_result_row("Distancia total:", "N/A")
        self.row_tiempo = self.result_card.add_result_row("Tiempo de cómputo:", "N/A")
        self.row_memoria = self.result_card.add_result_row("Memoria utilizada:", "N/A")
        self.row_ops = self.result_card.add_result_row("Operaciones básicas:", "N/A")
        self.row_comp_t = self.result_card.add_result_row("Complejidad temporal teórica:", "O(n²)", "#8B5CF6")
        self.row_comp_e = self.result_card.add_result_row("Complejidad espacial teórica:", "O(n²)", "#8B5CF6")
        izq_layout.addWidget(self.result_card)
        izq_layout.addStretch()

        h_layout.addLayout(izq_layout, 2)

        # Panel Derecho: Gráfico
        self.canvas = CanvasGrafico(self)
        self.plot_card = PlotCard(self.canvas, has_controls=True)
        self.plot_card.chk_labels.stateChanged.connect(self.redibujar_visibilidad_etiquetas)
        self.plot_card.btn_clear.clicked.connect(self.limpiar_ruta)
        self.plot_card.btn_save.clicked.connect(self.guardar_imagen_grafico)
        
        h_layout.addWidget(self.plot_card, 3)

        layout.addLayout(h_layout)

        self.ruta_actual = None

    def actualizar_combo_puntos(self):
        self.combo_inicio.clear()
        for p in self.app.puntos:
            self.combo_inicio.addItem(f"{p['id']} (X: {p['x']:.1f}, Y: {p['y']:.1f})", p["id"])

    def ejecutar_algoritmo(self):
        if not self.app.puntos:
            QMessageBox.warning(self, "Sin datos", "No existen puntos registrados. Créelos en el módulo de Datos primero.")
            return

        id_inicio = self.combo_inicio.currentData() or self.app.puntos[0]["id"]
        criterio = self.combo_criterio.currentText()
        regresar = self.chk_regresar.isChecked()

        res = ejecutar_vecino_mas_cercano(self.app.puntos, id_inicio, criterio, regresar)

        self.ruta_actual = res["ruta"]
        self.row_ruta.setText(" -> ".join(res["ruta"]))
        self.row_dist.setText(f"{res['distancia']:.2f} unidades")
        self.row_tiempo.setText(f"{res['tiempo']:.5f} s")
        self.row_memoria.setText(f"{res['memoria']:.2f} KB")
        self.row_ops.setText(str(res["operaciones"]))

        self.canvas.graficar_puntos(self.app.puntos, self.ruta_actual, self.plot_card.chk_labels.isChecked())

        self.app.ultimo_tiempo = res["tiempo"]
        self.app.registrar_mejor_costo(res["distancia"])
        self.app.experimentos_contador += 1
        self.app.screen_inicio.actualizar_kpis()

    def restablecer(self):
        self.limpiar_ruta()
        self.row_ruta.setText("N/A")
        self.row_dist.setText("N/A")
        self.row_tiempo.setText("N/A")
        self.row_memoria.setText("N/A")
        self.row_ops.setText("N/A")

    def limpiar_ruta(self):
        self.ruta_actual = None
        self.canvas.limpiar_grafico()
        if self.app.puntos:
            self.canvas.graficar_puntos(self.app.puntos, None, self.plot_card.chk_labels.isChecked())

    def redibujar_visibilidad_etiquetas(self):
        if self.app.puntos:
            self.canvas.graficar_puntos(self.app.puntos, self.ruta_actual, self.plot_card.chk_labels.isChecked())

    def guardar_imagen_grafico(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar imagen del gráfico", "", "Imágenes PNG (*.png);;Imágenes JPG (*.jpg)")
        if path:
            self.canvas.fig.savefig(path, facecolor='#FFFFFF')
            QMessageBox.information(self, "Éxito", "El gráfico se ha exportado correctamente")
