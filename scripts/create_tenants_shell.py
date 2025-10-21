#!/usr/bin/env python
"""
Script para crear tenants usando shell de Django
Django-tenants DEBE crear los esquemas automáticamente al save()
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from tenants.models import Clinica, Domain
from django.db import connection

print("🚀 Creando Tenants\n")
print("="*60)

# Configuración de tenants
tenants_config = [
    {'schema_name': 'demo', 'nombre': 'Clínica Demo'},
    {'schema_name': 'sgdental', 'nombre': 'SG Dental'},
    {'schema_name': 'cgdental', 'nombre': 'CG Dental Care'}
]

# Asegurar que estamos en esquema público
connection.set_schema_to_public()

print("\n📊 Verificando tenant público...")
try:
    public_tenant = Clinica.objects.get(schema_name='public')
    print(f"✅ Tenant público: {public_tenant.nombre}\n")
except Clinica.DoesNotExist:
    print("❌ ERROR: No existe tenant público")
    print("   Ejecuta: python manage.py migrate_schemas --shared\n")
    sys.exit(1)

print("🏥 Creando tenants...")
print("-"*60)

for config in tenants_config:
    schema_name = config['schema_name']
    nombre = config['nombre']
    
    try:
        # Verificar si ya existe
        existing = Clinica.objects.filter(schema_name=schema_name).first()
        
        if existing:
            print(f"ℹ️  {nombre} ({schema_name}): Ya existe")
        else:
            # Crear el tenant - django-tenants crea el esquema automáticamente
            print(f"🔨 Creando {nombre} ({schema_name})...")
            
            tenant = Clinica(
                schema_name=schema_name,
                nombre=nombre
            )
            
            # Al hacer save(), django-tenants ejecuta CREATE SCHEMA automáticamente
            tenant.save()
            
            print(f"✅ {nombre}: Tenant y esquema creados\n")
            
    except Exception as e:
        print(f"❌ Error con {nombre}: {e}")
        import traceback
        traceback.print_exc()
        print()

print("="*60)
print("\n📋 Tenants actuales:")

for tenant in Clinica.objects.all():
    print(f"  - {tenant.nombre} (schema: {tenant.schema_name})")

print("\n" + "="*60)
print("\n✅ Proceso completado")
print("\n⚠️  IMPORTANTE: Ahora ejecuta las migraciones:")
print("   python manage.py migrate_schemas --shared")
print("   python manage.py migrate_schemas\n")
