package com.unibe.lambda;

import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.pattern.Patterns;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.unibe.actors.Messages.ProcessTask;
import com.unibe.actors.Messages.TaskResult;
import com.unibe.actors.SupervisorActor;
import scala.concurrent.Await;
import scala.concurrent.Future;
import scala.concurrent.duration.Duration;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

/**
 * Punto de entrada serverless (AWS Lambda + API Gateway).
 *
 * IMPORTANTE (tolerancia a fallos tipica de serverless):
 * - El ActorSystem se crea UNA sola vez por contenedor Lambda (patron de
 *   "warm start"), como campo estatico. Si Lambda reutiliza el contenedor
 *   en la siguiente invocacion, no se vuelve a levantar el sistema de
 *   actores completo -> mejora la latencia (evita "cold start" repetido).
 * - Cada invocacion es un mensaje "ask" con timeout: si el actor no
 *   responde a tiempo (por caida, sobrecarga, etc.) devolvemos 504 en
 *   vez de dejar la Lambda colgada hasta su timeout maximo.
 */
public class ActorLambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    private static final ActorSystem SYSTEM = ActorSystem.create("microservicio-actores");
    private static final ActorRef SUPERVISOR = SYSTEM.actorOf(SupervisorActor.props(), "supervisor");
    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final long ASK_TIMEOUT_SECONDS = 5;

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", "application/json");

        try {
            Map<String, Object> body = MAPPER.readValue(request.getBody(), Map.class);
            String operation = (String) body.getOrDefault("operation", "SUM");
            String payload = String.valueOf(body.get("payload"));
            String taskId = UUID.randomUUID().toString();

            ProcessTask task = new ProcessTask(taskId, operation, payload);

            // "ask pattern": envia el mensaje y devuelve un Future con la respuesta
            Future<Object> future = Patterns.ask(SUPERVISOR, task, ASK_TIMEOUT_SECONDS * 1000);
            TaskResult result = (TaskResult) Await.result(future,
                    Duration.create(ASK_TIMEOUT_SECONDS, TimeUnit.SECONDS));

            Map<String, Object> responseBody = new HashMap<>();
            responseBody.put("taskId", result.taskId);
            responseBody.put("result", result.result);
            responseBody.put("processedBy", result.workerName);

            return new APIGatewayProxyResponseEvent()
                    .withStatusCode(200)
                    .withHeaders(headers)
                    .withBody(MAPPER.writeValueAsString(responseBody));

        } catch (java.util.concurrent.TimeoutException te) {
            return errorResponse(headers, 504, "El actor no respondio a tiempo (timeout de tolerancia a fallos).");
        } catch (Exception e) {
            context.getLogger().log("Error procesando la peticion: " + e.getMessage());
            return errorResponse(headers, 500, "Error interno: " + e.getMessage());
        }
    }

    private APIGatewayProxyResponseEvent errorResponse(Map<String, String> headers, int status, String message) {
        try {
            Map<String, String> err = new HashMap<>();
            err.put("error", message);
            return new APIGatewayProxyResponseEvent()
                    .withStatusCode(status)
                    .withHeaders(headers)
                    .withBody(MAPPER.writeValueAsString(err));
        } catch (Exception ex) {
            return new APIGatewayProxyResponseEvent().withStatusCode(500).withBody("{\"error\":\"fallo critico\"}");
        }
    }
}
