#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append('.')
django.setup()

from django.db import connection
from tenants.models import Clinica, Domain
from django.contrib.auth.models import User, Group

def recreate_demo_tenant():
    """Recrear el tenant demo completamente."""
    
    print("=== RECREANDO TENANT DEMO ===")
    
    # 1. Eliminar el schema manualmente
    with connection.cursor() as cursor:
        try:
            print("1. Eliminando schema demo...")
            cursor.execute("DROP SCHEMA IF EXISTS demo CASCADE")
            print("✅ Schema demo eliminado")
        except Exception as e:
            print(f"⚠️ Error eliminando schema: {e}")
    
    # 2. Eliminar registros en la tabla principal (shared)
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO public")
        
        try:
            print("2. Eliminando dominios del tenant demo...")
            cursor.execute("DELETE FROM tenants_domain WHERE tenant_id IN (SELECT id FROM tenants_clinica WHERE schema_name = 'demo')")
            print("✅ Dominios eliminados")
        except Exception as e:
            print(f"⚠️ Error eliminando dominios: {e}")
        
        try:
            print("3. Eliminando tenant demo de la tabla principal...")
            cursor.execute("DELETE FROM tenants_clinica WHERE schema_name = 'demo'")
            print("✅ Tenant eliminado de tabla principal")
        except Exception as e:
            print(f"⚠️ Error eliminando tenant: {e}")
    
    # 3. Crear el tenant nuevamente
    print("4. Creando nuevo tenant demo...")
    tenant = Clinica(
        schema_name='demo',
        nombre='Clínica Demo'
    )
    tenant.save()
    print("✅ Tenant demo creado")
    
    # 4. Crear el dominio
    print("5. Creando dominio para el tenant...")
    domain = Domain(
        domain='demo.localhost',
        tenant=tenant,
        is_primary=True
    )
    domain.save()
    print("✅ Dominio creado")
    
    print("\n=== TENANT DEMO RECREADO EXITOSAMENTE ===")
    print("Ahora puedes:")
    print("1. Ejecutar migraciones: python manage.py migrate_schemas --tenant -s demo")
    print("2. Crear usuario de prueba")
    print("3. Poblar datos iniciales")

if __name__ == '__main__':
    recreate_demo_tenant()
