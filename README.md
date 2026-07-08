# SmartRoute

Sistema comparativo de algoritmos inteligentes para predicción y optimización de rutas.

## Descripción general

SmartRoute es una aplicación académica de escritorio desarrollada en Python utilizando PySide6 para la interfaz gráfica y Matplotlib para la visualización interactiva de gráficos. 

El sistema está diseñado para el análisis y diseño de algoritmos de optimización de rutas en redes de transporte, permitiendo trabajar con puntos de atención al cliente, clasificar la prioridad de los mismos y ejecutar algoritmos de optimización de recorridos (TSP - Traveling Salesperson Problem).

Actualmente, el sistema se encuentra desarrollado e integrado en su totalidad, incluyendo los siguientes módulos:
* **Random Forest**: Algoritmo de ensamble clasificador para predecir la prioridad (Alta, Media, Baja) de los puntos de servicio.
* **Vecino más cercano** (Nearest Neighbor): Heurística voraz para construir rutas iniciales de TSP.
* **Colonia de hormigas** (Ant Colony Optimization): Metaheurística bio-inspirada para optimización recursiva de rutas.
* **Programación genética** (Genetic Programming): Generador evolutivo de reglas y fórmulas algebraicas para optimización y ruteo.

---

## Estado actual del proyecto

El estado de los componentes del software es el siguiente:
* **Interfaz principal (Shell / Dashboard)**: Creada y estilizada.
* **Navegación entre módulos**: Creada y funcional.
* **Módulo Random Forest**: Implementado en su totalidad.
* **Generación de datos de prueba para Random Forest**: Implementada (genera 60 registros balanceados).
* **Entrenamiento de Random Forest**: Implementado (soporta split estratificado y registro de recursos reales).
* **Clasificación de puntos**: Implementada de forma interactiva.
* **Métricas del clasificador**: Implementadas (Accuracy, Macro Precision, Macro Recall y matriz de confusión calculadas sobre el set de prueba).
* **Gráficos del módulo Random Forest**: Implementados (importancia de atributos, matriz de confusión 3x3 y distribución real vs predicha).
* **Vecino más cercano**: Implementado y conectado (incluye medición de tiempo y memoria en MB).
* **Colonia de hormigas**: Implementado y conectado (incluye parámetros avanzados y convergencia interactiva).
* **Programación genética**: Implementado y conectado (grafica la evolución de aptitud y dibuja el árbol sintáctico).
* **Comparación global**: Implementado y conectado (compara los tiempos, memoria y costos reales de los algoritmos).
* **Experimentos de escalabilidad**: Implementado y conectado (ejecuta pruebas masivas reales en la interfaz).

---

## Integrantes y responsabilidades

| Integrante | Responsabilidad | Estado |
| ---------- | --------------- | ------ |
| **Katherine** | Random Forest | Implementado |
| **Gabriel** | Vecino más cercano | Implementado |
| **Diana** | Colonia de hormigas | Implementado |
| **Ryan** | Programación genética | Implementado |

---

## Estructura del proyecto

La estructura de carpetas real del código fuente es la siguiente:

```text
smartroute/
│
├── backend/                             # Carpeta destinada a la lógica de algoritmos
│   ├── __init__.py
│   ├── algorithms.py                    # Wrapper principal e integración
│   ├── ant_colony.py                    # Algoritmo de Colonia de Hormigas (ACO)
│   ├── genetic_programming.py           # Algoritmo de Programación Genética
│   ├── nearest_neighbor.py              # Algoritmo de Vecino Más Cercano
│   └── random_forest.py                 # Algoritmo RandomForest desarrollado desde cero
│
├── frontend/                            # Carpeta destinada a la interfaz de usuario en PySide6
│   ├── __init__.py
│   ├── main.py                          # Punto de entrada principal de la aplicación
│   ├── styles.py                        # Definición centralizada del tema y hojas de estilos (QSS)
│   │
│   ├── components/                      # Componentes visuales personalizados reutilizables
│   │   ├── __init__.py
│   │   ├── canvas_grafico.py            # Canvas integrado de Matplotlib
│   │   ├── page_header.py
│   │   ├── parameter_card.py
│   │   ├── plot_card.py
│   │   ├── result_card.py
│   │   ├── sidebar_button.py
│   │   └── styled_table.py              # Tabla autoajustable
│   │
│   └── screens/                         # Vistas de la aplicación (QStackedWidget)
│       ├── __init__.py
│       ├── acerca.py
│       ├── comparacion.py
│       ├── datos.py
│       ├── experimentos.py
│       ├── genetica.py
│       ├── hormigas.py
│       ├── inicio.py
│       ├── random_forest.py             # Pantalla interactiva del módulo Random Forest
│       └── vecino.py
│
├── casos_prueba.py                      # Script de pruebas automáticas y proyecciones asintóticas
├── README.md
└── requirements.txt                     # Dependencias del proyecto
```

