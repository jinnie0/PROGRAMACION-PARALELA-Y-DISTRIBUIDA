"""
word_count_rdd.py
Semana 13 - Frameworks de Big Data: Apache Spark (RDDs)
UNIBE - Parallel and Distributed Computing

Cuenta palabras de un archivo de texto grande usando la API de RDDs
(flatMap -> map -> reduceByKey) y mide el tiempo de ejecucion.
"""

import time
import sys
from pyspark import SparkContext, SparkConf


def main(input_path: str, output_path: str):
    # 1. Inicializacion de Spark ------------------------------------------------
    conf = SparkConf().setAppName("WordCountRDD").setMaster("local[*]")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")

    start = time.time()

    # 2. Carga del archivo como RDD de lineas ------------------------------------
    lines = sc.textFile(input_path)

    # 3. flatMap -> map -> reduceByKey -------------------------------------------
    # flatMap: separa cada linea en palabras (una linea -> muchas palabras)
    words = lines.flatMap(lambda line: line.lower().split())

    # map: convierte cada palabra en una tupla (palabra, 1)
    pairs = words.map(lambda word: (word, 1))

    # reduceByKey: suma los valores para cada palabra (llave) en paralelo
    counts = pairs.reduceByKey(lambda a, b: a + b)

    # Orden descendente por frecuencia (accion adicional, no obligatoria)
    sorted_counts = counts.sortBy(lambda pair: pair[1], ascending=False)

    # 4. Accion final: recopilar y guardar ----------------------------------------
    result = sorted_counts.collect()  # trae los resultados al driver

    elapsed = time.time() - start

    # Guardar en archivo de texto
    with open(output_path, "w", encoding="utf-8") as f:
        for word, count in result:
            f.write(f"{word}\t{count}\n")

    total_words = sum(c for _, c in result)
    distinct_words = len(result)

    print(f"[RDD] Palabras totales: {total_words}")
    print(f"[RDD] Palabras distintas: {distinct_words}")
    print(f"[RDD] Tiempo de ejecucion: {elapsed:.3f} segundos")

    sc.stop()
    return elapsed


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output_rdd.txt"
    main(input_file, output_file)
