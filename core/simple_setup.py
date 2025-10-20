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
            
            # NO asignar dominio principal a PUBLIC - dejar que el middleware maneje las rutas
            # output += "ℹ️ Dominio principal se maneja por middleware\n"
        except Exception as e:
            output += f"⚠️ Error tenant público: {e}\n"
        
        # Crear clínicas con slugs identificables
        clinicas_config = [
            {
                'schema_name': 'demo',
                'name': 'Clínica Demo',
                'telefono': '+52 55 1234 5678',
                'email': 'contacto@demo.dental-saas.com',
                'direccion': 'Av. Demo #123, Ciudad Demo, CP 12345'
            },
            {
                'schema_name': 'sgdental',
                'name': 'SG Dental',
                'telefono': '+52 55 9876 5432',
                'email': 'contacto@sgdental.com',
                'direccion': 'Calle Sonrisas #456, Col. Dental, CP 54321'
            },
            {
                'schema_name': 'cgdental',
                'name': 'CG Dental Care',
                'telefono': '+52 55 5555 0000',
                'email': 'info@cgdental.com',
                'direccion': 'Av. Salud Oral #789, Centro, CP 67890'
            }
        ]
        
        output += "\n📋 Creando clínicas...\n"
        for config in clinicas_config:
            try:
                tenant = Clinica.objects.filter(schema_name=config['schema_name']).first()
                if not tenant:
                    tenant = Clinica.objects.create(**config)
                    output += f"✅ Clínica {config['name']} ({config['schema_name']}) creada\n"
                else:
                    output += f"ℹ️ Clínica {config['name']} ya existe\n"
            
            # Las clínicas ahora se acceden por rutas: /sgdental/, /cgdental/, /demo/
            # No necesitamos dominios específicos
                
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
        
        # Configurar usuarios para todas las clínicas
        output += "\n👤 Configurando usuarios...\n"
        
        from django.contrib.auth.models import User, Group
        
        # Configurar cada clínica
        for config in clinicas_config:
            try:
                output += f"\n🏥 Configurando {config['name']}...\n"
                
                # Cambiar al esquema de esta clínica
                tenant = Clinica.objects.get(schema_name=config['schema_name'])
                connection.set_tenant(tenant)
                
                # Crear grupos estándar
                admin_group, _ = Group.objects.get_or_create(name="Administrador")
                dentist_group, _ = Group.objects.get_or_create(name="Dentista")
                recep_group, _ = Group.objects.get_or_create(name="Recepcionista")
                
                # Crear usuario admin para esta clínica
                if not User.objects.filter(username='admin').exists():
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email=config['email'].replace('contacto@', 'admin@').replace('info@', 'admin@'),
                        password='DemoAdmin2025!'
                    )
                    admin_user.groups.add(admin_group)
                    output += f"✅ Usuario admin creado para {config['name']}\n"
                else:
                    output += f"ℹ️ Usuario admin ya existe en {config['name']}\n"
                
        except Exception as e:
            output += f"⚠️ Error config demo: {e}\n"
        
        output += "\n🎉 Setup completado!\n"
        
    except Exception as e:
        output += f"\n❌ Error general: {e}\n"
    
    # Respuesta simple sin HTML complejo
    response_text = f"""Setup Dental SaaS - Resultado:

{output}

URLs disponibles:
- 🏠 Landing Page: https://dental-saas.onrender.com/
- ⚙️ Admin Principal: https://dental-saas.onrender.com/admin/

Clínicas disponibles:
- 🏥 Demo: https://dental-saas.onrender.com/demo/
- 🏥 SG Dental: https://dental-saas.onrender.com/sgdental/
- 🏥 CG Dental: https://dental-saas.onrender.com/cgdental/

Credenciales para todas las clínicas: admin / DemoAdmin2025!

NOTA: Ahora cada clínica tiene su propia ruta identificable. 🎉
"""
    
    return HttpResponse(response_text, content_type='text/plain; charset=utf-8')