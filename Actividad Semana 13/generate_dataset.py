"""
generate_dataset.py
Genera un archivo de texto de ~100 MB con palabras aleatorias de un
vocabulario tematico, usado como dataset de entrada para los jobs de
Word Count (RDD y DataFrame).
"""

import random

VOCAB = [
    "spark", "datos", "big", "data", "framework", "distribuido", "cluster", "nodo",
    "procesamiento", "memoria", "transformacion", "accion", "dataframe", "rdd",
    "optimizacion", "catalyst", "particion", "shuffle", "reduce", "map",
    "ejecucion", "tiempo", "rendimiento", "analisis", "sistema", "arquitectura",
    "paralelo", "computacion", "algoritmo", "red", "universidad", "proyecto",
    "estudiante", "curso", "semana", "entrega", "python", "scala", "java", "codigo",
]


def generate(output_path="input.txt", target_bytes=105 * 1024 * 1024, seed=42):
    random.seed(seed)
    size = 0
    buffer = []
    with open(output_path, "w", encoding="utf-8") as f:
        while size < target_bytes:
            line = " ".join(random.choice(VOCAB) for _ in range(random.randint(8, 20))) + "\n"
            buffer.append(line)
            size += len(line)
            if len(buffer) >= 5000:
                f.writelines(buffer)
                buffer = []
        f.writelines(buffer)
    print(f"Dataset generado: {output_path} ({size / (1024*1024):.1f} MB aprox.)")


if __name__ == "__main__":
    generate()
