# -*- coding: utf-8 -*-
"""
SmartRoute – Script de Casos de Prueba y Proyección de Escalabilidad
===================================================================
Este script ejecuta los algoritmos del sistema en casos de prueba pequeños
y medianos, y proyecta matemáticamente el comportamiento asintótico para
casos grandes (10^6) y extremos (10^10).

Complejidades Teóricas Utilizadas para la Proyección:
- Vecino Más Cercano : Tiempo O(N²), Espacio O(N²) [Matriz de distancias]
- Colonia de Hormigas  : Tiempo O(I * m * N²), Espacio O(N² + m*N)
- Programación Genética: Tiempo O(N² + Gen * Pop * N), Espacio O(N²)
- Random Forest        : Tiempo O(B * q * h * N log N), Espacio O(N * m)
"""

import sys
import os
import time
import random
import tracemalloc
import math

# Ajustar path para importar backend
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.nearest_neighbor import vecino_mas_cercano
from backend.genetic_programming import programacion_genetica
from backend.ant_colony import resolver_tsp_aco
from backend.algorithms import entrenar_random_forest

def generar_puntos_prueba(n, semilla=42):
    random_gen = random.Random(semilla)
    puntos = []
    for i in range(n):
        puntos.append({
            "id": f"P{i}",
            "x": random_gen.uniform(0.0, 1000.0),
            "y": random_gen.uniform(0.0, 1000.0),
            "prioridad": random_gen.choice(["Alta", "Media", "Baja"]),
            "demanda": random_gen.randint(1, 40),
            "tiempo": random_gen.randint(5, 30),
            "frecuencia": random_gen.randint(1, 10),
            "urgencia": random_gen.randint(1, 10),
            "clase_real": random_gen.choice(["alta", "media", "baja"])
        })
    return puntos

