#!/usr/bin/env python
"""
Script para crear usuarios de prueba para validar el sistema de permisos.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django_tenants.utils import tenant_context
from tenants.models import Clinica

def crear_usuarios_prueba():
    """Crea usuarios de prueba para cada rol en el tenant demo."""
    
    # Obtener el tenant demo
    try:
        clinica_demo = Clinica.objects.get(schema_name='demo')
        print(f"✅ Tenant demo encontrado: {clinica_demo.nombre}")
    except Clinica.DoesNotExist:
        print("❌ Error: No se encontró el tenant 'demo'")
        return False
    
    with tenant_context(clinica_demo):
        print("🔄 Creando usuarios de prueba...")
        
        # Obtener grupos
        try:
            admin_group = Group.objects.get(name='Administrador')
            dentista_group = Group.objects.get(name='Dentista')
            recepcionista_group = Group.objects.get(name='Recepcionista')
            print("👥 Grupos encontrados correctamente")
        except Group.DoesNotExist as e:
            print(f"❌ Error: No se encontró el grupo {e}")
            return False
        
        # Usuarios a crear
        usuarios = [
            {
                'username': 'admin_test',
                'email': 'admin@test.com',
                'first_name': 'Administrador',
                'last_name': 'Prueba',
                'password': 'test123456',
                'grupo': admin_group,
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'dentista_test',
                'email': 'dentista@test.com',
                'first_name': 'Doctor',
                'last_name': 'Dentista',
                'password': 'test123456',
                'grupo': dentista_group,
                'is_staff': False,
                'is_superuser': False
            },
            {
                'username': 'recepcionista_test',
                'email': 'recepcionista@test.com',
                'first_name': 'Recepcionista',
                'last_name': 'Prueba',
                'password': 'test123456',
                'grupo': recepcionista_group,
                'is_staff': False,
                'is_superuser': False
            }
        ]
        
        created_count = 0
        for usuario_data in usuarios:
            username = usuario_data['username']
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                print(f"⚠️  Usuario {username} ya existe, actualizando...")
                user = User.objects.get(username=username)
            else:
                print(f"👤 Creando usuario {username}...")
                user = User.objects.create_user(
                    username=username,
                    email=usuario_data['email'],
                    password=usuario_data['password'],
                    first_name=usuario_data['first_name'],
                    last_name=usuario_data['last_name']
                )
                created_count += 1
            
            # Actualizar propiedades
            user.is_staff = usuario_data['is_staff']
            user.is_superuser = usuario_data['is_superuser']
            user.save()
            
            # Asignar al grupo
            user.groups.clear()
            user.groups.add(usuario_data['grupo'])
            
            print(f"   ✅ {username} configurado en grupo '{usuario_data['grupo'].name}'")
        
        # Resumen
        total_users = User.objects.count()
        print(f"\n📊 RESUMEN:")
        print(f"   • Usuarios creados: {created_count}")
        print(f"   • Total usuarios en demo: {total_users}")
        print(f"   • Usuarios de prueba disponibles:")
        print(f"     - admin_test (Administrador) - Contraseña: test123456")
        print(f"     - dentista_test (Dentista) - Contraseña: test123456")
        print(f"     - recepcionista_test (Recepcionista) - Contraseña: test123456")
        
        return True

if __name__ == '__main__':
    print("🚀 Iniciando creación de usuarios de prueba...")
    success = crear_usuarios_prueba()
    
    if success:
        print("\n✅ ¡Usuarios de prueba creados exitosamente!")
        print("💡 Ahora puedes probar el sistema de permisos con diferentes roles.")
        print("🔗 Accede al sistema en: http://demo.localhost:8000/")
    else:
        print("\n❌ Error durante la creación de usuarios de prueba.")
        sys.exit(1)
