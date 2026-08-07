# Actividad Semana 9 – MPI Avanzado: Comunicaciones Colectivas

Programa en C que calcula, de forma distribuida, el promedio de valores generados aleatoriamente por cada proceso, usando las operaciones colectivas de MPI `MPI_Bcast` y `MPI_Reduce`.

**Curso:** Computación Paralela y Distribuida
**Estudiante:** Jinnie
**Universidad:** UNIBE

## Descripción

Cada proceso genera N valores aleatorios y calcula su suma parcial. Las sumas parciales se combinan con `MPI_Reduce` en el proceso raíz, que calcula el promedio global y lo distribuye de nuevo a todos los procesos con `MPI_Bcast`.

## Archivos

- `promedio_colectivo.c` — código fuente del programa.
- `Informe_Semana9_MPI_Colectivas.docx` — informe explicativo (PDF/Word) con justificación, salidas de ejemplo y reflexión sobre sincronización.

## Requisitos

- Compilador MPI (OpenMPI o MPICH)
- Linux (probado en Ubuntu 22.04 LTS, VirtualBox)

Instalación de OpenMPI si no lo tienes:

```bash
sudo apt update
sudo apt install libopenmpi-dev openmpi-bin
```

## Compilación

```bash
mpicc promedio_colectivo.c -o promedio_colectivo
```

## Ejecución

```bash
mpirun -np 4 ./promedio_colectivo
```

Al ejecutarlo, el proceso raíz (rank 0) pedirá el valor de **N** (cantidad de valores por proceso). Cambia `-np 4` por el número de procesos que quieras usar.

### Ejemplo de salida

```
Proceso raiz: ingrese la cantidad de valores (N) por proceso: 5
Proceso 0: suma parcial = 245.3821 (con N = 5 valores)
Proceso 1: suma parcial = 198.7452 (con N = 5 valores)
Proceso 2: suma parcial = 267.1098 (con N = 5 valores)
Proceso 3: suma parcial = 221.6304 (con N = 5 valores)

--- Proceso raiz ---
Suma total de todos los procesos: 932.8675
Promedio global: 46.6434

Proceso 0 recibio el promedio global: 46.6434
Proceso 1 recibio el promedio global: 46.6434
Proceso 2 recibio el promedio global: 46.6434
Proceso 3 recibio el promedio global: 46.6434
```

## Estructura del código

1. Inicialización de MPI (`MPI_Init`, `MPI_Comm_rank`, `MPI_Comm_size`).
2. Lectura de N en el proceso raíz y distribución con `MPI_Bcast`.
3. Generación local de valores aleatorios y suma parcial por proceso.
4. Reducción de las sumas parciales con `MPI_Reduce` (`MPI_SUM`).
5. Cálculo del promedio global en el proceso raíz.
6. Distribución del promedio a todos los procesos con `MPI_Bcast`.
7. Impresión del promedio recibido en cada proceso.
8. Finalización con `MPI_Finalize`.

## Nota sobre sincronización

`MPI_Bcast` y `MPI_Reduce` son operaciones **bloqueantes**: ningún proceso avanza más allá de la llamada colectiva hasta que todos los procesos del comunicador la hayan invocado. Por eso ninguna llamada colectiva está condicionada por `rank` en este código; solo la lectura de N (exclusiva del proceso raíz) ocurre antes del primer punto de sincronización.

## Licencia

Uso académico – UNIBE.
