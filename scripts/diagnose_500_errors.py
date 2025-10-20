import os
import sys
import django
import requests

# Configurar Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.conf import settings
from tenants.models import Clinica

# URLs problemáticas reportadas
PROBLEMATIC_URLS = [
    'http://demo.localhost:8000/usuarios/',
    'http://demo.localhost:8000/reportes/ingresos/',
    'http://demo.localhost:8000/reportes/saldos/',
    'http://demo.localhost:8000/services/new/',
    'http://demo.localhost:8000/agenda/',
    'http://demo.localhost:8000/admin/',
]

# URLs que deberían funcionar (con namespace correcto)
CORRECT_URLS = [
    'http://demo.localhost:8000/usuarios/',
    'http://demo.localhost:8000/reportes/ingresos/',
    'http://demo.localhost:8000/reportes/saldos/',
    'http://demo.localhost:8000/services/new/',
    'http://demo.localhost:8000/agenda/',
    'http://demo.localhost:8000/admin/',
]

def test_url_with_auth(url, session):
    """Probar una URL con autenticación."""
    try:
        response = session.get(url, allow_redirects=False)
        return {
            'url': url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content_preview': response.text[:200] if response.text else '',
            'error': None
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'headers': {},
            'content_preview': '',
            'error': str(e)
        }

def diagnose_urls():
    """Diagnosticar URLs problemáticas."""
    print("🔍 DIAGNÓSTICO DE URLs PROBLEMÁTICAS")
    print("=" * 50)
    
    # Crear sesión autenticada
    session = requests.Session()
    session.headers.update({'Host': 'demo.localhost'})
    
    # Hacer login primero
    print("\n1. Autenticando...")
    login_url = 'http://demo.localhost:8000/accounts/login/'
    login_page = session.get(login_url)
    csrf_token = login_page.cookies.get('csrftoken')
    
    login_data = {
        'username': 'admin',
        'password': 'password',
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(login_url, data=login_data, allow_redirects=False)
    
    if login_response.status_code == 302:
        print("✅ Login exitoso")
    else:
        print("❌ Login falló")
        return
    
    # Probar URLs problemáticas
    print("\n2. Probando URLs problemáticas...")
    print("-" * 40)
    
    results = []
    for url in PROBLEMATIC_URLS:
        print(f"\nProbando: {url}")
        result = test_url_with_auth(url, session)
        results.append(result)
        
        if result['error']:
            print(f"❌ ERROR: {result['error']}")
        elif result['status_code'] == 500:
            print(f"❌ ERROR 500 - Internal Server Error")
            print(f"   Preview: {result['content_preview']}")
        elif result['status_code'] == 404:
            print(f"❌ ERROR 404 - Not Found")
        elif result['status_code'] == 302:
            redirect_to = result['headers'].get('Location', 'Unknown')
            print(f"⚠️  REDIRECT 302 → {redirect_to}")
        elif result['status_code'] == 200:
            print(f"✅ OK 200 - Funciona correctamente")
        else:
            print(f"⚠️  CÓDIGO {result['status_code']}")
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 50)
    
    errors_500 = [r for r in results if r['status_code'] == 500]
    errors_404 = [r for r in results if r['status_code'] == 404]
    working = [r for r in results if r['status_code'] == 200]
    redirects = [r for r in results if r['status_code'] == 302]
    
    print(f"✅ URLs funcionando: {len(working)}")
    print(f"🔄 URLs con redirect: {len(redirects)}")
    print(f"❌ Errores 500: {len(errors_500)}")
    print(f"❌ Errores 404: {len(errors_404)}")
    
    if errors_500:
        print(f"\n🚨 URLs con ERROR 500:")
        for result in errors_500:
            print(f"   - {result['url']}")
    
    if errors_404:
        print(f"\n🚨 URLs con ERROR 404:")
        for result in errors_404:
            print(f"   - {result['url']}")
    
    return results

def check_admin_access():
    """Verificar acceso al admin de Django."""
    print("\n" + "=" * 50)
    print("🔧 VERIFICANDO ADMIN DE DJANGO")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({'Host': 'demo.localhost'})
    
    admin_urls = [
        'http://demo.localhost:8000/admin/',
        'http://localhost:8000/admin/',
        'http://127.0.0.1:8000/admin/',
    ]
    
    for admin_url in admin_urls:
        print(f"\nProbando: {admin_url}")
        try:
            response = session.get(admin_url, allow_redirects=False)
            print(f"   Status: {response.status_code}")
            if response.status_code == 302:
                print(f"   Redirect → {response.headers.get('Location', 'Unknown')}")
            elif response.status_code == 200:
                print(f"   ✅ Admin accesible")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    diagnose_urls()
    check_admin_access()
