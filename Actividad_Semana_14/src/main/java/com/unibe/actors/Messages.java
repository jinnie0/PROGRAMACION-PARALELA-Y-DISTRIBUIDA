package com.unibe.actors;

import java.io.Serializable;

/**
 * Contenedor de todos los mensajes que viajan entre Supervisor y Workers.
 * En Akka la comunicacion es 100% asincrona y por mensajes inmutables,
 * nunca por memoria compartida (por eso no hacen falta locks).
 */
public class Messages {

    // ---- Trabajo que el cliente HTTP (Lambda) le pide al Supervisor ----
    public static class ProcessTask implements Serializable {
        public final String taskId;
        public final String operation; // "SUM" o "STRING"
        public final String payload;   // ej: "3,4,5" o "hola mundo"

        public ProcessTask(String taskId, String operation, String payload) {
            this.taskId = taskId;
            this.operation = operation;
            this.payload = payload;
        }
    }

    // ---- Supervisor -> Worker: despacha el trabajo ----
    public static class WorkerJob implements Serializable {
        public final String taskId;
        public final String operation;
        public final String payload;
        public final boolean simulateFailure;

        public WorkerJob(String taskId, String operation, String payload, boolean simulateFailure) {
            this.taskId = taskId;
            this.operation = operation;
            this.payload = payload;
            this.simulateFailure = simulateFailure;
        }
    }

    // ---- Worker -> Supervisor -> Cliente: resultado exitoso ----
    public static class TaskResult implements Serializable {
        public final String taskId;
        public final String result;
        public final String workerName;

        public TaskResult(String taskId, String result, String workerName) {
            this.taskId = taskId;
            this.result = result;
            this.workerName = workerName;
        }
    }

    // ---- Worker -> Supervisor: error controlado (antes de relanzar excepcion) ----
    public static class TaskFailed implements Serializable {
        public final String taskId;
        public final String reason;

        public TaskFailed(String taskId, String reason) {
            this.taskId = taskId;
            this.reason = reason;
        }
    }
}
