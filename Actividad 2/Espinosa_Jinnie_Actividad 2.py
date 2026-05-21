"""
Ejemplo Práctico: Simulación de Paralelismo tipo OpenMP y TBB en Python
=======================================================================
Este script simula el comportamiento de OpenMP (fork-join con reducción)
y TBB (work-stealing con parallel_reduce) usando las bibliotecas estándar
de Python: multiprocessing y concurrent.futures.

Puedes ejecutarlo directamente:
    python ejemplo_paralelo.py

Requisitos: Python 3.8+ (sin instalaciones adicionales)
"""

import time
import math
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

# ─────────────────────────────────────────────────────────
# DATOS COMPARTIDOS (el "arreglo" que sumaremos en paralelo)
# ─────────────────────────────────────────────────────────
N = 10_000_000  # 10 millones de elementos
ARRAY = [i * 0.5 for i in range(N)]  # genera la lista una sola vez

CPU_COUNT = multiprocessing.cpu_count()


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1 — VERSIÓN SECUENCIAL (referencia de velocidad)
# ─────────────────────────────────────────────────────────────────────────────
def suma_secuencial(arr: list) -> float:
    """Suma todos los elementos del arreglo de forma secuencial."""
    total = 0.0
    for x in arr:
        total += x
    return total


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2 — ESTILO OpenMP: fork-join con reducción por chunk
# Simula:  #pragma omp parallel for reduction(+:suma) schedule(static)
# ─────────────────────────────────────────────────────────────────────────────
def _worker_chunk(args):
    """Tarea worker: suma un fragmento (chunk) del arreglo."""
    arr, inicio, fin = args
    return sum(arr[inicio:fin])


def suma_estilo_openmp(arr: list, num_hilos: int) -> float:
    """
    Divide el arreglo en chunks iguales (schedule=static) y
    lanza un proceso por chunk.  Los resultados parciales se
    suman al final (reducción).

    Equivale en C a:
        #pragma omp parallel for reduction(+:suma) schedule(static)
        for (int i = 0; i < n; i++) suma += arr[i];
    """
    n = len(arr)
    chunk_size = math.ceil(n / num_hilos)

    # Construir rangos de cada "hilo"
    rangos = [
        (arr, i * chunk_size, min((i + 1) * chunk_size, n))
        for i in range(num_hilos)
    ]

    # Fork: lanzar procesos en paralelo
    with multiprocessing.Pool(processes=num_hilos) as pool:
        parciales = pool.map(_worker_chunk, rangos)

    # Reducción: combinar resultados parciales
    return sum(parciales)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3 — ESTILO TBB: work-stealing con ProcessPoolExecutor
# Simula:  tbb::parallel_reduce(blocked_range<int>(0,n), 0.0, ...)
# ─────────────────────────────────────────────────────────────────────────────
def _worker_rango(args):
    """Tarea granular para work-stealing: suma un rango pequeño."""
    arr, inicio, fin = args
    return sum(arr[inicio:fin])


def suma_estilo_tbb(arr: list, num_workers: int, granularidad: int = 500_000) -> float:
    """
    Divide el arreglo en tareas finas (granularidad dinámica) y las
    encola en un ExecutorPool.  Los workers toman tareas de la cola
    de manera oportunista, simulando el planificador work-stealing de TBB.

    Equivale en C++ a:
        tbb::parallel_reduce(
            tbb::blocked_range<int>(0, n, granularidad),
            0.0,
            [&](auto r, double init){ ... },
            std::plus<double>()
        );
    """
    n = len(arr)
    # Generar lista de sub-rangos (blocked_range en TBB)
    tareas = [
        (arr, i, min(i + granularidad, n))
        for i in range(0, n, granularidad)
    ]

    total = 0.0
    # ProcessPoolExecutor con as_completed simula el scheduler work-stealing
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futuros = {executor.submit(_worker_rango, t): t for t in tareas}
        for futuro in as_completed(futuros):
            total += futuro.result()

    return total


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL — BENCHMARK COMPARATIVO
# ─────────────────────────────────────────────────────────────────────────────
def benchmark(nombre: str, func, *args) -> tuple[float, float]:
    """Ejecuta la función, mide el tiempo y devuelve (resultado, tiempo_seg)."""
    t0 = time.perf_counter()
    resultado = func(*args)
    t1 = time.perf_counter()
    return resultado, round(t1 - t0, 4)


