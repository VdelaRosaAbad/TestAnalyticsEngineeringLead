### Visión técnica

Este proyecto implementa un Data Mart en BigQuery sobre el dataset Bank Marketing (UCI), con orquestación diaria vía GitHub Actions, modelado en dbt y visualización en Looker.

Componentes principales:
- Ingesta: `scripts/ingest_bank_marketing.py` descarga el ZIP del UCI Repository y carga la tabla `bank_marketing_raw.bank_marketing`.
- Modelado: dbt (`dbt/`) construye `bank_marketing_dm.customer_kpis` con campos: `conversion_rate`, `successful_contacts_count`, `customer_segment`.
- Calidad de datos: pruebas dbt y auditoría a `bank_marketing_dm.data_quality_audits` por `scripts/data_quality_audit.py`.
- CI/CD: Workflows en `.github/workflows/` para validar, testear y ejecutar diario 6:00 CDT.
- LookML: `looker/` para explorar KPIs y auditorías.

Variables/convenciones consistentes:
- `conversion_rate`, `successful_contacts_count`, `customer_segment` usados uniformemente en SQL, LookML y documentación.

Cómo ejecutar local/Cloud Shell:
1) `pip install -r requirements.txt`
2) `export GOOGLE_CLOUD_PROJECT=...; export BQ_LOCATION=US`
3) `python scripts/ingest_bank_marketing.py`
4) `dbt deps && dbt run --project-dir dbt --profiles-dir dbt/profiles`
5) `dbt test --project-dir dbt --profiles-dir dbt/profiles && python scripts/data_quality_audit.py`

Despliegue/seguridad:
- Autenticación vía `google-github-actions/auth@v2` con secreto `GCP_CREDENTIALS_JSON`.
- Permisos mínimos: BigQuery Data Editor para datasets `bank_marketing_raw` y `bank_marketing_dm`.

Monitoreo/alertas:
- Envia correo en fallas del workflow diario usando `dawidd6/action-send-mail` con secretos SMTP.
- Consultar `bank_marketing_dm.data_quality_audits` para auditorías periódicas.

