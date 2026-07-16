#!/bin/bash
# Compila y ejecuta la demo de checkpoint / rollback recovery
set -e

echo "== Limpiando checkpoints y marcadores anteriores =="
rm -f checkpoint_rank_*.dat fail_injected.marker

echo "== Compilando =="
mpicc -Wall -o checkpoint_rollback checkpoint_rollback.c

echo ""
echo "== Ejecucion 1: se espera un fallo simulado en el proceso 1 =="
mpirun -np 3 ./checkpoint_rollback || echo "(el trabajo termino con fallo, como se esperaba)"

echo ""
echo "== Ejecucion 2: rollback recovery, debe reanudar desde el ultimo checkpoint =="
mpirun -np 3 ./checkpoint_rollback

# Nota: si tu maquina/VM tiene menos nucleos que procesos (-np 3),
# agrega --oversubscribe despues de mpirun.
