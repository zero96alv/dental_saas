#!/usr/bin/env bash
# build.sh
set -o errexit

echo "🚀 Iniciando build del proyecto Dental SaaS..."

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip install -r requirements.txt

# Ejecutar collectstatic
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input --settings=dental_saas.settings_production

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones de base de datos..."
python manage.py migrate --settings=dental_saas.settings_production

# Crear tabla de cache
echo "💾 Creando tabla de cache..."
python manage.py createcachetable --settings=dental_saas.settings_production

echo "✅ Build completado exitosamente!"
