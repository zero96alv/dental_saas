from django.http import JsonResponse

def debug_tenant(request):
    return JsonResponse({
        'has_tenant': hasattr(request, 'tenant'),
        'tenant_name': getattr(request.tenant, 'nombre', None) if hasattr(request, 'tenant') else None,
        'has_tenant_prefix': hasattr(request, 'tenant_prefix'),
        'tenant_prefix': getattr(request, 'tenant_prefix', None),
        'path_info': request.path_info,
        'full_path': request.get_full_path(),
    })
