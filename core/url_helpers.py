"""
Helper functions for generating tenant-aware URLs in views
"""
from django.urls import reverse


def tenant_reverse(request, viewname, args=None, kwargs=None):
    """
    Genera una URL incluyendo el prefijo del tenant si existe.

    Esta función es el equivalente en vistas de la template tag tenant_url.

    Uso en vistas:
        from core.url_helpers import tenant_reverse

        # URL simple
        url = tenant_reverse(request, 'core:paciente_list')

        # URL con parámetros
        url = tenant_reverse(request, 'core:paciente_detail', kwargs={'pk': paciente.id})

        # Usar en redirect
        return HttpResponseRedirect(tenant_reverse(request, 'core:dashboard'))

    Args:
        request: HttpRequest object
        viewname: Nombre de la vista (ej: 'core:paciente_list')
        args: Argumentos posicionales para reverse()
        kwargs: Argumentos con nombre para reverse()

    Returns:
        str: URL completa con prefijo del tenant si existe
    """
    # Obtener la URL normal usando reverse de Django
    url = reverse(viewname, args=args, kwargs=kwargs)

    # Obtener el prefijo del tenant del request
    tenant_prefix = getattr(request, 'tenant_prefix', '')

    # Si existe prefijo y la URL no lo incluye ya, agregarlo
    if tenant_prefix and not url.startswith(tenant_prefix):
        # Asegurar que la URL no tenga doble slash
        if url.startswith('/'):
            url = url[1:]
        url = f'{tenant_prefix}/{url}'

    return url
