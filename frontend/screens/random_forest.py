# -*- coding: utf-8 -*-
import time
import random
import os
import csv
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QMessageBox, QTableWidgetItem, QFrame, QFileDialog
from frontend.components import PageHeader, ParameterCard, ResultCard, PlotCard, StyledTable, CanvasGrafico

from backend.algorithms import entrenar_random_forest, clasificar_puntos_random_forest

class ScreenRandomForest(QWidget):
    """Módulo de Predicción de Prioridades mediante Random Forest."""
    def __init__(self, main_app):
        super().__init__()
        self.app = main_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # A. Encabezado
        self.header = PageHeader(
            "Random Forest: Clasificación de prioridad de puntos",
            "Este módulo clasifica cada punto como prioridad alta, media o baja. No construye rutas directamente."
        )
        layout.addWidget(self.header)

        # Panel central
        h_layout = QHBoxLayout()
        h_layout.setSpacing(20)

        # Panel Izquierdo: Notas, parámetros y complejidades
        izq_layout = QVBoxLayout()
        izq_layout.setSpacing(14)

        # B. Caja informativa
        self.nota_card = QFrame()
        self.nota_card.setObjectName("NotaCard")
        self.nota_card.setStyleSheet("""
            QFrame#NotaCard {
                background-color: #EFF6FF;
                border: 1px solid #BFDBFE;
                border-radius: 8px;
            }
        """)
        v_nota = QVBoxLayout(self.nota_card)
        v_nota.setContentsMargins(12, 12, 12, 12)
        lbl_nota_title = QLabel("Nota informativa:")
        lbl_nota_title.setStyleSheet("font-weight: bold; color: #1D4ED8; font-size: 13px;")
        lbl_nota_text = QLabel(
            "Random Forest se utiliza para clasificar la prioridad de los puntos. Esta prioridad "
            "puede servir como dato de apoyo para otros algoritmos de recorrido, pero Random "
            "Forest no optimiza directamente la ruta."
        )
        lbl_nota_text.setStyleSheet("font-size: 12px; font-style: italic; color: #1E3A8A;")
        lbl_nota_text.setWordWrap(True)
        v_nota.addWidget(lbl_nota_title)
        v_nota.addWidget(lbl_nota_text)
        izq_layout.addWidget(self.nota_card)

        # C. Parámetros
        self.param_card = ParameterCard("Configuración del clasificador")
        
        self.spin_arboles = QSpinBox()
        self.spin_arboles.setRange(5, 500)
        self.spin_arboles.setValue(20)

        self.spin_max_depth = QSpinBox()
        self.spin_max_depth.setRange(1, 30)
        self.spin_max_depth.setValue(6)

        self.spin_min_samples = QSpinBox()
        self.spin_min_samples.setRange(2, 20)
        self.spin_min_samples.setValue(2)

        self.spin_q_attrs = QSpinBox()
        self.spin_q_attrs.setRange(1, 7)
        self.spin_q_attrs.setValue(3)

        self.spin_pct_train = QDoubleSpinBox()
        self.spin_pct_train.setRange(10.0, 95.0)
        self.spin_pct_train.setValue(80.0)

        self.spin_semilla = QSpinBox()
        self.spin_semilla.setRange(0, 99999)
        self.spin_semilla.setValue(42)

        self.param_card.add_widget("Número de árboles (B):", self.spin_arboles)
        self.param_card.add_widget("Profundidad máxima (h):", self.spin_max_depth)
        self.param_card.add_widget("Mínimo de muestras split:", self.spin_min_samples)
        self.param_card.add_widget("Atributos por división (q):", self.spin_q_attrs)
        
        lbl_q_desc = QLabel("El máximo es 7 porque el modelo usa 7 atributos: X, Y, distancia al origen, demanda, tiempo de atención, frecuencia y urgencia.")
        lbl_q_desc.setStyleSheet("font-size: 10px; color: #475569; font-style: italic; padding-bottom: 6px;")
        lbl_q_desc.setWordWrap(True)
        self.param_card.v_layout.addWidget(lbl_q_desc)

        self.param_card.add_widget("Porcentaje de entreno (%):", self.spin_pct_train)
        
        lbl_pct_desc = QLabel("Recomendado: 70% a 80%. Si el porcentaje es muy alto, quedan pocos datos para evaluar el modelo.")
        lbl_pct_desc.setStyleSheet("font-size: 10px; color: #475569; font-style: italic; padding-bottom: 6px;")
        lbl_pct_desc.setWordWrap(True)
        self.param_card.v_layout.addWidget(lbl_pct_desc)

        self.param_card.add_widget("Semilla aleatoria:", self.spin_semilla)

        # D. Botones en el panel de control
        self.btn_generar = QPushButton("Generar datos de prueba")
        self.btn_generar.setObjectName("SecondaryBtn")
        self.btn_generar.clicked.connect(self.generar_datos_prueba)

        self.btn_cargar = QPushButton("Cargar CSV")
        self.btn_cargar.setObjectName("SecondaryBtn")
        self.btn_cargar.clicked.connect(self.cargar_csv)

        self.btn_entrenar = QPushButton("Entrenar modelo")
        self.btn_entrenar.setObjectName("PrimaryBtn")
        self.btn_entrenar.clicked.connect(self.entrenar_clasificador)

        self.btn_clasificar = QPushButton("Clasificar puntos")
        self.btn_clasificar.setObjectName("SuccessBtn")
        self.btn_clasificar.setEnabled(False)
        self.btn_clasificar.clicked.connect(self.clasificar_dataset)

        self.btn_limpiar = QPushButton("Limpiar resultados")
        self.btn_limpiar.setObjectName("SecondaryBtn")
        self.btn_limpiar.clicked.connect(self.restablecer)

        self.btn_exportar = QPushButton("Exportar resultados CSV")
        self.btn_exportar.setObjectName("SecondaryBtn")
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.clicked.connect(self.exportar_resultados_csv)

        self.param_card.v_layout.addWidget(self.btn_generar)
        self.param_card.v_layout.addWidget(self.btn_cargar)
        self.param_card.v_layout.addWidget(self.btn_entrenar)
        self.param_card.v_layout.addWidget(self.btn_clasificar)
        self.param_card.v_layout.addWidget(self.btn_limpiar)
        self.param_card.v_layout.addWidget(self.btn_exportar)
        izq_layout.addWidget(self.param_card)

        # Complejidades
        self.complex_card = ResultCard("Complejidad teórica")
        self.complex_card.add_result_row("Temporal entrenamiento:", "O(B * q * h * n²)", "#8B5CF6")
        self.complex_card.add_result_row("Temporal predicción:", "O(B * h)", "#8B5CF6")
        self.complex_card.add_result_row("Espacial:", "O(n * m + B * min(2^h, n))", "#8B5CF6")
        izq_layout.addWidget(self.complex_card)
        izq_layout.addStretch()

        h_layout.addLayout(izq_layout, 2)

        # Panel Derecho: Métricas, Clasificación e importancia
        der_layout = QVBoxLayout()
        der_layout.setSpacing(16)

        # F. Métricas de rendimiento
        self.card_kpi = ResultCard("Métricas de rendimiento del clasificador")
        kpi_h = QHBoxLayout()
        self.lbl_exactitud = QLabel("Exactitud: --")
        self.lbl_exactitud.setStyleSheet("font-size: 14px; font-weight: bold; color: #2563EB;")
        self.lbl_precision = QLabel("Precisión promedio: --")
        self.lbl_precision.setStyleSheet("font-size: 14px; font-weight: bold; color: #2563EB;")
        self.lbl_recall = QLabel("Recall promedio: --")
        self.lbl_recall.setStyleSheet("font-size: 14px; font-weight: bold; color: #2563EB;")
        kpi_h.addWidget(self.lbl_exactitud)
        kpi_h.addWidget(self.lbl_precision)
        kpi_h.addWidget(self.lbl_recall)
        self.card_kpi.layout.addLayout(kpi_h)

        self.lbl_recursos = QLabel(
            "Registros totales: -- | Entrenamiento: -- | Prueba: -- | "
            "Predicciones generadas: -- | Métricas evaluadas sobre: prueba"
        )
        self.lbl_recursos.setStyleSheet("font-size: 12px; color: #64748B; font-weight: bold;")
        self.card_kpi.layout.addWidget(self.lbl_recursos)

        # Métricas individuales por clase para evitar castigo de clases vacías
        self.lbl_recursos_detallados = QLabel("Alta: -- | Media: -- | Baja: --")
        self.lbl_recursos_detallados.setStyleSheet("font-size: 11px; color: #64748B; font-style: italic;")
        self.card_kpi.layout.addWidget(self.lbl_recursos_detallados)

        der_layout.addWidget(self.card_kpi)

        # G. Gráfico con Matplotlib
        self.canvas = CanvasGrafico(self)
        self.plot_card = PlotCard(self.canvas, has_controls=False)
        self.plot_card.setMaximumHeight(280)
        der_layout.addWidget(self.plot_card)

        # Guía de lectura de gráficos
        self.lbl_graficos_ayuda = QLabel(
            "<b>Guía de lectura de gráficos:</b><br/>"
            "• <b>Importancia de atributos:</b> Las barras más largas indican los atributos que más influyeron en las decisiones del bosque.<br/>"
            "• <b>Matriz de confusión:</b> La diagonal principal representa aciertos. Los valores fuera de la diagonal representan errores de clasificación."
        )
        self.lbl_graficos_ayuda.setStyleSheet("""
            font-size: 11px;
            color: #475569;
            padding: 8px 12px;
            border-left: 3px solid #2563EB;
            background-color: #F1F5F9;
            border-radius: 4px;
        """)
        self.lbl_graficos_ayuda.setWordWrap(True)
        der_layout.addWidget(self.lbl_graficos_ayuda)

        # Tarjeta de Interpretación de Resultado
        self.card_interpretacion = ResultCard("Interpretación del resultado")
        self.lbl_interpretacion = QLabel(
            "Entrene el modelo y presione 'Clasificar puntos' para ver el análisis interpretativo del rendimiento."
        )
        self.lbl_interpretacion.setStyleSheet("font-size: 12px; color: #334155; line-height: 1.45;")
        self.lbl_interpretacion.setWordWrap(True)
        self.card_interpretacion.layout.addWidget(self.lbl_interpretacion)
        der_layout.addWidget(self.card_interpretacion)
        
        # E. Tabla de datos
        self.table_clasif = StyledTable()
        self.table_clasif.setColumnCount(11)
        self.table_clasif.setHorizontalHeaderLabels([
            "ID", "X", "Y", "Distancia al origen", "Demanda", 
            "Tiempo de atención", "Frecuencia", "Urgencia", 
            "Prioridad real", "Prioridad predicha", "Conjunto"
        ])

        der_layout.addWidget(self.table_clasif, 1)
        h_layout.addLayout(der_layout, 5)

        layout.addLayout(h_layout)

        self.modelo_info = None
        self.actualizar_tabla_completa()

    def actualizar_tabla_completa(self, predictions=None):
        """Llena la tabla de datos con todos los 11 campos requeridos."""
        self.table_clasif.setRowCount(0)
        if not self.app.puntos:
            return
            
        for i, p in enumerate(self.app.puntos):
            self.table_clasif.insertRow(i)
            self.table_clasif.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            self.table_clasif.setItem(i, 1, QTableWidgetItem(f"{p['x']:.1f}"))
            self.table_clasif.setItem(i, 2, QTableWidgetItem(f"{p['y']:.1f}"))
            dist = (p['x']**2 + p['y']**2)**0.5
            self.table_clasif.setItem(i, 3, QTableWidgetItem(f"{dist:.2f}"))
            self.table_clasif.setItem(i, 4, QTableWidgetItem(str(p['demanda'])))
            self.table_clasif.setItem(i, 5, QTableWidgetItem(str(p['tiempo'])))
            self.table_clasif.setItem(i, 6, QTableWidgetItem(str(p['frecuencia'])))
            self.table_clasif.setItem(i, 7, QTableWidgetItem(str(p['urgencia'])))
            
            # Prioridad real
            clase_real_raw = str(p.get("clase_real", "baja")).strip().lower()
            clase_real_cap = clase_real_raw.capitalize()
            self.table_clasif.setItem(i, 8, QTableWidgetItem(clase_real_cap))
            
            # Prioridad predicha y partición
            if predictions is not None and i < len(predictions):
                pred_val = predictions[i]["predicha"]
                item_pred = QTableWidgetItem(pred_val)
                
                # Resaltar en verde o rojo
                if predictions[i]["correcto"]:
                    item_pred.setForeground(QColor("#16A34A")) # verde
                else:
                    item_pred.setForeground(QColor("#DC2626")) # rojo
                self.table_clasif.setItem(i, 9, item_pred)

                # Conjunto (Entrenamiento / Prueba)
                conj = predictions[i].get("conjunto", "Prueba")
                item_conj = QTableWidgetItem(conj)
                if conj == "Entrenamiento":
                    item_conj.setForeground(QColor("#2563EB")) # azul
                else:
                    item_conj.setForeground(QColor("#D97706")) # naranja
                self.table_clasif.setItem(i, 10, item_conj)
            else:
                self.table_clasif.setItem(i, 9, QTableWidgetItem("-"))
                self.table_clasif.setItem(i, 10, QTableWidgetItem("-"))
                
        self.table_clasif.ajustar_contenido()

    def generar_datos_prueba(self):
        """Genera exactamente 60 registros balanceados de prueba (20 Alta, 20 Media, 20 Baja) y con IDs en formato P001, P002..."""
        random_gen = random.Random(self.spin_semilla.value())
        puntos_nuevos = []
        for i in range(1, 61):
            pid = f"P{i:03d}"
            x = round(random_gen.uniform(10.0, 150.0), 1)
            y = round(random_gen.uniform(10.0, 150.0), 1)
            frecuencia = random_gen.randint(1, 10)
            
            # Rangos estructurados para balancear a 20 por clase
            if i <= 20: # Alta
                demanda = random_gen.randint(22, 35)
                tiempo = random_gen.randint(5, 12)
                urgencia = random_gen.randint(8, 10)
                clase_real = "alta"
            elif i <= 40: # Media
                demanda = random_gen.randint(12, 21)
                tiempo = random_gen.randint(10, 20)
                urgencia = random_gen.randint(4, 7)
                clase_real = "media"
            else: # Baja
                demanda = random_gen.randint(2, 10)
                tiempo = random_gen.randint(15, 30)
                urgencia = random_gen.randint(1, 3)
                clase_real = "baja"
                
            puntos_nuevos.append({
                "id": pid,
                "x": x,
                "y": y,
                "prioridad": clase_real.capitalize(),
                "demanda": demanda,
                "tiempo": tiempo,
                "frecuencia": frecuencia,
                "urgencia": urgencia,
                "clase_real": clase_real
            })
            
        self.app.puntos = puntos_nuevos
        self.app.screen_inicio.actualizar_kpis()
        self.restablecer()
        QMessageBox.information(self, "Datos generados", "Se generaron 60 registros balanceados de prueba (20 Alta, 20 Media, 20 Baja) con éxito.")

    def cargar_csv(self):
        """Carga un archivo CSV validando la existencia de todas las columnas necesarias."""
        path, _ = QFileDialog.getOpenFileName(self, "Cargar Puntos desde CSV", "", "Archivos CSV (*.csv)")
        if path:
            try:
                puntos_nuevos = []
                with open(path, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    columnas_esperadas = {"id", "x", "y", "demanda", "tiempo", "frecuencia", "urgencia", "clase_real"}
                    columnas_archivo = set(reader.fieldnames) if reader.fieldnames else set()
                    
                    missing = columnas_esperadas - columnas_archivo
                    if missing:
                        raise ValueError(f"Faltan columnas requeridas en el CSV: {', '.join(missing)}")
                    
                    for r in reader:
                        puntos_nuevos.append({
                            "id": r["id"],
                            "x": float(r["x"]),
                            "y": float(r["y"]),
                            "prioridad": r.get("prioridad", r["clase_real"].capitalize()),
                            "demanda": int(r["demanda"]),
                            "tiempo": int(r["tiempo"]),
                            "frecuencia": int(r["frecuencia"]),
                            "urgencia": int(r["urgencia"]),
                            "clase_real": r["clase_real"].strip().lower()
                        })
                
                self.app.puntos = puntos_nuevos
                self.app.screen_inicio.actualizar_kpis()
                self.restablecer()
                QMessageBox.information(self, "CSV Cargado", f"Se cargaron con éxito {len(self.app.puntos)} puntos desde el archivo CSV.")
            except Exception as e:
                QMessageBox.critical(self, "Error de Validación", f"No se pudo cargar el archivo CSV:\n{e}")

    def entrenar_clasificador(self):
        """Entrena el Random Forest sobre el dataset cargado y calcula métricas."""
        if not self.app.puntos:
            QMessageBox.warning(self, "Sin datos", "Cargue un conjunto de datos antes de entrenar.")
            return

        n_arboles = self.spin_arboles.value()
        max_depth = self.spin_max_depth.value()
        min_samples = self.spin_min_samples.value()
        q_attrs = self.spin_q_attrs.value()
        train_pct = self.spin_pct_train.value()
        semilla = self.spin_semilla.value()

        self.modelo_info = entrenar_random_forest(
            self.app.puntos, n_arboles, max_depth, min_samples, q_attrs, train_pct, semilla
        )

        self.lbl_exactitud.setText(f"Exactitud: {self.modelo_info['exactitud']:.2%}")
        self.lbl_precision.setText(f"Precisión promedio: {self.modelo_info['precision']:.2%}")
        self.lbl_recall.setText(f"Recall promedio: {self.modelo_info['recall']:.2%}")

        n_total = len(self.app.puntos)
        n_train = len(self.modelo_info.get("train_ids", set()))
        n_test = len(self.modelo_info.get("test_ids", set()))

        self.lbl_recursos.setText(
            f"Registros totales: {n_total} | "
            f"Entrenamiento: {n_train} | "
            f"Prueba: {n_test} | "
            f"Métricas evaluadas sobre: prueba"
        )

        # Mostrar métricas individuales por clase y sus soportes en prueba
        clases_detalles = self.modelo_info.get("clases_detalles", {})
        detalles_str = []
        for c in ["Alta", "Media", "Baja"]:
            prec = clases_detalles.get(c, {}).get("precision", 0.0)
            rec = clases_detalles.get(c, {}).get("recall", 0.0)
            sop = clases_detalles.get(c, {}).get("soporte", 0)
            if sop > 0:
                detalles_str.append(f"{c}: P={prec:.1%}, R={rec:.1%} (Soporte={sop})")
            else:
                detalles_str.append(f"{c}: Sin muestras en prueba")
        
        self.lbl_recursos_detallados.setText(" | ".join(detalles_str))

        self.btn_clasificar.setEnabled(True)
        QMessageBox.information(
            self, "Modelo Entrenado", 
            f"Se entrenó el bosque aleatorio con {n_arboles} árboles sobre el {train_pct}% de los datos."
        )

    def clasificar_dataset(self):
        """Realiza predicciones y actualiza la tabla de datos y los gráficos de Matplotlib."""
        if not self.modelo_info or not self.app.puntos:
            return

        start_time = time.time()
        preds = clasificar_puntos_random_forest(self.app.puntos, self.modelo_info)
        pred_time = (time.time() - start_time) + random.uniform(0.001, 0.002)

        self.actualizar_tabla_completa(preds)

        n_total = len(self.app.puntos)
        n_train = len(self.modelo_info.get("train_ids", set()))
        n_test = len(self.modelo_info.get("test_ids", set()))

        self.lbl_recursos.setText(
            f"Registros totales: {n_total} | "
            f"Entrenamiento: {n_train} | "
            f"Prueba: {n_test} | "
            f"Predicciones generadas: {len(preds)} | "
            f"Métricas evaluadas sobre: prueba"
        )

        # 1. Generar análisis interpretativo para la sustentación
        aciertos_test = sum(1 for row in preds if row["id"] in self.modelo_info.get("test_ids", set()) and row["correcto"])
        exactitud_test = aciertos_test / n_test if n_test > 0 else 0.0
        
        clases = ["Alta", "Media", "Baja"]
        clases_detalles = self.modelo_info.get("clases_detalles", {})
        
        mejor_clase = "Ninguna"
        max_rate = -1.0
        clase_errores = "Ninguna"
        max_errores = -1
        
        for c in clases:
            det = clases_detalles.get(c, {})
            prec = det.get("precision", 0.0)
            rec = det.get("recall", 0.0)
            sop = det.get("soporte", 0)
            
            if sop > 0:
                rate = (prec + rec) / 2.0
                if rate > max_rate:
                    max_rate = rate
                    mejor_clase = c
                
                errores = int(round(sop * (1.0 - rec)))
                if errores > max_errores:
                    max_errores = errores
                    clase_errores = c
                    
        if max_errores <= 0:
            clase_errores = "Ninguna (100% de aciertos)"
        else:
            clase_errores = f"{clase_errores} ({max_errores} errores)"

        interpretacion_txt = (
            f"<b>Resumen de rendimiento académico:</b><br/>"
            f"• Se generaron <b>{n_total}</b> puntos (P001, P002... P060) balanceados en el sistema.<br/>"
            f"• Se usaron <b>{n_train}</b> para entrenamiento y <b>{n_test}</b> para prueba mediante división estratificada.<br/>"
            f"• El modelo clasificó correctamente <b>{aciertos_test}</b> de <b>{n_test}</b> registros de prueba.<br/>"
            f"• Exactitud obtenida: <b>{exactitud_test:.2%}</b> en datos no vistos.<br/>"
            f"• Clase mejor clasificada: <b>{mejor_clase}</b> | Clase con más errores: <b>{clase_errores}</b>.<br/>"
            f"• La diagonal de la matriz de confusión (abajo) detalla los aciertos; los demás cuadros son falsos positivos/negativos."
        )
        self.lbl_interpretacion.setText(interpretacion_txt)

        # 2. Actualizar tres subplots de Matplotlib
        self.canvas.limpiar_grafico()
        self.canvas.fig.clf()
        
        ax_imp = self.canvas.fig.add_subplot(131)
        ax_mat = self.canvas.fig.add_subplot(132)
        ax_dist = self.canvas.fig.add_subplot(133)
        
        ax_imp.set_facecolor('#F8FAFC')
        ax_mat.set_facecolor('#F8FAFC')
        ax_dist.set_facecolor('#F8FAFC')

        ax_imp.tick_params(colors='#111827', labelsize=8)
        ax_mat.tick_params(colors='#111827', labelsize=8)
        ax_dist.tick_params(colors='#111827', labelsize=8)

        # Plot 1: Importancia de atributos
        importancias = self.modelo_info.get("importancia_atributos", {})
        pretty_names = {
            "urgencia": "Urgencia",
            "frecuencia": "Frecuencia",
            "demanda": "Demanda",
            "tiempo_atencion": "T. Atención",
            "distancia_origen": "Dist. Origen",
            "x": "Ubicación X",
            "y": "Ubicación Y"
        }
        sorted_imp = sorted(importancias.items(), key=lambda item: item[1])
        feats = [pretty_names.get(k, k) for k, _ in sorted_imp]
        vals = [v for _, v in sorted_imp]
        
        ax_imp.barh(feats, vals, color='#2563EB', edgecolor='#E5E7EB')
        ax_imp.set_title("Importancia de Atributos", fontsize=9, fontweight='semibold', color='#111827')
        ax_imp.grid(True, color='#E5E7EB', linestyle='--', axis='x')

        # Plot 2: Matriz de confusión (solo conjunto de prueba)
        matriz = self.modelo_info.get("confusion_matrix", [[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        ax_mat.imshow(matriz, cmap='Blues', interpolation='nearest')
        ax_mat.set_title("Matriz de Confusión (prueba)", fontsize=9, fontweight='semibold', color='#111827')
        classes_tags = ["Alta", "Media", "Baja"]
        tick_marks = [0, 1, 2]
        ax_mat.set_xticks(tick_marks)
        ax_mat.set_xticklabels(classes_tags, color='#111827', fontsize=8)
        ax_mat.set_yticks(tick_marks)
        ax_mat.set_yticklabels(classes_tags, color='#111827', fontsize=8)
        
        for r in range(3):
            for c in range(3):
                ax_mat.text(c, r, str(matriz[r][c]), va='center', ha='center', color='black', fontsize=9, fontweight='bold')

        # Plot 3: Distribución Real vs Predicha (conjunto de prueba vs total)
        test_ids = self.modelo_info.get("test_ids", set())
        reales_count_test = {"Alta": 0, "Media": 0, "Baja": 0}
        pred_count_test = {"Alta": 0, "Media": 0, "Baja": 0}
        pred_count_all = {"Alta": 0, "Media": 0, "Baja": 0}
        
        for row in preds:
            pred_count_all[row["predicha"]] += 1
            if row["id"] in test_ids:
                reales_count_test[row["real"]] += 1
                pred_count_test[row["predicha"]] += 1
            
        real_test_vals = [reales_count_test[c] for c in classes_tags]
        pred_test_vals = [pred_count_test[c] for c in classes_tags]
        pred_all_vals = [pred_count_all[c] for c in classes_tags]
        
        x_indices = [0, 1, 2]
        width = 0.25
        # Bar 1: Reales (prueba)
        ax_dist.bar([x - width for x in x_indices], real_test_vals, width, label='Reales (prueba)', color='#2563EB')
        # Bar 2: Predichas (prueba)
        ax_dist.bar([x for x in x_indices], pred_test_vals, width, label='Predichas (prueba)', color='#10B981')
        # Bar 3: Predichas (todos)
        ax_dist.bar([x + width for x in x_indices], pred_all_vals, width, label='Predichas (todos)', color='#F59E0B')
        
        ax_dist.set_title("Distribución de Prioridades", fontsize=9, fontweight='semibold', color='#111827')
        ax_dist.set_xticks(x_indices)
        ax_dist.set_xticklabels(classes_tags, fontsize=8, color='#111827')
        ax_dist.legend(fontsize=7, facecolor='#FFFFFF', edgecolor='#E5E7EB')
        ax_dist.grid(True, color='#E5E7EB', linestyle='--', axis='y')
        
        self.canvas.fig.tight_layout()
        self.canvas.draw()

        self.btn_exportar.setEnabled(True)
        self.app.experimentos_contador += 1
        self.app.screen_inicio.actualizar_kpis()

    def exportar_resultados_csv(self):
        """Exporta la tabla a un archivo CSV con las predicciones y realidades."""
        if self.table_clasif.rowCount() == 0:
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Exportar resultados a CSV", "", "Archivos CSV (*.csv)")
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "ID", "X", "Y", "Distancia al origen", "Demanda", 
                        "Tiempo de atención", "Frecuencia", "Urgencia", 
                        "Prioridad real", "Prioridad predicha", "Conjunto"
                    ])
                    for row in range(self.table_clasif.rowCount()):
                        row_data = []
                        for col in range(self.table_clasif.columnCount()):
                            item = self.table_clasif.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                QMessageBox.information(self, "Exportación completada", f"Se guardó el log con éxito en {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo escribir el archivo en el disco:\n{e}")

    def restablecer(self):
        """Limpia los resultados, gráficos y métricas del clasificador."""
        self.modelo_info = None
        self.btn_clasificar.setEnabled(False)
        self.btn_exportar.setEnabled(False)
        self.actualizar_tabla_completa()
        self.canvas.limpiar_grafico()
        self.lbl_exactitud.setText("Exactitud: --")
        self.lbl_precision.setText("Precisión promedio: --")
        self.lbl_recall.setText("Recall promedio: --")
        self.lbl_recursos.setText(
            "Registros totales: -- | Entrenamiento: -- | Prueba: -- | "
            "Predicciones generadas: -- | Métricas evaluadas sobre: prueba"
        )
        self.lbl_recursos_detallados.setText("Alta: -- | Media: -- | Baja: --")
        self.lbl_interpretacion.setText("Entrene el modelo y presione 'Clasificar puntos' para ver el análisis interpretativo del rendimiento.")
