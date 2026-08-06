# Spark Word Count: RDD vs DataFrame

Actividad Semana 13 - Frameworks de Big Data (Apache Spark) - Parallel and Distributed Computing - UNIBE

Implementacion de un job de Word Count sobre un dataset de texto de ~100 MB usando dos enfoques de Apache Spark (PySpark): **RDDs** y **DataFrames**, con medicion y comparacion de tiempos de ejecucion.

## Contenido del repositorio

| Archivo | Descripcion |
|---|---|
| `word_count_rdd.py` | Word Count usando la API de RDDs (`flatMap` → `map` → `reduceByKey`) |
| `word_count_dataframe.py` | Word Count usando la API de DataFrames (`explode`, `split`, `groupBy`, `orderBy`) |
| `compare_performance.py` | Ejecuta ambos jobs, mide tiempos, calcula el speedup y genera `tiempos.csv` / `tiempos.png` |
| `generate_dataset.py` | Genera el dataset de prueba de ~100 MB |
| `tiempos.csv` / `tiempos.json` | Resultados de tiempos obtenidos en la ejecucion de referencia |

## Requisitos

- Python 3.9+
- Java 8, 11, 17 o 21 (requerido por Spark)
- PySpark

```bash
pip install pyspark matplotlib
```

## Como ejecutar

1. Genera el dataset de prueba (~100 MB):
   ```bash
   python3 generate_dataset.py
   ```

2. Ejecuta el job de RDD:
   ```bash
   python3 word_count_rdd.py input.txt output_rdd.txt
   ```

3. Ejecuta el job de DataFrame:
   ```bash
   python3 word_count_dataframe.py input.txt output_dataframe
   ```

4. Corre la comparacion completa (ambos jobs + tabla + grafica):
   ```bash
   python3 compare_performance.py
   ```

## Resumen de resultados (ejecucion de referencia, local[*])

| Metrica | RDD | DataFrame |
|---|---|---|
| Tiempo de ejecucion | 18.32 s | 29.50 s |
| Palabras totales | 13,069,638 | 13,069,638 |
| Palabras distintas | 40 | 40 |

> Los tiempos varian segun el hardware, el numero de cores disponibles y el tamano del dataset. El detalle del analisis de estos resultados esta en el informe PDF entregado junto con este repositorio.

## Arquitectura

- **RDD**: coleccion distribuida e inmutable de objetos, sin esquema. Transformaciones perezosas (`flatMap`, `map`, `reduceByKey`) y una accion final (`collect`) disparan la ejecucion.
- **DataFrame**: coleccion distribuida organizada en columnas con esquema. Se beneficia del optimizador **Catalyst** y del motor de ejecucion **Tungsten**, que optimizan el plan de consulta antes de ejecutarlo.

## Autor

Jinnie - UNIBE - Parallel and Distributed Computing
