# -*- coding: utf-8 -*-
import os
import csv
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDoubleSpinBox, QComboBox, QSpinBox, QGroupBox, QFileDialog, QMessageBox, QTableWidgetItem, QFrame
from frontend.components import PageHeader, ParameterCard, StyledTable

class ScreenDatos(QWidget):
    """Pantalla de Gestión de Puntos de Atención."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Administración de datos", 
            "Formulario de registro individual de nodos de demanda y controles para generación aleatoria o carga en CSV"
        )
        layout.addWidget(self.header)

        # Layout horizontal principal de datos
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # 1. Panel Izquierdo (Formulario)
        form_panel = ParameterCard("Registrar / modificar punto")
        form_panel.setMaximumWidth(400)

        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("Ej: P13")
        
        self.input_x = QDoubleSpinBox()
        self.input_x.setRange(0.0, 1000.0)
        self.input_x.setValue(50.0)
        
        self.input_y = QDoubleSpinBox()
        self.input_y.setRange(0.0, 1000.0)
        self.input_y.setValue(50.0)

        self.input_prioridad = QComboBox()
        self.input_prioridad.addItems(["Alta", "Media", "Baja"])

        self.input_demanda = QSpinBox()
        self.input_demanda.setRange(1, 1000)
        self.input_demanda.setValue(10)

        self.input_tiempo = QSpinBox()
        self.input_tiempo.setRange(1, 120)
        self.input_tiempo.setValue(15)

        self.input_frecuencia = QSpinBox()
        self.input_frecuencia.setRange(1, 30)
        self.input_frecuencia.setValue(5)

        self.input_urgencia = QSpinBox()
        self.input_urgencia.setRange(1, 10)
        self.input_urgencia.setValue(5)

        self.input_clase = QComboBox()
        self.input_clase.addItems(["alta", "media", "baja"])

        form_panel.add_widget("Identificador de punto (ID)", self.input_id)
        
        coord_layout = QHBoxLayout()
        v1, v2 = QVBoxLayout(), QVBoxLayout()
        v1.addWidget(QLabel("Coordenada X:"))
        v1.addWidget(self.input_x)
        v2.addWidget(QLabel("Coordenada Y:"))
        v2.addWidget(self.input_y)
        coord_layout.addLayout(v1)
        coord_layout.addLayout(v2)
        form_panel.add_layout(coord_layout)

        form_panel.add_widget("Prioridad de visita (heurística)", self.input_prioridad)
        form_panel.add_widget("Demanda de carga (unidades)", self.input_demanda)
        form_panel.add_widget("Tiempo de atención (minutos)", self.input_tiempo)
        form_panel.add_widget("Frecuencia de atención mensual", self.input_frecuencia)
        form_panel.add_widget("Nivel de urgencia crítica (1-10)", self.input_urgencia)
        form_panel.add_widget("Clase real (Prioridad Supervisada)", self.input_clase)

        # Botones del CRUD
        crud_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar punto")
        self.btn_guardar.setObjectName("PrimaryBtn")
        self.btn_guardar.clicked.connect(self.guardar_punto)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setObjectName("DangerBtn")
        self.btn_eliminar.clicked.connect(self.eliminar_punto)
        
        crud_layout.addWidget(self.btn_guardar)
        crud_layout.addWidget(self.btn_eliminar)
        form_panel.add_layout(crud_layout)

        # Generador de puntos rápido
        group_generador = QGroupBox("Generación rápida")
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
        self.table.itemSelectionChanged.connect(self.cargar_datos_en_formulario)
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
        self.input_id.clear()

    def cargar_datos_en_formulario(self):
        seleccion = self.table.selectedItems()
        if not seleccion:
            return
        row = seleccion[0].row()
        p = self.app.puntos[row]
        self.input_id.setText(p["id"])
        self.input_x.setValue(p["x"])
        self.input_y.setValue(p["y"])
        self.input_prioridad.setCurrentText(p["prioridad"])
        self.input_demanda.setValue(p["demanda"])
        self.input_tiempo.setValue(p["tiempo"])
        self.input_frecuencia.setValue(p["frecuencia"])
        self.input_urgencia.setValue(p["urgencia"])
        self.input_clase.setCurrentText(p["clase_real"])

    def guardar_punto(self):
        pid = self.input_id.text().strip()
        if not pid:
            QMessageBox.warning(self, "Error de validación", "El identificador del punto no puede estar vacío")
            return

        p_existente = next((p for p in self.app.puntos if p["id"] == pid), None)
        punto = {
            "id": pid,
            "x": self.input_x.value(),
            "y": self.input_y.value(),
            "prioridad": self.input_prioridad.currentText(),
            "demanda": self.input_demanda.value(),
            "tiempo": self.input_tiempo.value(),
            "frecuencia": self.input_frecuencia.value(),
            "urgencia": self.input_urgencia.value(),
            "clase_real": self.input_clase.currentText()
        }

        if p_existente:
            idx = self.app.puntos.index(p_existente)
            self.app.puntos[idx] = punto
        else:
            self.app.puntos.append(punto)

        self.actualizar_tabla()
        self.app.screen_inicio.actualizar_kpis()

    def eliminar_punto(self):
        pid = self.input_id.text().strip()
        if not pid:
            QMessageBox.warning(self, "Eliminar punto", "Por favor, seleccione un punto de la tabla o digite el ID")
            return

        p_existente = next((p for p in self.app.puntos if p["id"] == pid), None)
        if p_existente:
            self.app.puntos.remove(p_existente)
            self.actualizar_tabla()
            self.app.screen_inicio.actualizar_kpis()
        else:
            QMessageBox.warning(self, "No encontrado", f"No se encontró un punto con ID '{pid}'.")

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
