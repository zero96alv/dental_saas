from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

@csrf_exempt
@never_cache
@require_http_methods(["GET", "POST"])
def setup_domains(request):
    """
    Vista para configurar dominios para cada clínica
    """
    # Verificar clave secreta
    secret_key = request.GET.get('key') or request.POST.get('key')
    if secret_key != "DentalSaaS2025Setup!":
        return HttpResponse("❌ Acceso denegado", status=403)
    
    output = "🌐 Configurando dominios para clínicas...\n\n"
    
    try:
        from tenants.models import Clinica, Domain
        
        # Configuración de dominios para cada clínica
        domain_config = [
            {
                'tenant': 'demo',
                'domains': [
                    'demo.dental-saas.onrender.com',
                    'demo.localhost',
                ]
            },
            {
                'tenant': 'sgdental', 
                'domains': [
                    'sgdental.dental-saas.onrender.com',
                    'sgdental.localhost',
                ]
            },
            {
                'tenant': 'cgdental',
                'domains': [
                    'cgdental.dental-saas.onrender.com', 
                    'cgdental.localhost',
                ]
            }
        ]
        
        # Crear dominios para cada clínica
        for config in domain_config:
            try:
                tenant = Clinica.objects.get(schema_name=config['tenant'])
                output += f"🏥 Configurando dominios para {tenant.nombre}:\n"
                
                for domain_name in config['domains']:
                    domain, created = Domain.objects.get_or_create(
                        domain=domain_name,
                        defaults={'tenant': tenant}
                    )
                    
                    if created:
                        output += f"   ✅ Dominio {domain_name} creado\n"
                    else:
                        output += f"   ℹ️ Dominio {domain_name} ya existe\n"
                        
                output += "\n"
                        
            except Clinica.DoesNotExist:
                output += f"❌ Clínica '{config['tenant']}' no encontrada\n"
            except Exception as e:
                output += f"⚠️ Error configurando {config['tenant']}: {e}\n"
        
        output += "🎉 Configuración de dominios completada!\n\n"
        output += "URLs de acceso:\n"
        output += "- 🏥 Demo: https://demo.dental-saas.onrender.com/\n"
        output += "- 🏥 SG Dental: https://sgdental.dental-saas.onrender.com/\n"
        output += "- 🏥 CG Dental: https://cgdental.dental-saas.onrender.com/\n\n"
        output += "Para desarrollo local:\n"
        output += "- 🏥 Demo: http://demo.localhost:8000/\n"
        output += "- 🏥 SG Dental: http://sgdental.localhost:8000/\n"
        output += "- 🏥 CG Dental: http://cgdental.localhost:8000/\n"
        
    except Exception as e:
        output += f"❌ Error general: {e}\n"
    
    return HttpResponse(output, content_type='text/plain; charset=utf-8')