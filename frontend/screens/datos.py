# -*- coding: utf-8 -*-
import os
import csv
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QGroupBox, QFileDialog, QMessageBox, QTableWidgetItem, QFrame
from frontend.components import PageHeader, ParameterCard, StyledTable

class ScreenDatos(QWidget):
    """Pantalla de Gestión de Puntos de Atención."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header actualizado para reflejar la simplificación
        self.header = PageHeader(
            "Administración de datos", 
            "Controles para la generación masiva aleatoria o carga de nodos mediante archivo CSV"
        )
        layout.addWidget(self.header)

        # Layout horizontal principal de datos
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # 1. Panel Izquierdo (Solo Generación Rápida)
        form_panel = ParameterCard("Generación de puntos")
        form_panel.setMaximumWidth(400)

        # Generador de puntos rápido
        group_generador = QGroupBox("Generación rápida masiva")
        group_generador.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: bold;
                color: #111827;
            }
        """)
        gen_v_layout = QVBoxLayout(group_generador)
        
        gen_btns_layout = QHBoxLayout()
        btn_gen_10 = QPushButton("10 pts")
        btn_gen_10.setObjectName("SecondaryBtn")
        btn_gen_10.clicked.connect(lambda: self.generar_puntos_rapido(10))
        
        btn_gen_100 = QPushButton("100 pts")
        btn_gen_100.setObjectName("SecondaryBtn")
        btn_gen_100.clicked.connect(lambda: self.generar_puntos_rapido(100))
        
        btn_gen_1000 = QPushButton("1000 pts")
        btn_gen_1000.setObjectName("SecondaryBtn")
        btn_gen_1000.clicked.connect(lambda: self.generar_puntos_rapido(1000))
        
        gen_btns_layout.addWidget(btn_gen_10)
        gen_btns_layout.addWidget(btn_gen_100)
        gen_btns_layout.addWidget(btn_gen_1000)
        gen_v_layout.addLayout(gen_btns_layout)

        custom_layout = QHBoxLayout()
        self.spin_cant_custom = QSpinBox()
        self.spin_cant_custom.setRange(5, 50000)
        self.spin_cant_custom.setValue(150)
        
        btn_gen_custom = QPushButton("Generar")
        btn_gen_custom.setObjectName("PrimaryBtn")
        btn_gen_custom.clicked.connect(lambda: self.generar_puntos_rapido(self.spin_cant_custom.value()))
        
        custom_layout.addWidget(self.spin_cant_custom)
        custom_layout.addWidget(btn_gen_custom)
        gen_v_layout.addLayout(custom_layout)
        
        form_panel.v_layout.addWidget(group_generador)
        
        # Un espacio en blanco (stretch) para empujar los controles hacia arriba y mantener el diseño limpio
        form_panel.v_layout.addStretch()

        h_layout.addWidget(form_panel)

        # 2. Panel Derecho (Tabla y carga de datos)
        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.setSpacing(12)

        lbl_tbl_title = QLabel("Listado de nodos del sistema")
        lbl_tbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827;")
        table_layout.addWidget(lbl_tbl_title)

        # Tabla
        self.table = StyledTable()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "X", "Y", "Prioridad", "Demanda", "T. Atención", "Frecuencia", "Urgencia", "Clase Real"
        ])
        # (Se eliminó la conexión al formulario individual, ya que no existe)
        table_layout.addWidget(self.table)

        # Botones de importación/limpieza
        table_btns = QHBoxLayout()
        btn_limpiar = QPushButton("Limpiar todo")
        btn_limpiar.setObjectName("DangerBtn")
        btn_limpiar.clicked.connect(self.limpiar_puntos)
        
        btn_importar_csv = QPushButton("Cargar CSV")
        btn_importar_csv.setObjectName("SecondaryBtn")
        btn_importar_csv.clicked.connect(self.app.cargar_datos_csv)
        
        btn_guardar_csv = QPushButton("Exportar CSV")
        btn_guardar_csv.setObjectName("SecondaryBtn")
        btn_guardar_csv.clicked.connect(self.exportar_csv)

        table_btns.addWidget(btn_importar_csv)
        table_btns.addWidget(btn_guardar_csv)
        table_btns.addStretch()
        table_btns.addWidget(btn_limpiar)
        table_layout.addLayout(table_btns)

        h_layout.addWidget(table_container, 1)

        layout.addLayout(h_layout)

    def actualizar_tabla(self):
        self.table.setRowCount(0)
        for i, p in enumerate(self.app.puntos):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(f"{p['x']:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{p['y']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(str(p["prioridad"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(p["demanda"])))
            self.table.setItem(i, 5, QTableWidgetItem(str(p["tiempo"])))
            self.table.setItem(i, 6, QTableWidgetItem(str(p["frecuencia"])))
            self.table.setItem(i, 7, QTableWidgetItem(str(p["urgencia"])))
            self.table.setItem(i, 8, QTableWidgetItem(str(p["clase_real"])))
        self.table.ajustar_contenido()

    def limpiar_puntos(self):
        confirm = QMessageBox.question(
            self, "Confirmar Limpieza", "¿Desea eliminar todos los puntos cargados?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.app.puntos = []
            self.actualizar_tabla()
            self.app.screen_inicio.actualizar_kpis()

    def generar_puntos_rapido(self, cantidad):
        self.app.generar_masivo_puntos(cantidad)
        self.actualizar_tabla()
        self.app.screen_inicio.actualizar_kpis()

    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar dataset CSV", "", "Archivos CSV (*.csv)")
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["id", "x", "y", "prioridad", "demanda", "tiempo", "frecuencia", "urgencia", "clase_real"])
                    for p in self.app.puntos:
                        writer.writerow([p["id"], p["x"], p["y"], p["prioridad"], p["demanda"], p["tiempo"], p["frecuencia"], p["urgencia"], p["clase_real"]])
                QMessageBox.information(self, "Exportación completada", f"Se exportó el dataset con éxito a {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error de guardado", f"No se pudo escribir el archivo:\n{e}")