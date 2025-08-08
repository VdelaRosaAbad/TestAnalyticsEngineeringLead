-- 1. KPIs por Segmento de Cliente
SELECT
  customer_segment,
  AVG(conversion_rate) AS avg_conversion_rate,
  SUM(successful_contacts_count) AS total_successful_contacts,
  SUM(total_contacts) AS total_contacts,
  SAFE_DIVIDE(SUM(successful_contacts_count), SUM(total_contacts)) AS overall_conversion_rate
FROM `bank_marketing_dm.customer_kpis`
GROUP BY customer_segment
ORDER BY avg_conversion_rate DESC;

-- 2. Resumen General de KPIs
SELECT
  'Overall' AS metric_type,
  AVG(conversion_rate) AS conversion_rate,
  SUM(successful_contacts_count) AS successful_contacts_count,
  SUM(total_contacts) AS total_contacts,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM `bank_marketing_dm.customer_kpis`
UNION ALL
SELECT
  'By Segment' AS metric_type,
  AVG(conversion_rate) AS conversion_rate,
  SUM(successful_contacts_count) AS successful_contacts_count,
  SUM(total_contacts) AS total_contacts,
  COUNT(DISTINCT customer_id) AS unique_customers
FROM `bank_marketing_dm.customer_kpis`
GROUP BY customer_segment;

-- 3. Top 10 Clientes por Conversión
SELECT
  customer_id,
  customer_segment,
  conversion_rate,
  successful_contacts_count,
  total_contacts
FROM `bank_marketing_dm.customer_kpis`
WHERE conversion_rate > 0
ORDER BY conversion_rate DESC
LIMIT 10;

-- 4. Distribución de Conversión por Segmento
SELECT
  customer_segment,
  CASE 
    WHEN conversion_rate = 0 THEN '0%'
    WHEN conversion_rate BETWEEN 0.01 AND 0.25 THEN '1-25%'
    WHEN conversion_rate BETWEEN 0.26 AND 0.50 THEN '26-50%'
    WHEN conversion_rate BETWEEN 0.51 AND 0.75 THEN '51-75%'
    WHEN conversion_rate > 0.75 THEN '76-100%'
  END AS conversion_bucket,
  COUNT(*) AS customer_count
FROM `bank_marketing_dm.customer_kpis`
GROUP BY customer_segment, conversion_bucket
ORDER BY customer_segment, conversion_bucket;

-- 5. Auditorías de Calidad de Datos - Resumen
SELECT
  status,
  check_name,
  COUNT(*) AS check_count,
  MAX(audit_timestamp) AS last_check
FROM `bank_marketing_dm.data_quality_audits`
GROUP BY status, check_name
ORDER BY status DESC, check_count DESC;

-- 6. Auditorías de Calidad de Datos - Detalle Reciente
SELECT
  audit_timestamp,
  check_name,
  status,
  details
FROM `bank_marketing_dm.data_quality_audits`
ORDER BY audit_timestamp DESC
LIMIT 50;

-- 7. Tendencias de Auditorías (últimos 7 días)
SELECT
  DATE(audit_timestamp) AS audit_date,
  status,
  COUNT(*) AS daily_checks
FROM `bank_marketing_dm.data_quality_audits`
WHERE audit_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY audit_date, status
ORDER BY audit_date DESC, status;

-- 8. KPIs con Alertas (conversión < 10%)
SELECT
  customer_id,
  customer_segment,
  conversion_rate,
  successful_contacts_count,
  total_contacts,
  CASE 
    WHEN conversion_rate < 0.10 THEN 'ALERTA: Baja conversión'
    WHEN conversion_rate < 0.25 THEN 'ADVERTENCIA: Conversión moderada'
    ELSE 'OK: Buena conversión'
  END AS alert_level
FROM `bank_marketing_dm.customer_kpis`
WHERE conversion_rate < 0.25
ORDER BY conversion_rate ASC;

-- 9. Resumen Ejecutivo (para dashboard principal)
SELECT
  'KPIs Principales' AS section,
  'Tasa de Conversión Promedio' AS metric_name,
  CAST(AVG(conversion_rate) AS STRING) AS metric_value
FROM `bank_marketing_dm.customer_kpis`
UNION ALL
SELECT
  'KPIs Principales' AS section,
  'Total Contactos Exitosos' AS metric_name,
  CAST(SUM(successful_contacts_count) AS STRING) AS metric_value
FROM `bank_marketing_dm.customer_kpis`
UNION ALL
SELECT
  'KPIs Principales' AS section,
  'Total Clientes' AS metric_name,
  CAST(COUNT(DISTINCT customer_id) AS STRING) AS metric_value
FROM `bank_marketing_dm.customer_kpis`
UNION ALL
SELECT
  'Calidad de Datos' AS section,
  'Auditorías Fallidas' AS metric_name,
  CAST(COUNT(*) AS STRING) AS metric_value
FROM `bank_marketing_dm.data_quality_audits`
WHERE status = 'FAIL';
