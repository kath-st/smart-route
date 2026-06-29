# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel

class ParameterCard(QGroupBox):
    """Panel contenedor de formularios y parámetros de entrada."""
    def __init__(self, titulo, parent=None):
        super().__init__(titulo, parent)
        self.setObjectName("ParameterCard")
        self.setStyleSheet("""
            QGroupBox#ParameterCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                color: #1D4ED8;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox#ParameterCard::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 4px;
                background-color: #FFFFFF;
            }
        """)
        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(12, 12, 12, 12)
        self.v_layout.setSpacing(8)
        
    def add_widget(self, label_text, widget):
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 13px; color: #111827; font-weight: 500;")
        self.v_layout.addWidget(lbl)
        self.v_layout.addWidget(widget)
        
    def add_layout(self, layout):
        self.v_layout.addLayout(layout)
