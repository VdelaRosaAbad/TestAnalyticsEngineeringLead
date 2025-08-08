import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe
import datetime as dt

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
    """
}

def get_bigquery_client():
    """Inicializar cliente BigQuery"""
    return bigquery.Client(project=PROJECT_ID, location=LOCATION)

def get_sheets_client():
    """Inicializar cliente Google Sheets"""
    if CREDENTIALS_FILE:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
    else:
        # Usar credenciales por defecto (gcloud auth application-default login)
        credentials = None
    
    return gspread.authorize(credentials)

def execute_query(client, query_name, query_sql):
    """Ejecutar consulta y retornar DataFrame"""
    try:
        formatted_sql = query_sql.format(project_id=PROJECT_ID)
        df = client.query(formatted_sql).to_dataframe()
        print(f"✓ {query_name}: {len(df)} filas")
        return df
    except Exception as e:
        print(f"✗ Error en {query_name}: {e}")
        return pd.DataFrame()

def create_or_get_sheet(sheets_client, sheet_name):
    """Crear o obtener Google Sheet"""
    try:
        # Intentar abrir sheet existente
        sheet = sheets_client.open(sheet_name)
        print(f"✓ Sheet '{sheet_name}' encontrado")
    except gspread.SpreadsheetNotFound:
        # Crear nuevo sheet
        sheet = sheets_client.create(sheet_name)
        print(f"✓ Sheet '{sheet_name}' creado")
    
    return sheet

def update_sheet_worksheet(sheet, worksheet_name, df):
    """Actualizar worksheet con DataFrame"""
    try:
        # Crear o limpiar worksheet
        try:
            worksheet = sheet.worksheet(worksheet_name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
        
        # Añadir timestamp de actualización
        timestamp_df = pd.DataFrame({
            'Última Actualización': [dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Registros': [len(df)]
        })
        
        # Combinar timestamp con datos
        if not df.empty:
            combined_df = pd.concat([timestamp_df, df], axis=1)
        else:
            combined_df = timestamp_df
        
        # Escribir a Google Sheets
        set_with_dataframe(worksheet, combined_df)
        print(f"✓ Worksheet '{worksheet_name}' actualizado")
        
    except Exception as e:
        print(f"✗ Error actualizando '{worksheet_name}': {e}")

def main():
    """Función principal"""
    if not PROJECT_ID:
        raise EnvironmentError("GOOGLE_CLOUD_PROJECT debe estar configurado")
    
    print(f"🔄 Actualizando Google Sheets: {SHEET_NAME}")
    print(f"📊 Proyecto: {PROJECT_ID}")
    print(f"⏰ Timestamp: {dt.datetime.now()}")
    
    # Inicializar clientes
    bq_client = get_bigquery_client()
    sheets_client = get_sheets_client()
    
    # Crear/obtener sheet
    sheet = create_or_get_sheet(sheets_client, SHEET_NAME)
    
    # Ejecutar consultas y actualizar worksheets
    for query_name, query_sql in QUERIES.items():
        print(f"\n📋 Procesando: {query_name}")
        df = execute_query(bq_client, query_name, query_sql)
        update_sheet_worksheet(sheet, query_name, df)
    
    print(f"\n✅ Actualización completada: {sheet.url}")
    return sheet.url

if __name__ == "__main__":
    main()
