# -*- coding: utf-8 -*-
"""
SmartRoute: Módulo de Programación Genética

UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS
Facultad de Ingeniería de Sistemas e Informática
Curso: Análisis y Diseño de Algoritmos - Grupo 06

Implementación del algoritmo de Programación Genética para optimización
de rutas (TSP). Los individuos son permutaciones de puntos evaluadas
mediante una función de aptitud que combina distancia total y prioridad.

Responsable: Ryan
"""

import math
import random
import tracemalloc
import time


# =====================================================================
# ESTRUCTURAS DE DATOS
# =====================================================================

def calcular_distancia(p1, p2):
    """
    Calcula la distancia euclidiana entre dos puntos.
    d(p_a, p_b) = sqrt((x_b - x_a)^2 + (y_b - y_a)^2)
    Complejidad: O(1)
    """
    return math.sqrt((p2["x"] - p1["x"]) ** 2 + (p2["y"] - p1["y"]) ** 2)


def calcular_matriz_distancias(puntos):
    """
    Pre-calcula la matriz de distancias D[i][j] entre todos los puntos.
    Evita recalcular distancias en cada evaluación de aptitud.
    Complejidad: O(n^2) tiempo y espacio.
    """
    n = len(puntos)
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                D[i][j] = calcular_distancia(puntos[i], puntos[j])
    return D


# =====================================================================
# FUNCIÓN DE APTITUD
# =====================================================================

def evaluar_aptitud(individuo, D, peso_prioridad):
    """
    Evalúa el costo total de una ruta (individuo).

    f(σ) = Σ D[σ_i][σ_{i+1}] + λ * Σ (1 - prioridad(σ_i))

    Donde:
      - D es la matriz de distancias pre-calculada
      - λ (peso_prioridad) pondera la importancia de la prioridad
      - prioridad normalizada ∈ [0, 1] (Alta=1.0, Media=0.5, Baja=0.0)

    Complejidad: O(n)
    """
    costo = 0.0
    n = len(individuo)

    # Mapa de prioridad normalizada
    mapa_prioridad = {"alta": 1.0, "media": 0.5, "baja": 0.0}

    for i in range(n - 1):
        idx_actual   = individuo[i]["_idx"]
        idx_siguiente = individuo[i + 1]["_idx"]
        costo += D[idx_actual][idx_siguiente]

        pri_str = str(individuo[i].get("prioridad", "baja")).strip().lower()
        pri_val = mapa_prioridad.get(pri_str, 0.0)
        costo += peso_prioridad * (1.0 - pri_val)

    # Penalización del último punto
    pri_str = str(individuo[-1].get("prioridad", "baja")).strip().lower()
    pri_val = mapa_prioridad.get(pri_str, 0.0)
    costo += peso_prioridad * (1.0 - pri_val)

    return costo


# =====================================================================
# POBLACIÓN INICIAL
# =====================================================================

def generar_poblacion_inicial(puntos, tam_poblacion, rng):
    """
    Genera la población inicial con N permutaciones aleatorias de los puntos.
    Complejidad: O(N * n)
    """
    poblacion = []
    for _ in range(tam_poblacion):
        individuo = puntos[:]
        rng.shuffle(individuo)
        poblacion.append(individuo)
    return poblacion


# =====================================================================
# SELECCIÓN POR TORNEO
# =====================================================================

def seleccionar_por_torneo(poblacion, aptitudes, tam_torneo, rng):
    """
    Selecciona el mejor individuo de un subconjunto aleatorio de tamaño k.

    σ* = argmin_{σ ∈ T} f(σ),  |T| = k

    Complejidad: O(k)
    """
    indices = rng.sample(range(len(poblacion)), min(tam_torneo, len(poblacion)))
    ganador_idx = min(indices, key=lambda i: aptitudes[i])
    return poblacion[ganador_idx]


# =====================================================================
# OPERADOR DE CRUCE OX (Order Crossover)
# =====================================================================

def cruzar_ox(padre1, padre2, rng):
    """
    Cruce de orden (OX): preserva la validez de la permutación.

    - Copia el segmento padre1[i..j] en hijo1
    - Completa con los elementos de padre2 no presentes, en orden

    Complejidad: O(n)
    """
    n = len(padre1)
    i = rng.randint(0, n - 2)
    j = rng.randint(i + 1, n - 1)

    def _ox(p1, p2):
        hijo = [None] * n
        segmento_ids = set(p["id"] for p in p1[i:j + 1])

        # Copiar segmento del padre1
        for k in range(i, j + 1):
            hijo[k] = p1[k]

        # Completar con elementos de padre2 en orden circular
        restantes = [p for p in p2 if p["id"] not in segmento_ids]
        pos_libre = [(k) for k in range(n) if hijo[k] is None]
        for idx, p in zip(pos_libre, restantes):
            hijo[idx] = p

        return hijo

    hijo1 = _ox(padre1, padre2)
    hijo2 = _ox(padre2, padre1)
    return hijo1, hijo2


# =====================================================================
# OPERADOR DE MUTACIÓN POR INTERCAMBIO
# =====================================================================

def mutar_intercambio(individuo, rng):
    """
    Intercambia dos posiciones aleatorias distintas del individuo.

    σ'_i = σ_j,  σ'_j = σ_i

    Complejidad: O(1)
    """
    n = len(individuo)
    if n < 2:
        return individuo
    i, j = rng.sample(range(n), 2)
    individuo[i], individuo[j] = individuo[j], individuo[i]
    return individuo


# =====================================================================
# ALGORITMO PRINCIPAL
# =====================================================================

