/*
 * suma_paralela.c
 * Suma paralela de arreglo con OpenMP
 * Calcula speedup, eficiencia y aplica la Ley de Amdahl
 *
 * === COMPILACION Y EJECUCION EN VISUAL STUDIO CODE ===
 *
 * Linux / macOS:
 *   gcc -fopenmp -O2 -o suma_paralela suma_paralela.c
 *   ./suma_paralela
 *
 * Windows (con MinGW-w64 instalado):
 *   gcc -fopenmp -O2 -o suma_paralela.exe suma_paralela.c
 *   suma_paralela.exe
 *
 * NOTA: En Windows, descargar MinGW-w64 desde https://winlibs.com/
 *       y agregar la carpeta bin al PATH del sistema.
 *       Visual Studio Code usa el terminal integrado para compilar y ejecutar.
 */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

/* ---------------------------------------------------------------
 * CONSTANTES
 * --------------------------------------------------------------- */
#define ARRAY_SIZE 100000000L   /* 100 millones de elementos */
#define F_PARALELO  0.97        /* Fraccion paralelizable estimada: 97% */

/* ---------------------------------------------------------------
 * PROTOTIPOS
 * --------------------------------------------------------------- */
long long suma_secuencial(volatile long long *arr, long long n);
long long suma_paralela_omp(volatile long long *arr, long long n, int hilos);
double   ley_amdahl(double f, int p);

/* ---------------------------------------------------------------
 * MAIN
 * --------------------------------------------------------------- */
int main(void) {
    long long n = ARRAY_SIZE;

    volatile long long *arr = (volatile long long *)malloc(n * sizeof(long long));
    if (!arr) {
        fprintf(stderr, "Error: memoria insuficiente.\n");
        return 1;
    }

    /* Inicializar arreglo: todos los valores = 1 */
    for (long long i = 0; i < n; i++) arr[i] = 1;

    printf("=========================================================\n");
    printf("   Suma Paralela con OpenMP - Metricas de Rendimiento    \n");
    printf("   Tamano del arreglo : %lld elementos                   \n", n);
    printf("   Procesadores disp. : %d                               \n", omp_get_max_threads());
    printf("   Fraccion paraleliz.: %.2f (Ley de Amdahl)             \n", F_PARALELO);
    printf("=========================================================\n\n");

    /* ---------- Medicion con 1 hilo (secuencial) ---------- */
    struct timespec ts, te;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    volatile long long res1 = suma_secuencial(arr, n);
    clock_gettime(CLOCK_MONOTONIC, &te);
    double T1 = (te.tv_sec - ts.tv_sec) + (te.tv_nsec - ts.tv_nsec) * 1e-9;

    printf("Resultado verificado: suma = %lld (esperado: %lld)\n\n", (long long)res1, n);

    /* ---------- Tabla de resultados ---------- */
    int hilos_list[] = {1, 2, 4, 8, 16};
    int m = sizeof(hilos_list) / sizeof(hilos_list[0]);

    printf("%-8s %-14s %-10s %-12s %-14s\n",
           "Hilos", "Tiempo (s)", "Speedup", "Eficiencia", "Amdahl (teo)");
    printf("--------------------------------------------------------------\n");

    /* Fila p=1 */
    printf("%-8d %-14.6f %-10.4f %-12.4f %-14.4f\n",
           1, T1, 1.0, 1.0, ley_amdahl(F_PARALELO, 1));

    for (int k = 1; k < m; k++) {
        int p = hilos_list[k];

        clock_gettime(CLOCK_MONOTONIC, &ts);
        volatile long long resp = suma_paralela_omp(arr, n, p);
        clock_gettime(CLOCK_MONOTONIC, &te);
        double Tp = (te.tv_sec - ts.tv_sec) + (te.tv_nsec - ts.tv_nsec) * 1e-9;

        double speedup    = T1 / Tp;
        double eficiencia = speedup / (double)p;
        double amdahl     = ley_amdahl(F_PARALELO, p);

        printf("%-8d %-14.6f %-10.4f %-12.4f %-14.4f\n",
               p, Tp, speedup, eficiencia, amdahl);
        (void)resp;
    }

    printf("--------------------------------------------------------------\n");
    printf("\nFormulas aplicadas:\n");
    printf("  Speedup(p)    = T1 / Tp\n");
    printf("  Eficiencia(p) = Speedup(p) / p\n");
    printf("  Amdahl(p)     = 1 / [(1-f) + f/p]  con f = %.2f\n\n", F_PARALELO);

    free((void *)arr);
    return 0;
}

/* ---------------------------------------------------------------
 * SUMA SECUENCIAL
 * volatile evita que el compilador elimine el bucle
 * --------------------------------------------------------------- */
long long suma_secuencial(volatile long long *arr, long long n) {
    long long suma = 0;
    for (long long i = 0; i < n; i++) {
        suma += arr[i];
    }
    return suma;
}

/* ---------------------------------------------------------------
 * SUMA PARALELA CON OpenMP
 *   - #pragma omp parallel for: distribuye las iteraciones entre hilos
 *   - reduction(+:suma): cada hilo acumula su parcial; al final se suman
 *   - num_threads(hilos): controla el numero de hilos en tiempo de ejecucion
 *   - schedule(static): distribucion estatica e igual entre hilos
 * --------------------------------------------------------------- */
long long suma_paralela_omp(volatile long long *arr, long long n, int hilos) {
    long long suma = 0;
    #pragma omp parallel for reduction(+:suma) num_threads(hilos) schedule(static)
    for (long long i = 0; i < n; i++) {
        suma += arr[i];
    }
    return suma;
}

/* ---------------------------------------------------------------
 * LEY DE AMDAHL
 *   f: fraccion del codigo que puede ejecutarse en paralelo
 *   p: numero de procesadores/hilos
 * --------------------------------------------------------------- */
double ley_amdahl(double f, int p) {
    return 1.0 / ((1.0 - f) + f / (double)p);
}
