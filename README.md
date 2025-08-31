## Tech Lead Challenge

Proyecto FastAPI que aborda tres áreas: Algoritmos y Estructuras de Datos, Diseño y Arquitectura del Sistema, y un ejercicio de Codificación con API REST (cálculo de cotización de pedidos con envío y descuento). Incluye dataset sintético, endpoints documentados y pruebas automatizadas.

---

## 1. Algoritmos y Estructuras de Datos

### 1.1 Pregunta 1 – Top clientes más frecuentes por ventana de tiempo
- **Descripción**: A partir de un dataset de transacciones con `timestamp`, `customer_id`, `amount`, se identifica a los top K clientes más frecuentes dentro de un rango temporal.
- **Implementación**:
  - Lector de CSV en streaming con soporte `.gz`: `app/algorithms/top_customers.py` (función `iter_csv_transactions`).
  - **Modo exacto (memoria)**: `top_k_exact` usa `Counter` + `heapq.nlargest`.
  - **Modo streaming (grandes volúmenes)**: `Misra–Gries` en 2 pasadas (`top_k_from_file_two_pass`):
    1) Encuentra candidatos con memoria acotada.
    2) Recorre nuevamente para contar exactamente solo candidatos.
  - Servicio y heurística de selección: `app/services/analytics.py` decide `exact` vs `stream` según el `mode` solicitado o tamaño del archivo.

- **Complejidad**:
  - Modo exacto: tiempo O(N) para contar + O(M log K) para top-K (M = clientes únicos); espacio O(M).
  - Modo streaming (Misra–Gries + verificación):
    - Pasada 1: O(N · b) amortizado cercano a O(N) con `b = capacidad` pequeña; espacio O(b).
    - Pasada 2: O(N) para contar solo candidatos; espacio O(b).
  - Adecuado para datasets que pueden exceder memoria gracias a la estrategia de dos pasadas y capacidad acotada.

- **Generación creativa del dataset**:
  - Servicio: `app/services/dataset.py` y CLI: `app/scripts/generate_transactions.py`.
  - Características: pesos Zipf-like para simular heavy users, variación de montos, perfiles de cliente (nombre/ciudad/email), y salida `csv`/`csv.gz` en streaming sin cargar todo a RAM.

### 1.2 Pregunta 2 – Índice de rutas de transporte público
- **Descripción**: Se gestiona un conjunto de rutas (cada una con identificador y paradas). Se requiere recuperación eficiente de rutas por parada y mutaciones eficientes (agregar/eliminar paradas).
- **Estructura elegida**: `app/algorithms/transit_routes.py` define `TransitIndex` con dos mapas:
  - `stops_by_route[route_id] -> set(stop_id)`
  - `routes_by_stop[stop_id] -> set(route_id)`
- **Operaciones**:
  - Lectura: `get_routes_by_stop`, `get_stops_by_route` en O(1) promedio.
  - Mutación: `add_route`, `add_stop_to_route`, `remove_stop_from_route`, `remove_route` en O(1) promedio.
- **Justificación**: El doble índice hash mantiene simetría y permite consultas y mutaciones eficientes con conjuntos, evitando duplicados y con costo amortizado constante.

---

## 2. Diseño y Arquitectura del Sistema

Escenario: start-up de delivery en rápido crecimiento, se busca escalabilidad, fiabilidad y mantenibilidad. Este repo exhibe una versión monolítica bien estructurada con separación por capas (API, servicios, algoritmos, esquemas), preparada para evolucionar a servicios.

### 2.1 Visión de arquitectura distribuida propuesta
- **API Gateway**: expone REST/HTTP y autentica; enruta a microservicios.
- **Microservicios**: `orders/pricing`, `analytics`, `transit`, `catalog/inventory`, `users`, etc.
- **Mensajería**: cola/stream (p. ej., Kafka/RabbitMQ) para eventos de pedidos, pagos, actualizaciones de inventario.
- **Datos**:
  - OLTP por dominio (p. ej., Postgres para pedidos/usuarios, Redis para caché, Elastic para búsqueda, S3/lake para históricos).
  - OLAP/Streaming (p. ej., Kafka + Flink/Spark + warehouse) para analítica near-real-time.
- **Caching**: Redis para respuestas calientes (cotizaciones, catálogos, rutas).
- **Observabilidad**: logs estructurados, métricas (Prometheus), trazas (OpenTelemetry).
- **Infra**: contenedores (Docker), orquestación (Kubernetes), despliegues blue/green o canary, autoescalado.

### 2.2 Diseño de API y contratos
- Contratos versionados (`/api/v1/...`) con `pydantic` como esquema de validación y OpenAPI generado por FastAPI.
- Idempotencia en endpoints de mutación cuando aplique; códigos de estado adecuados (400/404/409, etc.).

### 2.3 Estrategia de datos y consistencia
- Consistencia fuerte dentro de cada servicio; consistencia eventual entre dominios mediante eventos.
- Esquemas evolutivos con migraciones por servicio; CDC para sincronizaciones analíticas.

### 2.4 Colas de mensajes y patrones
- Event-driven: `OrderCreated`, `PaymentAuthorized`, `OrderDispatched`.
- Patrones: outbox/inbox, saga orchestration para flujos largo alcance.

