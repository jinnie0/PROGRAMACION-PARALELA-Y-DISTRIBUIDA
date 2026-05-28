"""
Actividad: Sincronización con Secciones Críticas y Semáforos
Semana 3 - Programación Concurrente
Simulación con threading y semáforos en Python (equivalente a POSIX)
"""

import threading
import time

# ─────────────────────────────────────────────
# VARIABLE COMPARTIDA (recurso crítico)
# ─────────────────────────────────────────────
contador_compartido = 0

# ─────────────────────────────────────────────
# SEMÁFORO (inicializado en 1 → exclusión mutua)
# Equivalente a sem_init(&sem, 0, 1) en C/POSIX
# ─────────────────────────────────────────────
semaforo = threading.Semaphore(1)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
NUM_HILOS      = 5
ITERACIONES    = 1000
VALOR_ESPERADO = NUM_HILOS * ITERACIONES   # 5000


# ─────────────────────────────────────────────
# FUNCIÓN QUE EJECUTA CADA HILO
# ─────────────────────────────────────────────
def incrementar(id_hilo: int) -> None:
    """
    Cada hilo intenta incrementar `contador_compartido` 1000 veces.
    Usa el semáforo para proteger la sección crítica.
    """
    global contador_compartido

    for _ in range(ITERACIONES):
        # ── WAIT (P) ── equivale a sem_wait(&sem)
        semaforo.acquire()

        # ══ SECCIÓN CRÍTICA ══════════════════
        contador_compartido += 1
        # ══ FIN SECCIÓN CRÍTICA ══════════════

        # ── SIGNAL (V) ── equivale a sem_post(&sem)
        semaforo.release()

    print(f"  [Hilo {id_hilo}] finalizado ✔")


# ─────────────────────────────────────────────
# PROGRAMA PRINCIPAL
# ─────────────────────────────────────────────
def main():
    print("=" * 52)
    print("  SINCRONIZACIÓN CON SEMÁFOROS  —  Semana 3")
    print("=" * 52)
    print(f"  Hilos        : {NUM_HILOS}")
    print(f"  Iteraciones  : {ITERACIONES} por hilo")
    print(f"  Valor esperado: {VALOR_ESPERADO}")
    print("-" * 52)

    # Crear los hilos
    hilos = [
        threading.Thread(target=incrementar, args=(i + 1,))
        for i in range(NUM_HILOS)
    ]

    inicio = time.perf_counter()

    # Lanzar todos los hilos
    for h in hilos:
        h.start()

    # Esperar a que todos terminen (join)
    for h in hilos:
        h.join()

    duracion = time.perf_counter() - inicio

    print("-" * 52)
    print(f"  Valor final del contador : {contador_compartido}")
    print(f"  Valor esperado           : {VALOR_ESPERADO}")
    print(f"  ¿Sincronización correcta?: {'SÍ ✔' if contador_compartido == VALOR_ESPERADO else 'NO ✘'}")
    print(f"  Tiempo de ejecución      : {duracion:.4f} segundos")
    print("=" * 52)


if __name__ == "__main__":
    main()