#!/usr/bin/env python
"""
Setup de tenants usando SOLO comandos de django-tenants
Sin crear esquemas manualmente (django-tenants los crea automáticamente)
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def setup_all():
    """
    Configuración completa usando django-tenants
    """
    print("🚀 Setup Tenants - Dental SaaS\n")
    print("="*60)
    
    from tenants.models import Clinica, Domain
    from django.db import connection
    from django.contrib.auth.models import User, Group
    from django.core.management import call_command
    
    # PASO 1: Asegurar que estamos en esquema público
    print("\n📋 PASO 1: Verificando esquema público...\n")
    connection.set_schema_to_public()
    
    # Verificar tenant público
    try:
        public_tenant = Clinica.objects.get(schema_name='public')
        print(f"  ✅ Tenant público existe: {public_tenant.nombre}")
    except Clinica.DoesNotExist:
        print("  ❌ Error: No existe tenant público")
        print("     Ejecuta primero: python manage.py migrate_schemas --shared")
        return False
    
    # PASO 2: Crear tenants (django-tenants crea los esquemas automáticamente)
    print("\n🏥 PASO 2: Creando tenants...\n")
    
    tenants_config = [
        {'schema_name': 'demo', 'nombre': 'Clínica Demo'},
        {'schema_name': 'sgdental', 'nombre': 'SG Dental'},
        {'schema_name': 'cgdental', 'nombre': 'CG Dental Care'}
    ]
    
    for config in tenants_config:
        try:
            # Al crear un Clinica (TenantMixin), django-tenants crea el esquema automáticamente
            tenant, created = Clinica.objects.get_or_create(
                schema_name=config['schema_name'],
                defaults={'nombre': config['nombre']}
            )
            
            if created:
                print(f"  ✅ Creado: {config['nombre']} (esquema: {config['schema_name']})")
                # django-tenants ejecuta CREATE SCHEMA automáticamente
                print(f"     Django-tenants creó el esquema '{config['schema_name']}'")
            else:
                print(f"  ℹ️  Ya existe: {config['nombre']} ({config['schema_name']})")
                
        except Exception as e:
            print(f"  ❌ Error creando {config['nombre']}: {e}")
            import traceback
            traceback.print_exc()
    
    # PASO 3: Migrar tenants usando migrate_schemas
    print("\n🔄 PASO 3: Migrando esquemas de tenants...\n")
    
    for config in tenants_config:
        schema_name = config['schema_name']
        print(f"  📊 Migrando {config['nombre']} ({schema_name})...")
        
        try:
            # Verificar que el tenant existe
            tenant = Clinica.objects.get(schema_name=schema_name)
            
            # Migrar usando migrate_schemas
            call_command(
                'migrate_schemas',
                schema_name=schema_name,
                interactive=False,
                verbosity=0
            )
            print(f"     ✅ Migrado correctamente\n")
            
        except Clinica.DoesNotExist:
            print(f"     ❌ Tenant no existe\n")
        except Exception as e:
            print(f"     ❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
    
    # PASO 4: Crear usuarios admin
    print("\n👤 PASO 4: Configurando usuarios admin...\n")
    
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
                print(f"  ✅ Admin creado: {config['nombre']}")
            else:
                print(f"  ℹ️  Admin ya existe: {config['nombre']}")
                
        except Exception as e:
            print(f"  ❌ Error en {config['nombre']}: {e}")
    
    # RESUMEN
    print("\n" + "="*60)
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print("\n📍 Accede a tus clínicas:")
    print("  - Demo:     https://lobster-app-4op4x.ondigitalocean.app/demo/")
    print("  - SG Dental: https://lobster-app-4op4x.ondigitalocean.app/sgdental/")
    print("  - CG Dental: https://lobster-app-4op4x.ondigitalocean.app/cgdental/")
    print("\n🔑 Credenciales:")
    print("  Usuario:    admin")
    print("  Contraseña: DemoAdmin2025!")
    print("\n⚠️  IMPORTANTE: Si ves errores de 'relation does not exist',")
    print("   las migraciones no se completaron. Revisa los errores arriba.")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = setup_all()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
