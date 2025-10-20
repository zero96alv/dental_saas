import os
import sys
import django
from django.test import Client
from django.contrib.auth.models import User

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def test_urls():
    """
    Prueba las URLs para verificar si están funcionando correctamente
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
    
    # Iniciar sesión
    client.login(username='admin', password='admin123')
    
    # URLs a probar
    urls_to_test = [
        '/usuarios/',
        '/reportes/ingresos/',
        '/reportes/saldos/',
        '/services/new/',
        '/agenda/',
        '/admin/',
        '/pacientes/',
        '/pagos/'
    ]
    
    print("=== DIAGNÓSTICO DE URLS ===")
    print("Probando URLs después de la corrección...")
    print("-" * 50)
    
    for url in urls_to_test:
        try:
            response = client.get(url)
            status = response.status_code
            
            if status == 200:
                status_text = "✅ OK"
            elif status == 302:
                status_text = "🔄 REDIRECT"
            elif status == 403:
                status_text = "🚫 FORBIDDEN"
            elif status == 404:
                status_text = "❌ NOT FOUND"
            elif status == 500:
                status_text = "💥 ERROR 500"
            else:
                status_text = f"⚠️ {status}"
                
            print(f"{url:<25} | {status:<3} | {status_text}")
            
            # Si es error 500, intentar obtener más información
            if status == 500:
                try:
                    print(f"    Error en: {response.content.decode()[:200]}...")
                except:
                    print("    Error interno del servidor - revisar logs")
                    
        except Exception as e:
            print(f"{url:<25} | ERR | ❌ Exception: {str(e)}")
    
    print("-" * 50)
    print("Diagnóstico completado.")

if __name__ == '__main__':
    test_urls()