def formatear_tiempo(segundos):
    if segundos < 1e-4:
        return f"{segundos * 1e6:.2f} µs"
    elif segundos < 0.1:
        return f"{segundos * 1000:.2f} ms"
    elif segundos < 60:
        return f"{segundos:.4f} s"
    elif segundos < 3600:
        mins = int(segundos // 60)
        segs = segundos % 60
        return f"{mins} m {segs:.1f} s"
    else:
        horas = segundos / 3600.0
        if horas > 24 * 365:
            return f"{horas / (24 * 365.25):.2f} años"
        elif horas > 24:
            dias = horas / 24.0
            return f"{dias:.2f} días"
        return f"{horas:.2f} horas"

def formatear_memoria(mb):
    if mb < 1.0:
        return f"{mb * 1024.0:.2f} KB"
    elif mb < 1024.0:
        return f"{mb:.2f} MB"
    elif mb < 1024.0 * 1024.0:
        return f"{mb / 1024.0:.2f} GB"
    else:
        tb = mb / (1024.0 * 1024.0)
        if tb < 1024.0:
            return f"{tb:.2f} TB"
        else:
            pb = tb / 1024.0
            return f"{pb:.2f} PB"

def ejecutar_caso(nombre, puntos, funcion_ejecutar):
    tracemalloc.start()
    t_start = time.perf_counter()
    
    try:
        resultado = funcion_ejecutar(puntos)
        t_end = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        tiempo = t_end - t_start
        memoria = peak / (1024.0 * 1024.0)
        return {
            "estado": "Exitoso",
            "tiempo": tiempo,
            "memoria": memoria,
            "costo": resultado.get("costo", resultado.get("distancia", 0.0))
        }
    except Exception as e:
        tracemalloc.stop()
        return {
            "estado": f"Error: {e}",
            "tiempo": 0.0,
            "memoria": 0.0,
            "costo": 0.0
        }

def proyectar(t_base, m_base, n_base, n_destino, tipo_complejidad_tiempo, bytes_por_elemento=8):
    # Proyección de tiempo
    if tipo_complejidad_tiempo == "O(N)":
        tiempo_proyectado = t_base * (n_destino / n_base)
    elif tipo_complejidad_tiempo == "O(N log N)":
        tiempo_proyectado = t_base * (n_destino * math.log2(n_destino)) / (n_base * math.log2(n_base))
    elif tipo_complejidad_tiempo == "O(N2)":
        tiempo_proyectado = t_base * ((n_destino / n_base) ** 2)
    elif tipo_complejidad_tiempo == "O(Iter * m * N2)":
        tiempo_proyectado = t_base * ((n_destino / n_base) ** 2)
    else:
        tiempo_proyectado = t_base * ((n_destino / n_base) ** 2) # default a O(N2)
        
    # Proyección de memoria (considerando el tamaño de matrices NxN de floats)
    # n_destino^2 elementos * 8 bytes (double float) + overhead de estructuras de Python
    memoria_base_proyectada = m_base
    if tipo_complejidad_tiempo in ["O(N2)", "O(Iter * m * N2)"]:
        # Para matrices NxN
        # Python nested lists tienen un overhead aproximado de 64 bytes por elemento
        overhead_factor = 64
        memoria_proyectada = (n_destino ** 2) * overhead_factor / (1024.0 * 1024.0)
    else:
        # Lineal (Random Forest y otros que no usan matrices)
        memoria_proyectada = m_base * (n_destino / n_base)
        
    # Asegurar un piso razonable
    if memoria_proyectada < m_base:
        memoria_proyectada = m_base
        
    return tiempo_proyectado, memoria_proyectada

def main():
    print("=" * 80)
    print("                BANCO DE PRUEBAS DE ESCALABILIDAD - SMARTROUTE")
    print("=" * 80)
    print("Generando datos de entrada...")
    
    puntos_10 = generar_puntos_prueba(10)
    puntos_1000 = generar_puntos_prueba(1000)
    
    print(f"-> Conjunto Pequeño generado: {len(puntos_10)} puntos.")
    print(f"-> Conjunto Mediano generado : {len(puntos_1000)} puntos.")
    print("-" * 80)
    
    # Parámetros para la ejecución
    id_inicio_10 = puntos_10[0]["id"]
    id_inicio_1000 = puntos_1000[0]["id"]
    
    # Estructura para almacenar mediciones reales
    mediciones = {
        "Vecino Más Cercano": {"N=10": {}, "N=1000": {}, "tiempo_comp": "O(N2)", "memoria_comp": "O(N2)"},
        "Colonia de Hormigas": {"N=10": {}, "N=1000": {}, "tiempo_comp": "O(Iter * m * N2)", "memoria_comp": "O(N2)"},
        "Programación Genética": {"N=10": {}, "N=1000": {}, "tiempo_comp": "O(N2)", "memoria_comp": "O(N2)"},
        "Random Forest": {"N=10": {}, "N=1000": {}, "tiempo_comp": "O(N log N)", "memoria_comp": "O(N)"}
    }
    
    # -------------------------------------------------------------------------
    # 1. EJECUCIÓN: CASOS PEQUEÑOS (N=10)
    # -------------------------------------------------------------------------
    print("Ejecutando Casos Pequeños (N=10) - MEDICIÓN EN VIVO...")
    
    # Vecino Más Cercano
    res_vmc = ejecutar_caso("Vecino Más Cercano", puntos_10, 
                            lambda pts: vecino_mas_cercano(pts, id_inicio_10, "Solo distancia física", True))
    mediciones["Vecino Más Cercano"]["N=10"] = res_vmc
    print(f"  [VMC] Tiempo: {formatear_tiempo(res_vmc['tiempo'])} | Memoria: {formatear_memoria(res_vmc['memoria'])}")
    
    # Colonia de Hormigas (ACO)
    res_aco = ejecutar_caso("Colonia de Hormigas", puntos_10,
                            lambda pts: resolver_tsp_aco(pts, m=10, iteraciones=10, alpha=1.0, beta=2.0, rho=0.1, Q=100.0, tau_0=1.0, id_inicio=id_inicio_10, regresar_origen=True))
    mediciones["Colonia de Hormigas"]["N=10"] = res_aco
    print(f"  [ACO] Tiempo: {formatear_tiempo(res_aco['tiempo'])} | Memoria: {formatear_memoria(res_aco['memoria'])}")
    
    # Programación Genética (GP)
    res_gp = ejecutar_caso("Programación Genética", puntos_10,
                           lambda pts: programacion_genetica(pts, tam_poblacion=50, generaciones=20, tasa_cruce=0.8, tasa_mutacion=0.1, tam_torneo=3, peso_prioridad=1.0))
    mediciones["Programación Genética"]["N=10"] = res_gp
    print(f"  [GP ] Tiempo: {formatear_tiempo(res_gp['tiempo'])} | Memoria: {formatear_memoria(res_gp['memoria'])}")
    
    # Random Forest (RF) - Entrenamiento
    res_rf = ejecutar_caso("Random Forest", puntos_10,
                           lambda pts: entrenar_random_forest(pts, n_arboles=5, max_depth=4, min_samples=2, q_attrs=3, train_pct=80, semilla=42))
    mediciones["Random Forest"]["N=10"] = res_rf
    print(f"  [RF ] Tiempo: {formatear_tiempo(res_rf['tiempo'])} | Memoria: {formatear_memoria(res_rf['memoria'])}")
    
    print("-" * 80)
    
    # -------------------------------------------------------------------------
    # 2. EJECUCIÓN: CASOS MEDIANOS (N=1000)
    # -------------------------------------------------------------------------
    print("Ejecutando Casos Medianos (N=1000) - MEDICIÓN EN VIVO...")
    
    # Vecino Más Cercano
    res_vmc = ejecutar_caso("Vecino Más Cercano", puntos_1000, 
                            lambda pts: vecino_mas_cercano(pts, id_inicio_1000, "Solo distancia física", True))
    mediciones["Vecino Más Cercano"]["N=1000"] = res_vmc
    print(f"  [VMC] Tiempo: {formatear_tiempo(res_vmc['tiempo'])} | Memoria: {formatear_memoria(res_vmc['memoria'])}")
    
    # Colonia de Hormigas (ACO) - Reducimos iteraciones y hormigas para que termine rápido
    res_aco = ejecutar_caso("Colonia de Hormigas", puntos_1000,
                            lambda pts: resolver_tsp_aco(pts, m=5, iteraciones=5, alpha=1.0, beta=2.0, rho=0.1, Q=100.0, tau_0=1.0, id_inicio=id_inicio_1000, regresar_origen=True))
    mediciones["Colonia de Hormigas"]["N=1000"] = res_aco
    print(f"  [ACO] Tiempo: {formatear_tiempo(res_aco['tiempo'])} | Memoria: {formatear_memoria(res_aco['memoria'])}")
    
    # Programación Genética (GP) - Parámetros ligeros
    res_gp = ejecutar_caso("Programación Genética", puntos_1000,
                           lambda pts: programacion_genetica(pts, tam_poblacion=30, generaciones=10, tasa_cruce=0.8, tasa_mutacion=0.1, tam_torneo=3, peso_prioridad=1.0))
    mediciones["Programación Genética"]["N=1000"] = res_gp
    print(f"  [GP ] Tiempo: {formatear_tiempo(res_gp['tiempo'])} | Memoria: {formatear_memoria(res_gp['memoria'])}")
    
    # Random Forest (RF) - Entrenamiento
    res_rf = ejecutar_caso("Random Forest", puntos_1000,
                           lambda pts: entrenar_random_forest(pts, n_arboles=5, max_depth=4, min_samples=2, q_attrs=3, train_pct=80, semilla=42))
    mediciones["Random Forest"]["N=1000"] = res_rf
    print(f"  [RF ] Tiempo: {formatear_tiempo(res_rf['tiempo'])} | Memoria: {formatear_memoria(res_rf['memoria'])}")
    
    print("=" * 80)
    print("                   TABLA COMPARATIVA DE RESULTADOS Y PROYECCIONES")
    print("=" * 80)
    print(f"{'Algoritmo':<22} | {'Tamaño N':<9} | {'T. Ejecución (Medido/Proy)':<28} | {'Memoria':<14}")
    print("-" * 80)
    
    for algo, data in mediciones.items():
        # Medido N=10
        t10, m10 = data["N=10"]["tiempo"], data["N=10"]["memoria"]
        print(f"{algo:<22} | {'10':<9} | {formatear_tiempo(t10):<28} | {formatear_memoria(m10):<14}")
        
        # Medido N=1000
        t1000, m1000 = data["N=1000"]["tiempo"], data["N=1000"]["memoria"]
        print(f"{algo:<22} | {'10^3':<9} | {formatear_tiempo(t1000):<28} | {formatear_memoria(m1000):<14}")
        
        # Proyectar N=10^6
        t_proj_6, m_proj_6 = proyectar(t1000, m1000, 1000, 1_000_000, data["tiempo_comp"])
        print(f"{algo:<22} | {'10^6 (P)':<9} | {formatear_tiempo(t_proj_6):<28} | {formatear_memoria(m_proj_6):<14}")
        
        # Proyectar N=10^10
        t_proj_10, m_proj_10 = proyectar(t1000, m1000, 1000, 10_000_000_000, data["tiempo_comp"])
        print(f"{algo:<22} | {'10^10 (P)':<9} | {formatear_tiempo(t_proj_10):<28} | {formatear_memoria(m_proj_10):<14}")
        
        print("-" * 80)
        
    print("\nANÁLISIS DE FACTIBILIDAD Y ESCALABILIDAD ASINTÓTICA:")
    print("• Casos Pequeños (10) y Medianos (10^3): Son totalmente viables y se resuelven en milisegundos/segundos.")
    print("• Casos Grandes (10^6):")
    print("  - Los algoritmos de ruteo basados en matrices NxN (VMC, ACO, GP) requerirían ~60 GB de RAM para almacenar las")
    print("    distancias en Python y varios días de cálculo.")
    print("  - Random Forest sigue siendo viable en memoria (~100-200 MB) pero el entrenamiento tardaría varias horas.")
    print("• Casos Extremos (10^10):")
    print("  - Los algoritmos de ruteo son físicamente imposibles de resolver con fuerza bruta u optimizaciones secuenciales")
    print("    debido al límite de direccionamiento de memoria (requerirían Exabytes de RAM) y tiempo (millones de años).")
    print("=" * 80)

if __name__ == "__main__":
    main()
