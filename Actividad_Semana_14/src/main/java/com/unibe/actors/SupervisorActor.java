package com.unibe.actors;

import akka.actor.*;
import akka.event.Logging;
import akka.event.LoggingAdapter;
import com.unibe.actors.Messages.*;
import scala.concurrent.duration.Duration;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Actor Supervisor: crea y administra un pool fijo de WorkerActor.
 * Implementa el patron "one-for-one supervision": si un worker falla,
 * SOLO ese worker se reinicia; los demas siguen operando sin interrupcion.
 *
 * Ademas hace de "router" simple: reparte las tareas entrantes en round-robin
 * y lleva un mapa de que cliente (ActorRef original) espera cada resultado,
 * para poder responderle aunque el resultado llegue de forma asincrona.
 */
public class SupervisorActor extends AbstractActor {

    private final LoggingAdapter log = Logging.getLogger(getContext().getSystem(), this);

    private static final int POOL_SIZE = 4;
    private final List<ActorRef> workers = new ArrayList<>();
    private final Map<String, ActorRef> pendingReplies = new HashMap<>(); // taskId -> quien pidio la tarea
    private int nextWorker = 0;

    public static Props props() {
        return Props.create(SupervisorActor.class);
    }

    @Override
    public void preStart() {
        for (int i = 0; i < POOL_SIZE; i++) {
            ActorRef worker = getContext().actorOf(WorkerActor.props(), "worker-" + i);
            getContext().watch(worker); // por si el worker muere definitivamente
            workers.add(worker);
        }
        log.info("Supervisor iniciado con {} workers.", POOL_SIZE);
    }

    /**
     * Estrategia de supervision "one-for-one":
     * - RuntimeException (fallo simulado o de negocio) -> RESTART del worker afectado
     * - IllegalArgumentException (payload invalido)     -> RESUME (ignora el error, sigue igual)
     * - Cualquier otro Throwable                        -> ESCALATE al padre
     * maxNrOfRetries=5 dentro de una ventana de 1 minuto evita loops infinitos de reinicio.
     */
    @Override
    public SupervisorStrategy supervisorStrategy() {
        return new OneForOneStrategy(
                5,
                Duration.create(1, TimeUnit.MINUTES),
                cause -> {
                    if (cause instanceof IllegalArgumentException) {
                        log.warning("Error de argumento, se resume el worker: {}", cause.getMessage());
                        return SupervisorStrategy.resume();
                    } else if (cause instanceof RuntimeException) {
                        log.warning("Fallo en worker, se reinicia: {}", cause.getMessage());
                        return SupervisorStrategy.restart();
                    } else {
                        return SupervisorStrategy.escalate();
                    }
                }
        );
    }

    @Override
    public Receive createReceive() {
        return receiveBuilder()
                .match(ProcessTask.class, this::dispatchToWorker)
                .match(TaskResult.class, this::forwardResult)
                .match(Terminated.class, t -> log.error("Worker terminado definitivamente: {}", t.getActor()))
                .build();
    }

    private void dispatchToWorker(ProcessTask task) {
        ActorRef chosen = workers.get(nextWorker);
        nextWorker = (nextWorker + 1) % workers.size();

        // Guardamos quien nos pidio la tarea para poder contestarle luego
        pendingReplies.put(task.taskId, getSender());

        boolean simulateFailure = "FAIL".equalsIgnoreCase(task.operation);
        String realOp = simulateFailure ? "SUM" : task.operation;

        log.info("Despachando tarea {} al worker {}", task.taskId, chosen.path().name());
        chosen.tell(new WorkerJob(task.taskId, realOp, task.payload, simulateFailure), getSelf());
    }

    private void forwardResult(TaskResult result) {
        ActorRef originalSender = pendingReplies.remove(result.taskId);
        if (originalSender != null) {
            originalSender.tell(result, getSelf());
        }
        log.info("Resultado de {} listo: {}", result.taskId, result.result);
    }
}
