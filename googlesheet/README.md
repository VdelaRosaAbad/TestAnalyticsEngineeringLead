# Google Sheets - Bank Marketing KPIs

Esta carpeta contiene scripts para exportar automáticamente los KPIs de Bank Marketing desde BigQuery a Google Sheets.

## 📁 Archivos

- `export_to_sheets.py` - Script principal que ejecuta las 9 consultas SQL y las exporta a Google Sheets
- `setup_sheets_cron.sh` - Script de configuración inicial y setup automático
- `requirements_sheets.txt` - Dependencias específicas para Google Sheets
- `README.md` - Esta documentación

## 🚀 Configuración Rápida

### 1. Configuración inicial
```bash
cd googlesheet
chmod +x setup_sheets_cron.sh
./setup_sheets_cron.sh
```

### 2. Actualización manual
```bash
python export_to_sheets.py
```

### 3. Actualización automática cada hora
```bash
crontab -e
# Añadir línea:
0 * * * * cd /ruta/a/googlesheet && python export_to_sheets.py
```

## 📊 Worksheets Creados

El script crea un Google Sheet con 9 worksheets:

1. **KPIs por Segmento** - `conversion_rate`, `successful_contacts_count` por segmento
2. **Resumen General KPIs** - métricas overall y por segmento  
3. **Top 10 Clientes** - mejores conversiones
4. **Distribución Conversión** - buckets de conversión
5. **Auditorías Resumen** - resumen de calidad de datos
6. **Auditorías Recientes** - últimas 50 auditorías
7. **Tendencias Auditorías** - últimos 7 días
8. **KPIs con Alertas** - conversiones < 25%
9. **Resumen Ejecutivo** - métricas principales

## ⚙️ Configuración

### Variables de entorno:
- `GOOGLE_CLOUD_PROJECT` - Tu proyecto GCP
- `BQ_LOCATION` - Región de BigQuery (default: US)
- `SHEET_NAME` - Nombre del Google Sheet (default: "Bank Marketing KPIs")
- `GOOGLE_APPLICATION_CREDENTIALS` - Ruta a credenciales de service account (opcional)

### Autenticación:
- **Opción 1**: `gcloud auth application-default login` (recomendado para desarrollo)
- **Opción 2**: Service account con permisos de Google Sheets

## 🔧 Dependencias

Instalar con:
```bash
pip install -r requirements_sheets.txt
```

## 📈 Características

- ✅ Exportación automática de 9 consultas SQL
- ✅ Timestamp de última actualización en cada worksheet
- ✅ Manejo de errores y logging
- ✅ Creación automática de Google Sheet si no existe
- ✅ Limpieza y actualización de worksheets existentes
- ✅ Configuración para actualización automática cada hora

## 🚨 Alertas y Monitoreo

- Conversión < 10%: ALERTA
- Conversión < 25%: ADVERTENCIA  
- Auditorías FAIL: Revisar calidad de datos

## 📋 Uso

1. **Primera vez**: Ejecutar `setup_sheets_cron.sh`
2. **Actualización manual**: `python export_to_sheets.py`
3. **Automático**: Configurar crontab para ejecutar cada hora
4. **Ver resultados**: Abrir URL del Google Sheet que se muestra al ejecutar

## 🔗 Integración

Este módulo se integra con:
- BigQuery datasets: `bank_marketing_raw`, `bank_marketing_dm`
- Tablas: `customer_kpis`, `data_quality_audits`
- Variables consistentes: `conversion_rate`, `successful_contacts_count`, `customer_segment`
