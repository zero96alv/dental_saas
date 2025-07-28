from django.http import JsonResponse
from .models import Clinica, Domain

def tenant_check_view(request):
    """
    Una vista de diagnóstico para mostrar todas las clínicas y dominios
    en el esquema público.
    """
    response_data = {
        'clinicas': [],
        'dominios': []
    }

    try:
        # Obtener todas las clínicas
        clinicas = Clinica.objects.all()
        for clinica in clinicas:
            response_data['clinicas'].append({
                'schema_name': clinica.schema_name,
                'nombre': clinica.nombre,
            })

        # Obtener todos los dominios
        dominios = Domain.objects.all()
        for dominio in dominios:
            response_data['dominios'].append({
                'domain': dominio.domain,
                'tenant_schema_name': dominio.tenant.schema_name,
                'is_primary': dominio.is_primary,
            })
            
    except Exception as e:
        response_data['error'] = str(e)

    return JsonResponse(response_data)