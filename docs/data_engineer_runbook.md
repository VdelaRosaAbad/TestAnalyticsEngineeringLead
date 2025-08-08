### Runbook de Ingeniería de Datos

Operaciones diarias (06:00 AM CDT):
1) Ingesta UCI -> `bank_marketing_raw.bank_marketing`.
2) `dbt run` -> genera `bank_marketing_dm.customer_kpis`.
3) `dbt test` -> valida reglas.
4) `data_quality_audit.py` -> inserta auditorías.
5) En caso de falla -> correo automático.

Cómo re-ejecutar manualmente:
```bash
export GOOGLE_CLOUD_PROJECT=...
export BQ_LOCATION=US
python scripts/ingest_bank_marketing.py
dbt deps --project-dir dbt
dbt run  --project-dir dbt --profiles-dir dbt/profiles
dbt test --project-dir dbt --profiles-dir dbt/profiles
python scripts/data_quality_audit.py
```

Tablas involucradas:
- `bank_marketing_raw.bank_marketing`: fuente cruda.
- `bank_marketing_dm.customer_kpis`: KPIs por cliente.
- `bank_marketing_dm.data_quality_audits`: resultados de auditorías.

Resolución de problemas:
- Revisar logs de GitHub Actions.
- Validar credenciales `GCP_CREDENTIALS_JSON`, `GCP_PROJECT_ID`, `BQ_LOCATION`.
- Confirmar existencia de datasets y cuotas de BigQuery.

