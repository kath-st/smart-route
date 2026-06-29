# pip install PySide6 matplotlib
# python frontend/main.py

# -*- coding: utf-8 -*-
"""
SmartRoute: Sistema comparativo de algoritmos inteligentes para predicción y optimización de rutas

UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS
Facultad de Ingeniería de Sistemas e Informática
Curso: Análisis y Diseño de Algoritmos - Grupo 06

Este es el punto de entrada principal del Frontend (Modularizado).
"""

import sys
import os
import random
import csv

# =====================================================================
# CONFIGURACIÓN DE PATHS PARA IMPORTAR DESDE EL SIBLING 'backend'
# =====================================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar constantes y hojas de estilo
from frontend.styles import STYLE_SHEET, COLOR_TEXT, COLOR_SIDEBAR, COLOR_BG, COLOR_CARD, COLOR_BORDER

# Importar componentes reutilizables
from frontend.components import SidebarButton

# Importar pantallas
from frontend.screens import (
    ScreenInicio,
    ScreenDatos,
    ScreenVecino,
    ScreenRandomForest,
    ScreenHormigas,
    ScreenGenetica,
    ScreenComparacion,
    ScreenExperimentos,
    ScreenAcerca
)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QStackedWidget, QScrollArea, QFileDialog, QMessageBox
)

# =====================================================================
# DATOS INICIALES (12 PUNTOS ACADÉMICOS)
# =====================================================================
DATASET_INICIAL = [
    {"id": "P1", "x": 12.0, "y": 25.0, "prioridad": "Alta", "demanda": 15, "tiempo": 10, "frecuencia": 5, "urgencia": 9, "clase_real": "alta"},
    {"id": "P2", "x": 18.0, "y": 48.0, "prioridad": "Media", "demanda": 8, "tiempo": 15, "frecuencia": 3, "urgencia": 5, "clase_real": "media"},
    {"id": "P3", "x": 35.0, "y": 75.0, "prioridad": "Baja", "demanda": 5, "tiempo": 5, "frecuencia": 2, "urgencia": 2, "clase_real": "baja"},
    {"id": "P4", "x": 42.0, "y": 15.0, "prioridad": "Alta", "demanda": 20, "tiempo": 12, "frecuencia": 8, "urgencia": 10, "clase_real": "alta"},
    {"id": "P5", "x": 55.0, "y": 55.0, "prioridad": "Alta", "demanda": 18, "tiempo": 8, "frecuencia": 6, "urgencia": 8, "clase_real": "alta"},
    {"id": "P6", "x": 62.0, "y": 28.0, "prioridad": "Media", "demanda": 10, "tiempo": 10, "frecuencia": 4, "urgencia": 6, "clase_real": "media"},
    {"id": "P7", "x": 78.0, "y": 68.0, "prioridad": "Baja", "demanda": 3, "tiempo": 5, "frecuencia": 1, "urgencia": 1, "clase_real": "baja"},
    {"id": "P8", "x": 82.0, "y": 12.0, "prioridad": "Media", "demanda": 12, "tiempo": 20, "frecuencia": 4, "urgencia": 4, "clase_real": "media"},
    {"id": "P9", "x": 95.0, "y": 88.0, "prioridad": "Alta", "demanda": 25, "tiempo": 15, "frecuencia": 7, "urgencia": 9, "clase_real": "alta"},
    {"id": "P10", "x": 22.0, "y": 62.0, "prioridad": "Baja", "demanda": 4, "tiempo": 5, "frecuencia": 2, "urgencia": 3, "clase_real": "baja"},
    {"id": "P11", "x": 45.0, "y": 68.0, "prioridad": "Media", "demanda": 9, "tiempo": 12, "frecuencia": 3, "urgencia": 5, "clase_real": "media"},
    {"id": "P12", "x": 68.0, "y": 82.0, "prioridad": "Alta", "demanda": 14, "tiempo": 10, "frecuencia": 5, "urgencia": 7, "clase_real": "alta"},
]

class SmartRouteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartRoute: Sistema comparativo de optimización de rutas y algoritmos inteligentes")
        self.resize(1400, 850)
        self.setMinimumSize(1200, 750)

        # Estado global
        self.puntos = list(DATASET_INICIAL)
        self.mejor_costo = float('inf')
        self.ultimo_tiempo = None
        self.experimentos_contador = 0

        self.setup_ui()
        self.ir_a_inicio()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================================
        # 1. BARRA LATERAL (SIDEBAR) - Slate Oscuro (#0F172A)
        # ==========================================================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setMinimumWidth(260)
        self.sidebar.setMaximumWidth(260)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(6)

        lbl_sidebar_brand = QLabel(" SmartRoute")
        lbl_sidebar_brand.setStyleSheet("font-size: 22px; font-weight: bold; color: #1D4ED8; padding-left: 10px;")
        lbl_sidebar_sub = QLabel("  Comparador de Algoritmos")
        lbl_sidebar_sub.setStyleSheet("font-size: 12px; color: #94A3B8; padding-left: 10px;")
        sidebar_layout.addWidget(lbl_sidebar_brand)
        sidebar_layout.addWidget(lbl_sidebar_sub)
        sidebar_layout.addSpacing(24)

        self.btn_group = []

        def agregar_encabezado_seccion(texto):
            lbl = QLabel(f"  {texto.upper()}")
            lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #475569; margin-top: 12px; margin-bottom: 4px; letter-spacing: 1px;")
            sidebar_layout.addWidget(lbl)

        agregar_encabezado_seccion("General")
        self.btn_inicio = SidebarButton("Inicio / dashboard")
        self.btn_inicio.clicked.connect(self.ir_a_inicio)
        self.btn_datos = SidebarButton("Gestión de datos")
        self.btn_datos.clicked.connect(self.ir_a_datos)
        
        sidebar_layout.addWidget(self.btn_inicio)
        sidebar_layout.addWidget(self.btn_datos)
        self.btn_group.extend([self.btn_inicio, self.btn_datos])

        agregar_encabezado_seccion("Algoritmos")
        self.btn_vecino = SidebarButton("Vecino más cercano")
        self.btn_vecino.clicked.connect(self.ir_a_vecino)
        self.btn_rf = SidebarButton("Random forest priority")
        self.btn_rf.clicked.connect(self.ir_a_rf)
        self.btn_aco = SidebarButton("Colonia de hormigas")
        self.btn_aco.clicked.connect(self.ir_a_aco)
        self.btn_gp = SidebarButton("Programación genética")
        self.btn_gp.clicked.connect(self.ir_a_gp)

        sidebar_layout.addWidget(self.btn_vecino)
        sidebar_layout.addWidget(self.btn_rf)
        sidebar_layout.addWidget(self.btn_aco)
        sidebar_layout.addWidget(self.btn_gp)
        self.btn_group.extend([self.btn_vecino, self.btn_rf, self.btn_aco, self.btn_gp])

        agregar_encabezado_seccion("Análisis")
        self.btn_comp = SidebarButton("Comparación global")
        self.btn_comp.clicked.connect(self.ir_a_comparacion)
        self.btn_exps = SidebarButton("Experimentos masivos")
        self.btn_exps.clicked.connect(self.ir_a_experimentos)

        sidebar_layout.addWidget(self.btn_comp)
        sidebar_layout.addWidget(self.btn_exps)
        self.btn_group.extend([self.btn_comp, self.btn_exps])

        agregar_encabezado_seccion("Información")
        self.btn_acerca = SidebarButton("Acerca del proyecto")
        self.btn_acerca.clicked.connect(self.ir_a_acerca)
        sidebar_layout.addWidget(self.btn_acerca)
        self.btn_group.append(self.btn_acerca)

        sidebar_layout.addStretch()

        lbl_uni_muted = QLabel("UNMSM - FISI - 2026")
        lbl_uni_muted.setStyleSheet("font-size: 11px; color: #475569; padding-left: 20px;")
        sidebar_layout.addWidget(lbl_uni_muted)

        # ==========================================================
        # 2. SECTOR CENTRAL / CONTENEDOR DERECHO - Gris Claro (#F5F7FA)
        # ==========================================================
        self.derecho_container = QWidget()
        self.derecho_container.setObjectName("WorkspaceContainer")
        derecho_layout = QVBoxLayout(self.derecho_container)
        derecho_layout.setContentsMargins(0, 0, 0, 0)
        derecho_layout.setSpacing(0)

        self.header_bar = QFrame()
        self.header_bar.setObjectName("HeaderBar")
        self.header_bar.setFixedHeight(60)
        
        hb_layout = QHBoxLayout(self.header_bar)
        hb_layout.setContentsMargins(24, 0, 24, 0)
        
        lbl_hb_title = QLabel("SmartRoute")
        lbl_hb_title.setObjectName("TopBarBrand")
        
        lbl_academic_sub = QLabel("  |   Sistema comparativo de optimización de rutas y algoritmos inteligentes")
        lbl_academic_sub.setStyleSheet("font-size: 12px; color: #6B7280; font-weight: bold;")
        
        hb_layout.addWidget(lbl_hb_title)
        hb_layout.addWidget(lbl_academic_sub)
        hb_layout.addStretch()
        
        derecho_layout.addWidget(self.header_bar)

        self.stacked_widget = QStackedWidget()
        
        # Instanciar vistas pasando la referencia global de la aplicación
        self.screen_inicio = ScreenInicio(self)
        self.screen_datos = ScreenDatos(self)
        self.screen_vecino = ScreenVecino(self)
        self.screen_rf = ScreenRandomForest(self)
        self.screen_aco = ScreenHormigas(self)
        self.screen_gp = ScreenGenetica(self)
        self.screen_comp = ScreenComparacion(self)
        self.screen_exps = ScreenExperimentos(self)
        self.screen_acerca = ScreenAcerca(self)

        self.stacked_widget.addWidget(self.screen_inicio)
        self.stacked_widget.addWidget(self.screen_datos)
        self.stacked_widget.addWidget(self.screen_vecino)
        self.stacked_widget.addWidget(self.screen_rf)
        self.stacked_widget.addWidget(self.screen_aco)
        self.stacked_widget.addWidget(self.screen_gp)
        self.stacked_widget.addWidget(self.screen_comp)
        self.stacked_widget.addWidget(self.screen_exps)
        self.stacked_widget.addWidget(self.screen_acerca)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(self.stacked_widget)

        derecho_layout.addWidget(scroll_area)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.derecho_container)

    # ==========================================================
    # CONTROLADORES DE RUTA / NAVEGACIÓN
    # ==========================================================

    def marcar_boton_activo(self, index):
        if 0 <= index < len(self.btn_group):
            self.btn_group[index].setChecked(True)

    def ir_a_inicio(self):
        self.screen_inicio.actualizar_kpis()
        self.stacked_widget.setCurrentWidget(self.screen_inicio)
        self.marcar_boton_activo(0)

    def ir_a_datos(self):
        self.screen_datos.actualizar_tabla()
        self.stacked_widget.setCurrentWidget(self.screen_datos)
        self.marcar_boton_activo(1)

    def ir_a_vecino(self):
        self.screen_vecino.actualizar_combo_puntos()
        self.screen_vecino.restablecer()
        self.stacked_widget.setCurrentWidget(self.screen_vecino)
        self.marcar_boton_activo(2)

    def ir_a_rf(self):
        self.screen_rf.restablecer()
        self.stacked_widget.setCurrentWidget(self.screen_rf)
        self.marcar_boton_activo(3)

    def ir_a_aco(self):
        self.screen_aco.actualizar_combo_aco()
        self.screen_aco.restablecer()
        self.stacked_widget.setCurrentWidget(self.screen_aco)
        self.marcar_boton_activo(4)

    def ir_a_gp(self):
        self.screen_gp.restablecer()
        self.stacked_widget.setCurrentWidget(self.screen_gp)
        self.marcar_boton_activo(5)

    def ir_a_comparacion(self):
        self.screen_comp.actualizar_comparativa_completa()
        self.stacked_widget.setCurrentWidget(self.screen_comp)
        self.marcar_boton_activo(6)

    def ir_a_experimentos(self):
        self.stacked_widget.setCurrentWidget(self.screen_exps)
        self.marcar_boton_activo(7)

    def ir_a_acerca(self):
        self.stacked_widget.setCurrentWidget(self.screen_acerca)
        self.marcar_boton_activo(8)

    # ==========================================================
    # LÓGICA DE NEGOCIO INTERNA
    # ==========================================================

    def registrar_mejor_costo(self, costo):
        if costo < self.mejor_costo:
            self.mejor_costo = costo

    def calcular_costo_ruta_simulada(self, ruta=None):
        if not self.puntos:
            return 0.0
        if not ruta:
            ruta = [p["id"] for p in self.puntos] + [self.puntos[0]["id"]]
        
        p_dict = {p["id"]: p for p in self.puntos}
        costo_acumulado = 0.0
        for i in range(len(ruta) - 1):
            p1 = p_dict.get(ruta[i])
            p2 = p_dict.get(ruta[i+1])
            if p1 and p2:
                costo_acumulado += ((p2["x"] - p1["x"])**2 + (p2["y"] - p1["y"])**2)**0.5
        return costo_acumulado

    def cargar_datos_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Cargar Puntos desde CSV", "", "Archivos CSV (*.csv)")
        if path:
            try:
                puntos_nuevos = []
                with open(path, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        puntos_nuevos.append({
                            "id": r["id"],
                            "x": float(r["x"]),
                            "y": float(r["y"]),
                            "prioridad": r.get("prioridad", "Media"),
                            "demanda": int(r.get("demanda", 10)),
                            "tiempo": int(r.get("tiempo", 15)),
                            "frecuencia": int(r.get("frecuencia", 5)),
                            "urgencia": int(r.get("urgencia", 5)),
                            "clase_real": r.get("clase_real", "media")
                        })
                self.puntos = puntos_nuevos
                self.ir_a_datos()
                QMessageBox.information(self, "Dataset Importado", f"Se importaron con éxito {len(self.puntos)} puntos desde el CSV.")
            except Exception as e:
                QMessageBox.critical(self, "Error de Lectura", f"El archivo CSV no cuenta con la estructura correcta:\n{e}")

    def generar_datos_prueba(self):
        self.puntos = list(DATASET_INICIAL)
        self.ir_a_datos()
        QMessageBox.information(self, "Dataset Restaurado", "Se han cargado los 12 puntos de atención predeterminados de la UNMSM.")

    def generar_masivo_puntos(self, cant):
        self.puntos = []
        prioridades = ["Alta", "Media", "Baja"]
        clases = ["alta", "media", "baja"]
        for i in range(1, cant + 1):
            prioridad = random.choice(prioridades)
            clase = clases[prioridades.index(prioridad)] if random.random() < 0.85 else random.choice(clases)
            self.puntos.append({
                "id": f"P{i}",
                "x": random.uniform(10.0, 950.0),
                "y": random.uniform(10.0, 800.0),
                "prioridad": prioridad,
                "demanda": random.randint(2, 60),
                "tiempo": random.randint(5, 90),
                "frecuencia": random.randint(1, 15),
                "urgencia": random.randint(1, 10),
                "clase_real": clase
            })
        QMessageBox.information(self, "Éxito", f"Se han generado {cant} puntos masivos aleatorios con éxito.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = SmartRouteApp()
    window.show()
    sys.exit(app.exec())
