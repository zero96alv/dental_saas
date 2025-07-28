import os
import sys
import django

# Añadir el directorio del proyecto al PYTHONPATH
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context
from tenants.models import Clinica

try:
    tenant = Clinica.objects.get(schema_name='demo')
    with tenant_context(tenant):
        User = get_user_model()
        try:
            u = User.objects.get(username='admin_demo')
            u.set_password('admin')
            u.save()
            print("Password for 'admin_demo' has been set to 'admin'")
        except User.DoesNotExist:
            print("User 'admin_demo' not found in tenant 'demo'")
except Clinica.DoesNotExist:
    print("Tenant 'demo' not found.")
