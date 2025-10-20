from django import template
from django.contrib.auth.models import Group
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Verifica si un usuario pertenece a un grupo.
    Permite comprobar múltiples grupos separados por comas.
    Ej: {% if user|has_group:"Administrador,Recepcionista" %}
    """
    group_names = [g.strip() for g in group_name.split(',')]
    return user.groups.filter(name__in=group_names).exists()

@register.filter
def es_url_con_parametros(url_name):
    """Detecta si una URL requiere parámetros"""
    try:
        # Intentar resolver la URL sin parámetros
        reverse(url_name)
        return False  # Si no falla, no requiere parámetros
    except NoReverseMatch:
        return True   # Si falla, probablemente requiere parámetros
    except Exception:
        return True   # En caso de cualquier otro error, asumir que requiere parámetros

@register.filter(name='es_reporte')
def es_reporte(url_name: str) -> bool:
    """Indica si el nombre de URL corresponde a un reporte (convención core:reporte_*)"""
    try:
        return isinstance(url_name, str) and url_name.startswith('core:reporte_')
    except Exception:
        return False
