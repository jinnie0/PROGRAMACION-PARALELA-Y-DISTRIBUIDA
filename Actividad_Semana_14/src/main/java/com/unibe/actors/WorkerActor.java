package com.unibe.actors;

import akka.actor.AbstractActor;
import akka.actor.Props;
import akka.event.Logging;
import akka.event.LoggingAdapter;
import com.unibe.actors.Messages.WorkerJob;
import com.unibe.actors.Messages.TaskResult;

/**
 * Actor Worker: procesa una sola tarea a la vez, encapsula su propio estado
 * (aqui, un contador de tareas procesadas) y esta aislado del resto del
 * sistema. Si algo sale mal, simplemente lanza una excepcion; el Supervisor
 * decide que hacer (reiniciarlo, detenerlo, etc.) segun su estrategia de
 * supervision. El worker NUNCA atrapa su propia excepcion para "arreglarla",
 * eso violaria el patron "let it crash" propio del Modelo de Actores.
 */
public class WorkerActor extends AbstractActor {

    private final LoggingAdapter log = Logging.getLogger(getContext().getSystem(), this);
    private int processedTasks = 0;

    public static Props props() {
        return Props.create(WorkerActor.class);
    }

    @Override
    public void preStart() {
        log.info("[{}] Worker iniciado, listo para recibir trabajo.", getSelf().path().name());
    }

    // Se ejecuta automaticamente cada vez que el Supervisor reinicia este actor
    @Override
    public void preRestart(Throwable reason, scala.Option<Object> message) {
        log.warning("[{}] Worker sera reiniciado por: {}", getSelf().path().name(), reason.getMessage());
    }

    @Override
    public void postRestart(Throwable reason) {
        log.info("[{}] Worker reiniciado exitosamente. Estado interno reseteado.", getSelf().path().name());
    }

    @Override
    public Receive createReceive() {
        return receiveBuilder()
                .match(WorkerJob.class, this::handleJob)
                .matchAny(msg -> log.warning("Mensaje no reconocido: {}", msg))
                .build();
    }

    private void handleJob(WorkerJob job) {
        // Falla intencional para probar el patron de supervision
        if (job.simulateFailure) {
            log.error("[{}] Simulando fallo intencional en tarea {}", getSelf().path().name(), job.taskId);
            throw new RuntimeException("Fallo simulado en tarea " + job.taskId);
        }

        String result;
        switch (job.operation) {
            case "SUM":
                result = sumNumbers(job.payload);
                break;
            case "STRING":
                result = processString(job.payload);
                break;
            default:
                throw new IllegalArgumentException("Operacion no soportada: " + job.operation);
        }

        processedTasks++;
        log.info("[{}] Tarea {} completada. Total procesadas por este worker: {}",
                getSelf().path().name(), job.taskId, processedTasks);

        getSender().tell(new TaskResult(job.taskId, result, getSelf().path().name()), getSelf());
    }

    private String sumNumbers(String payload) {
        String[] parts = payload.split(",");
        long sum = 0;
        for (String p : parts) {
            sum += Long.parseLong(p.trim());
        }
        return String.valueOf(sum);
    }

    private String processString(String payload) {
        // Ejemplo simple: cuenta palabras y devuelve el texto en mayusculas
        int words = payload.trim().isEmpty() ? 0 : payload.trim().split("\\s+").length;
        return "UPPER=" + payload.toUpperCase() + " | WORDS=" + words;
    }
}
