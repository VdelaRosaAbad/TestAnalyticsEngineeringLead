import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe
import datetime as dt
import google.auth
import google.auth.exceptions

# Configuración
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("BQ_LOCATION", "US")
SHEET_NAME = os.getenv("SHEET_NAME", "Bank Marketing KPIs")
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Consultas SQL
QUERIES = {
    "KPIs por Segmento": """
    SELECT
      customer_segment,
      AVG(conversion_rate) AS avg_conversion_rate,
      SUM(successful_contacts_count) AS total_successful_contacts,
      SUM(total_contacts) AS total_contacts,
      SAFE_DIVIDE(SUM(successful_contacts_count), SUM(total_contacts)) AS overall_conversion_rate
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    GROUP BY customer_segment
    ORDER BY avg_conversion_rate DESC
    """,
    
    "Resumen General KPIs": """
    SELECT
      'Overall' AS metric_type,
      AVG(conversion_rate) AS conversion_rate,
      SUM(successful_contacts_count) AS successful_contacts_count,
      SUM(total_contacts) AS total_contacts,
      COUNT(DISTINCT customer_id) AS unique_customers
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    UNION ALL
    SELECT
      customer_segment AS metric_type,
      AVG(conversion_rate) AS conversion_rate,
      SUM(successful_contacts_count) AS successful_contacts_count,
      SUM(total_contacts) AS total_contacts,
      COUNT(DISTINCT customer_id) AS unique_customers
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    GROUP BY customer_segment
    """,
    
    "Top 10 Clientes": """
    SELECT
      customer_id,
      customer_segment,
      conversion_rate,
      successful_contacts_count,
      total_contacts
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    WHERE conversion_rate > 0
    ORDER BY conversion_rate DESC
    LIMIT 10
    """,
    
    "Distribución Conversión": """
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
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    GROUP BY customer_segment, conversion_bucket
    ORDER BY customer_segment, conversion_bucket
    """,
    
    "Auditorías Resumen": """
    SELECT
      status,
      check_name,
      COUNT(*) AS check_count,
      MAX(audit_timestamp) AS last_check
    FROM `{project_id}.bank_marketing_dm.data_quality_audits`
    GROUP BY status, check_name
    ORDER BY status DESC, check_count DESC
    """,
    
    "Auditorías Recientes": """
    SELECT
      audit_timestamp,
      check_name,
      status,
      details
    FROM `{project_id}.bank_marketing_dm.data_quality_audits`
    ORDER BY audit_timestamp DESC
    LIMIT 50
    """,
    
    "Tendencias Auditorías": """
    SELECT
      DATE(audit_timestamp) AS audit_date,
      status,
      COUNT(*) AS daily_checks
    FROM `{project_id}.bank_marketing_dm.data_quality_audits`
    WHERE audit_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    GROUP BY audit_date, status
    ORDER BY audit_date DESC, status
    """,
    
    "KPIs con Alertas": """
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
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    WHERE conversion_rate < 0.25
    ORDER BY conversion_rate ASC
    """,
    
    "Resumen Ejecutivo": """
    SELECT
      'KPIs Principales' AS section,
      'Tasa de Conversión Promedio' AS metric_name,
      CAST(AVG(conversion_rate) AS STRING) AS metric_value
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    UNION ALL
    SELECT
      'KPIs Principales' AS section,
      'Total Contactos Exitosos' AS metric_name,
      CAST(SUM(successful_contacts_count) AS STRING) AS metric_value
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    UNION ALL
    SELECT
      'KPIs Principales' AS section,
      'Total Clientes' AS metric_name,
      CAST(COUNT(DISTINCT customer_id) AS STRING) AS metric_value
    FROM `{project_id}.bank_marketing_dm.customer_kpis`
    UNION ALL
    SELECT
      'Calidad de Datos' AS section,
      'Auditorías Fallidas' AS metric_name,
      CAST(COUNT(*) AS STRING) AS metric_value
    FROM `{project_id}.bank_marketing_dm.data_quality_audits`
    WHERE status = 'FAIL'
    """""
}

def run_queries_and_export():
    """
    Ejecuta las consultas en BigQuery y exporta los resultados a Google Sheets.
    """
    try:
        # Autenticación
        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform", "https://www.googleapis.com/auth/drive"]
        )
        client = bigquery.Client(credentials=credentials, project=project_id, location=LOCATION)
        
        if CREDENTIALS_FILE:
            gc = gspread.service_account(filename=CREDENTIALS_FILE)
        else:
            gc = gspread.authorize(credentials)
            
        spreadsheet = gc.open(SHEET_NAME)

        print("Autenticación exitosa.")

        for sheet_title, query_template in QUERIES.items():
            print(f"Ejecutando consulta para: {sheet_title}...")
            
            query = query_template.format(project_id=PROJECT_ID)
            
            try:
                df = client.query(query).to_dataframe()
                
                try:
                    worksheet = spreadsheet.worksheet(sheet_title)
                except gspread.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(title=sheet_title, rows=100, cols=20)
                
                # Limpiar la hoja antes de escribir nuevos datos
                worksheet.clear()
                
                set_with_dataframe(worksheet, df)
                print(f"Datos exportados a la hoja: '{sheet_title}'")

            except Exception as e:
                print(f"Error al procesar la hoja '{sheet_title}': {e}")

    except google.auth.exceptions.DefaultCredentialsError:
        print("Error de autenticación. Asegúrate de que las credenciales de Google Cloud están configuradas.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    run_queries_and_export()