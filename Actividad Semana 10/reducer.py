#!/usr/bin/env python3
import sys

palabra_actual = None
conteo_actual = 0

for linea in sys.stdin:
    linea = linea.strip()
    if not linea:
        continue
    palabra, valor = linea.split("\t", 1)
    valor = int(valor)

    if palabra == palabra_actual:
        conteo_actual += valor
    else:
        if palabra_actual is not None:
            print(f"{palabra_actual}\t{conteo_actual}")
        palabra_actual, conteo_actual = palabra, valor

if palabra_actual is not None:
    print(f"{palabra_actual}\t{conteo_actual}")