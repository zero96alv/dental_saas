"""
Utilidades para manejo consistente de zonas horarias en toda la aplicación.

Esto asegura que todas las fechas se muestren correctamente en la zona horaria
configurada en settings (America/Mexico_City) independientemente del tenant.
"""

from django.utils import timezone
from django.conf import settings
from datetime import datetime


def to_local_timezone(dt):
    """
    Convierte un datetime (aware o naive) a la zona horaria local configurada.
    
    Args:
        dt: datetime object (puede ser aware o naive)
        
    Returns:
        datetime object en zona horaria local
    """
    if dt is None:
        return None
        
    # Si no tiene zona horaria, asumirla como UTC
    if not timezone.is_aware(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    
    # Activar temporalmente la zona horaria local
    current_tz = timezone.get_current_timezone()
    timezone.activate(settings.TIME_ZONE)
    
    try:
        # Convertir a zona local
        local_dt = timezone.localtime(dt)
        return local_dt
    finally:
        # Restaurar zona horaria anterior
        timezone.activate(current_tz)


def to_local_isoformat(dt):
    """
    Convierte un datetime a formato ISO en zona horaria local.
    
    Args:
        dt: datetime object
        
    Returns:
        string en formato ISO (YYYY-MM-DDTHH:MM:SS-OFFSET)
    """
    local_dt = to_local_timezone(dt)
    return local_dt.isoformat() if local_dt else None


def to_local_strftime(dt, format_str='%Y-%m-%dT%H:%M'):
    """
    Convierte un datetime a string con formato específico en zona horaria local.
    
    Args:
        dt: datetime object
        format_str: formato de fecha (default: '%Y-%m-%dT%H:%M')
        
    Returns:
        string con fecha formateada en zona local
    """
    local_dt = to_local_timezone(dt)
    return local_dt.strftime(format_str) if local_dt else None


def parse_local_datetime_string(date_str, time_str=None):
    """
    Parsea strings de fecha y hora asumiendo zona horaria local.
    
    Args:
        date_str: string de fecha (YYYY-MM-DD)
        time_str: string de hora opcional (HH:MM)
        
    Returns:
        datetime object aware en zona horaria local
    """
    if time_str:
        dt_str = f"{date_str}T{time_str}:00"
        dt = datetime.fromisoformat(dt_str)
    else:
        dt = datetime.fromisoformat(f"{date_str}T00:00:00")
    
    # Activar temporalmente la zona horaria local
    current_tz = timezone.get_current_timezone()
    timezone.activate(settings.TIME_ZONE)
    
    try:
        # Hacer el datetime aware en zona local
        local_dt = timezone.make_aware(dt)
        return local_dt
    finally:
        # Restaurar zona horaria anterior
        timezone.activate(current_tz)


def get_local_now():
    """
    Obtiene la fecha/hora actual en zona horaria local.
    
    Returns:
        datetime object con hora actual en zona local
    """
    return to_local_timezone(timezone.now())


class LocalTimezoneMixin:
    """
    Mixin para vistas que necesitan manejar fechas en zona horaria local.
    
    Activa automáticamente la zona horaria local durante la ejecución
    de los métodos de la vista.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Activa zona horaria local durante toda la vista"""
        original_tz = timezone.get_current_timezone()
        timezone.activate(settings.TIME_ZONE)
        
        try:
            response = super().dispatch(request, *args, **kwargs)
            return response
        finally:
            timezone.activate(original_tz)