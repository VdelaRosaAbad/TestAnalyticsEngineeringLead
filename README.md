---
## Proyecto de Data Mart en BigQuery con Python, dbt, GitHub Actions, LookML y Alertas

Este repositorio contiene una solución completa para el ejercicio práctico: ingesta del dataset Bank Marketing (UCI), modelado con dbt, visualización con LookML, CI/CD con GitHub Actions, ejecución diaria a las 6:00 AM CDT, auditorías de calidad de datos y alertas por correo ante fallas.

### Componentes

- Ingesta con Python a BigQuery (`scripts/ingest_bank_marketing.py`).
- Modelos dbt en `dbt/` que calculan: `conversion_rate`, `successful_contacts_count` y `customer_segment` (segmentación).
- Auditoría de calidad de datos: pruebas nativas de dbt y registro de resultados en `bank_marketing_dm.data_quality_audits` vía `scripts/data_quality_audit.py`.
- Visualización Looker (LookML) en `looker/` para KPIs y errores.
- CI/CD con GitHub Actions (`.github/workflows/`): validación en PR y job diario 6:00 AM CDT (11:00 UTC) que envía correo con resultados y fallas.
- Infraestructura opcional con Terraform (`infra/`) para datasets y canal de notificación.

### Requisitos previos

- Proyecto de Google Cloud con BigQuery habilitado.
- Acceso a Cloud Shell (o local con `gcloud auth application-default login`).
- Permisos BigQuery Admin en el proyecto para la configuración inicial.
- GitHub repo con permisos para GitHub Actions y Secrets/Variables.

### Configuración rápida (Cloud Shell)

1. Clonar el repo y preparar entorno:
   ```bash
   git clone <URL_DE_TU_FORK>
   cd TestAnalyticsEngineeringLead
   ./scripts/bootstrap_cloudshell.sh
   ```
2. Exportar variables de entorno (ajusta tu `PROJECT_ID` y localización):
   ```bash
   export GOOGLE_CLOUD_PROJECT=<tu_project_id>
   export BQ_LOCATION=US
   ```
3. Crear datasets (si no usas Terraform):
   ```bash
   bq --location=$BQ_LOCATION mk -d bank_marketing_raw || true
   bq --location=$BQ_LOCATION mk -d bank_marketing_dm || true
   ```
4. Ingestar datos UCI a BigQuery:
   ```bash
   pip install -r requirements.txt
   python scripts/ingest_bank_marketing.py
   ```
5. Ejecutar modelos y pruebas dbt (asegura nombres de variables consistentes: `conversion_rate`, `successful_contacts_count`, `customer_segment`):
   ```bash
   pip install dbt-bigquery
   dbt deps --project-dir dbt
   dbt run  --project-dir dbt --profiles-dir dbt/profiles
   dbt test --project-dir dbt --profiles-dir dbt/profiles
   python scripts/data_quality_audit.py
   ```

### Programación diaria y alertas por correo

- El workflow `.github/workflows/daily_run.yml` corre a las 06:00 AM CDT (11:00 UTC), ejecuta ingesta, `dbt run`, `dbt test`, registra auditorías y envía correo a `victordelarosa91@hotmail.com` ante fallas. Requiere configurar secretos SMTP o Gmail App Password (ver comentarios en el workflow).

#### Configuración de GitHub Actions

- Variables (Repository Settings → Variables):
  - `GCP_PROJECT_ID`: ID del proyecto de GCP
  - `BQ_LOCATION`: Región de BigQuery (p.ej. `US`)
- Secrets (Repository Settings → Secrets):
  - `GCP_CREDENTIALS_JSON`: contenido del JSON de la service account con permisos de BigQuery
  - `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: credenciales SMTP para envío de correos

### Documentación

- Guía técnica: `docs/technical_overview.md`
- Guía de negocio: `docs/business_explainer.md`
- Runbook de ingeniería de datos: `docs/data_engineer_runbook.md`
- Guía LookML: `docs/lookml_guide.md`

Todos los nombres de variables de negocio clave son consistentes en todo el proyecto: `conversion_rate`, `successful_contacts_count`, `customer_segment`.

