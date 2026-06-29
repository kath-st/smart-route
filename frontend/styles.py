# -*- coding: utf-8 -*-
"""
SmartRoute: Estilos y Colores del Frontend

Este módulo almacena las variables de la paleta de colores académica y la
hoja de estilos QSS global para toda la aplicación.
"""

class Theme:
    COLORS = {
        "bg": "#F5F7FA",
        "bg_central": "#F8FAFC",
        "card": "#FFFFFF",
        "sidebar": "#0F172A",
        "sidebar_active": "#1E293B",
        "primary": "#2563EB",
        "primary_hover": "#1D4ED8",
        "success": "#16A34A",
        "text": "#111827",
        "text_muted": "#64748B",
        "border": "#E5E7EB",
        "table_header": "#F1F5F9",
        "error": "#DC2626",
        "warning": "#D97706"
    }

    FONTS = {
        "family": "Segoe UI",
        "title_size": "24px",
        "section_size": "16px",
        "body_size": "13px",
        "subtitle_size": "14px",
        "kpi_size": "26px"
    }

    @staticmethod
    def get_global_stylesheet():
        return f"""
        QMainWindow {{
            background-color: {Theme.COLORS['bg']};
        }}
        QWidget#WorkspaceContainer {{
            background-color: {Theme.COLORS['bg_central']};
        }}
        QScrollArea, QScrollArea > QWidget > QWidget {{
            background-color: {Theme.COLORS['bg_central']};
            border: none;
        }}
        QWidget {{
            font-family: '{Theme.FONTS['family']}', Arial, sans-serif;
            color: {Theme.COLORS['text']};
        }}
        QDialog, QMessageBox {{
            background-color: #FFFFFF;
        }}
        QDialog QLabel, QMessageBox QLabel {{
            color: #111827;
            font-size: 13px;
        }}
        QDialog QPushButton, QMessageBox QPushButton {{
            background-color: {Theme.COLORS['primary']};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: bold;
            font-size: 12px;
            min-width: 65px;
        }}
        QDialog QPushButton:hover, QMessageBox QPushButton:hover {{
            background-color: {Theme.COLORS['primary_hover']};
        }}
        QFrame#Sidebar {{
            background-color: {Theme.COLORS['sidebar']};
            border-right: 1px solid #1E293B;
        }}
        QFrame#HeaderBar {{
            background-color: {Theme.COLORS['card']};
            border-bottom: 1px solid {Theme.COLORS['border']};
        }}
        QLabel#TopBarBrand {{
            font-size: 20px;
            font-weight: bold;
            color: {Theme.COLORS['text']};
        }}
        QPushButton#PrimaryBtn {{
            background-color: {Theme.COLORS['primary']};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton#PrimaryBtn:hover {{
            background-color: {Theme.COLORS['primary_hover']};
        }}
        QPushButton#SecondaryBtn {{
            background-color: #FFFFFF;
            border: 1px solid {Theme.COLORS['border']};
            color: {Theme.COLORS['text']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton#SecondaryBtn:hover {{
            background-color: {Theme.COLORS['bg']};
        }}
        QPushButton#DangerBtn {{
            background-color: {Theme.COLORS['error']};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton#DangerBtn:hover {{
            background-color: #B91C1C;
        }}
        QPushButton#SuccessBtn {{
            background-color: {Theme.COLORS['success']};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton#SuccessBtn:hover {{
            background-color: #15803D;
        }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {Theme.COLORS['card']};
            border: 1px solid {Theme.COLORS['border']};
            border-radius: 6px;
            padding: 6px;
            font-size: 13px;
            color: {Theme.COLORS['text']};
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {Theme.COLORS['primary']};
        }}
        QCheckBox {{
            font-size: 13px;
            color: {Theme.COLORS['text']};
        }}
        QProgressBar {{
            border: 1px solid {Theme.COLORS['border']};
            border-radius: 6px;
            text-align: center;
            background-color: {Theme.COLORS['border']};
            font-size: 11px;
            font-weight: bold;
            color: {Theme.COLORS['text']};
        }}
        QProgressBar::chunk {{
            background-color: {Theme.COLORS['success']};
            border-radius: 6px;
        }}
        QScrollBar:vertical {{
            background-color: {Theme.COLORS['bg']};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: #CBD5E1;
            border-radius: 5px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: #94A3B8;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """

# Exposición de alias para compatibilidad retroactiva
COLOR_BG = Theme.COLORS["bg"]
COLOR_CARD = Theme.COLORS["card"]
COLOR_SIDEBAR = Theme.COLORS["sidebar"]
COLOR_PRIMARY = Theme.COLORS["primary"]
COLOR_PRIMARY_HOVER = Theme.COLORS["primary_hover"]
COLOR_SUCCESS = Theme.COLORS["success"]
COLOR_TEXT = Theme.COLORS["text"]
COLOR_TEXT_MUTED = Theme.COLORS["text_muted"]
COLOR_BORDER = Theme.COLORS["border"]
COLOR_ERROR = Theme.COLORS["error"]
COLOR_WARNING = Theme.COLORS["warning"]

STYLE_SHEET = Theme.get_global_stylesheet()
