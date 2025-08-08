---

# Ejercicios para Analytics Engineering Lead

Debe realizar un fork de este repositorio para desarrollar, documentar y entregar su trabajo.

Si está interesado en aplicar al test, puede enviar un correo a jguerrero@deacero.com.

## Ejercicio de Gestión

Tu equipo de Analytics Engineering está trabajando con un pipeline de datos clave para la organización que alimenta informes diarios utilizados por varias áreas de negocio. Sin embargo, el pipeline ha comenzado a fallar esporádicamente, provocando retrasos en la entrega de datos críticos. Las interrupciones no son constantes, pero cuando ocurren, generan importantes tiempos de inactividad y requieren intervención manual, lo que afecta la confianza en los datos.

El equipo tiene el 80% de su capacidad dedicada a tareas prioritarias de la unidad de negocio fuera de tu alcance, dejando solo el 20% disponible para abordar la optimización de este pipeline.

#### Objetivos:
1. Diseña una estrategia de optimización para este pipeline legado con el tiempo y recursos disponibles. Se debe reducir la frecuencia de fallos y minimizar el impacto en el tiempo de intervención manual, generando un uso eficiente de los recursos.
2. Diseña una arquitectura tecnológica moderna para la migración futura de este pipeline.

#### Información clave:
- No se tiene restricciones tecnológicas o de licenciamientos por herramientas.
- El pipeline gestiona una gran cantidad de datos provenientes de múltiples fuentes.
- Las fallas ocurren esporádicamente debido a la latencia y a problemas con la calidad de los datos de algunas fuentes.
- Las intervenciones manuales actuales consisten en verificar logs y reiniciar el proceso cuando los datos fallan en cargarse correctamente.
- El equipo tiene acceso a herramientas de monitoreo básicas y logs, pero no hay automatización en el proceso de detección y resolución de problemas.
- Solo cuentas con un 20% del tiempo del equipo para esta optimización, por lo que debes priorizar las soluciones de mayor impacto.

## Ejercicio Práctico

Este ejercicio utiliza datos de una campaña de marketing por correo electrónico disponibles en el [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/222/bank+marketing). Los datos contienen información sobre diversas campañas de marketing directo de una institución bancaria.

**Objetivo:**

Crear y desplegar un Data Mart que permita al equipo de marketing analizar la efectividad de sus campañas, enfocándose en KPIs como la tasa de conversión, el número de contactos exitosos y la segmentación de clientes.

#### Información clave:

- El diseño de la arquitectura, capas y modelos de datos es a libre elección.
- La solución debe contemplar pruebas unitarias, mantener la calidad de los datos y desplegar modelos de datos en BigQuery
- Los datos se pueden obtener desde [Bank Marketing dataset](https://archive.ics.uci.edu/dataset/222/bank+marketing).
- El modelo final debe calcular:
  - Tasa de conversión: porcentaje de contactos exitosos sobre el total de contactos.
  - Número de contactos exitosos: total de conversiones logradas.
  - Segmentación de clientes: clasificación de clientes basada en criterios relevantes como edad, ocupación, etc.
- Las pruebas unitarias minimas a contemplar son:
  - Validar tipos de datos.
  - Comprobar valores nulos.
  - Verificar rangos y unicidad de campos clave.
- Para el despliegue puede configurarse un pipeline CI/CD en cualquier herramienta que considere:
  - Validación de código.
  - Ejecución de pruebas unitarias.
  - Despliegue en BigQuery.
  - Configura alertas para pruebas fallidas y realiza auditorías periódicas de calidad de datos.

#### Entrega del Ejercicio

- Suba su proyecto a un repositorio de GitHub y comparta el enlace en un correo dirigido a jguerrero@deacero.com.
- Asegúrese de que el repositorio incluya:
    - Todos los recursos usados o generados para la solucion de los ejercicios.
    - Documentación que explique el proceso seguido, las decisiones tomadas.
    - Instrucciones claras sobre cómo configurar y ejecutar el proyecto y sus artefactos.


Suerte a todos!!! :metal: :nerd_face: :computer:

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

