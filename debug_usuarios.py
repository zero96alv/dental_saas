import os
import sys
import django
import traceback
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def debug_usuarios_view():
    """
    Intenta acceder a la vista de usuarios y captura el error detallado
    """
    client = Client()
    
    # Crear usuario de prueba si no existe
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser(
            username='admin', 
            email='admin@demo.com', 
            password='admin123'
        )
        print("Usuario admin creado")
    
    # Iniciar sesión
    login_success = client.login(username='admin', password='admin123')
    if not login_success:
        print("❌ Error al iniciar sesión")
        return
    
    print("✅ Usuario autenticado correctamente")
    
    # Intentar acceder a /usuarios/
    try:
        print("🔍 Intentando acceso a /usuarios/...")
        response = client.get('/usuarios/')
        
        if response.status_code == 200:
            print("✅ /usuarios/ funciona correctamente")
        elif response.status_code == 500:
            print("❌ Error 500 en /usuarios/")
            # Intentar obtener el contenido del error
            print("Contenido de la respuesta:")
            try:
                content = response.content.decode('utf-8')
                if content:
                    print(content[:1000])  # Primeros 1000 caracteres
                else:
                    print("Contenido vacío")
            except Exception as e:
                print(f"Error al decodificar contenido: {e}")
        else:
            print(f"Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Excepción capturada: {e}")
        print("\n📋 Traceback completo:")
        traceback.print_exc()

if __name__ == '__main__':
    debug_usuarios_view()
