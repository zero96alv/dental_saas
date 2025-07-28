
import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from tenants.models import Domain

print("--- Checking Domains in Database ---")

all_domains = Domain.objects.all()

if not all_domains:
    print("No domains found in the database.")
else:
    for d in all_domains:
        print(f"Domain: '{d.domain}' -> Tenant: '{d.tenant.schema_name}' (Is Primary: {d.is_primary})")

print("------------------------------------")
