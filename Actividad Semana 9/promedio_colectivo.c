/* ============================================================
 * Actividad Semana 9 - MPI Avanzado: Comunicaciones Colectivas
 * Programa: Calculo distribuido de un promedio usando
 *           MPI_Bcast y MPI_Reduce
 * Autora: Jinnie
 * ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

int main(int argc, char *argv[]) {

    /* -----------------------------------------------------
     * FASE 1: Inicializacion de MPI
     * ----------------------------------------------------- */
    int rank, num_procs;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

    /* -----------------------------------------------------
     * FASE 2: El proceso raiz (rank 0) pide el valor N
     * y lo distribuye a todos los procesos con MPI_Bcast
     * ----------------------------------------------------- */
    int N;

    if (rank == 0) {
        printf("Proceso raiz: ingrese la cantidad de valores (N) por proceso: ");
        fflush(stdout);
        scanf("%d", &N);
    }

    /* Bloquea a todos los procesos hasta que rank 0 entregue N */
    MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);

    /* -----------------------------------------------------
     * FASE 3: Generacion local de valores aleatorios
     * y calculo de la suma parcial de cada proceso
     * ----------------------------------------------------- */
    srand((unsigned int) time(NULL) + rank * 100);

    double suma_local = 0.0;
    double valor;

    for (int i = 0; i < N; i++) {
        valor = (double) (rand() % 100) + ((double) rand() / RAND_MAX);
        suma_local += valor;
    }

    printf("Proceso %d: suma parcial = %.4f (con N = %d valores)\n",
           rank, suma_local, N);

    /* -----------------------------------------------------
     * FASE 4: Reduccion de las sumas parciales en el proceso raiz
     * ----------------------------------------------------- */
    double suma_total = 0.0;

    MPI_Reduce(&suma_local, &suma_total, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    /* -----------------------------------------------------
     * FASE 5: El proceso raiz calcula el promedio total
     * ----------------------------------------------------- */
    double promedio = 0.0;

    if (rank == 0) {
        promedio = suma_total / (N * num_procs);
        printf("\n--- Proceso raiz ---\n");
        printf("Suma total de todos los procesos: %.4f\n", suma_total);
        printf("Promedio global: %.4f\n\n", promedio);
    }

    /* -----------------------------------------------------
     * FASE 6: Distribucion del promedio a todos los procesos
     * ----------------------------------------------------- */
    MPI_Bcast(&promedio, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    /* -----------------------------------------------------
     * FASE 7: Cada proceso imprime el promedio recibido
     * ----------------------------------------------------- */
    printf("Proceso %d recibio el promedio global: %.4f\n", rank, promedio);

    /* -----------------------------------------------------
     * FASE 8: Finalizacion de MPI
     * ----------------------------------------------------- */
    MPI_Finalize();

    return 0;
}
