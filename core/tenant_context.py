def tenant_context(request):
    """Context processor para agregar información del tenant"""
    tenant_prefix = ''
    if hasattr(request, 'tenant') and request.tenant:
        if hasattr(request, 'tenant_prefix'):
            tenant_prefix = request.tenant_prefix
    
    return {
        'TENANT_PREFIX': tenant_prefix,
    }
