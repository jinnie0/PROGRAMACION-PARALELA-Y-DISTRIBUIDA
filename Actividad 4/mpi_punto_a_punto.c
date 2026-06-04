/*
 * Actividad 4 - Comunicación Punto a Punto con MPI
 * Semana 4: Programación Paralela
 *
 * Compilación:
 *   mpicc -o mpi_punto_a_punto mpi_punto_a_punto.c
 *
 * Ejecución:
 *   mpirun -np 2 ./mpi_punto_a_punto
 */

#include <stdio.h>
#include <mpi.h>

int main(int argc, char *argv[]) {

    int rank;        /* Identificador del proceso actual */
    int size;        /* Número total de procesos         */
    int valor = 0;   /* Variable que se enviará/recibirá */

    /* ── 1. Inicializar el entorno MPI ─────────────────────────────────── */
    MPI_Init(&argc, &argv);

    /* ── 2. Obtener el rank e el número total de procesos ───────────────── */
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /* Verificar que se ejecuten exactamente 2 procesos */
    if (size != 2) {
        if (rank == 0) {
            fprintf(stderr, "Este programa requiere exactamente 2 procesos.\n");
            fprintf(stderr, "Uso: mpirun -np 2 ./mpi_punto_a_punto\n");
        }
        MPI_Finalize();
        return 1;
    }

    /* ── 3. Comunicación Punto a Punto ──────────────────────────────────── */
    if (rank == 0) {
        /* Proceso emisor */
        valor = 100;
        printf("[Proceso %d] Enviando valor: %d al proceso 1\n", rank, valor);

        /*
         * MPI_Send(buffer, count, datatype, dest, tag, comm)
         *   buffer   : dirección de la variable a enviar
         *   count    : número de elementos
         *   datatype : tipo de dato MPI (MPI_INT = entero)
         *   dest     : rank del proceso destino (1)
         *   tag      : etiqueta del mensaje (0)
         *   comm     : comunicador (MPI_COMM_WORLD)
         */
        MPI_Send(&valor, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        printf("[Proceso %d] Mensaje enviado exitosamente.\n", rank);

    } else if (rank == 1) {
        /* Proceso receptor */
        MPI_Status status;  /* Estructura con información del mensaje recibido */

        /*
         * MPI_Recv(buffer, count, datatype, source, tag, comm, status)
         *   buffer   : dirección donde se almacenará el dato recibido
         *   count    : número máximo de elementos esperados
         *   datatype : tipo de dato MPI (MPI_INT)
         *   source   : rank del proceso emisor (0)
         *   tag      : etiqueta del mensaje esperado (0)
         *   comm     : comunicador (MPI_COMM_WORLD)
         *   status   : información sobre el mensaje recibido
         */
        MPI_Recv(&valor, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);

        printf("[Proceso %d] Valor recibido: %d  (enviado por el proceso %d)\n",
               rank, valor, status.MPI_SOURCE);
    }

    /* ── 4. Finalizar el entorno MPI ────────────────────────────────────── */
    MPI_Finalize();
    return 0;
}
