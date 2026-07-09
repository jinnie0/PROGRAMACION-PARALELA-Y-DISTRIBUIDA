import time
import multiprocessing as mp
from collections import defaultdict
import subprocess

def fase_map(archivos):
    pares = []
    for archivo in archivos:
        with open(archivo, encoding="utf-8") as f:
            resultado = subprocess.run(["python", "mapper.py"], stdin=f, capture_output=True, text=True)
        for linea in resultado.stdout.strip().split("\n"):
            palabra, valor = linea.split("\t")
            pares.append((palabra, int(valor)))
    return pares

def reduce_particion(particion):
    conteos = defaultdict(int)
    for palabra, valor in particion:
        conteos[palabra] += valor
    return dict(conteos)

def particionar(pares, num_reducers):
    particiones = [[] for _ in range(num_reducers)]
    for palabra, valor in pares:
        particiones[hash(palabra) % num_reducers].append((palabra, valor))
    return particiones

def ejecutar_job(pares, num_reducers):
    particiones = particionar(pares, num_reducers)
    inicio = time.perf_counter()
    with mp.Pool(processes=num_reducers) as pool:
        resultados = pool.map(reduce_particion, particiones)
    fin = time.perf_counter()
    return fin - inicio, sum(len(r) for r in resultados), [len(p) for p in particiones]

if __name__ == "__main__":
    archivos = ["documento1.txt", "documento2.txt"]
    pares = fase_map(archivos)
    print(f"Total de pares (palabra,1) generados por el map: {len(pares)}\n")
    print(f"{'Reducers':<10}{'Tiempo (s)':<15}{'Unicas':<10}{'Particiones'}")
    for n in (1, 2, 4):
        tiempo, unicas, tam = ejecutar_job(pares, n)
        print(f"{n:<10}{tiempo:<15.6f}{unicas:<10}{tam}")