import random
import math

class NodoArbol:
    """Clase que representa un nodo (interno o de hoja) en el Árbol de Decisión."""
    def __init__(self, feature=None, threshold=None, left=None, right=None, *, value=None):
        self.feature = feature          # Nombre de la característica usada para la división
        self.threshold = threshold      # Umbral numérico para la división
        self.left = left                # NodoArbol hijo izquierdo
        self.right = right              # NodoArbol hijo derecho
        self.value = value              # Valor de la clase (solo si es un nodo de hoja)

    def es_hoja(self):
        """Retorna True si el nodo es una hoja final de predicción."""
        return self.value is not None


def generar_muestra_bootstrap(X, y, random_gen):
    """
    Genera un dataset Db muestreando registros con reemplazo a partir de X e y.
    Tiene la misma longitud que el dataset original.
    """
    n = len(X)
    X_boot = []
    y_boot = []
    for _ in range(n):
        idx = random_gen.randint(0, n - 1)
        X_boot.append(X[idx])
        y_boot.append(y[idx])
    return X_boot, y_boot


def calcular_gini(y_sub):
    """
    Calcula el índice de impureza de Gini para una lista de etiquetas de clase.
    Fórmula: Gini = 1 - suma(p_i^2)
    """
    if not y_sub:
        return 0.0
    n = len(y_sub)
    counts = {}
    for val in y_sub:
        counts[val] = counts.get(val, 0) + 1
    sum_sq = sum((count / n) ** 2 for count in counts.values())
    return 1.0 - sum_sq


def calcular_gini_ponderado(y_izq, y_der):
    """
    Calcula el Gini ponderado de una división candidata de datos.
    Fórmula: Gini_pond = (N_izq / N) * Gini_izq + (N_der / N) * Gini_der
    """
    n_izq = len(y_izq)
    n_der = len(y_der)
    n_total = n_izq + n_der
    if n_total == 0:
        return 0.0
    gini_izq = calcular_gini(y_izq)
    gini_der = calcular_gini(y_der)
    return (n_izq / n_total) * gini_izq + (n_der / n_total) * gini_der


def dividir(X, y, feature, threshold):
    """
    Divide las muestras en hijo izquierdo (<= umbral) e hijo derecho (> umbral).
    """
    X_izq, y_izq = [], []
    X_der, y_der = [], []
    for i in range(len(X)):
        if X[i][feature] <= threshold:
            X_izq.append(X[i])
            y_izq.append(y[i])
        else:
            X_der.append(X[i])
            y_der.append(y[i])
    return X_izq, y_izq, X_der, y_der


def clase_mayoritaria(y_sub):
    """
    Retorna la clase más frecuente (moda) de una lista de etiquetas.
    En caso de empate, retorna la de menor orden alfabético.
    """
    if not y_sub:
        return None
    counts = {}
    for val in y_sub:
        counts[val] = counts.get(val, 0) + 1
    # max() con desempate alfabético por clave si empatan en valor
    return max(counts.keys(), key=lambda k: (counts[k], k))


