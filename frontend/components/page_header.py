# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PageHeader(QWidget):
    """Título y descripción consistente para cada pantalla."""
    def __init__(self, titulo, descripcion, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(4)
        
        self.lbl_title = QLabel(titulo)
        self.lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111827;")
        
        self.lbl_desc = QLabel(descripcion)
        self.lbl_desc.setStyleSheet("font-size: 14px; color: #6B7280;")
        self.lbl_desc.setWordWrap(True)
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_desc)
