import os
import sys
import django

# Añadir el directorio del proyecto al PYTHONPATH
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth.models import Group
from django_tenants.utils import tenant_context
from tenants.models import Clinica

print("--- Grupos en el tenant DEMO ---")
try:
    tenant = Clinica.objects.get(schema_name='demo')
    with tenant_context(tenant):
        grupos = Group.objects.all()
        if grupos:
            for g in grupos:
                print(f"- {g.name}")
        else:
            print("No se encontraron grupos. Es necesario crearlos.")
except Clinica.DoesNotExist:
    print("Tenant 'demo' not found.")