class ArbolDecision:
    """Clase que implementa un árbol de decisión de clasificación construido con índice Gini."""
    def __init__(self, max_depth=10, min_samples_split=2, max_features=None, random_state=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.random_state = random_state
        self.root = None
        self.random_gen = random.Random(random_state)
        # Registro de reducción de impureza para importancia de atributos
        self.feature_importances_dict = {}

    def fit(self, X, y, feature_names):
        """Construye el árbol de decisión entrenándolo sobre X e y."""
        self.feature_importances_dict = {name: 0.0 for name in feature_names}
        self.root = self._construir_arbol(X, y, feature_names, depth=0)

    def _construir_arbol(self, X, y, feature_names, depth):
        n_muestras = len(X)
        if n_muestras == 0:
            return None

        # 1. Si todos los registros pertenecen a la misma clase, retornar hoja con esa clase.
        clases_unicas = set(y)
        if len(clases_unicas) == 1:
            return NodoArbol(value=list(clases_unicas)[0])

        # 2. Si se alcanza la profundidad máxima, retornar hoja con la clase mayoritaria.
        if depth >= self.max_depth:
            return NodoArbol(value=clase_mayoritaria(y))

        # 3. Si el tamaño del subconjunto es menor o igual al mínimo de muestras, retornar hoja con la clase mayoritaria.
        if n_muestras < self.min_samples_split:
            return NodoArbol(value=clase_mayoritaria(y))

        # 4. Seleccionar aleatoriamente q atributos (max_features).
        q = self.max_features
        if q is None:
            q = len(feature_names)
        else:
            q = min(q, len(feature_names))
        
        # Selección de q atributos aleatorios sin reemplazo
        features_candidatas = self.random_gen.sample(feature_names, q)

        # 5. Buscar el mejor atributo y mejor umbral usando índice Gini ponderado.
        mejor_gini = float('inf')
        mejor_feature = None
        mejor_threshold = None
        gini_actual = calcular_gini(y)

        for feature in features_candidatas:
            # Obtener valores numéricos únicos ordenados para este atributo
            valores = sorted(list(set(row[feature] for row in X)))
            if len(valores) <= 1:
                continue
            
            # Evaluar puntos medios como posibles umbrales de división
            for idx in range(len(valores) - 1):
                threshold = (valores[idx] + valores[idx+1]) / 2.0
                X_izq, y_izq, X_der, y_der = dividir(X, y, feature, threshold)
                
                # Evitar divisiones que dejen un subconjunto vacío
                if not y_izq or not y_der:
                    continue
                
                gini_ponderado = calcular_gini_ponderado(y_izq, y_der)
                if gini_ponderado < mejor_gini:
                    mejor_gini = gini_ponderado
                    mejor_feature = feature
                    mejor_threshold = threshold

        # Si no se encuentra ninguna división válida que reduzca impureza
        if mejor_feature is None:
            return NodoArbol(value=clase_mayoritaria(y))

        # Guardar ganancia de impureza Gini ponderada por el tamaño del nodo (reducción de impureza total)
        ganancia = (gini_actual - mejor_gini) * n_muestras
        self.feature_importances_dict[mejor_feature] = self.feature_importances_dict.get(mejor_feature, 0.0) + ganancia

        # 6. Dividir el conjunto en hijo izquierdo e hijo derecho.
        X_izq, y_izq, X_der, y_der = dividir(X, y, mejor_feature, mejor_threshold)

        # 7. Construir recursivamente ambos hijos.
        hijo_izq = self._construir_arbol(X_izq, y_izq, feature_names, depth + 1)
        hijo_der = self._construir_arbol(X_der, y_der, feature_names, depth + 1)

        # Manejar fallos de división inválida
        if hijo_izq is None:
            return NodoArbol(value=clase_mayoritaria(y))
        if hijo_der is None:
            return NodoArbol(value=clase_mayoritaria(y))

        # 8. Retornar nodo interno con atributo, umbral, hijo izquierdo e hijo derecho.
        return NodoArbol(feature=mejor_feature, threshold=mejor_threshold, left=hijo_izq, right=hijo_der)

    def predict_one(self, x):
        """Predice recursivamente la etiqueta de clase de una sola muestra x (diccionario)."""
        return self._predecir_recursivo(self.root, x)

    def _predecir_recursivo(self, nodo, x):
        if nodo is None:
            return None
        if nodo.es_hoja():
            return nodo.value
        # Evaluar contra el umbral numérico
        if x[nodo.feature] <= nodo.threshold:
            return self._predecir_recursivo(nodo.left, x)
        else:
            return self._predecir_recursivo(nodo.right, x)


class RandomForest:
    """Clase que representa el ensamble del Bosque Aleatorio construido desde cero."""
    def __init__(self, n_trees=20, max_depth=6, min_samples_split=2, max_features=3, random_state=42):
        self.n_trees = n_trees                      # B: número de árboles del bosque
        self.max_depth = max_depth                  # maxProfundidad
        self.min_samples_split = min_samples_split  # minMuestras
        self.max_features = max_features            # q: número de atributos seleccionados por división
        self.random_state = random_state            # Semilla aleatoria
        self.arboles = []                           # F: lista de árboles
        self.feature_names = []
        self.random_gen = random.Random(random_state)

    def fit(self, X, y, feature_names):
        """Entrena los B árboles del bosque usando bootstrap y muestreo de atributos."""
        self.feature_names = feature_names
        self.arboles = []
        
        # 1. Crear una lista vacía F (self.arboles)
        # 2. Para b desde 1 hasta B:
        for _ in range(self.n_trees):
            # Obtener una semilla reproducible e independiente para cada árbol
            semilla_arbol = self.random_gen.randint(0, 999999)
            
            # Generar muestra bootstrap Db
            X_boot, y_boot = generar_muestra_bootstrap(X, y, random.Random(semilla_arbol))
            
            # Construir árbol de decisión usando Db
            arbol = ArbolDecision(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                max_features=self.max_features,
                random_state=semilla_arbol
            )
            arbol.fit(X_boot, y_boot, feature_names)
            
            # Agregar el árbol a F
            self.arboles.append(arbol)

    def predict_one(self, x):
        """Predice la clase para una sola muestra mediante votación mayoritaria del bosque."""
        # 1. Cada árbol predice una clase.
        # 2. El Random Forest acumula votos.
        votos = {}
        for arbol in self.arboles:
            pred = arbol.predict_one(x)
            if pred is not None:
                votos[pred] = votos.get(pred, 0) + 1
        
        # 3. La clase final es la clase con más votos.
        if not votos:
            return None
        return max(votos.keys(), key=lambda k: (votos[k], k))

    def predict(self, X):
        """Predice clases para una lista completa de muestras."""
        return [self.predict_one(x) for x in X]

    def get_feature_importances(self):
        """Retorna la importancia promedio normalizada de cada atributo según ganancia Gini."""
        importancias = {name: 0.0 for name in self.feature_names}
        total_acumulado = 0.0
        
        for arbol in self.arboles:
            for feat, val in arbol.feature_importances_dict.items():
                importancias[feat] += val
                total_acumulado += val
                
        # Normalizar para que sumen 1.0
        if total_acumulado > 0.0:
            for feat in importancias:
                importancias[feat] /= total_acumulado
                
        return importancias
