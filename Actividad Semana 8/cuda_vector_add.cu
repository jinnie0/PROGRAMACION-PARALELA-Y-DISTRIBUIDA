/*
 * cuda_vector_add.cu
 * Suma de vectores en GPU utilizando CUDA.
 * Compilar:  nvcc -O2 cuda_vector_add.cu -o cuda_vector_add
 * Ejecutar:  ./cuda_vector_add
 */

#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>

#define N 1048576          /* 1,048,576 = 1M elementos */
#define HILOS_POR_BLOQUE 256

/* Macro para revisar errores de CUDA en cada llamada */
#define CUDA_CHECK(llamada)                                                 \
    do {                                                                    \
        cudaError_t err = (llamada);                                       \
        if (err != cudaSuccess) {                                          \
            fprintf(stderr, "Error CUDA en %s:%d -> %s\n", __FILE__,       \
                    __LINE__, cudaGetErrorString(err));                    \
            exit(EXIT_FAILURE);                                            \
        }                                                                   \
    } while (0)

/* Kernel: cada hilo calcula un elemento del vector resultado */
__global__ void add_vectors(const float *A, const float *B, float *C, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        C[i] = A[i] + B[i];
    }
}

int main(void) {
    size_t bytes = N * sizeof(float);

    /* Reserva de memoria en el host (CPU) */
    float *h_A = (float *) malloc(bytes);
    float *h_B = (float *) malloc(bytes);
    float *h_C = (float *) malloc(bytes);

    for (int i = 0; i < N; i++) {
        h_A[i] = (float) i;
        h_B[i] = (float) (2 * i);
    }

    /* Reserva de memoria en el device (GPU) */
    float *d_A, *d_B, *d_C;
    CUDA_CHECK(cudaMalloc((void **) &d_A, bytes));
    CUDA_CHECK(cudaMalloc((void **) &d_B, bytes));
    CUDA_CHECK(cudaMalloc((void **) &d_C, bytes));

    /* Eventos CUDA para medir el tiempo total (incluye transferencias) */
    cudaEvent_t inicio, fin;
    CUDA_CHECK(cudaEventCreate(&inicio));
    CUDA_CHECK(cudaEventCreate(&fin));

    CUDA_CHECK(cudaEventRecord(inicio));

    /* Host -> Device */
    CUDA_CHECK(cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice));

    /* Configuracion de la ejecucion: bloques necesarios para cubrir N */
    int bloques = (N + HILOS_POR_BLOQUE - 1) / HILOS_POR_BLOQUE;
    add_vectors<<<bloques, HILOS_POR_BLOQUE>>>(d_A, d_B, d_C, N);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());

    /* Device -> Host */
    CUDA_CHECK(cudaMemcpy(h_C, d_C, bytes, cudaMemcpyDeviceToHost));

    CUDA_CHECK(cudaEventRecord(fin));
    CUDA_CHECK(cudaEventSynchronize(fin));

    float tiempo_ms = 0;
    CUDA_CHECK(cudaEventElapsedTime(&tiempo_ms, inicio, fin));

    /* Verificacion de resultados */
    int errores = 0;
    for (int i = 0; i < N; i++) {
        if (h_C[i] != h_A[i] + h_B[i]) errores++;
    }

    printf("Elementos procesados: %d\n", N);
    printf("Configuracion: %d bloques x %d hilos\n", bloques, HILOS_POR_BLOQUE);
    printf("Errores de verificacion: %d\n", errores);
    printf("Tiempo total GPU (transferencias + kernel): %f ms\n", tiempo_ms);

    /* Liberar memoria */
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    free(h_A);
    free(h_B);
    free(h_C);

    cudaEventDestroy(inicio);
    cudaEventDestroy(fin);

    return 0;
}
