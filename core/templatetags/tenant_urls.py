"""
Template tags personalizados para generar URLs con prefijo de tenant
"""
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def tenant_url(context, viewname, *args, **kwargs):
    """
    Genera una URL incluyendo el prefijo del tenant si existe.
    
    Uso en templates:
        {% load tenant_urls %}
        <a href="{% tenant_url 'core:paciente_list' %}">Pacientes</a>
        <a href="{% tenant_url 'core:paciente_detail' pk=paciente.id %}">Ver paciente</a>
    """
    # Obtener la URL normal
    url = reverse(viewname, args=args, kwargs=kwargs)
    
    # Obtener el request del contexto
    request = context.get('request')
    if request:
        # Obtener el prefijo del tenant si existe
        tenant_prefix = getattr(request, 'tenant_prefix', '')
        
        # Si existe prefijo y la URL no lo incluye ya, agregarlo
        if tenant_prefix and not url.startswith(tenant_prefix):
            # Asegurar que la URL no tenga doble slash
            if url.startswith('/'):
                url = url[1:]
            url = f'{tenant_prefix}/{url}'
    
    return url
