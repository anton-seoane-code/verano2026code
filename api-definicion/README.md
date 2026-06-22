# ¿Qué es una API?

**API** son las siglas de **Application Programming Interface** (Interfaz de Programación de Aplicaciones).

## Definición

Una API es un conjunto de reglas, protocolos y herramientas que permite que dos aplicaciones de software se comuniquen entre sí. Actúa como un **contrato** entre el que ofrece un servicio y el que lo consume, definiendo cómo se deben formular las solicitudes (requests) y qué respuestas (responses) se pueden esperar.

## Analogía: El restaurante

Imagina que vas a un restaurante:

| Elemento | En el restaurante | En una API |
|----------|-------------------|------------|
| Cliente | Tú (comensal) | La aplicación que consume la API |
| Menú | Lista de platillos | Documentación de endpoints disponibles |
| Mesero | Intermediario que toma tu pedido | El servidor API |
| Cocina | Preparación de la comida | Lógica interna del backend |
| Plato servido | La comida que recibes | La respuesta de la API (JSON, XML, etc.) |

El mesero (**API**) te permite pedir comida (**solicitud**) sin tener que entrar a la cocina (**sistema interno**) y te trae el plato terminado (**respuesta**).

## Componentes clave

- **Endpoint**: URL específica donde se accede al recurso (ej. `https://api.ejemplo.com/usuarios`)
- **Método HTTP**: Acción a realizar (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- **Headers**: Metadatos de la solicitud (autenticación, formato, etc.)
- **Body**: Datos enviados en solicitudes `POST`/`PUT`/`PATCH`
- **Response**: Lo que devuelve el servidor (típicamente en JSON)

## Tipos comunes de API

| Tipo | Descripción |
|------|-------------|
| **REST** | Arquitectura basada en recursos, usa HTTP estándar. La más común. |
| **GraphQL** | Permite al cliente pedir exactamente los datos que necesita. |
| **SOAP** | Protocolo más antiguo y estricto, usa XML. |
| **WebSocket** | Comunicación bidireccional en tiempo real. |
| **gRPC** | Alto rendimiento, usa Protocol Buffers y HTTP/2. |

## Ejemplo conceptual

```
Solicitud:  GET /api/usuarios/42
Cabeceras:  Authorization: Bearer token123
            Accept: application/json

Respuesta:  HTTP 200 OK
            {
              "id": 42,
              "nombre": "Ana López",
              "email": "ana@ejemplo.com"
            }
```

## ¿Por qué son importantes?

- **Abstracción**: Ocultan la complejidad interna del sistema.
- **Reutilización**: Un mismo servicio puede ser consumido por múltiples clientes (web, móvil, IoT).
- **Seguridad**: Exponen solo lo necesario y permiten controlar accesos.
- **Escalabilidad**: Permiten evolucionar el backend sin afectar a los consumidores.