### 2.5 Espacio reservado para diagramas
- [Pendiente] Inserte aquí los diagramas de:
  - Contexto (C4-1)
  - Contenedores/servicios (C4-2)
  - Componentes clave por servicio (C4-3)
  - Flujos de eventos (pedido de punta a punta)

---

## 3. Codificación y Resolución de Problemas (API REST)

### 3.1 Endpoint de cotización de pedido
- Ruta: `POST /api/v1/orders/quote`
- Request (`OrderRequest`):
  - `stratum`: 1..6 (sistema de estratos en Colombia)
  - `items[]`: lista de objetos `{ sku, price, quantity }`
- Lógica (`app/services/pricing.py`):
  - `subtotal = sum(price * quantity)`
  - Envío base configurable (`delivery_base_fee`) ajustado por estrato con multiplicador: estratos altos pagan un poco más/menos según regla del ejemplo.
  - Descuento si `subtotal >= discount_threshold` con `discount_rate`.
  - `total = subtotal + shipping - discount` (no negativo).
- Response (`OrderResponse`): `{ subtotal, shipping, discount, total }`.

Ejemplo:

```json
POST /api/v1/orders/quote
{
  "stratum": 3,
  "items": [
    {"sku": "A", "price": 10000, "quantity": 3}
  ]
}
```

```json
200 OK
{
  "subtotal": 30000,
  "shipping": 5000,
  "discount": 0,
  "total": 35000
}
```

### 3.2 Endpoints de Analítica y Dataset
- `POST /api/v1/analytics/top-customers` (`TopCustomersRequest`):
  - Parámetros: `path`, ventana de tiempo (`days` o `start`/`end`), `top_customers`, `mode` (`auto|exact|stream`), `capacity`.
  - Devuelve `results[]` con `customer_id` y `count`, `mode` utilizado y timestamps.

- `POST /api/v1/datasets/transactions/generate` (`DatasetGenRequest`):
  - Genera CSV/CSV.GZ sintético con campos: `timestamp, customer_id, amount, customer_name, customer_city, customer_email`.
  - Devuelve ruta de salida y metadatos.

### 3.3 Endpoints de Rutas de Transporte
- `POST /api/v1/transit/routes` crea ruta.
- `GET /api/v1/transit/routes/{route_id}/stops` consulta paradas por ruta.
- `POST /api/v1/transit/routes/{route_id}/stops` agrega parada.
- `DELETE /api/v1/transit/routes/{route_id}/stops/{stop_id}` elimina parada.
- `GET /api/v1/transit/stops/{stop_id}/routes` consulta rutas por parada.
- `DELETE /api/v1/transit/routes/{route_id}` elimina ruta.
- `GET /api/v1/transit/routes` lista rutas.
- `GET /api/v1/transit/stops` lista paradas.
- `GET /api/v1/transit/routes-with-stops` todas las rutas con sus paradas.

---

## Cómo ejecutar el proyecto

### Opción A) Local (sin Docker)
1. Requisitos: Python 3.11+ y `pip`.
2. Instalar dependencias:
   - `pip install -r requirements.txt`
3. Ejecutar la API:
   - `uvicorn app.main:app --reload`
4. Abrir documentación interactiva:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - Healthcheck: `http://127.0.0.1:8000/health`

### Opción B) Docker / Docker Compose
1. Construir y levantar:
   - `docker compose up --build`
2. API disponible en `http://localhost:8000`
3. Volúmenes mapeados: `./app -> /app/app` y `./data -> /app/data`.

### Variables de entorno (pricing)
Configurar en `.env` si desea cambiar reglas:
- `DELIVERY_BASE_FEE` (por defecto 5000)
- `DISCOUNT_THRESHOLD` (por defecto 100000)
- `DISCOUNT_RATE` (por defecto 0.05)

---

## Cómo probar

### Pruebas unitarias y de API
- Ejecutar todas las pruebas:
  - `pytest -q`
- Cobertura:
  - `pytest --cov=app -q`

### Probar endpoints manualmente
- Cotización:
  - `POST http://localhost:8000/api/v1/orders/quote`
- Top customers (usando dataset por defecto en `/app/data/transactions.csv.gz`):
  - `POST http://localhost:8000/api/v1/analytics/top-customers`
- Generar dataset:
  - `POST http://localhost:8000/api/v1/datasets/transactions/generate`
- Rutas de transporte (CRUD y consultas): ver rutas en sección 3.3 o Swagger UI.

---

## Estructura del proyecto (carpetas principales)
- `app/main.py`: instancia FastAPI y health.
- `app/api/v1/routes.py`: definición de endpoints.
- `app/services/*`: lógica de dominio (pricing, analytics, dataset, transit).
- `app/algorithms/*`: algoritmos puros (top customers, índice de rutas).
- `app/schemas/*`: contratos de entrada/salida con `pydantic`.
- `app/tests/*`: pruebas unitarias y de endpoints.
- `data/`: datasets de ejemplo/salida.

---

## Buenas prácticas aplicadas
- Validación de datos con `pydantic` (request/response), tipado estático.
- Separación de capas (API/servicios/algoritmos/esquemas).
- Endpoints versionados y códigos de estado adecuados (`400/404/409`).
- Pruebas automatizadas con `pytest` y `TestClient`.
- Lectura/escritura en streaming para datasets grandes.

