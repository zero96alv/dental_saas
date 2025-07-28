import os
import sys
import django

# Añadir el directorio del proyecto al PYTHONPATH
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from tenants.models import Clinica, Domain
from django_tenants.utils import schema_context

print("--- Running Tenant Creation Script ---")

with schema_context('public'):
    # Crear la clínica 'demo'
    clinica, created = Clinica.objects.get_or_create(
        schema_name='demo',
        defaults={'nombre': 'Clinica Demo'}
    )
    
    if created:
        print(f"Tenant '{clinica.schema_name}' created.")
    else:
        print(f"Tenant '{clinica.schema_name}' already exists.")

    # Crear el dominio 'demo.localhost' y asociarlo
    domain, created = Domain.objects.get_or_create(
        domain='demo.localhost',
        tenant=clinica,
        defaults={'is_primary': True}
    )

    if created:
        print(f"Domain '{domain.domain}' created and linked to '{clinica.schema_name}'.")
    else:
        print(f"Domain '{domain.domain}' already exists.")

print("--- Script finished ---")
