### Guía LookML

Conectar el proyecto Looker a BigQuery y establecer la conexión `bigquery`.

Explores disponibles:
- `customer_kpis`: métricas `conversion_rate`, `successful_contacts_count`, cortes por `customer_segment`.
- `data_quality_audits`: visibilidad de auditorías y estatus.

Buenas prácticas:
- Usar filtros por `customer_segment` y rango de fechas (si se incluye timestamp de carga futuro).
- Crear dashboards con tiles: Conversión por segmento, Tendencia de conversión, Auditorías recientes.

