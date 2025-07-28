from django import template
from django.contrib.auth.models import Group

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
