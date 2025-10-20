from django.http import HttpResponse, Http404
from django.core.management import call_command
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from io import StringIO
import sys

@csrf_exempt
@never_cache  # Evitar problemas de cache
def setup_tenants_migrations(request):
    """
    Vista especial para ejecutar migraciones en tenants desde URL
    Con setup automático de tenants
    """
    # Verificar clave secreta en parámetro
    secret_key = request.GET.get('key') or request.POST.get('key')
    expected_key = "DentalSaaS2025Setup!"
    
    if secret_key != expected_key:
        raise Http404("Clave incorrecta")
    
    output = "🚀 Iniciando setup automático...\n\n"
    
    try:
        # Deshabilitar sesiones temporalmente para evitar errores
        if hasattr(request, 'session'):
            try:
                # Limpiar sesiones problemáticas
                request.session.flush()
            except:
                pass
        
        # 1. Crear tenants si no existen
        from tenants.models import Clinica, Domain
        from django.db import connection
        
        # Asegurar que estamos en el esquema público
        connection.set_schema_to_public()
        
        # Crear tenant público
        try:
            public_tenant, public_created = Clinica.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public Schema'}
            )
            
            if public_created:
                Domain.objects.get_or_create(
                    domain='dental-saas.onrender.com',
                    defaults={'tenant': public_tenant, 'is_primary': True}
                )
                output += "✅ Tenant público creado\n"
            else:
                output += "ℹ️ Tenant público ya existe\n"
        except Exception as e:
            output += f"⚠️ Error con tenant público: {e}\n"
        
        # Crear tenant demo
        try:
            demo_tenant, demo_created = Clinica.objects.get_or_create(
                schema_name='demo',
                defaults={
                    'name': 'Clínica Demo',
                    'telefono': '+52 55 1234 5678',
                    'email': 'contacto@demo.dental-saas.com',
                    'direccion': 'Av. Demo #123, Ciudad Demo, CP 12345'
                }
            )
            
            if demo_created:
                Domain.objects.get_or_create(
                    domain='demo.dental-saas.onrender.com',
                    defaults={'tenant': demo_tenant, 'is_primary': True}
                )
                # También crear dominio para localhost
                Domain.objects.get_or_create(
                    domain='demo.localhost',
                    defaults={'tenant': demo_tenant, 'is_primary': False}
                )
                output += "✅ Tenant demo creado\n"
            else:
                output += "ℹ️ Tenant demo ya existe\n"
        except Exception as e:
            output += f"⚠️ Error con tenant demo: {e}\n"
        
        output += "\n🔄 Ejecutando migraciones...\n"
        
        # 2. Ejecutar migraciones
        out = StringIO()
        call_command('migrate_all_tenants', stdout=out)
        migration_output = out.getvalue()
        output += migration_output
        
        # También ejecutar setup de datos iniciales directamente
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
                output += "\n✅ Usuario admin creado para demo"
            else:
                output += "\nℹ️ Usuario admin ya existe en demo"
                
            output += "\n✅ Datos iniciales configurados para demo"
            
        except Exception as e:
            output += f"\n❌ Error configurando demo: {e}"
        
        output += "\n\n🎉 Setup completado exitosamente!"
        
    except Exception as e:
        output += f"\n\n❌ Error ejecutando setup: {str(e)}"
    
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