from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def subtract(value, arg):
    """Resta el argumento del valor."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def split(value, arg):
    """Divide un string por un separador."""
    if isinstance(value, str):
        return value.split(arg)
    return value

@register.filter
def sumar_campo(queryset, campo):
    """Suma los valores de un campo específico en un queryset."""
    if queryset:
        return queryset.aggregate(total=Sum(campo))['total'] or 0
    return 0
