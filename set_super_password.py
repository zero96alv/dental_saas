import os
import sys
import django

# Añadir el directorio del proyecto al PYTHONPATH
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

print("--- Setting password for global superuser ---")

with schema_context('public'):
    User = get_user_model()
    try:
        u = User.objects.get(username='superadmin')
        u.set_password('admin')
        u.save()
        print("Password for 'superadmin' has been set to 'admin'")
    except User.DoesNotExist:
        print("User 'superadmin' not found.")

print("--- Script finished ---")
