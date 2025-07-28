import os
import sys
import django

# Configurar entorno
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django_tenants.utils import tenant_context, schema_context
from tenants.models import Clinica, Domain
from core.models import PerfilDentista

print("--- Running Initial Setup Script ---")

# --- 1. Configuración del Esquema Público ---
with schema_context('public'):
    # Crear superusuario global
    if not User.objects.filter(username='superadmin').exists():
        User.objects.create_superuser('superadmin', 'superadmin@example.com', 'admin')
        print("Global superuser 'superadmin' created with password 'admin'.")
    else:
        print("Global superuser 'superadmin' already exists.")

# --- 2. Configuración del Tenant 'demo' ---
clinica, created = Clinica.objects.get_or_create(
    schema_name='demo',
    defaults={'nombre': 'Clinica Demo'}
)
if created:
    print(f"Tenant '{clinica.schema_name}' created.")
else:
    print(f"Tenant '{clinica.schema_name}' already exists.")

# Asociar dominio al tenant 'demo'
Domain.objects.get_or_create(
    domain='demo.localhost',
    tenant=clinica,
    is_primary=True
)
print(f"Domain '{Domain.objects.get(domain='demo.localhost').domain}' linked to '{clinica.schema_name}'.")

# --- 3. Configuración DENTRO del Tenant 'demo' ---
with tenant_context(clinica):
    # Crear grupos de permisos
    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    dentista_group, _ = Group.objects.get_or_create(name='Dentista')
    recepcionista_group, _ = Group.objects.get_or_create(name='Recepcionista')
    print("Permission groups created/verified in 'demo' tenant.")

    # Crear superusuario del tenant
    if not User.objects.filter(username='admin_demo').exists():
        demo_user = User.objects.create_superuser('admin_demo', 'admin@demo.com', 'admin')
        print("Tenant superuser 'admin_demo' created with password 'admin'.")
    else:
        demo_user = User.objects.get(username='admin_demo')
        print("Tenant superuser 'admin_demo' already exists.")

    # Asignar al grupo Administrador
    demo_user.groups.add(admin_group)
    print(f"User '{demo_user.username}' added to '{admin_group.name}' group.")

    # Crear PerfilDentista asociado (CRUCIAL)
    PerfilDentista.objects.get_or_create(
        usuario=demo_user,
        defaults={
            'nombre': 'Admin',
            'apellido': 'Demo',
            'email': 'admin@demo.com'
        }
    )
    print(f"PerfilDentista for '{demo_user.username}' created/verified.")

print("--- Script finished successfully ---")
