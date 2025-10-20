#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import PerfilDentista, Especialidad

def create_demo_users():
    """Crear usuarios de prueba en el tenant demo."""
    
    print("=== CREANDO USUARIOS DE PRUEBA EN TENANT DEMO ===")
    
    try:
        # 1. Crear grupos necesarios
        print("1. Creando grupos...")
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        if created:
            print("  ✅ Grupo 'Administrador' creado")
        
        dentista_group, created = Group.objects.get_or_create(name='Dentista')
        if created:
            print("  ✅ Grupo 'Dentista' creado")
        
        recepcionista_group, created = Group.objects.get_or_create(name='Recepcionista')
        if created:
            print("  ✅ Grupo 'Recepcionista' creado")
        
        # 2. Verificar si las tablas principales existen
        print("2. Verificando tablas...")
        try:
            especialidad, created = Especialidad.objects.get_or_create(
                nombre='Odontología General'
            )
            tablas_disponibles = True
            print("  ✅ Tablas disponibles")
        except:
            print("  ⚠️ Tablas principales no disponibles, creando solo usuarios básicos")
            tablas_disponibles = False
        
        # 3. Crear usuario admin_test
        print("3. Creando admin_test...")
        try:
            admin_user = User.objects.get(username='admin_test')
            print("  ⚠️ Usuario admin_test ya existe, actualizando...")
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                username='admin_test',
                email='admin@demo.com',
                password='test123456',
                first_name='Admin',
                last_name='Demo'
            )
            print("  ✅ Usuario admin_test creado")
        
        admin_user.groups.clear()
        admin_user.groups.add(admin_group)
        admin_user.is_active = True
        admin_user.save()
        
        # 4. Crear usuario dentista_test
        print("4. Creando dentista_test...")
        try:
            dentista_user = User.objects.get(username='dentista_test')
            print("  ⚠️ Usuario dentista_test ya existe, actualizando...")
        except User.DoesNotExist:
            dentista_user = User.objects.create_user(
                username='dentista_test',
                email='dentista@demo.com',
                password='test123456',
                first_name='Doctor',
                last_name='Demo'
            )
            print("  ✅ Usuario dentista_test creado")
        
        dentista_user.groups.clear()
        dentista_user.groups.add(dentista_group)
        dentista_user.is_active = True
        dentista_user.save()
        
        # 5. Crear PerfilDentista para dentista_test (solo si las tablas están disponibles)
        if tablas_disponibles:
            print("5. Creando PerfilDentista...")
            try:
                perfil = PerfilDentista.objects.get(usuario=dentista_user)
                print("  ⚠️ PerfilDentista ya existe, actualizando...")
            except PerfilDentista.DoesNotExist:
                perfil = PerfilDentista.objects.create(
                    usuario=dentista_user,
                    nombre=dentista_user.first_name,
                    apellido=dentista_user.last_name,
                    email=dentista_user.email,
                    activo=True
                )
                print("  ✅ PerfilDentista creado")
            
            perfil.especialidades.clear()
            perfil.especialidades.add(especialidad)
        else:
            print("5. Saltando PerfilDentista (tablas no disponibles)")
        
        # 6. Crear usuario recepcionista_test
        print("6. Creando recepcionista_test...")
        try:
            recepcionista_user = User.objects.get(username='recepcionista_test')
            print("  ⚠️ Usuario recepcionista_test ya existe, actualizando...")
        except User.DoesNotExist:
            recepcionista_user = User.objects.create_user(
                username='recepcionista_test',
                email='recepcionista@demo.com',
                password='test123456',
                first_name='Recepcionista',
                last_name='Demo'
            )
            print("  ✅ Usuario recepcionista_test creado")
        
        recepcionista_user.groups.clear()
        recepcionista_user.groups.add(recepcionista_group)
        recepcionista_user.is_active = True
        recepcionista_user.save()
        
        print("\n=== USUARIOS CREADOS EXITOSAMENTE ===")
        print("Credenciales de acceso:")
        print("  🔑 admin_test / test123456 (Administrador)")
        print("  🔑 dentista_test / test123456 (Dentista)")
        print("  🔑 recepcionista_test / test123456 (Recepcionista)")
        print(f"\n📍 URL de acceso: http://demo.localhost:8000/")
        print("📊 Después del login serás redirigido al dashboard correspondiente")
        
    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_demo_users()
