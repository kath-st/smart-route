# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QTableWidget, QHeaderView

class StyledTable(QTableWidget):
    """Tabla con diseño académico profesional, colores claros y bordes ordenados."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                gridline-color: #E5E7EB;
                border-radius: 6px;
                font-size: 13px;
                color: #111827;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E5E7EB;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1D4ED8;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #111827;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        # Cambiamos a Interactive con estiramiento de la última sección por defecto
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def ajustar_contenido(self):
        """Ajusta automáticamente el ancho de las columnas según su contenido actual."""
        self.resizeColumnsToContents()

    def fijar_modo_stretch(self):
        """Estira uniformemente todas las columnas de la tabla (ideal para pocas columnas)."""
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
