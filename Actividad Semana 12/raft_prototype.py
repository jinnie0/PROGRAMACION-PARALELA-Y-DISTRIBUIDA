"""
Prototipo de consenso distribuido usando el algoritmo Raft.
Simula un clúster de 3 nodos con hilos y colas en memoria (sin red real).

Roles: follower, candidate, leader.
Fases: elección de líder (RequestVote) y replicación de log (AppendEntries).
Incluye simulación de fallo del líder y recuperación automática del clúster.

Ejecutar: python raft_prototype.py
"""

import queue
import random
import threading
import time

NUM_NODOS = 3
HEARTBEAT_INTERVALO = 0.3           # segundos entre heartbeats del líder
ELECCION_TIMEOUT_RANGO = (1.0, 2.0)  # rango aleatorio del timeout de elección

FOLLOWER, CANDIDATE, LEADER = "FOLLOWER", "CANDIDATE", "LEADER"

lock_consola = threading.Lock()


def log(nodo_id, mensaje):
    with lock_consola:
        print(f"[t={time.time() - INICIO:6.2f}s] Nodo-{nodo_id}: {mensaje}")


class Nodo:
    def __init__(self, nodo_id, todos_los_ids):
        self.id = nodo_id
        self.pares = [n for n in todos_los_ids if n != nodo_id]
        self.estado = FOLLOWER
        self.term = 0
        self.voted_for = None
        self.log_replicado = []          # entradas confirmadas, p.ej. "A=1"
        self.buzon = queue.Queue()       # mensajes entrantes
        self.buzones_globales = {}       # referencia a los buzones de todos los nodos
        self.activo = True               # False simula un nodo caído
        self.leader_id = None
        self._ultimo_heartbeat = time.time()
        self._lock = threading.Lock()

    # --- utilidades de comunicación ---
    def enviar(self, destino_id, mensaje):
        if destino_id in self.buzones_globales:
            self.buzones_globales[destino_id].put(mensaje)

    def difundir(self, mensaje):
        for p in self.pares:
            self.enviar(p, mensaje)

    def reiniciar_timeout(self):
        self._ultimo_heartbeat = time.time()
        self._timeout_actual = random.uniform(*ELECCION_TIMEOUT_RANGO)

    # --- ciclo principal del nodo ---
    def correr(self):
        self.reiniciar_timeout()
        while True:
            if not self.activo:
                time.sleep(0.1)
                continue

            self._procesar_mensajes_pendientes()

            if self.estado == LEADER:
                self._actuar_como_lider()
            else:
                self._verificar_timeout_eleccion()

            time.sleep(0.05)

    def _procesar_mensajes_pendientes(self):
        while not self.buzon.empty():
            try:
                msg = self.buzon.get_nowait()
            except queue.Empty:
                break
            self._manejar_mensaje(msg)

    def _manejar_mensaje(self, msg):
        tipo = msg["tipo"]

        if msg.get("term", 0) > self.term:
            self.term = msg["term"]
            self.estado = FOLLOWER
            self.voted_for = None

        if tipo == "RequestVote":
            concede = (self.voted_for in (None, msg["candidato_id"])) and msg["term"] >= self.term
            if concede:
                self.voted_for = msg["candidato_id"]
                self.reiniciar_timeout()
            self.enviar(msg["candidato_id"], {
                "tipo": "VoteResponse", "term": self.term,
                "votante_id": self.id, "concedido": concede,
            })

        elif tipo == "VoteResponse" and self.estado == CANDIDATE:
            if msg["concedido"]:
                self._votos_recibidos.add(msg["votante_id"])
                mayoria = (NUM_NODOS // 2) + 1
                if len(self._votos_recibidos) + 1 >= mayoria:
                    self._convertirse_en_lider()

        elif tipo == "AppendEntries":
            self.estado = FOLLOWER
            self.leader_id = msg["lider_id"]
            self.reiniciar_timeout()
            if msg["entrada"] and msg["entrada"] not in self.log_replicado:
                self.log_replicado.append(msg["entrada"])
                log(self.id, f"replicó entrada '{msg['entrada']}' del líder {msg['lider_id']} (term {self.term})")
            self.enviar(msg["lider_id"], {"tipo": "AppendAck", "term": self.term, "seguidor_id": self.id})

    def _verificar_timeout_eleccion(self):
        if time.time() - self._ultimo_heartbeat >= self._timeout_actual:
            self._iniciar_eleccion()

    def _iniciar_eleccion(self):
        self.estado = CANDIDATE
        self.term += 1
        self.voted_for = self.id
        self._votos_recibidos = set()
        self.reiniciar_timeout()
        log(self.id, f"timeout de elección -> se postula como candidato (term {self.term})")
        self.difundir({"tipo": "RequestVote", "term": self.term, "candidato_id": self.id})

    def _convertirse_en_lider(self):
        self.estado = LEADER
        self.leader_id = self.id
        log(self.id, f"*** obtuvo mayoría de votos -> nuevo LÍDER (term {self.term}) ***")

    def _actuar_como_lider(self):
        if time.time() - self._ultimo_heartbeat >= HEARTBEAT_INTERVALO:
            entrada = "A=1" if "A=1" not in self.log_replicado else None
            if entrada and entrada not in self.log_replicado:
                self.log_replicado.append(entrada)
            self.difundir({
                "tipo": "AppendEntries", "term": self.term,
                "lider_id": self.id, "entrada": entrada,
            })
            self._ultimo_heartbeat = time.time()


def main():
    global INICIO
    INICIO = time.time()

    ids = list(range(NUM_NODOS))
    nodos = {i: Nodo(i, ids) for i in ids}
    buzones = {i: n.buzon for i, n in nodos.items()}
    for n in nodos.values():
        n.buzones_globales = buzones

    hilos = []
    for n in nodos.values():
        h = threading.Thread(target=n.correr, daemon=True)
        hilos.append(h)
        h.start()

    print("== Fase 1: elección inicial de líder y replicación de 'A=1' ==\n")
    time.sleep(4)

    lider_actual = next(n for n in nodos.values() if n.estado == LEADER)
    print(f"\n== Fase 2: simulando la caída del líder actual (Nodo-{lider_actual.id}) ==\n")
    lider_actual.activo = False

    time.sleep(4)

    supervivientes = [n for n in nodos.values() if n.activo]
    nuevo_lider = next((n for n in supervivientes if n.estado == LEADER), None)
    print("\n== Resultado final ==")
    for n in nodos.values():
        estado_desc = "CAÍDO" if not n.activo else n.estado
        print(f"Nodo-{n.id}: estado={estado_desc}, term={n.term}, log={n.log_replicado}")

    if nuevo_lider:
        print(f"\nEl clúster se recuperó: Nodo-{nuevo_lider.id} es el nuevo líder y el consenso sigue funcionando "
              f"con {len(supervivientes)} de {NUM_NODOS} nodos activos (mayoría).")
    else:
        print("\nNo se eligió un nuevo líder en el tiempo de espera dado (probar de nuevo o ampliar el tiempo).")


if __name__ == "__main__":
    main()
