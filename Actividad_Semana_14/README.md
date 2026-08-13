# Microservicio de Actores con Despliegue Serverless

Proyecto de la Actividad Semana 14 — Parallel and Distributed Computing (UNIBE).
Implementa el **Modelo de Actores** con Akka (Java) y lo expone como función
**AWS Lambda** detrás de API Gateway.

## Estructura

```
actor-serverless/
├── pom.xml
├── src/main/java/com/unibe/
│   ├── Main.java                     # prueba local (sin AWS)
│   ├── actors/
│   │   ├── Messages.java             # mensajes inmutables entre actores
│   │   ├── SupervisorActor.java      # supervisor + pool de workers
│   │   └── WorkerActor.java          # worker que procesa SUM / STRING
│   └── lambda/
│       └── ActorLambdaHandler.java   # handler HTTP de AWS Lambda
└── src/main/resources/application.conf
```

## Correr en local (recomendado antes de desplegar)

```bash
mvn clean compile
mvn exec:java -Dexec.mainClass="com.unibe.Main"
```

Esto despacha 5 tareas, una de ellas con fallo intencional (`operation: "FAIL"`),
y deja ver en consola cómo el `SupervisorActor` reinicia solo al worker afectado
mientras los demás siguen respondiendo.

## Empaquetar para Lambda

```bash
mvn clean package
# genera target/actor-serverless.jar (con todas las dependencias, shaded)
```

## Desplegar en AWS Lambda

1. Consola AWS → Lambda → Create function → Java 11 → subir `actor-serverless.jar`.
2. Handler: `com.unibe.lambda.ActorLambdaHandler::handleRequest`
3. Memoria recomendada: 512 MB (el ActorSystem necesita algo más que el mínimo de 128 MB).
4. Timeout: 15 segundos (mayor al `ASK_TIMEOUT_SECONDS` del handler).
5. API Gateway → REST API → método `POST /procesar` → integración Lambda Proxy.

### Ejemplo de petición

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/procesar \
  -H "Content-Type: application/json" \
  -d '{"operation":"SUM","payload":"5,10,15"}'
```

### Ejemplo de respuesta

```json
{
  "taskId": "a1b2c3d4-...",
  "result": "30",
  "processedBy": "worker-2"
}
```

### Probar la tolerancia a fallos

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/procesar \
  -H "Content-Type: application/json" \
  -d '{"operation":"FAIL","payload":"n/a"}'
```

El worker elegido lanza una excepción intencional; el `SupervisorActor` lo reinicia
automáticamente (estrategia `OneForOneStrategy`) sin afectar a los otros 3 workers
ni a la disponibilidad del endpoint.

## Autor

Jinnie — 24-0648 — Grupo 9 — Ingeniería en TIC, UNIBE
