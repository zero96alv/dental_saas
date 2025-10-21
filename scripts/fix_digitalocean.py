#!/usr/bin/env python
"""
Script de corrección completa para DigitalOcean
Crea tenants, esquemas, migraciones y usuarios
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def fix_digitalocean():
    """
    Corrección completa del setup en DigitalOcean
    """
    print("🚀 Iniciando corrección completa para DigitalOcean...")
    
    from tenants.models import Clinica, Domain
    from django.contrib.auth.models import User, Group
    from django.db import connection
    from django.core.management import call_command
    
    try:
        # PASO 1: Verificar y crear tenant público
        print("\n📋 PASO 1: Configurando tenant público...")
        public_tenant, created = Clinica.objects.get_or_create(
            schema_name='public',
            defaults={'nombre': 'Public Schema'}
        )
        print(f"   {'✅ Creado' if created else 'ℹ️ Ya existe'}")
        
        # PASO 2: Crear dominio para DigitalOcean
        print("\n🌐 PASO 2: Configurando dominio...")
        hostname = 'lobster-app-4op4x.ondigitalocean.app'
        domain, created = Domain.objects.get_or_create(
            domain=hostname,
            defaults={'tenant': public_tenant, 'is_primary': True}
        )
        print(f"   Dominio {hostname}: {'✅ Creado' if created else 'ℹ️ Ya existe'}")
        
        # PASO 3: Crear clínicas (sin migrar aún)
        print("\n🏥 PASO 3: Creando clínicas...")
        clinicas_config = [
            {'schema_name': 'demo', 'nombre': 'Clínica Demo'},
            {'schema_name': 'sgdental', 'nombre': 'SG Dental'},
            {'schema_name': 'cgdental', 'nombre': 'CG Dental Care'}
        ]
        
        clinicas_creadas = []
        for config in clinicas_config:
            tenant, created = Clinica.objects.get_or_create(
                schema_name=config['schema_name'],
                defaults={'nombre': config['nombre']}
            )
            clinicas_creadas.append(tenant)
            print(f"   {config['nombre']}: {'✅ Creada' if created else 'ℹ️ Ya existe'}")
        
        # PASO 4: Migrar esquema compartido (si no está hecho)
        print("\n🔄 PASO 4: Verificando migraciones compartidas...")
        try:
            call_command('migrate_schemas', schema_name='public', verbosity=0)
            print("   ✅ Esquema público migrado")
        except Exception as e:
            print(f"   ℹ️ Esquema público ya migrado o error: {e}")
        
        # PASO 5: Migrar cada tenant individualmente
        print("\n🔄 PASO 5: Migrando esquemas de tenants...")
        for clinica in clinicas_creadas:
            print(f"\n   📊 Migrando {clinica.nombre} ({clinica.schema_name})...")
            try:
                # Cambiar al esquema del tenant
                connection.set_tenant(clinica)
                
                # Ejecutar migraciones
                call_command('migrate', verbosity=0, interactive=False)
                
                print(f"      ✅ Esquema {clinica.schema_name} migrado correctamente")
                
            except Exception as e:
                print(f"      ⚠️ Error en {clinica.schema_name}: {e}")
                # Intentar con migrate_schemas
                try:
                    call_command('migrate_schemas', schema_name=clinica.schema_name, verbosity=0)
                    print(f"      ✅ Esquema {clinica.schema_name} migrado con migrate_schemas")
                except Exception as e2:
                    print(f"      ❌ Error persistente: {e2}")
        
        # PASO 6: Configurar usuarios admin para cada clínica
        print("\n👤 PASO 6: Configurando usuarios admin...")
        for clinica in clinicas_creadas:
            try:
                print(f"\n   🏥 Configurando {clinica.nombre}...")
                
                # Cambiar al esquema de esta clínica
                connection.set_tenant(clinica)
                
                # Crear grupos estándar
                admin_group, _ = Group.objects.get_or_create(name="Administrador")
                dentist_group, _ = Group.objects.get_or_create(name="Dentista")
                recep_group, _ = Group.objects.get_or_create(name="Recepcionista")
                
                # Crear usuario admin
                if not User.objects.filter(username='admin').exists():
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email=f'admin@{clinica.schema_name}.dental-saas.com',
                        password='DemoAdmin2025!'
                    )
                    admin_user.groups.add(admin_group)
                    print(f"      ✅ Usuario admin creado")
                else:
                    print(f"      ℹ️ Usuario admin ya existe")
                    
            except Exception as e:
                print(f"      ⚠️ Error configurando usuario: {e}")
        
        # RESUMEN FINAL
        print("\n" + "="*60)
        print("🎉 CONFIGURACIÓN COMPLETADA!")
        print("="*60)
        print("\n📍 URL de tu aplicación:")
        print(f"   https://{hostname}/")
        print("\n🏥 Clínicas disponibles:")
        print(f"   - Demo: https://{hostname}/?tenant=demo")
        print(f"   - SG Dental: https://{hostname}/?tenant=sgdental")
        print(f"   - CG Dental: https://{hostname}/?tenant=cgdental")
        print("\n🔑 Credenciales:")
        print("   Usuario: admin")
        print("   Contraseña: DemoAdmin2025!")
        print("\n✅ Todo listo para usar!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_digitalocean()
    sys.exit(0 if success else 1)