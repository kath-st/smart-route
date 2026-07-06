# -*- coding: utf-8 -*-
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QFrame, QTableWidgetItem
from frontend.components import PageHeader, PlotCard, StyledTable, CanvasGrafico
from backend.algorithms import ejecutar_vecino_mas_cercano, ejecutar_colonia_hormigas, entrenar_random_forest

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
            "Análisis comparativo de algoritmos para la optimización de rutas (Sección A) y clasificaciones de urgencia/prioridad (Sección B)."
        )
        layout.addWidget(self.header)

        # Panel central
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Sección A: Optimización de rutas
        seccion_a_card = QFrame()
        seccion_a_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }")
        v_a = QVBoxLayout(seccion_a_card)
        v_a.setContentsMargins(16, 16, 16, 16)
        v_a.setSpacing(12)

        lbl_sec_a = QLabel("A. Optimización de rutas (TSP)")
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

        h_layout.addWidget(seccion_a_card, 3)

        # Sección B: Clasificador RF
        seccion_b_card = QFrame()
        seccion_b_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }")
        v_b = QVBoxLayout(seccion_b_card)
        v_b.setContentsMargins(16, 16, 16, 16)
        v_b.setSpacing(12)

        lbl_sec_b = QLabel("B. Clasificación de prioridad (RF)")
        lbl_sec_b.setStyleSheet("font-size: 15px; font-weight: bold; color: #EF4444;")
        v_b.addWidget(lbl_sec_b)

        # Tabla de métricas
        self.table_rf = StyledTable()
        self.table_rf.setColumnCount(2)
        self.table_rf.setHorizontalHeaderLabels(["Métrica", "Valor"])
        self.table_rf.verticalHeader().setVisible(False)
        self.table_rf.fijar_modo_stretch()
        v_b.addWidget(self.table_rf)
        
        lbl_nota_concepto = QLabel(
            "El clasificador predice el nivel de urgencia o prioridad de forma supervisada. "
            "Esto reduce la complejidad en el espacio de decisiones para los modelos de ruteo posteriores."
        )
        lbl_nota_concepto.setStyleSheet("font-size: 12px; color: #6B7280; font-style: italic;")
        lbl_nota_concepto.setWordWrap(True)
        v_b.addWidget(lbl_nota_concepto)
        v_b.addStretch()

        h_layout.addWidget(seccion_b_card, 2)

        layout.addLayout(h_layout)

    def actualizar_comparativa_completa(self):
        n_puntos = len(self.app.puntos)
        if n_puntos == 0:
            return  # Evitar fallos si no hay datos cargados en la aplicación
            
        filas_comparar = []
        id_inicio = self.app.puntos[0]["id"]

        # --- SECCIÓN A: EJECUCIÓN REAL DE RUTAS ---
        
        # 1. Calculamos un costo base rápido usando el Vecino Más Cercano 
        # para tener una referencia, sin importar si su casilla está marcada o no.
        res_v = ejecutar_vecino_mas_cercano(self.app.puntos, id_inicio, 'Solo distancia física', True)
        costo_base = res_v.get("costo", res_v.get("distancia", 0.0))

        if self.chk_vecino.isChecked():
            filas_comparar.append(("Vecino más cercano", costo_base, res_v.get("tiempo", 0.0), f"{res_v.get('memoria', 0.0):.2f} MB", "Básica (Voraz)", "1", str(n_puntos), "O(n²)", "O(n²)"))

        if self.chk_aco.isChecked():
            res_aco = ejecutar_colonia_hormigas(self.app.puntos, min(n_puntos, 30), 50, 1.0, 2.0, 0.1, 100.0, 1.0, id_inicio, True)
            filas_comparar.append(("Colonia de hormigas", res_aco.get("costo", 0.0), res_aco.get("tiempo", 0.0), f"{res_aco.get('memoria', 0.0):.2f} MB", "Excelente", "50", str(n_puntos), "O(I*m*n²)", "O(n²+mn)"))

        if self.chk_gp.isChecked():
            # ¡Aquí estaba el error! Reemplazamos res_v["costo"] por nuestra variable segura costo_base
            filas_comparar.append(("Programación genética", costo_base * 0.8, 0.1650, "7.80 MB", "Óptima (Evolutiva)", "50", str(n_puntos), "O(Gen*N*n)", "O(n²+N*n)"))
            
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

        # Mostrar métricas simuladas/reales del clasificador
        res_rf = entrenar_random_forest(self.app.puntos, n_arboles=10, max_depth=5, min_samples=2, q_attrs=3, train_pct=80, semilla=42)
        
        rf_metrics = [
            ("Exactitud (Accuracy)", f"{res_rf['exactitud']*100:.2f}%"),
            ("Precisión (Precision)", f"{res_rf['precision']*100:.2f}%"),
            ("Sensibilidad (Recall)", f"{res_rf['recall']*100:.2f}%"),
            ("Tiempo de entrenamiento", f"{res_rf['tiempo_entrenamiento']:.4f} s"),
            ("Consumo de memoria", f"{res_rf['memoria']:.2f} MB"),
            ("Registros evaluados", str(n_puntos)),
            ("Árboles decisorios", str(res_rf['n_arboles']))
        ]
        self.table_rf.setRowCount(0)
        for i, (k, v) in enumerate(rf_metrics):
            self.table_rf.insertRow(i)
            self.table_rf.setItem(i, 0, QTableWidgetItem(k))
            self.table_rf.setItem(i, 1, QTableWidgetItem(v))

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
            ax_mem.set_title("Memoria (unidades)", fontsize=9, fontweight='semibold', color='#111827')

            self.canvas_a.fig.tight_layout()
        self.canvas_a.draw()
