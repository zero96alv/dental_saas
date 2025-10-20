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

# Crear datos iniciales
echo "🏥 Configurando datos iniciales..."
python manage.py shell --settings=dental_saas.settings_production -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings_production')

try:
    from tenants.models import Clinica, Domain
    from django.contrib.auth.models import User, Group
    
    # Crear tenant público si no existe
    if not Clinica.objects.filter(schema_name='public').exists():
        public_tenant = Clinica(
            schema_name='public',
            nombre='Dental SaaS - Sistema Principal'
        )
        public_tenant.save()
        
        public_domain = Domain(
            domain='dental-saas.onrender.com',
            tenant=public_tenant,
            is_primary=True
        )
        public_domain.save()
        print('✅ Tenant público creado')
    
    # Crear superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@dental-saas.com',
            password='DentalSaaS2025!'
        )
        print('✅ Superusuario admin creado')
    
    print('✅ Configuración inicial completada')
    
except Exception as e:
    print(f'⚠️ Error en configuración inicial: {e}')
"

echo "✅ Build completado exitosamente!"