# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from frontend.components import PageHeader, MetricCard, AlgorithmCard, SectionTitle

class ScreenInicio(QWidget):
    """Pantalla de Inicio / Dashboard Principal."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header de la página
        self.header = PageHeader(
            "SmartRoute Dashboard", 
            "Sistema académico de comparación y análisis empírico de algoritmos de optimización de rutas y clasificación de prioridades."
        )
        layout.addWidget(self.header)

        # KPIs Superiores en MetricCards
        layout_kpis = QHBoxLayout()
        self.card_puntos = MetricCard("Cantidad de Puntos", "12", "#1D4ED8")
        self.card_exps = MetricCard("Experimentos Corridos", "0", "#22C55E")
        self.card_costo = MetricCard("Mejor Costo Registrado", "N/A", "#F59E0B")
        self.card_tiempo = MetricCard("Último Tiempo de Ejecución", "N/A", "#8B5CF6")
        
        layout_kpis.addWidget(self.card_puntos)
        layout_kpis.addWidget(self.card_exps)
        layout_kpis.addWidget(self.card_costo)
        layout_kpis.addWidget(self.card_tiempo)
        layout.addLayout(layout_kpis)

        # Sección del listado de algoritmos
        self.lbl_algos = SectionTitle("Algoritmos soportados en el sistema")
        layout.addWidget(self.lbl_algos)

        layout_cards = QHBoxLayout()
        self.cards = [
            AlgorithmCard(
                "Vecino más cercano", 
                "Heurística voraz de secuenciación que selecciona el nodo más cercano en cada iteración.", 
                self.app.ir_a_vecino, 
                "#1D4ED8"
            ),
            AlgorithmCard(
                "Random forest", 
                "Algoritmo supervisor que clasifica la urgencia y prioridad de atención de los nodos.", 
                self.app.ir_a_rf, 
                "#EF4444"
            ),
            AlgorithmCard(
                "Colonia de hormigas", 
                "Metaheurística bio-inspirada para la optimización iterativa global basada en feromonas.", 
                self.app.ir_a_aco, 
                "#22C55E"
            ),
            AlgorithmCard(
                "Programación genética", 
                "Búsqueda evolutiva que genera fórmulas algebraicas de priorización y recorrido.", 
                self.app.ir_a_gp, 
                "#8B5CF6"
            )
        ]
        for card in self.cards:
            layout_cards.addWidget(card)
        layout.addLayout(layout_cards)

        # Botones inferiores de acción
        layout_btns = QHBoxLayout()
        btn_cargar = QPushButton("Cargar CSV de Puntos")
        btn_cargar.setObjectName("SecondaryBtn")
        btn_cargar.clicked.connect(self.app.cargar_datos_csv)
        
        btn_generar = QPushButton("Generar Dataset predeterminado")
        btn_generar.setObjectName("SecondaryBtn")
        btn_generar.clicked.connect(self.app.generar_datos_prueba)
        
        btn_comparar = QPushButton("Ejecutar comparativa general")
        btn_comparar.setObjectName("PrimaryBtn")
        btn_comparar.clicked.connect(self.app.ir_a_comparacion)

        layout_btns.addWidget(btn_cargar)
        layout_btns.addWidget(btn_generar)
        layout_btns.addStretch()
        layout_btns.addWidget(btn_comparar)
        layout.addLayout(layout_btns)

    def actualizar_kpis(self):
        self.card_puntos.set_value(str(len(self.app.puntos)))
        self.card_exps.set_value(str(self.app.experimentos_contador))
        if self.app.mejor_costo != float('inf'):
            self.card_costo.set_value(f"{self.app.mejor_costo:.2f}")
        else:
            self.card_costo.set_value("N/A")
        if self.app.ultimo_tiempo is not None:
            self.card_tiempo.set_value(f"{self.app.ultimo_tiempo:.4f} s")
        else:
            self.card_tiempo.set_value("N/A")
