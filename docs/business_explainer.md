### Explicación de negocio

Objetivo: Analizar la efectividad de campañas de marketing directo.

KPIs clave:
- Tasa de conversión (`conversion_rate`): porcentaje de contactos que terminaron en conversión.
- Contactos exitosos (`successful_contacts_count`): número de conversiones por cliente.
- Segmentación de clientes (`customer_segment`): jóvenes (<30), adultos (30-50), seniors (>50) para comparar desempeño.

Uso en decisiones:
- Priorizar segmentos con mejor conversión.
- Identificar optimizaciones en frecuencia de campañas y canales.
- Monitorear calidad de datos y consistencia de métricas.

Flujo operacional:
- Datos se ingestan diariamente a BigQuery.
- dbt recalcula KPIs; pruebas aseguran integridad.
- Looker habilita dashboards y análisis ad hoc, incluyendo vista de errores/auditorías.

