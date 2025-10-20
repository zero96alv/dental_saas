#!/usr/bin/env python
"""
Script para configurar datos iniciales después del primer deploy
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings_production')
django.setup()

from tenants.models import Clinica, Domain
from django.contrib.auth.models import User

def main():
    print("🏥 Configurando datos iniciales...")
    
    try:
        # Crear tenant público si no existe
        if not Clinica.objects.filter(schema_name='public').exists():
            public_tenant = Clinica(
                schema_name='public',
                nombre='Dental SaaS - Sistema Principal'
            )
            public_tenant.save()
            
            # Usar el hostname de Render que se pase por variable de entorno
            hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME', 'dental-saas.onrender.com')
            print(f'Configurando dominio: {hostname}')
            
            public_domain = Domain(
                domain=hostname,
                tenant=public_tenant,
                is_primary=True
            )
            public_domain.save()
            print(f'✅ Tenant público creado con dominio: {hostname}')
        else:
            print('ℹ️ Tenant público ya existe')
        
        # Crear superusuario si no existe
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@dental-saas.com',
                password='DentalSaaS2025!'
            )
            print('✅ Superusuario admin creado')
        else:
            print('ℹ️ Superusuario admin ya existe')
        
        print('✅ Configuración inicial completada')
        
        # Crear tenant demo también
        if not Clinica.objects.filter(schema_name='demo').exists():
            demo_tenant = Clinica(
                schema_name='demo',
                nombre='Demo - Clínica Dental de Prueba'
            )
            demo_tenant.save()
            
            demo_domain = Domain(
                domain=f'demo.{hostname}',
                tenant=demo_tenant,
                is_primary=True
            )
            demo_domain.save()
            print(f'✅ Tenant demo creado con dominio: demo.{hostname}')
        
    except Exception as e:
        print(f'❌ Error en configuración inicial: {e}')
        raise

if __name__ == '__main__':
    main()