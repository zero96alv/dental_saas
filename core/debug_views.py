from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@csrf_exempt
def tenant_debug(request):
    """
    Vista de diagnóstico para verificar el estado del tenant y usuario
    """
    try:
        from django.db import connection
        from tenants.models import Clinica
        
        # Información básica
        info = []
        info.append("=== DIAGNÓSTICO DE TENANT ===\n")
        
        # Usuario
        info.append(f"👤 Usuario: {request.user}")
        info.append(f"🔐 Autenticado: {request.user.is_authenticated}")
        info.append(f"🆔 User ID: {getattr(request.user, 'id', 'None')}")
        info.append(f"📧 Email: {getattr(request.user, 'email', 'None')}")
        
        # Tenant actual
        try:
            tenant = connection.tenant
            info.append(f"\n🏥 Tenant actual: {tenant.name}")
            info.append(f"📋 Schema: {tenant.schema_name}")
            info.append(f"🆔 Tenant ID: {tenant.id}")
        except Exception as e:
            info.append(f"\n❌ Error obteniendo tenant: {e}")
        
        # Parámetros de request
        info.append(f"\n🔗 URL: {request.path}")
        info.append(f"📊 Método: {request.method}")
        info.append(f"🎯 GET params: {dict(request.GET.items())}")
        info.append(f"📝 POST params: {dict(request.POST.items()) if request.method == 'POST' else 'N/A'}")
        
        # Headers importantes
        info.append(f"\n📡 Host: {request.META.get('HTTP_HOST', 'Unknown')}")
        info.append(f"🌐 User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}...")
        
        # Session info
        info.append(f"\n🍪 Session Key: {request.session.session_key}")
        info.append(f"📋 Session Data: {dict(request.session.items())}")
        
        # Listar todos los tenants disponibles
        info.append(f"\n📚 Tenants disponibles:")
        try:
            tenants = Clinica.objects.all()
            for t in tenants:
                info.append(f"  - {t.name} ({t.schema_name})")
        except Exception as e:
            info.append(f"  ❌ Error listando tenants: {e}")
        
        # Información de base de datos
        info.append(f"\n💾 DB Name: {connection.settings_dict.get('NAME', 'Unknown')}")
        info.append(f"🖥️ DB Host: {connection.settings_dict.get('HOST', 'Unknown')}")
        info.append(f"👤 DB User: {connection.settings_dict.get('USER', 'Unknown')}")
        
        response_text = "\n".join(info)
        return HttpResponse(response_text, content_type='text/plain; charset=utf-8')
        
    except Exception as e:
        return HttpResponse(f"❌ Error en diagnóstico: {e}", content_type='text/plain; charset=utf-8')


@csrf_exempt
def user_debug(request):
    """
    Vista específica para debugging de usuario
    """
    try:
        from django.contrib.auth import get_user_model
        from django.db import connection
        
        info = []
        info.append("=== DIAGNÓSTICO DE USUARIO ===\n")
        
        # Información del usuario actual
        user = request.user
        info.append(f"👤 Usuario actual: {user}")
        info.append(f"🔐 Autenticado: {user.is_authenticated}")
        info.append(f"🏅 Es superuser: {getattr(user, 'is_superuser', False)}")
        info.append(f"🏢 Es staff: {getattr(user, 'is_staff', False)}")
        
        if user.is_authenticated:
            info.append(f"🆔 ID: {user.id}")
            info.append(f"📧 Email: {user.email}")
            info.append(f"👥 Grupos: {list(user.groups.values_list('name', flat=True))}")
            info.append(f"📅 Último login: {user.last_login}")
            info.append(f"📅 Fecha creación: {user.date_joined}")
        
        # Intentar listar usuarios en el tenant actual
        info.append(f"\n👥 Usuarios en tenant actual:")
        try:
            User = get_user_model()
            users = User.objects.all()[:10]  # Solo primeros 10
            for u in users:
                info.append(f"  - {u.username} ({u.email}) - Activo: {u.is_active}")
        except Exception as e:
            info.append(f"  ❌ Error listando usuarios: {e}")
        
        # Schema actual
        try:
            tenant = connection.tenant
            info.append(f"\n🏥 Schema actual: {tenant.schema_name}")
        except Exception as e:
            info.append(f"\n❌ Error obteniendo schema: {e}")
            
        response_text = "\n".join(info)
        return HttpResponse(response_text, content_type='text/plain; charset=utf-8')
        
    except Exception as e:
        return HttpResponse(f"❌ Error en diagnóstico de usuario: {e}", content_type='text/plain; charset=utf-8')


@csrf_exempt
def force_tenant_switch(request):
    """
    Vista para forzar cambio de tenant
    """
    tenant_param = request.GET.get('tenant', 'demo')
    
    try:
        from tenants.models import Clinica
        from django.db import connection
        from django.shortcuts import redirect
        
        # Buscar el tenant
        tenant = Clinica.objects.get(schema_name=tenant_param)
        
        # Forzar cambio de tenant
        connection.set_tenant(tenant)
        
        info = f"""✅ Tenant cambiado exitosamente a: {tenant.name} ({tenant.schema_name})

🔗 Enlaces de prueba:
- Dashboard: /dashboard/?tenant={tenant_param}
- Admin: /admin/?tenant={tenant_param}
- Login: /accounts/login/?tenant={tenant_param}

👤 Usuario actual: {request.user}
🔐 Autenticado: {request.user.is_authenticated}
"""
        
        return HttpResponse(info, content_type='text/plain; charset=utf-8')
        
    except Exception as e:
        return HttpResponse(f"❌ Error forzando cambio de tenant: {e}", content_type='text/plain; charset=utf-8')