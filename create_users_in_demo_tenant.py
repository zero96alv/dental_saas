#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append('.')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Clinica
from django.contrib.auth.models import User, Group

def create_users_in_demo_tenant():
    """Crear usuarios correctamente en el tenant demo."""
    
    print("=== CREANDO USUARIOS EN TENANT DEMO ===")
    
    try:
        # Obtener el tenant demo
        demo_tenant = Clinica.objects.get(schema_name='demo')
        print(f"✅ Tenant demo encontrado: {demo_tenant.nombre}")
        
        # Conectar al tenant demo
        with tenant_context(demo_tenant):
            from django.db import connection
            print(f"📍 Conectado al schema: {connection.schema_name}")
            
            # 1. Crear grupos necesarios
            print("\n1. Creando grupos...")
            admin_group, created = Group.objects.get_or_create(name='Administrador')
            if created:
                print("  ✅ Grupo 'Administrador' creado")
            else:
                print("  ⚠️ Grupo 'Administrador' ya existe")
            
            dentista_group, created = Group.objects.get_or_create(name='Dentista')
            if created:
                print("  ✅ Grupo 'Dentista' creado")
            else:
                print("  ⚠️ Grupo 'Dentista' ya existe")
            
            recepcionista_group, created = Group.objects.get_or_create(name='Recepcionista')
            if created:
                print("  ✅ Grupo 'Recepcionista' creado")
            else:
                print("  ⚠️ Grupo 'Recepcionista' ya existe")
            
            # 2. Crear usuarios
            users_to_create = [
                {
                    'username': 'admin_test',
                    'password': 'test123456',
                    'first_name': 'Admin',
                    'last_name': 'Demo',
                    'email': 'admin@demo.com',
                    'groups': [admin_group]
                },
                {
                    'username': 'dentista_test',
                    'password': 'test123456',
                    'first_name': 'Doctor',
                    'last_name': 'Demo',
                    'email': 'dentista@demo.com',
                    'groups': [dentista_group]
                },
                {
                    'username': 'recepcionista_test',
                    'password': 'test123456',
                    'first_name': 'Recepcionista',
                    'last_name': 'Demo',
                    'email': 'recepcionista@demo.com',
                    'groups': [recepcionista_group]
                }
            ]
            
            print("\n2. Creando usuarios...")
            for user_data in users_to_create:
                username = user_data['username']
                
                try:
                    user = User.objects.get(username=username)
                    print(f"  ⚠️ Usuario {username} ya existe, actualizando...")
                    
                    # Actualizar datos
                    user.first_name = user_data['first_name']
                    user.last_name = user_data['last_name']
                    user.email = user_data['email']
                    user.is_active = True
                    user.set_password(user_data['password'])
                    user.save()
                    
                except User.DoesNotExist:
                    print(f"  ✅ Creando usuario {username}...")
                    
                    # Crear nuevo usuario
                    user = User.objects.create_user(
                        username=user_data['username'],
                        password=user_data['password'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        email=user_data['email']
                    )
                    user.is_active = True
                    user.save()
                
                # Asignar grupos
                user.groups.clear()
                for group in user_data['groups']:
                    user.groups.add(group)
                
                print(f"    Grupos asignados: {[g.name for g in user.groups.all()]}")
            
            # 3. Verificar creación
            print("\n3. Verificando usuarios creados...")
            users = User.objects.all()
            print(f"Total usuarios: {users.count()}")
            
            for user in users:
                print(f"  - {user.username}: {user.first_name} {user.last_name}")
                groups = list(user.groups.values_list('name', flat=True))
                print(f"    Grupos: {groups}, Activo: {user.is_active}")
            
            # 4. Probar autenticación
            print("\n4. Probando autenticación...")
            from django.contrib.auth import authenticate
            
            for user_data in users_to_create:
                username = user_data['username']
                password = user_data['password']
                
                user = authenticate(username=username, password=password)
                if user:
                    print(f"  ✅ {username} - Autenticación exitosa")
                else:
                    print(f"  ❌ {username} - Autenticación falló")
            
            print("\n=== USUARIOS CREADOS EXITOSAMENTE EN TENANT DEMO ===")
            print("Credenciales de acceso:")
            print("  🔑 admin_test / test123456 (Administrador)")
            print("  🔑 dentista_test / test123456 (Dentista)")
            print("  🔑 recepcionista_test / test123456 (Recepcionista)")
            print(f"\n📍 URL de acceso: http://demo.localhost:8000/")
                    
    except Clinica.DoesNotExist:
        print("❌ Tenant demo no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_users_in_demo_tenant()
