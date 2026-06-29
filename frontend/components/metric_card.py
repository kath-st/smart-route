# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

class MetricCard(QFrame):
    """Tarjeta blanca de bordes redondeados para visualización de KPIs."""
    def __init__(self, titulo, valor_inicial="N/A", color_valor="#1D4ED8", parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setStyleSheet("""
            QFrame#MetricCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)
        
        self.lbl_title = QLabel(titulo)
        self.lbl_title.setStyleSheet("font-size: 13px; color: #6B7280; font-weight: 500;")
        self.lbl_title.setWordWrap(True)
        
        self.lbl_value = QLabel(valor_inicial)
        self.lbl_value.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color_valor};")
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        
    def set_value(self, valor):
        self.lbl_value.setText(str(valor))
