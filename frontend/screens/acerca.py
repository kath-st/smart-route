# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox

from frontend.components import PageHeader

class ScreenAcerca(QWidget):
    """Pantalla con información académica y créditos del proyecto."""
    def __init__(self, main_app):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        self.header = PageHeader(
            "Información académica",
            "Detalles institucionales, equipo de desarrollo y declaración sobre el uso responsable de inteligencia artificial"
        )
        layout.addWidget(self.header)

        # Layout horizontal principal
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Tarjeta Izquierda (Créditos universitarios)
        izq_card = QFrame()
        izq_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }")
        v_izq = QVBoxLayout(izq_card)
        v_izq.setContentsMargins(16, 16, 16, 16)
        v_izq.setSpacing(12)

        lbl_proy = QLabel("PROYECTO ACADÉMICO")
        lbl_proy.setStyleSheet("font-size: 15px; font-weight: bold; color: #1D4ED8;")
        v_izq.addWidget(lbl_proy)

        lbl_uni = QLabel(
            "Universidad Nacional Mayor de San Marcos\n"
            "Facultad de Ingeniería de Sistemas e Informática\n"
            "Escuela Profesional de Ingeniería de Software"
        )
        lbl_uni.setStyleSheet("font-weight: bold; color: #111827; font-size: 13px;")
        v_izq.addWidget(lbl_uni)

        lbl_curso = QLabel(
            "Curso: Análisis y Diseño de Algoritmos\n"
            "Docente: Luis Guerra Grados\n"
            "Grupo: Grupo 06\n"
            "Semestre: 2026-I"
        )
        lbl_curso.setStyleSheet("color: #6B7280; font-size: 13px; line-height: 1.5;")
        v_izq.addWidget(lbl_curso)

        group_integ = QGroupBox("Integrantes del equipo de investigación")
        group_integ.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: bold;
                color: #111827;
            }
        """)
        v_integ = QVBoxLayout(group_integ)
        integrantes = [
            "• Diana Carolina Postigo Vega (Código: 24200167)",
            "• Katherine Lizbeth Siesquen Torres (Código: 24200066)",
            "• Ryan Gabriel Bernal Hernández (Código: 25200179)",
            "• Uscamayta Sanchez Gabriel Omar (Código: 22200101)"
        ]
        for name in integrantes:
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-size: 13px; color: #111827;")
            v_integ.addWidget(lbl_name)
        v_izq.addWidget(group_integ)

        v_izq.addStretch()
        h_layout.addWidget(izq_card, 2)

        # Tarjeta Derecha (Acerca de algoritmos y descargo de responsabilidad de IA)
        der_card = QFrame()
        der_card.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; }")
        v_der = QVBoxLayout(der_card)
        v_der.setContentsMargins(16, 16, 16, 16)
        v_der.setSpacing(12)

        lbl_alg = QLabel("Descripción de los algoritmos evaluados")
        lbl_alg.setStyleSheet("font-size: 15px; font-weight: bold; color: #1D4ED8;")
        v_der.addWidget(lbl_alg)

        lbl_desc_algos = QLabel(
            "1. Vecino más cercano: Algoritmo voraz e intuitivo útil como línea base de comparación\n"
            "2. Random Forest: Método de clasificación en ensambles para predecir prioridades de atención\n"
            "3. Colonia de hormigas: Metaheurística para optimizar rutas en grandes espacios de búsqueda\n"
            "4. Programación genética: Algoritmo evolutivo que optimiza fórmulas matemáticas de ruteo"
        )
        lbl_desc_algos.setStyleSheet("font-size: 13px; color: #6B7280; line-height: 1.5;")
        lbl_desc_algos.setWordWrap(True)
        v_der.addWidget(lbl_desc_algos)

        group_ia = QGroupBox("Declaración de uso responsable de IA")
        group_ia.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: bold;
                color: #EF4444;
            }
        """)
        v_ia = QVBoxLayout(group_ia)
        lbl_ia_text = QLabel(
            "De acuerdo con los lineamientos académicos de la UNMSM, se declara que los diseños estructurales, "
            "visuales y de prototipado de esta aplicación han sido refinados con asistencia de inteligencia artificial. "
            "Los núcleos de resolución matemática de los algoritmos son de autoría exclusiva del equipo de desarrollo, "
            "respetando el código ético y la honestidad intelectual"
        )
        lbl_ia_text.setStyleSheet("font-size: 12px; color: #6B7280; font-style: italic; line-height: 1.4;")
        lbl_ia_text.setWordWrap(True)
        v_ia.addWidget(lbl_ia_text)
        v_der.addWidget(group_ia)

        v_der.addStretch()
        h_layout.addWidget(der_card, 3)

        layout.addLayout(h_layout)
