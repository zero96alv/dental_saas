#!/usr/bin/env python
"""
Script simplificado para crear y configurar tenants en DigitalOcean
Usa comandos de management de django-tenants directamente
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def setup_tenants():
    """
    Configuración paso a paso de tenants
    """
    print("🚀 Setup de Tenants - Dental SaaS\n")
    
    from tenants.models import Clinica, Domain
    from django.db import connection
    from django.contrib.auth.models import User, Group
    
    # PASO 1: Crear esquemas en PostgreSQL directamente
    print("📊 PASO 1: Creando esquemas en PostgreSQL...\n")
    
    schemas = ['demo', 'sgdental', 'cgdental']
    
    with connection.cursor() as cursor:
        for schema in schemas:
            try:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                print(f"  ✅ Esquema '{schema}' creado")
            except Exception as e:
                print(f"  ⚠️ Error con esquema '{schema}': {e}")
    
    # PASO 2: Crear tenants en Django
    print("\n🏥 PASO 2: Creando tenants...\n")
    
    tenants_config = [
        {'schema_name': 'demo', 'nombre': 'Clínica Demo'},
        {'schema_name': 'sgdental', 'nombre': 'SG Dental'},
        {'schema_name': 'cgdental', 'nombre': 'CG Dental Care'}
    ]
    
    for config in tenants_config:
        tenant, created = Clinica.objects.get_or_create(
            schema_name=config['schema_name'],
            defaults={'nombre': config['nombre']}
        )
        status = "✅ Creado" if created else "ℹ️ Ya existe"
        print(f"  {status}: {config['nombre']} ({config['schema_name']})")
    
    # PASO 3: Ejecutar migraciones en cada esquema
    print("\n🔄 PASO 3: Ejecutando migraciones...\n")
    
    from django.core.management import call_command
    
    for config in tenants_config:
        schema_name = config['schema_name']
        print(f"  📊 Migrando {config['nombre']}...")
        try:
            # Ejecutar migrate_schemas para este tenant específico
            call_command(
                'migrate_schemas',
                schema_name=schema_name,
                interactive=False,
                verbosity=1
            )
            print(f"     ✅ Migrado correctamente\n")
        except Exception as e:
            print(f"     ❌ Error: {e}\n")
    
    # PASO 4: Crear usuarios admin para cada tenant
    print("👤 PASO 4: Creando usuarios admin...\n")
    
    for config in tenants_config:
        try:
            tenant = Clinica.objects.get(schema_name=config['schema_name'])
            connection.set_tenant(tenant)
            
            # Crear grupos
            admin_group, _ = Group.objects.get_or_create(name="Administrador")
            Group.objects.get_or_create(name="Dentista")
            Group.objects.get_or_create(name="Recepcionista")
            
            # Crear admin
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email=f'admin@{config["schema_name"]}.dental-saas.com',
                    password='DemoAdmin2025!'
                )
                admin_user.groups.add(admin_group)
                print(f"  ✅ Admin creado para {config['nombre']}")
            else:
                print(f"  ℹ️ Admin ya existe en {config['nombre']}")
                
        except Exception as e:
            print(f"  ❌ Error en {config['nombre']}: {e}")
    
    # RESUMEN
    print("\n" + "="*60)
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print("\n📍 Accede a tus clínicas:")
    print("  - Demo: https://lobster-app-4op4x.ondigitalocean.app/demo/")
    print("  - SG Dental: https://lobster-app-4op4x.ondigitalocean.app/sgdental/")
    print("  - CG Dental: https://lobster-app-4op4x.ondigitalocean.app/cgdental/")
    print("\n🔑 Credenciales: admin / DemoAdmin2025!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        setup_tenants()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
