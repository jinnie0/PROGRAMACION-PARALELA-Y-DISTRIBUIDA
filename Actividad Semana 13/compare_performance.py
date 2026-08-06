"""
compare_performance.py
Semana 13 - Frameworks de Big Data: Apache Spark
UNIBE - Parallel and Distributed Computing

Ejecuta ambos jobs (RDD y DataFrame) sobre el mismo dataset, mide sus
tiempos de ejecucion, calcula el speedup relativo y guarda una tabla en
tiempos.csv y una grafica en tiempos.png.
"""

import time
import json
import subprocess
import sys

INPUT_FILE = "input.txt"


def run(script, out):
    start = time.time()
    subprocess.run([sys.executable, script, INPUT_FILE, out], check=True)
    return time.time() - start


def main():
    t_rdd = run("word_count_rdd.py", "output_rdd.txt")
    t_df = run("word_count_dataframe.py", "output_dataframe")

    speedup = t_rdd / t_df if t_df else float("nan")

    with open("tiempos.csv", "w", encoding="utf-8") as f:
        f.write("metodo,tiempo_segundos\n")
        f.write(f"RDD,{t_rdd:.3f}\n")
        f.write(f"DataFrame,{t_df:.3f}\n")

    with open("tiempos.json", "w", encoding="utf-8") as f:
        json.dump({"rdd_seconds": t_rdd, "dataframe_seconds": t_df, "speedup": speedup}, f, indent=2)

    print(f"RDD:       {t_rdd:.3f} s")
    print(f"DataFrame: {t_df:.3f} s")
    print(f"Speedup (RDD/DataFrame): {speedup:.2f}x")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(5, 4))
        plt.bar(["RDD", "DataFrame"], [t_rdd, t_df], color=["#8884d8", "#4fb3a9"])
        plt.ylabel("Tiempo de ejecucion (segundos)")
        plt.title("Word Count: RDD vs DataFrame (~100 MB)")
        for i, v in enumerate([t_rdd, t_df]):
            plt.text(i, v + 0.2, f"{v:.2f}s", ha="center")
        plt.tight_layout()
        plt.savefig("tiempos.png", dpi=150)
    except ImportError:
        print("matplotlib no disponible; se omitio la grafica.")


if __name__ == "__main__":
    main()
