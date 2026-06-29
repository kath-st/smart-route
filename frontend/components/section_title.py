# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SectionTitle(QWidget):
    """Componente de título reutilizable para delimitación de secciones académicas."""
    def __init__(self, texto, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(0)
        
        self.lbl_text = QLabel(texto)
        self.lbl_text.setStyleSheet("font-size: 16px; font-weight: bold; color: #111827;")
        layout.addWidget(self.lbl_text)
        
    def set_text(self, texto):
        self.lbl_text.setText(texto)
