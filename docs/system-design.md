# System Design – Food Delivery Backend (Scalable & Reliable)

## Objetivos
- Escalabilidad, fiabilidad, mantenibilidad.

## Arquitectura (visión general)
- API Gateway -> Services (Order, Catalog, Courier, Payment, Notification)
- Event Bus (Kafka/SQS) para eventos de dominio.
- Cache (Redis) para catálogos/quotes.
- DB: OLTP (PostgreSQL), analítico (S3/Lakehouse + jobs ETL).
- Observabilidad (OpenTelemetry + Prometheus/Grafana).

## Decisiones clave
- BFF para apps móviles/web.
- Idempotencia en pagos y órdenes.
- Outbox Pattern para consistencia eventual.
- Rate limiting y retries exponenciales.

## Diagramas
- (coloca aquí C4/diagrama de secuencia en /docs/diagrams)
