"""
word_count_dataframe.py
Semana 13 - Frameworks de Big Data: Apache Spark (DataFrames)
UNIBE - Parallel and Distributed Computing

Cuenta palabras de un archivo de texto grande usando la API estructurada
de DataFrames (explode, split, groupBy, count, orderBy) y mide el tiempo
de ejecucion.
"""

import time
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, lower, col


def main(input_path: str, output_path: str):
    # 1. Inicializacion de Spark ------------------------------------------------
    spark = (
        SparkSession.builder
        .appName("WordCountDataFrame")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    start = time.time()

    # 2. Lectura del archivo como DataFrame de lineas -----------------------------
    df_lines = spark.read.text(input_path)  # columna "value" con cada linea

    # 3. split + explode: separa cada linea en palabras individuales --------------
    df_words = df_lines.select(
        explode(split(lower(col("value")), r"\s+")).alias("word")
    ).filter(col("word") != "")

    # 4. groupBy + count: agrupa y cuenta ocurrencias por palabra -----------------
    df_counts = df_words.groupBy("word").count()

    # 5. orderBy: ordena de mayor a menor frecuencia ------------------------------
    df_sorted = df_counts.orderBy(col("count").desc())

    # 6. Accion final: forzar ejecucion y guardar en CSV ---------------------------
    df_sorted.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)

    total_words = df_words.count()
    distinct_words = df_sorted.count()

    elapsed = time.time() - start

    print(f"[DataFrame] Palabras totales: {total_words}")
    print(f"[DataFrame] Palabras distintas: {distinct_words}")
    print(f"[DataFrame] Tiempo de ejecucion: {elapsed:.3f} segundos")

    spark.stop()
    return elapsed


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output_dataframe"
    main(input_file, output_file)
