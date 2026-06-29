# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

class AlgorithmCard(QFrame):
    """Tarjeta descriptiva en el Dashboard para cada algoritmo."""
    def __init__(self, nombre, proposito, callback, color_borde="#1D4ED8", parent=None):
        super().__init__(parent)
        self.setObjectName("AlgorithmCard")
        self.setStyleSheet(f"""
            QFrame#AlgorithmCard {{
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-top: 4px solid {color_borde};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        lbl_name = QLabel(nombre)
        lbl_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #111827;")
        
        lbl_prop = QLabel(proposito)
        lbl_prop.setStyleSheet("font-size: 13px; color: #6B7280;")
        lbl_prop.setWordWrap(True)
        lbl_prop.setMinimumHeight(55)
        
        lbl_state_title = QLabel("Estado actual:")
        lbl_state_title.setStyleSheet("font-size: 12px; color: #6B7280; font-weight: bold;")
        
        self.lbl_state = QLabel("Simulado")
        self.lbl_state.setStyleSheet("font-size: 12px; color: #F59E0B; font-weight: bold;")
        
        state_layout = QHBoxLayout()
        state_layout.addWidget(lbl_state_title)
        state_layout.addWidget(self.lbl_state)
        state_layout.addStretch()
        
        btn_abrir = QPushButton("Abrir módulo")
        btn_abrir.setStyleSheet("""
            QPushButton {
                background-color: #1D4ED8;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1540C2;
            }
        """)
        btn_abrir.clicked.connect(callback)
        
        layout.addWidget(lbl_name)
        layout.addWidget(lbl_prop)
        layout.addLayout(state_layout)
        layout.addWidget(btn_abrir)
        
    def set_state(self, state, color="#F59E0B"):
        self.lbl_state.setText(state)
        self.lbl_state.setStyleSheet(f"font-size: 12px; color: {color}; font-weight: bold;")
