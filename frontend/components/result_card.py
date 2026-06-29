# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel

class ResultCard(QFrame):
    """Tarjeta blanca estructurada para mostrar resultados formateados."""
    def __init__(self, titulo, parent=None):
        super().__init__(parent)
        self.setObjectName("ResultCard")
        self.setStyleSheet("""
            QFrame#ResultCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(10)
        
        lbl_title = QLabel(titulo)
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #111827; border-bottom: 1px solid #E5E7EB; padding-bottom: 6px;")
        self.layout.addWidget(lbl_title)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(6)
        self.layout.addLayout(self.content_layout)
        
    def add_result_row(self, label, value, value_color="#111827"):
        row = QHBoxLayout()
        lbl_lbl = QLabel(label)
        lbl_lbl.setStyleSheet("font-size: 13px; color: #6B7280;")
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {value_color};")
        lbl_val.setWordWrap(True)
        
        row.addWidget(lbl_lbl)
        row.addWidget(lbl_val, 1, Qt.AlignRight)
        self.content_layout.addLayout(row)
        return lbl_val