def main():
    print("=" * 65)
    print("  Simulación de Paralelismo tipo OpenMP y TBB en Python")
    print("=" * 65)
    print(f"  Elementos del arreglo : {N:,}")
    print(f"  CPUs disponibles      : {CPU_COUNT}")
    print("-" * 65)

    # --- Secuencial ---
    res_sec, t_sec = benchmark("Secuencial", suma_secuencial, ARRAY)
    print(f"\n[1] SECUENCIAL")
    print(f"    Resultado  : {res_sec:,.2f}")
    print(f"    Tiempo     : {t_sec:.4f} s  (referencia base)")

    # --- Estilo OpenMP ---
    res_omp, t_omp = benchmark(
        "OpenMP-style", suma_estilo_openmp, ARRAY, CPU_COUNT
    )
    speedup_omp = round(t_sec / t_omp, 2) if t_omp > 0 else "∞"
    print(f"\n[2] ESTILO OpenMP  (fork-join, schedule=static, {CPU_COUNT} hilos)")
    print(f"    Resultado  : {res_omp:,.2f}")
    print(f"    Tiempo     : {t_omp:.4f} s")
    print(f"    Speedup    : {speedup_omp}x respecto a secuencial")

    # --- Estilo TBB ---
    res_tbb, t_tbb = benchmark(
        "TBB-style", suma_estilo_tbb, ARRAY, CPU_COUNT
    )
    speedup_tbb = round(t_sec / t_tbb, 2) if t_tbb > 0 else "∞"
    print(f"\n[3] ESTILO TBB     (work-stealing, granularidad=500k, {CPU_COUNT} workers)")
    print(f"    Resultado  : {res_tbb:,.2f}")
    print(f"    Tiempo     : {t_tbb:.4f} s")
    print(f"    Speedup    : {speedup_tbb}x respecto a secuencial")

    # --- Verificación de correctitud ---
    print("\n" + "-" * 65)
    tol = 1e-3
    correcto_omp = abs(res_omp - res_sec) < tol
    correcto_tbb = abs(res_tbb - res_sec) < tol
    print(f"  Verificación OpenMP : {'✅ Correcto' if correcto_omp else '❌ Error'}")
    print(f"  Verificación TBB    : {'✅ Correcto' if correcto_tbb else '❌ Error'}")

    # --- Tabla resumen ---
    print("\n" + "=" * 65)
    print(f"  {'Método':<22} {'Tiempo (s)':<15} {'Speedup':<12} {'Resultado'}")
    print("-" * 65)
    print(f"  {'Secuencial':<22} {t_sec:<15.4f} {'1.00x':<12} {res_sec:,.2f}")
    print(f"  {'OpenMP (fork-join)':<22} {t_omp:<15.4f} {str(speedup_omp)+'x':<12} {res_omp:,.2f}")
    print(f"  {'TBB (work-stealing)':<22} {t_tbb:<15.4f} {str(speedup_tbb)+'x':<12} {res_tbb:,.2f}")
    print("=" * 65)

    print("""
  EXPLICACIÓN DEL EJEMPLO
  ─────────────────────────────────────────────────────────────
  Secuencial   : suma lineal elemento a elemento (sin paralelismo).

  Estilo OpenMP: divide el arreglo en N_CPU chunks iguales
                 (schedule=static) y lanza un proceso por chunk.
                 Al final reduce (suma) los resultados parciales.
                 Replica:  #pragma omp parallel for reduction(+:suma)

  Estilo TBB   : genera muchas tareas pequeñas (granularidad fina)
                 y las distribuye dinámicamente entre los workers.
                 Los workers inactivos toman tareas pendientes (work-
                 stealing), balanceando la carga automáticamente.
                 Replica:  tbb::parallel_reduce(blocked_range<int>...)

  Referencias: Pacheco (2021); Reinders (2023); Anónimo (2023).
  ─────────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    main()