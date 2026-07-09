#!/usr/bin/env python3
import sys
import re

for linea in sys.stdin:
    linea = linea.strip().lower()
    palabras = re.findall(r"[a-záéíóúñü]+", linea)
    for palabra in palabras:
        print(f"{palabra}\t1")