# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QPushButton

class SidebarButton(QPushButton):
    """Botón de navegación estilizado dentro del menú lateral oscuro."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SidebarButton")
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setStyleSheet("""
            QPushButton#SidebarButton {
                background-color: transparent;
                color: #94A3B8;
                text-align: left;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
                border: none;
                border-left: 4px solid transparent;
                border-radius: 0px;
            }
            QPushButton#SidebarButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            QPushButton#SidebarButton:checked {
                background-color: #1E293B;
                color: #FFFFFF;
                border-left: 4px solid #1D4ED8;
                font-weight: bold;
            }
        """)
