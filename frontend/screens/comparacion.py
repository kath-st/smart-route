# -*- coding: utf-8 -*-
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QFrame, QTableWidgetItem
from frontend.components import PageHeader, PlotCard, StyledTable, CanvasGrafico
from backend.algorithms import (
    ejecutar_vecino_mas_cercano,
    ejecutar_colonia_hormigas,
    ejecutar_programacion_genetica
)

class ScreenComparacion(QWidget):
    """Módulo Comparativo de Métricas de Algoritmos."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Módulo comparativo de algoritmos",
            "Análisis comparativo de algoritmos para la optimización de rutas y tiempos de ejecución."
        )
        layout.addWidget(self.header)

        # Panel central
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Sección Única: Optimización de rutas
        seccion_a_card = QFrame()
        seccion_a_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }")
        v_a = QVBoxLayout(seccion_a_card)
        v_a.setContentsMargins(16, 16, 16, 16)
        v_a.setSpacing(12)

        lbl_sec_a = QLabel("Optimización de rutas (TSP)")
        lbl_sec_a.setStyleSheet("font-size: 15px; font-weight: bold; color: #1D4ED8;")
        v_a.addWidget(lbl_sec_a)

        # Filtros de exclusión
        filter_h = QHBoxLayout()
        self.chk_vecino = QCheckBox("Vecino más cercano")
        self.chk_vecino.setChecked(True)
        self.chk_vecino.stateChanged.connect(self.actualizar_comparativa_completa)
        self.chk_aco = QCheckBox("Colonia de hormigas")
        self.chk_aco.setChecked(True)
        self.chk_aco.stateChanged.connect(self.actualizar_comparativa_completa)
        self.chk_gp = QCheckBox("Programación genética")
        self.chk_gp.setChecked(True)
        self.chk_gp.stateChanged.connect(self.actualizar_comparativa_completa)

        filter_h.addWidget(self.chk_vecino)
        filter_h.addWidget(self.chk_aco)
        filter_h.addWidget(self.chk_gp)
        filter_h.addStretch() # Empuja los botones hacia la izquierda para mayor orden visual
        v_a.addLayout(filter_h)

        # Tabla comparativa
        self.table_rutas = StyledTable()
        self.table_rutas.setColumnCount(9)
        self.table_rutas.setHorizontalHeaderLabels([
            "Algoritmo", "Costo Total", "T. Ejecución", "Memoria", 
            "Calidad", "Iter/Gen", "Entrada", "Compl. Temp.", "Compl. Espac."
        ])
        v_a.addWidget(self.table_rutas)

        # Gráfico comparativo tri-partito
        self.canvas_a = CanvasGrafico(self)
        self.plot_a_card = PlotCard(self.canvas_a, has_controls=False)
        v_a.addWidget(self.plot_a_card, 1)

        # Agregamos la tarjeta principal al layout sin límite de proporción para que ocupe el 100%
        h_layout.addWidget(seccion_a_card)

        layout.addLayout(h_layout)

    def actualizar_comparativa_completa(self):
        n_puntos = len(self.app.puntos)
        if n_puntos == 0:
            return  # Evitar fallos si no hay datos cargados en la aplicación
            
        filas_comparar = []
        id_inicio = self.app.puntos[0]["id"]

        # --- EJECUCIÓN REAL DE RUTAS ---
        
        # 1. Calculamos un costo base rápido usando el Vecino Más Cercano 
        # para tener una referencia segura.
        res_v = ejecutar_vecino_mas_cercano(self.app.puntos, id_inicio, 'Solo distancia física', True)
        costo_base = res_v.get("costo", res_v.get("distancia", 0.0))

        if self.chk_vecino.isChecked():
            filas_comparar.append(("Vecino más cercano", costo_base, res_v.get("tiempo", 0.0), f"{res_v.get('memoria', 0.0):.2f} MB", "Básica (Voraz)", "1", str(n_puntos), "O(n²)", "O(n²)"))

        if self.chk_aco.isChecked():
            res_aco = ejecutar_colonia_hormigas(self.app.puntos, min(n_puntos, 30), 50, 1.0, 2.0, 0.1, 100.0, 1.0, id_inicio, True)
            filas_comparar.append(("Colonia de hormigas", res_aco.get("costo", 0.0), res_aco.get("tiempo", 0.0), f"{res_aco.get('memoria', 0.0):.2f} MB", "Excelente", "50", str(n_puntos), "O(I*m*n²)", "O(n²+mn)"))

        if self.chk_gp.isChecked():
            res_gp = ejecutar_programacion_genetica(
                puntos=self.app.puntos,
                pop_size=100,
                generaciones=50,
                crossover_t=0.85,
                mutacion_t=0.10,
                max_depth=5,
                torneo_size=4,
                peso_pri=1.5
            )
            filas_comparar.append((
                "Programación genética",
                res_gp.get("costo", 0.0),
                res_gp.get("tiempo", 0.0),
                f"{res_gp.get('memoria', 0.0):.2f} MB",
                "Óptima (Evolutiva)",
                "50",
                str(n_puntos),
                "O(Gen*N*n)",
                "O(n²+N*n)"
            ))
            
        self.table_rutas.setRowCount(0)
        costos_lista = []
        for i, row in enumerate(filas_comparar):
            self.table_rutas.insertRow(i)
            self.table_rutas.setItem(i, 0, QTableWidgetItem(row[0]))
            self.table_rutas.setItem(i, 1, QTableWidgetItem(f"{row[1]:.2f}"))
            self.table_rutas.setItem(i, 2, QTableWidgetItem(f"{row[2]:.4f} s"))
            self.table_rutas.setItem(i, 3, QTableWidgetItem(row[3]))
            self.table_rutas.setItem(i, 4, QTableWidgetItem(row[4]))
            self.table_rutas.setItem(i, 5, QTableWidgetItem(row[5]))
            self.table_rutas.setItem(i, 6, QTableWidgetItem(row[6]))
            self.table_rutas.setItem(i, 7, QTableWidgetItem(row[7]))
            self.table_rutas.setItem(i, 8, QTableWidgetItem(row[8]))
            costos_lista.append(row[1])

        # Destacar el algoritmo con menor costo de ruta
        if costos_lista:
            min_cost_idx = costos_lista.index(min(costos_lista))
            for col in range(9):
                self.table_rutas.item(min_cost_idx, col).setBackground(QColor("#DCFCE7"))
                self.table_rutas.item(min_cost_idx, col).setForeground(QColor("#15803D"))

        self.table_rutas.ajustar_contenido()

        # Dibujar gráfico triple
        self.canvas_a.limpiar_grafico()
        self.canvas_a.fig.clf()

        if filas_comparar:
            ax_cost = self.canvas_a.fig.add_subplot(131)
            ax_time = self.canvas_a.fig.add_subplot(132)
            ax_mem = self.canvas_a.fig.add_subplot(133)
            
            ax_cost.set_facecolor('#F5F7FA')
            ax_time.set_facecolor('#F5F7FA')
            ax_mem.set_facecolor('#F5F7FA')
            
            ax_cost.tick_params(colors='#111827', labelsize=8)
            ax_time.tick_params(colors='#111827', labelsize=8)
            ax_mem.tick_params(colors='#111827', labelsize=8)

            nombres = [r[0].replace(" ", "\n") for r in filas_comparar]
            costos = [r[1] for r in filas_comparar]
            tiempos = [r[2] for r in filas_comparar]
            memorias = [float(r[3].split(" ")[0]) for r in filas_comparar]

            ax_cost.bar(nombres, costos, color='#1D4ED8', edgecolor='#E5E7EB', width=0.5)
            ax_cost.set_title("Costo de Ruta", fontsize=9, fontweight='semibold', color='#111827')
            
            ax_time.bar(nombres, tiempos, color='#22C55E', edgecolor='#E5E7EB', width=0.5)
            ax_time.set_title("Tiempo (s)", fontsize=9, fontweight='semibold', color='#111827')
            
            ax_mem.bar(nombres, memorias, color='#8B5CF6', edgecolor='#E5E7EB', width=0.5)
            ax_mem.set_title("Memoria (MB)", fontsize=9, fontweight='semibold', color='#111827')

            self.canvas_a.fig.tight_layout()
        self.canvas_a.draw()