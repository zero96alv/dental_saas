import os
import django
from django.conf import settings

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django_tenants.utils import schema_context
from tenants.models import Domain, Clinica

print('--- Checking Domain in Public Schema ---')

# Forzar la consulta en el esquema público
with schema_context('public'):
    try:
        # Primero, verificar si el tenant 'demo' existe
        tenant = Clinica.objects.get(schema_name='demo')
        print(f"Tenant 'demo' found: {tenant.nombre}")

        # Luego, verificar si el dominio existe y está asociado al tenant correcto
        domain = Domain.objects.get(domain='demo.localhost')
        print(f"Domain 'demo.localhost' found.")
        
        if domain.tenant == tenant:
            print("Domain is correctly associated with the 'demo' tenant.")
        else:
            print(f"!!! MISMATCH: Domain is associated with tenant '{domain.tenant.schema_name}' instead of 'demo'.")

    except Clinica.DoesNotExist:
        print("!!! CRITICAL: Tenant with schema_name='demo' does NOT exist.")
    except Domain.DoesNotExist:
        print("!!! CRITICAL: Domain 'demo.localhost' does NOT exist in the public schema.")
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
