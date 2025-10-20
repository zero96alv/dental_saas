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
echo "🗄️ Ejecutando migraciones en esquema público..."
python manage.py migrate_schemas --schema=public --settings=dental_saas.settings_production

echo "🗄️ Ejecutando migraciones en esquemas tenant..."
python manage.py migrate_schemas --settings=dental_saas.settings_production

# Crear tabla de cache
echo "💾 Creando tabla de cache..."
python manage.py createcachetable --settings=dental_saas.settings_production

# Inicializar tenants y datos básicos
echo "🏥 Inicializando tenants..."
python init_production.py

echo "✅ Build completado exitosamente!"
