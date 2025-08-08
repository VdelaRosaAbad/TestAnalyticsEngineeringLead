#!/bin/bash

# Script para configurar actualización automática de Google Sheets cada hora
# Ejecutar en Cloud Shell

set -e

echo "🔧 Configurando actualización automática de Google Sheets..."

# Variables de entorno
export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
export BQ_LOCATION=${BQ_LOCATION:-US}
export SHEET_NAME=${SHEET_NAME:-"Bank Marketing KPIs"}

echo "📊 Proyecto: $GOOGLE_CLOUD_PROJECT"
echo "📍 Ubicación: $BQ_LOCATION"
echo "📋 Sheet: $SHEET_NAME"

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r ../requirements_good.txt

# Autenticar con Google
echo "🔐 Autenticando con Google..."
gcloud auth application-default login

# Crear datasets si no existen
echo "🗄️ Creando datasets..."
bq --location=$BQ_LOCATION mk -d bank_marketing_raw || true
bq --location=$BQ_LOCATION mk -d bank_marketing_dm || true

# Ejecutar pipeline inicial
echo "🚀 Ejecutando pipeline inicial..."
python ../scripts/ingest_bank_marketing.py
cd ../dbt && dbt deps --project-dir . --profiles-dir profiles
dbt run --project-dir . --profiles-dir profiles
dbt test --project-dir . --profiles-dir profiles
cd ../googlesheet
python ../scripts/data_quality_audit.py

# Exportar a Google Sheets
echo "📊 Exportando a Google Sheets..."
python export_to_sheets.py

echo "✅ Configuración completada!"
echo ""
echo "📋 Para actualización manual:"
echo "   python export_to_sheets.py"
echo ""
echo "⏰ Para actualización automática cada hora:"
echo "   crontab -e"
echo "   # Añadir línea: 0 * * * * cd $(pwd) && python export_to_sheets.py"
echo ""
echo "🔗 URL del Google Sheet se mostrará al ejecutar el script"