### Descripción breve de componentes:
* **frontend/main.py**: Punto de entrada de la aplicación. Inicializa el ciclo de Qt, aplica la hoja de estilos y gestiona el enrutamiento de vistas.
* **backend/**: Contiene las implementaciones matemáticas de los algoritmos de cálculo.
* **frontend/**: Código de renderizado de la UI de PySide6, paneles de control y lienzos gráficos.

---

## Parámetros disponibles

* **Número de árboles (B)**: Cantidad de árboles de decisión independientes que conformarán el bosque aleatorio.
* **Profundidad máxima (h)**: Límite máximo de niveles al construir recursivamente cada árbol (evita sobreajuste).
* **Mínimo de muestras split**: Cantidad mínima de registros requerida en un nodo interno para continuar la ramificación.
* **Atributos por división (q)**: Número de variables aleatorias evaluadas en cada división de nodo (máximo 7).
* **Porcentaje de entrenamiento**: Proporción de datos utilizada para el ajuste (`70%-80%` recomendado).
* **Semilla aleatoria**: Valor numérico inicializador del generador aleatorio para garantizar la reproducibilidad.

---

## Formato esperado para CSV

Si deseas cargar tu propio conjunto de datos a través de la interfaz, el CSV debe contar obligatoriamente con la siguiente fila de encabezado:

```csv
id,x,y,demanda,tiempo,frecuencia,urgencia,clase_real
```

### Reglas de datos:
* `id`: Identificador único del punto (ej. `P001`).
* `x`, `y`: Coordenadas numéricas de posición.
* `demanda`, `tiempo`, `frecuencia`, `urgencia`: Valores numéricos enteros o decimales.
* `clase_real`: Prioridad real del punto, debiendo ser exactamente uno de los siguientes valores:
  * `alta`
  * `media`
  * `baja`

---

## Instalación y ejecución

### En Windows:
Si tienes múltiples versiones de Python instaladas (por ejemplo, a través de MSYS2), se recomienda usar el lanzador oficial de Windows `py` en lugar de `python`:

**Usando Entorno Virtual:**
```bash
# 1. Crear el entorno virtual
py -m venv venv

# 2. Activar el entorno virtual
venv\Scripts\activate

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
py frontend/main.py

# 5. Ejecutar las pruebas de escalabilidad y casos de prueba
py casos_prueba.py
```

**Ejecución Global (sin entorno virtual):**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
py frontend/main.py

# Ejecutar pruebas de escalabilidad
py casos_prueba.py
```

### En Linux / macOS:
```bash
# 1. Crear el entorno virtual
python3 -m venv venv

# 2. Activar el entorno virtual
source venv/bin/activate

# 3. Instalar las dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python frontend/main.py

# 5. Ejecutar las pruebas de escalabilidad y casos de prueba
python casos_prueba.py
```

---

## Indicaciones para los demás integrantes

Para mantener la consistencia del repositorio y no alterar la parte de Random Forest, se deben seguir estas directrices:

1. **No modificar el módulo Random Forest sin coordinar**: No edites de forma directa los archivos `backend/random_forest.py` y `frontend/screens/random_forest.py`.
2. **No cambiar la interfaz pública del clasificador**: Evita alterar la firma de métodos esenciales del motor matemático (`fit()`, `predict()`, `predict_one()`, `get_feature_importances()`).
3. **Cada algoritmo debe tener su propio archivo**: Trabaja tu algoritmo en un módulo independiente dentro de la carpeta `backend/` (ej. `backend/nearest_neighbor.py`, `backend/ant_colony.py` o equivalentes).
4. **No mezclar lógica de algoritmos**: No agregues funciones relacionadas con Vecino Más Cercano, Colonia de Hormigas o Programación Genética dentro del archivo `backend/random_forest.py`.
5. **No usar Random Forest como algoritmo de optimización de rutas**: Recuerda que Random Forest solo clasifica la urgencia de los puntos. Tus algoritmos de ruta pueden consultar esta predicción como atributo de soporte, pero no deben intentar trazar caminos a través del bosque clasificador.
6. **Mantener la separación de responsabilidades (MVC)**: La matemática y lógica de cálculo debe residir en `backend/`. La construcción visual de los controles, inputs y tablas en `frontend/` y `frontend/screens/`.
7. **Modificar main.py solo para integración**: Limita tus cambios en `frontend/main.py` a la importación y conexión del disparador de navegación lateral de tu pantalla.
8. **No agregar dependencias sin mutuo acuerdo**: No agregues librerías pesadas en `requirements.txt` sin previa conversación del equipo.
9. **Mantener compatibilidad del modelo de datos**: Los puntos leídos por tus algoritmos deben seguir la estructura unificada de diccionarios con llaves `id`, `x`, `y`, `demanda`, `tiempo`, `frecuencia`, `urgencia`, `clase_real` y `prioridad`.

---

## Control de Pruebas y Validación

Todos los algoritmos han sido validados con el script central `casos_prueba.py`. Este script genera dinámicamente conjuntos de datos aleatorios, ejecuta las funciones correspondientes y mide sus métricas de hardware de manera formal. Además, proyecta las métricas para conjuntos a gran escala (N=10^6) y extremos (N=10^10) para el análisis de complejidad asintótica.

---


## Uso responsable de inteligencia artificial

Este software ha sido diseñado con fines académicos. El uso de herramientas de asistencia basadas en Inteligencia Artificial se ha enfocado de manera responsable como apoyo para la refactorización de estilos visuales, la redacción de explicaciones de la interfaz y la estructuración del código fuente. 
