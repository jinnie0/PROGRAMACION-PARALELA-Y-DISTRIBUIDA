package com.unibe;

import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import com.unibe.actors.Messages.ProcessTask;
import com.unibe.actors.SupervisorActor;

/**
 * Prueba local del microservicio de actores (sin AWS).
 * Sirve para grabar el video de sustentacion y para las capturas de logs
 * del informe: se ve el despacho de tareas, el fallo intencional y el
 * reinicio automatico del worker.
 */
public class Main {
    public static void main(String[] args) throws InterruptedException {
        ActorSystem system = ActorSystem.create("test-local");
        ActorRef supervisor = system.actorOf(SupervisorActor.props(), "supervisor");

        // Tareas normales, repartidas en round-robin entre los 4 workers
        supervisor.tell(new ProcessTask("t1", "SUM", "1,2,3"), ActorRef.noSender());
        supervisor.tell(new ProcessTask("t2", "STRING", "hola mundo"), ActorRef.noSender());
        supervisor.tell(new ProcessTask("t3", "SUM", "10,20,30"), ActorRef.noSender());

        // Tarea que provoca fallo intencional -> el supervisor debe reiniciar el worker
        supervisor.tell(new ProcessTask("t4-fail", "FAIL", "n/a"), ActorRef.noSender());

        // Tarea posterior, para comprobar que el worker reiniciado sigue funcionando
        Thread.sleep(500);
        supervisor.tell(new ProcessTask("t5", "SUM", "100,200"), ActorRef.noSender());

        Thread.sleep(2000);
        system.terminate();
    }
}
