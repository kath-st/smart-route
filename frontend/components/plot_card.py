# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton

class PlotCard(QFrame):
    """Contenedor de gráficos Matplotlib con barra de acciones."""
    def __init__(self, canvas, has_controls=True, parent=None):
        super().__init__(parent)
        self.setObjectName("PlotCard")
        self.setStyleSheet("""
            QFrame#PlotCard {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        self.canvas = canvas
        layout.addWidget(self.canvas, 1)
        
        if has_controls:
            self.controls_layout = QHBoxLayout()
            self.chk_labels = QCheckBox("Mostrar etiquetas de puntos")
            self.chk_labels.setChecked(True)
            self.chk_labels.setStyleSheet("font-size: 13px; color: #111827;")
            
            self.btn_clear = QPushButton("Limpiar Ruta")
            self.btn_clear.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #E5E7EB;
                    color: #111827;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #F5F7FA;
                }
            """)
            
            self.btn_save = QPushButton("Guardar Gráfico")
            self.btn_save.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #E5E7EB;
                    color: #111827;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #F5F7FA;
                }
            """)
            
            self.controls_layout.addWidget(self.chk_labels)
            self.controls_layout.addStretch()
            self.controls_layout.addWidget(self.btn_clear)
            self.controls_layout.addWidget(self.btn_save)
            layout.addLayout(self.controls_layout)
