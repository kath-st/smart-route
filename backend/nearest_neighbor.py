# -*- coding: utf-8 -*-
"""
SmartRoute – Algoritmo del Vecino Más Cercano
=============================================
UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS
Facultad de Ingeniería de Sistemas e Informática
Curso: Análisis y Diseño de Algoritmos – Grupo 06

Implementación matemática completa del algoritmo heurístico voraz
del Vecino Más Cercano para el Problema del Viajante (TSP).

Complejidad temporal : O(n²)
Complejidad espacial : O(n²)  [por la matriz de distancias]
"""

import math
import time
import tracemalloc


# ─────────────────────────────────────────────────────────────────────────────
# Funciones de distancia
# ─────────────────────────────────────────────────────────────────────────────

def _distancia_euclidiana(p1: dict, p2: dict) -> float:
    """Distancia euclidiana entre dos puntos con claves 'x' e 'y'.

    d(pₐ, p_b) = √[(x_b − x_a)² + (y_b − y_a)²]
    """
    return math.sqrt((p2["x"] - p1["x"]) ** 2 + (p2["y"] - p1["y"]) ** 2)


def _distancia_ponderada(p1: dict, p2: dict) -> float:
    """Distancia euclidiana ajustada inversamente por la prioridad del destino.

    Penaliza distancias hacia puntos de baja prioridad y favorece los de alta.
    Mapeo de prioridad: Alta → 3, Media → 2, Baja → 1.

    Criterio: d_pond = d(pₐ, p_b) / prioridad(p_b)
    """
    PRIORIDAD_MAP = {"Alta": 3, "Media": 2, "Baja": 1}
    prio = PRIORIDAD_MAP.get(p2.get("prioridad", "Baja"), 1)
    dist = _distancia_euclidiana(p1, p2)
    return dist / prio


def _construir_matriz_distancias(puntos: list, ponderada: bool) -> list:
    """Construye la matriz D[i][j] de distancias entre todos los pares de puntos.

    Complejidad: O(n²)
    """
    n = len(puntos)
    fn = _distancia_ponderada if ponderada else _distancia_euclidiana
    # Matriz simétrica n×n
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if ponderada:
                D[i][j] = _distancia_ponderada(puntos[i], puntos[j])  # prioridad de j
            else:
                D[i][j] = _distancia_euclidiana(puntos[i], puntos[j])
    return D


# ─────────────────────────────────────────────────────────────────────────────
# Núcleo del algoritmo
# ─────────────────────────────────────────────────────────────────────────────

def vecino_mas_cercano(puntos: list, id_inicio: str,
                       criterio: str, regresar_origen: bool) -> dict:
    """Ejecuta el algoritmo del Vecino Más Cercano.

    Parámetros
    ----------
    puntos          : lista de dicts con claves id, x, y, prioridad, …
    id_inicio       : id del punto de partida
    criterio        : 'Solo distancia física' | 'Distancia ponderada por prioridad'
    regresar_origen : si True, cierra el ciclo volviendo al punto inicial

    Retorna
    -------
    dict con:
        ruta        – lista ordenada de ids visitados
        distancia   – costo total euclidiano real del recorrido
        tiempo      – segundos de cómputo
        memoria     – KB de memoria máxima usada durante el algoritmo
        operaciones – número de comparaciones realizadas (≈ n²)
    """
    if not puntos:
        return {"ruta": [], "distancia": 0.0,
                "tiempo": 0.0, "memoria": 0.0, "operaciones": 0}

    # ── Inicio de medición ────────────────────────────────────────────────────
    tracemalloc.start()
    t_inicio = time.perf_counter()

    n = len(puntos)
    ponderada = (criterio == "Distancia ponderada por prioridad")

    # Índice id → posición en la lista
    idx_por_id = {p["id"]: i for i, p in enumerate(puntos)}
    inicio_idx = idx_por_id.get(id_inicio, 0)

    # Matriz de distancias D (criterio seleccionado) – O(n²)
    D = _construir_matriz_distancias(puntos, ponderada)

    # ── Recorrido voraz ───────────────────────────────────────────────────────
    visitado = [False] * n          # V (conjunto de visitados)
    orden_indices = []              # σ (secuencia de índices)
    operaciones = 0                 # contador de comparaciones

    actual = inicio_idx
    visitado[actual] = True
    orden_indices.append(actual)

    for _ in range(n - 1):
        mejor_j = -1
        mejor_d = math.inf

        # p* = arg min { D[actual][j] : j ∉ V }
        for j in range(n):
            operaciones += 1
            if not visitado[j] and D[actual][j] < mejor_d:
                mejor_d = D[actual][j]
                mejor_j = j

        visitado[mejor_j] = True
        orden_indices.append(mejor_j)
        actual = mejor_j

    # Cerrar ciclo si se requiere
    if regresar_origen:
        orden_indices.append(inicio_idx)

    # ── Calcular costo euclidiano REAL del recorrido ──────────────────────────
    # (siempre distancia física, independientemente del criterio de selección)
    distancia_real = 0.0
    for k in range(len(orden_indices) - 1):
        distancia_real += _distancia_euclidiana(
            puntos[orden_indices[k]],
            puntos[orden_indices[k + 1]]
        )

    t_fin = time.perf_counter()
    _, pico_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    ruta_ids = [puntos[i]["id"] for i in orden_indices]
    memoria_mb = pico_mem / (1024.0 * 1024.0)

    return {
        "ruta":        ruta_ids,
        "costo":       distancia_real,
        "distancia":   distancia_real,
        "tiempo":      t_fin - t_inicio,
        "memoria":     memoria_mb,
        "operaciones": operaciones,
    }
