"""
Ejemplo Práctico: Suma de listas con multiprocessing
=====================================================
Este programa divide una lista grande de números en partes iguales
y calcula la suma de cada parte en un proceso separado, aprovechando
múltiples núcleos del CPU (paralelismo real, no concurrencia simulada).

Conceptos demostrados:
  - Creación de procesos con multiprocessing.Pool
  - División de trabajo (descomposición de datos)
  - Reducción de resultados parciales
  - Medición de speedup respecto a la versión secuencial
"""

import multiprocessing
import time
import random


def suma_parcial(sublista):
    """Calcula la suma de una sublista. Cada proceso ejecuta esta función."""
    return sum(sublista)


def dividir_lista(lista, n):
    """Divide 'lista' en 'n' fragmentos de tamaño aproximadamente igual."""
    k, resto = divmod(len(lista), n)
    inicio = 0
    fragmentos = []
    for i in range(n):
        fin = inicio + k + (1 if i < resto else 0)
        fragmentos.append(lista[inicio:fin])
        inicio = fin
    return fragmentos


def suma_secuencial(lista):
    """Suma secuencial de referencia."""
    return sum(lista)


def suma_paralela(lista, num_procesos):
    """Suma paralela usando un Pool de procesos."""
    fragmentos = dividir_lista(lista, num_procesos)
    with multiprocessing.Pool(processes=num_procesos) as pool:
        resultados_parciales = pool.map(suma_parcial, fragmentos)
    return sum(resultados_parciales)


if __name__ == "__main__":
    # Parámetros del experimento
    TAMANO = 10_000_000          # 10 millones de elementos
    NUM_PROCESOS = multiprocessing.cpu_count()

    print("=" * 55)
    print("  Demostración de Paralelismo con multiprocessing")
    print("=" * 55)
    print(f"  Núcleos disponibles : {NUM_PROCESOS}")
    print(f"  Tamaño de la lista  : {TAMANO:,} números")
    print("-" * 55)

    # Generar datos aleatorios
    datos = [random.randint(1, 100) for _ in range(TAMANO)]

    # --- Versión Secuencial ---
    t0 = time.perf_counter()
    resultado_seq = suma_secuencial(datos)
    t_seq = time.perf_counter() - t0
    print(f"  [Secuencial]  Resultado: {resultado_seq:,}  |  Tiempo: {t_seq:.3f}s")

    # --- Versión Paralela ---
    t0 = time.perf_counter()
    resultado_par = suma_paralela(datos, NUM_PROCESOS)
    t_par = time.perf_counter() - t0
    print(f"  [Paralela]    Resultado: {resultado_par:,}  |  Tiempo: {t_par:.3f}s")

    # --- Verificación y Speedup ---
    coincide = "✓ Coinciden" if resultado_seq == resultado_par else "✗ Difieren"
    speedup = t_seq / t_par if t_par > 0 else float("inf")
    print("-" * 55)
    print(f"  Verificación: {coincide}")
    print(f"  Speedup     : {speedup:.2f}x  ({NUM_PROCESOS} procesos)")
    print("=" * 55)





