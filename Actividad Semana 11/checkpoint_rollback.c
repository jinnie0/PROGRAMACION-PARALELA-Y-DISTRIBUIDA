/* =====================================================================
 * checkpoint_rollback.c
 * Actividad Semana 11 - Tolerancia a Fallos: Checkpoint y Rollback Recovery
 * Computacion Paralela y Distribuida
 *
 * Aplicacion MPI que realiza una suma de vectores por bloques, toma
 * checkpoints COORDINADOS cada cierto numero de iteraciones y es capaz
 * de recuperar su estado (rollback recovery) tras un fallo simulado.
 * ===================================================================== */

#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define VECTOR_SIZE     999999    /* tamano total del vector a sumar (multiplo de 3 y de 10*3) */
#define TOTAL_ITER      10        /* numero total de "bloques" a procesar   */
#define CKPT_EVERY      2         /* frecuencia de checkpoint (iteraciones) */
#define FAIL_AT_ITER    5         /* iteracion en la que se simula el fallo */
#define FAIL_RANK       1         /* proceso que sufre el fallo simulado    */

/* Estado critico que se guarda/recupera en cada checkpoint */
typedef struct {
    int    rank;
    int    iter_done;   /* ultima iteracion completada */
    double local_sum;   /* acumulador parcial */
} CheckpointState;

static void checkpoint_path(int rank, char *buf, size_t len) {
    snprintf(buf, len, "checkpoint_rank_%d.dat", rank);
}

/* Guarda el estado en disco (checkpoint local) */
static void save_checkpoint(const CheckpointState *st) {
    char path[64];
    checkpoint_path(st->rank, path, sizeof(path));
    FILE *f = fopen(path, "wb");
    if (!f) { perror("fopen checkpoint"); return; }
    fwrite(st, sizeof(CheckpointState), 1, f);
    fclose(f);
}

/* Intenta cargar un checkpoint previo. Devuelve 1 si existia, 0 si no. */
static int load_checkpoint(int rank, CheckpointState *st) {
    char path[64];
    checkpoint_path(rank, path, sizeof(path));
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    size_t n = fread(st, sizeof(CheckpointState), 1, f);
    fclose(f);
    return n == 1;
}

/* Simula un fallo abortando el proceso solo la primera vez que se ejecuta.
 * Se usa un archivo "marcador" para no volver a fallar en la corrida
 * de recuperacion (rollback). */
static void maybe_simulate_failure(int rank, int iter) {
    if (rank != FAIL_RANK || iter != FAIL_AT_ITER) return;

    const char *marker = "fail_injected.marker";
    if (access(marker, F_OK) == 0) return;  /* ya fallamos antes, no repetir */

    FILE *f = fopen(marker, "w");
    if (f) { fclose(f); }

    fprintf(stderr,
        "[rank %d] *** FALLO SIMULADO en iteracion %d (exit forzado) ***\n",
        rank, iter);
    fflush(stderr);
    _exit(1);   /* aborta el proceso sin limpiar MPI: simula una caida real */
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank, nprocs;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    if (nprocs < 3) {
        if (rank == 0)
            fprintf(stderr, "Se requieren al menos 3 procesos (usa -np 3 o mas).\n");
        MPI_Finalize();
        return 1;
    }

    /* Reparto del vector entre procesos */
    int chunk = VECTOR_SIZE / nprocs;
    chunk -= chunk % TOTAL_ITER;   /* aseguramos que sea divisible entre las iteraciones */
    double *a = malloc(chunk * sizeof(double));
    double *b = malloc(chunk * sizeof(double));
    for (int i = 0; i < chunk; i++) {
        a[i] = 1.0;
        b[i] = 2.0;
    }

    CheckpointState state;
    int start_iter;

    /* --- ROLLBACK: verificar si existe checkpoint antes de continuar --- */
    if (load_checkpoint(rank, &state)) {
        start_iter = state.iter_done + 1;
        printf("[rank %d] Checkpoint encontrado. Reanudando desde iteracion %d "
               "(suma parcial = %.2f)\n", rank, start_iter, state.local_sum);
    } else {
        state.rank = rank;
        state.iter_done = -1;
        state.local_sum = 0.0;
        start_iter = 0;
        printf("[rank %d] No hay checkpoint previo. Iniciando desde cero.\n", rank);
    }

    int per_iter = chunk / TOTAL_ITER;

    for (int iter = start_iter; iter < TOTAL_ITER; iter++) {

        /* --- COMPUTO: suma parcial del bloque correspondiente a esta iteracion --- */
        int offset = iter * per_iter;
        for (int i = 0; i < per_iter; i++) {
            state.local_sum += a[offset + i] + b[offset + i];
        }
        state.iter_done = iter;

        /* --- FALLO SIMULADO --- */
        maybe_simulate_failure(rank, iter);

        /* --- CHECKPOINT COORDINADO --- */
        if ((iter + 1) % CKPT_EVERY == 0) {
            MPI_Barrier(MPI_COMM_WORLD);   /* sincroniza a todos antes de guardar */
            save_checkpoint(&state);
            if (rank == 0)
                printf(">>> Checkpoint coordinado global tomado en iteracion %d\n", iter);
            MPI_Barrier(MPI_COMM_WORLD);   /* asegura que todos terminaron de guardar */
        }
    }

    /* Reduccion final: suma global de todos los procesos */
    double global_sum = 0.0;
    MPI_Reduce(&state.local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    printf("[rank %d] Finalizado. Suma local = %.2f\n", rank, state.local_sum);
    if (rank == 0) {
        printf("=== Suma global de todos los procesos: %.2f ===\n", global_sum);
    }

    free(a);
    free(b);
    MPI_Finalize();
    return 0;
}
