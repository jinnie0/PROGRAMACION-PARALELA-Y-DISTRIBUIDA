/*
 * omp_vector_add.c
 * Suma de vectores en CPU utilizando OpenMP.
 * Compilar:  gcc -fopenmp -O2 omp_vector_add.c -o omp_vector_add
 * Ejecutar:  ./omp_vector_add
 */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define N 1048576  /* 1,048,576 = 1M elementos */

int main(void) {
    float *A = (float *) malloc(N * sizeof(float));
    float *B = (float *) malloc(N * sizeof(float));
    float *C = (float *) malloc(N * sizeof(float));

    if (A == NULL || B == NULL || C == NULL) {
        fprintf(stderr, "Error: no se pudo reservar memoria.\n");
        return 1;
    }

    /* Inicializar los vectores de entrada */
    for (int i = 0; i < N; i++) {
        A[i] = (float) i;
        B[i] = (float) (2 * i);
    }

    printf("Hilos disponibles (omp_get_max_threads): %d\n", omp_get_max_threads());

    double t_inicio = omp_get_wtime();

    #pragma omp parallel for
    for (int i = 0; i < N; i++) {
        C[i] = A[i] + B[i];
    }

    double t_fin = omp_get_wtime();
    double tiempo_omp = t_fin - t_inicio;

    /* Verificación de resultados */
    int errores = 0;
    for (int i = 0; i < N; i++) {
        if (C[i] != A[i] + B[i]) errores++;
    }

    printf("Elementos procesados: %d\n", N);
    printf("Errores de verificacion: %d\n", errores);
    printf("Tiempo de ejecucion OpenMP: %f segundos\n", tiempo_omp);

    free(A);
    free(B);
    free(C);
    return 0;
}