def programacion_genetica(
    puntos,
    tam_poblacion,
    generaciones,
    tasa_cruce,
    tasa_mutacion,
    tam_torneo,
    peso_prioridad,
    semilla=42
):
    """
    Algoritmo de Programación Genética para optimización de rutas (TSP).

    Parámetros:
      puntos         : list[dict] — puntos con claves id, x, y, prioridad, demanda, tiempo, frecuencia, urgencia
      tam_poblacion  : int  — N, número de individuos en la población
      generaciones   : int  — G, número de generaciones a evolucionar
      tasa_cruce     : float ∈ [0,1] — rc, probabilidad de cruce entre dos padres
      tasa_mutacion  : float ∈ [0,1] — rm, probabilidad de mutación por individuo
      tam_torneo     : int  — k, tamaño del subconjunto de selección
      peso_prioridad : float ≥ 0  — λ, ponderación de prioridad vs distancia
      semilla        : int  — semilla aleatoria para reproducibilidad

    Retorna dict con:
      ruta           : list[str]   — IDs de puntos en orden óptimo encontrado
      costo          : float       — costo de la mejor ruta
      aptitud        : float       — valor de la función de aptitud de la mejor ruta
      gen_encontrado : int         — generación en que se encontró la mejor solución
      regla          : str         — descripción textual de la función de aptitud usada
      arbol          : str         — representación del árbol de decisión de la función
      tiempo         : float       — tiempo de ejecución en segundos
      memoria        : float       — memoria pico usada en MB
    """
    if not puntos:
        return {
            "ruta": [], "costo": 0.0, "aptitud": 0.0,
            "gen_encontrado": 0, "regla": "", "arbol": "",
            "tiempo": 0.0, "memoria": 0.0
        }

    rng = random.Random(semilla)

    # --- Preparación: añadir índice a cada punto para acceso O(1) a la matriz ---
    puntos_idx = []
    for i, p in enumerate(puntos):
        p_copia = dict(p)
        p_copia["_idx"] = i
        puntos_idx.append(p_copia)

    # --- Pre-calcular matriz de distancias D ∈ R^{n×n} ---
    tracemalloc.start()
    inicio_time = time.perf_counter()

    D = calcular_matriz_distancias(puntos_idx)
    n = len(puntos_idx)

    # --- Generar población inicial Π^(0) ---
    poblacion = generar_poblacion_inicial(puntos_idx, tam_poblacion, rng)

    # --- Evaluar aptitudes iniciales ---
    aptitudes = [evaluar_aptitud(ind, D, peso_prioridad) for ind in poblacion]

    # --- Rastrear mejor individuo global a través de todas las generaciones ---
    mejor_idx   = min(range(len(aptitudes)), key=lambda i: aptitudes[i])
    mejor_individuo  = poblacion[mejor_idx][:]
    mejor_aptitud    = aptitudes[mejor_idx]
    mejor_generacion = 0

    # --- Ciclo evolutivo principal ---
    for t in range(1, generaciones + 1):
        nueva_poblacion = []

        while len(nueva_poblacion) < tam_poblacion:
            # Selección por torneo
            padre1 = seleccionar_por_torneo(poblacion, aptitudes, tam_torneo, rng)
            padre2 = seleccionar_por_torneo(poblacion, aptitudes, tam_torneo, rng)

            # Cruce OX
            if rng.random() < tasa_cruce:
                hijo1, hijo2 = cruzar_ox(padre1, padre2, rng)
            else:
                hijo1 = padre1[:]
                hijo2 = padre2[:]

            # Mutación por intercambio
            if rng.random() < tasa_mutacion:
                hijo1 = mutar_intercambio(hijo1, rng)
            if rng.random() < tasa_mutacion:
                hijo2 = mutar_intercambio(hijo2, rng)

            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(hijo2)

        poblacion = nueva_poblacion

        # Evaluar nueva generación
        aptitudes = [evaluar_aptitud(ind, D, peso_prioridad) for ind in poblacion]

        # Actualizar mejor global
        mejor_gen_idx = min(range(len(aptitudes)), key=lambda i: aptitudes[i])
        if aptitudes[mejor_gen_idx] < mejor_aptitud:
            mejor_aptitud    = aptitudes[mejor_gen_idx]
            mejor_individuo  = poblacion[mejor_gen_idx][:]
            mejor_generacion = t

    fin_time = time.perf_counter()
    _, pico_memoria = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tiempo_total = fin_time - inicio_time
    memoria_mb   = pico_memoria / (1024.0 * 1024.0)

    # --- Construir ruta como lista de IDs ---
    ruta_ids = [p["id"] for p in mejor_individuo]

    # --- Calcular costo real en distancia pura (sin penalización) ---
    costo_distancia = 0.0
    for i in range(len(mejor_individuo) - 1):
        ia = mejor_individuo[i]["_idx"]
        ib = mejor_individuo[i + 1]["_idx"]
        costo_distancia += D[ia][ib]

    # --- Descripción textual de la función de aptitud ---
    regla = f"distancia + {peso_prioridad} * (1 - prioridad_normalizada)"
    arbol = (
        f"           +\n"
        f"          / \\\n"
        f"    distancia  *\n"
        f"              / \\\n"
        f"            {peso_prioridad}   (1-pri)"
    )

    return {
        "ruta":           ruta_ids,
        "costo":          costo_distancia,
        "aptitud":        mejor_aptitud,
        "gen_encontrado": mejor_generacion,
        "regla":          regla,
        "arbol":          arbol,
        "tiempo":         tiempo_total,
        "memoria":        memoria_mb
    }