from django.http import HttpResponse, Http404
from django.core.management import call_command
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from io import StringIO
import sys

@csrf_exempt
@require_http_methods(["GET", "POST"])
def setup_tenants_migrations(request):
    """
    Vista especial para ejecutar migraciones en tenants desde URL
    Solo disponible en producción con clave secreta
    """
    # Verificar que esté en producción
    if settings.DEBUG:
        raise Http404("Solo disponible en producción")
    
    # Verificar clave secreta en parámetro
    secret_key = request.GET.get('key') or request.POST.get('key')
    expected_key = "DentalSaaS2025Setup!"
    
    if secret_key != expected_key:
        raise Http404("Clave incorrecta")
    
    # Capturar salida del comando
    out = StringIO()
    old_stdout = sys.stdout
    sys.stdout = out
    
    try:
        # Ejecutar comando de migración de tenants
        call_command('migrate_all_tenants', stdout=out)
        output = out.getvalue()
        
        # También ejecutar setup de datos iniciales
        call_command('shell', '-c', '''
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dental_saas.settings_production")

from tenants.models import Clinica
from django.db import connection
from django.contrib.auth.models import User, Group

# Configurar datos para tenant demo
try:
    demo_tenant = Clinica.objects.get(schema_name="demo")
    connection.set_tenant(demo_tenant)
    
    # Crear grupos
    Group.objects.get_or_create(name="Administrador")
    Group.objects.get_or_create(name="Dentista") 
    Group.objects.get_or_create(name="Recepcionista")
    
    # Crear usuario admin para demo
    if not User.objects.filter(username="admin").exists():
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@demo.dental-saas.com", 
            password="DemoAdmin2025!"
        )
        admin_user.groups.add(Group.objects.get(name="Administrador"))
        print("✅ Usuario admin creado para demo")
    else:
        print("ℹ️ Usuario admin ya existe en demo")
        
    print("✅ Datos iniciales configurados para demo")
    
except Exception as e:
    print(f"❌ Error configurando demo: {e}")
        ''', stdout=out)
        
        output += out.getvalue()
        
    except Exception as e:
        output = f"❌ Error ejecutando setup: {str(e)}"
    finally:
        sys.stdout = old_stdout
        out.close()
    
    # Devolver respuesta HTML con resultado
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Setup Tenants - Dental SaaS</title>
        <style>
            body {{ font-family: monospace; background: #f0f0f0; margin: 20px; }}
            .container {{ background: white; padding: 20px; border-radius: 8px; }}
            pre {{ background: #2d2d2d; color: #fff; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Setup de Tenants - Dental SaaS</h1>
            <h2>📊 Resultado:</h2>
            <pre>{output}</pre>
            <hr>
            <p><strong>URLs disponibles después del setup:</strong></p>
            <ul>
                <li><a href="https://dental-saas.onrender.com/admin/">Admin Principal</a></li>
                <li><a href="https://demo.dental-saas.onrender.com/admin/">Admin Demo</a></li>
                <li><a href="https://demo.dental-saas.onrender.com/">Sistema Demo</a></li>
            </ul>
            <p><strong>Credenciales Demo:</strong> admin / DemoAdmin2025!</p>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html)