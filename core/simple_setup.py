from django.http import HttpResponse, Http404
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from io import StringIO

@csrf_exempt
@never_cache
@require_http_methods(["GET", "POST"])
def simple_setup(request):
    """
    Vista ultra-simple para setup sin usar sesiones
    """
    # Verificar clave secreta
    secret_key = request.GET.get('key') or request.POST.get('key')
    if secret_key != "DentalSaaS2025Setup!":
        return HttpResponse("❌ Acceso denegado", status=403)
    
    output = "🚀 Setup Simple Iniciado...\n\n"
    
    try:
        # Importar modelos
        from tenants.models import Clinica, Domain
        from django.db import connection
        
        # Crear tenant público
        output += "📋 Creando tenant público...\n"
        try:
            public_tenant = Clinica.objects.filter(schema_name='public').first()
            if not public_tenant:
                public_tenant = Clinica.objects.create(
                    schema_name='public',
                    name='Public Schema'
                )
                output += "✅ Tenant público creado\n"
            else:
                output += "ℹ️ Tenant público ya existe\n"
            
            # Dominio público
            public_domain = Domain.objects.filter(domain='dental-saas.onrender.com').first()
            if not public_domain:
                Domain.objects.create(
                    domain='dental-saas.onrender.com',
                    tenant=public_tenant,
                    is_primary=True
                )
                output += "✅ Dominio público creado\n"
        except Exception as e:
            output += f"⚠️ Error tenant público: {e}\n"
        
        # Crear tenant demo
        output += "\n📋 Creando tenant demo...\n"
        try:
            demo_tenant = Clinica.objects.filter(schema_name='demo').first()
            if not demo_tenant:
                demo_tenant = Clinica.objects.create(
                    schema_name='demo',
                    name='Clínica Demo',
                    telefono='+52 55 1234 5678',
                    email='contacto@demo.dental-saas.com',
                    direccion='Av. Demo #123, Ciudad Demo, CP 12345'
                )
                output += "✅ Tenant demo creado\n"
            else:
                output += "ℹ️ Tenant demo ya existe\n"
            
            # Dominios demo - Usar dominio único para evitar conflictos
            demo_domain_prod = Domain.objects.filter(domain='demo.dental-saas.onrender.com').first()
            if not demo_domain_prod:
                # Intentar crear dominio específico (aunque Render no lo soporte)
                Domain.objects.create(
                    domain='demo.dental-saas.onrender.com',
                    tenant=demo_tenant,
                    is_primary=True
                )
                output += "✅ Dominio demo específico creado\n"
                
            demo_domain_local = Domain.objects.filter(domain='demo.localhost').first()
            if not demo_domain_local:
                Domain.objects.create(
                    domain='demo.localhost',
                    tenant=demo_tenant,
                    is_primary=True  # Este sí es primario para desarrollo
                )
                output += "✅ Dominio demo local creado\n"
                
        except Exception as e:
            output += f"⚠️ Error tenant demo: {e}\n"
        
        # Ejecutar migraciones
        output += "\n🔄 Ejecutando migraciones...\n"
        try:
            out = StringIO()
            call_command('migrate_all_tenants', stdout=out)
            migration_output = out.getvalue()
            output += migration_output + "\n"
        except Exception as e:
            output += f"⚠️ Error migraciones: {e}\n"
        
        # Configurar datos demo
        output += "\n👤 Configurando usuario demo...\n"
        try:
            # Cambiar al esquema demo
            demo_tenant = Clinica.objects.get(schema_name='demo')
            connection.set_tenant(demo_tenant)
            
            from django.contrib.auth.models import User, Group
            
            # Crear grupos
            admin_group, _ = Group.objects.get_or_create(name="Administrador")
            dentist_group, _ = Group.objects.get_or_create(name="Dentista")
            recep_group, _ = Group.objects.get_or_create(name="Recepcionista")
            output += "✅ Grupos creados\n"
            
            # Crear usuario admin
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@demo.dental-saas.com',
                    password='DemoAdmin2025!'
                )
                admin_user.groups.add(admin_group)
                output += "✅ Usuario admin creado\n"
            else:
                output += "ℹ️ Usuario admin ya existe\n"
                
        except Exception as e:
            output += f"⚠️ Error config demo: {e}\n"
        
        output += "\n🎉 Setup completado!\n"
        
    except Exception as e:
        output += f"\n❌ Error general: {e}\n"
    
    # Respuesta simple sin HTML complejo
    response_text = f"""Setup Dental SaaS - Resultado:

{output}

URLs disponibles:
- Admin Principal: https://dental-saas.onrender.com/admin/
- Admin Demo (parámetro): https://dental-saas.onrender.com/admin/?tenant=demo
- Sistema Demo: https://dental-saas.onrender.com/?tenant=demo
- Login Demo: https://dental-saas.onrender.com/accounts/login/?tenant=demo

Credenciales Demo: admin / DemoAdmin2025!

NOTA: Render no soporta subdominios. Usa ?tenant=demo para acceder al tenant demo.
"""
    
    return HttpResponse(response_text, content_type='text/plain; charset=utf-8')