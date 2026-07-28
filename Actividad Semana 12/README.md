# Prototipo de Consenso Distribuido — Raft

Prototipo en Python que simula un clúster de **3 nodos** ejecutando el algoritmo de consenso **Raft**, incluyendo elección de líder, replicación de log y recuperación ante fallo de nodo.

Actividad Semana 12 — Parallel and Distributed Computing — UNIBE.

## Descripción

El script simula el clúster con hilos (`threading`) y colas en memoria (`queue`), sin necesidad de red real. Cada nodo implementa la máquina de estados de Raft:

- **Follower**: estado inicial de todo nodo. Espera heartbeats del líder.
- **Candidate**: si expira su timeout de elección (aleatorio), se postula y pide votos con `RequestVote`.
- **Leader**: el nodo que obtiene mayoría de votos. Envía heartbeats (`AppendEntries`) y replica la entrada de log `"A=1"` a los demás nodos.

El programa ejecuta dos fases automáticamente:

1. **Elección inicial y replicación**: los 3 nodos arrancan como followers, se elige un líder y este replica `"A=1"` a los otros dos.
2. **Simulación de fallo**: el script detiene al nodo líder (`activo = False`). Los nodos restantes dejan de recibir heartbeats, disparan una nueva elección y uno de ellos se convierte en el nuevo líder, demostrando que el clúster tolera la caída de un nodo mientras mantenga mayoría.

## Requisitos

- Python 3.8 o superior (no requiere librerías externas).

## Cómo ejecutarlo

```bash
git clone <url-del-repositorio>
cd <carpeta-del-repositorio>
python raft_prototype.py
```

La ejecución dura unos 9 segundos y muestra en consola:

- El timeout de elección y la postulación del candidato.
- El nodo que gana la mayoría y se vuelve líder.
- La replicación de la entrada `"A=1"` en cada follower.
- El mensaje de la caída simulada del líder.
- La nueva elección y el líder de reemplazo.
- Un resumen final con el estado, término (`term`) y log de cada nodo.

## Archivos

| Archivo | Contenido |
|---|---|
| `raft_prototype.py` | Código fuente del prototipo. |
| `raft_log.txt` | Log de una ejecución de ejemplo, usado como evidencia en el informe. |

## Notas de diseño

- Los timeouts de elección son aleatorios (entre 1.0 y 2.0 segundos) para evitar que dos nodos se postulen exactamente al mismo tiempo, tal como lo indica el algoritmo original.
- La mayoría requerida es `(NUM_NODOS // 2) + 1`, es decir 2 de 3 nodos.
- El "fallo" del líder se simula marcándolo como inactivo (`activo = False`), lo que detiene su procesamiento de mensajes sin eliminarlo del clúster, simulando una caída temporal.

## Referencias

- Ongaro, D., & Ousterhout, J. (2014). *In search of an understandable consensus algorithm (extended version)*. Stanford University. https://raft.github.io/raft.pdf
- The Raft Consensus Algorithm. (s.f.). *Raft: Home*. https://raft.github.io/
