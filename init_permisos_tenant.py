#!/usr/bin/env python
"""
Script rápido para inicializar permisos en cualquier tenant
Uso: python init_permisos_tenant.py <schema_name>
Ejemplo: python init_permisos_tenant.py dev
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection
from django.core.management import call_command
from tenants.models import Clinica

def main():
    if len(sys.argv) < 2:
        print("❌ Error: Debes proporcionar el schema_name del tenant")
        print("Uso: python init_permisos_tenant.py <schema_name>")
        print("Ejemplo: python init_permisos_tenant.py dev")
        print("\nTenants disponibles:")
        for clinica in Clinica.objects.exclude(schema_name='public'):
            print(f"  • {clinica.schema_name} - {clinica.nombre}")
        sys.exit(1)

    schema_name = sys.argv[1]

    try:
        tenant = Clinica.objects.get(schema_name=schema_name)
        print(f"=== Inicializando permisos para: {tenant.nombre} ({schema_name}) ===\n")

        # Cambiar al tenant
        connection.set_tenant(tenant)

        # Ejecutar comando de inicialización
        call_command('init_permisos')

        print(f"\n✅ Permisos inicializados correctamente para {tenant.nombre}")
        print(f"🌐 Accede en: http://localhost:8000/{schema_name}/")

    except Clinica.DoesNotExist:
        print(f"❌ Error: No existe el tenant '{schema_name}'")
        print("\nTenants disponibles:")
        for clinica in Clinica.objects.exclude(schema_name='public'):
            print(f"  • {clinica.schema_name} - {clinica.nombre}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
