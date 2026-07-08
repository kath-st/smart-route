# -*- coding: utf-8 -*-
"""
Algoritmo de Optimización por Colonia de Hormigas (ACO) para TSP.
Estructura modular basada estrictamente en los pseudocódigos del documento del proyecto (Sección 3.3.1).
"""
import math
import random

def calcular_distancia_euclidiana(p1, p2):
    """Calcula la distancia entre dos puntos (Función auxiliar)."""
    return math.sqrt((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)

# =====================================================================
# 1. Función Inicializar_Parametros
# =====================================================================
def inicializar_parametros(n_nodos, distancias, tau_0):
    feromona = [[tau_0 for _ in range(n_nodos)] for _ in range(n_nodos)]
    heuristica = [[0.0 for _ in range(n_nodos)] for _ in range(n_nodos)]
    
    for i in range(n_nodos):
        for j in range(n_nodos):
            if i != j and distancias[i][j] > 0:
                heuristica[i][j] = 1.0 / distancias[i][j]
                
    return feromona, heuristica

# =====================================================================
# 2. Función Seleccion_Por_Ruleta
# =====================================================================
def seleccion_por_ruleta(probabilidad_parcial, suma_probabilidades, nodos_destinos):
    # Si las probabilidades son 0, elegimos al azar como medida de seguridad
    if suma_probabilidades == 0.0:
        return random.choice(nodos_destinos)
        
    r = random.uniform(0.0, suma_probabilidades)
    suma_acumulada = 0.0
    
    for indice, atractivo in enumerate(probabilidad_parcial):
        suma_acumulada = suma_acumulada + atractivo
        if suma_acumulada >= r:
            return nodos_destinos[indice]
            
    # Retornar el último nodo evaluado por defecto (por errores de precisión de coma flotante)
    return nodos_destinos[-1]

# =====================================================================
# 3. Función Calcular_Transicion
# =====================================================================
def calcular_transicion(nodo_actual, lista_tabu, n_nodos, feromona, heuristica, alpha, beta):
    visitados = set(lista_tabu)
    # nodos_no_visitados = G.nodos - lista_tabu
    nodos_no_visitados = [i for i in range(n_nodos) if i not in visitados]
    
    suma_probabilidades = 0.0
    probabilidad_parcial = []
    
    for nodo_destino in nodos_no_visitados:
        # atractivo = (feromona^alpha) * (heuristica^beta)
        tau = feromona[nodo_actual][nodo_destino] ** alpha
        eta = heuristica[nodo_actual][nodo_destino] ** beta
        atractivo = tau * eta
        
        probabilidad_parcial.append(atractivo)
        suma_probabilidades = suma_probabilidades + atractivo
        
    return seleccion_por_ruleta(probabilidad_parcial, suma_probabilidades, nodos_no_visitados)

# =====================================================================
# 4. Función Calcular_Costo_Ruta
# =====================================================================
def calcular_costo_ruta(lista_tabu, distancias):
    costo_total = 0.0
    cantidad_nodos_recorridos = len(lista_tabu)
    
    for i in range(cantidad_nodos_recorridos - 1):
        nodo_origen = lista_tabu[i]
        nodo_destino = lista_tabu[i + 1]
        costo_total = costo_total + distancias[nodo_origen][nodo_destino]
        
    return costo_total

# =====================================================================
# 5. Función Construir_Ruta_Hormiga
# =====================================================================
def construir_ruta_hormiga(n_nodos, distancias, feromona, heuristica, alpha, beta, nodo_inicio, regresar_origen):
    lista_tabu = []
    nodo_actual = nodo_inicio 
    lista_tabu.append(nodo_actual)
    
    while len(lista_tabu) < n_nodos:
        siguiente_nodo = calcular_transicion(nodo_actual, lista_tabu, n_nodos, feromona, heuristica, alpha, beta)
        lista_tabu.append(siguiente_nodo)
        nodo_actual = siguiente_nodo
        
    # Añadir lista_tabu[0] a lista_tabu (retornar al origen)
    if regresar_origen:
        lista_tabu.append(lista_tabu[0])
        
    costo_total = calcular_costo_ruta(lista_tabu, distancias)
    
    return lista_tabu, costo_total

# =====================================================================
# 6. Función Actualizar_Feromonas
# =====================================================================
def actualizar_feromonas(n_nodos, feromona, rutas_iteracion, costos_iteracion, rho, Q):
    # Evaporación: Para cada arista (i, j) en G
    for i in range(n_nodos):
        for j in range(n_nodos):
            feromona[i][j] = (1.0 - rho) * feromona[i][j]
            
    # Depósito: Para índice = 1 hasta tamaño(rutas_iteracion)
    for indice in range(len(rutas_iteracion)):
        ruta = rutas_iteracion[indice]
        costo = costos_iteracion[indice]
        delta_tau = Q / costo
        
        # Para cada arista (i, j) en la ruta
        for i in range(len(ruta) - 1):
            nodo_origen = ruta[i]
            nodo_destino = ruta[i + 1]
            feromona[nodo_origen][nodo_destino] = feromona[nodo_origen][nodo_destino] + delta_tau
            feromona[nodo_destino][nodo_origen] = feromona[nodo_destino][nodo_origen] + delta_tau # Grafo simétrico

# =====================================================================
# 7. Función Principal ACO
# =====================================================================
def resolver_tsp_aco(puntos, m, iteraciones, alpha, beta, rho, Q, tau_0, id_inicio, regresar_origen):
    """
    Función contenedora principal (ACO).
    Prepara la estructura del Grafo G a partir de los puntos y ejecuta el bucle iterativo.
    """
    n_nodos = len(puntos)
    if n_nodos < 2:
        return {"ruta": [p["id"] for p in puntos], "costo": 0.0, "mejor_iter": 1, "feromonas": []}

    # Crear diccionarios para traducir IDs de texto a índices numéricos (0 a n-1)
    id_a_idx = {p["id"]: i for i, p in enumerate(puntos)}
    idx_a_id = {i: p["id"] for i, p in enumerate(puntos)}
    idx_inicio = id_a_idx.get(id_inicio, 0)

    # Precalcular matriz de distancias (Representa a G.d del pseudocódigo)
    distancias = [[0.0 for _ in range(n_nodos)] for _ in range(n_nodos)]
    for i in range(n_nodos):
        for j in range(n_nodos):
            distancias[i][j] = calcular_distancia_euclidiana(puntos[i], puntos[j])

    # Llamada al pseudocódigo: Inicializar_Parametros(G)
    feromona, heuristica = inicializar_parametros(n_nodos, distancias, tau_0)
    
    mejor_ruta_global = None
    mejor_costo_global = float('inf')
    mejor_iteracion = 0
    
    # Para iteracion = 1 hasta max_iter
    for iteracion in range(1, iteraciones + 1):
        rutas_iteracion = []
        costos_iteracion = []
        
        # Para cada hormiga k desde 1 hasta m
        for k in range(m):
            ruta, costo = construir_ruta_hormiga(
                n_nodos, distancias, feromona, heuristica, alpha, beta, idx_inicio, regresar_origen
            )
            
            rutas_iteracion.append(ruta)
            costos_iteracion.append(costo)
            
            # Si costo < mejor_costo_global
            if costo < mejor_costo_global:
                mejor_ruta_global = list(ruta)
                mejor_costo_global = costo
                mejor_iteracion = iteracion
                
        # Actualizar_Feromonas(...)
        actualizar_feromonas(n_nodos, feromona, rutas_iteracion, costos_iteracion, rho, Q)

    # Preparar el formato de salida para el frontend (traducir índices a IDs string)
    ruta_final_ids = [idx_a_id[idx] for idx in mejor_ruta_global]
    
    lista_fero_ui = []
    for i in range(len(mejor_ruta_global) - 1):
        orig = mejor_ruta_global[i]
        dest = mejor_ruta_global[i+1]
        lista_fero_ui.append((idx_a_id[orig], idx_a_id[dest], feromona[orig][dest]))

    # Retornar mejor_ruta_global, mejor_costo_global
    return {
        "ruta": ruta_final_ids,
        "costo": mejor_costo_global,
        "mejor_iter": mejor_iteracion,
        "feromonas": lista_fero_ui
    }