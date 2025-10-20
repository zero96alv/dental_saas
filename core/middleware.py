from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_tenant_domain_model
import logging
import re

logger = logging.getLogger(__name__)

class ForceAuthenticationMiddleware:
    """
    Middleware que fuerza autenticación para todas las rutas excepto login, logout, admin y archivos estáticos
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que no requieren autenticación
        self.exempt_urls = [
            '/accounts/login/',
            '/accounts/logout/',
            '/admin/',
        ]
        
        # Prefijos de URL que se deben ignorar completamente (archivos estáticos, media, etc.)
        self.static_prefixes = [
            '/static/',
            '/media/',
            '/favicon.ico',
        ]
        
        # Patrones de URL que no requieren autenticación
        self.exempt_url_patterns = [
            'admin:',
            'login',
            'logout',
        ]

    def __call__(self, request):
        # Verificar si la URL está exenta
        path = request.path
        user = request.user
        
        # Log para diagnóstico (solo para URLs que no sean estáticas)
        if not any(path.startswith(prefix) for prefix in self.static_prefixes):
            logger.info(f"ForceAuth: Path={path}, User={user}, Authenticated={user.is_authenticated}")
        
        # PRIMERO: Archivos estáticos - permitir siempre sin procesamiento
        if any(path.startswith(prefix) for prefix in self.static_prefixes):
            return self.get_response(request)
        
        # SEGUNDO: URLs específicas exentas
        if any(path.startswith(exempt) for exempt in self.exempt_urls):
            logger.info(f"ForceAuth: Path {path} exenta por URL específica")
            return self.get_response(request)

        # TERCERO: Si el usuario no está autenticado, redirigir al login
        if not request.user.is_authenticated:
            logger.info(f"ForceAuth: Redirigiendo usuario no autenticado desde {path} a {settings.LOGIN_URL}")
            return redirect(settings.LOGIN_URL)
        
        logger.info(f"ForceAuth: Permitiendo acceso autenticado a {path}")
        return self.get_response(request)

class NoCacheMiddleware:
    """
    Middleware que agrega headers a cada respuesta para prevenir
    el cacheo en el navegador.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo aplicar a respuestas HTML para no afectar archivos estáticos o APIs
        if 'text/html' in response.get('Content-Type', ''):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response


class LocalTimezoneMiddleware(MiddlewareMixin):
    """
    Middleware que activa automáticamente la zona horaria local para todas las peticiones.
    
    Esto asegura que todas las vistas, formularios y APIs muestren fechas/horas
    correctamente en la zona horaria configurada (America/Mexico_City).
    """
    
    def process_request(self, request):
        """Activa la zona horaria local al inicio de cada petición"""
        timezone.activate(settings.TIME_ZONE)
        return None
    
    def process_response(self, request, response):
        """Limpia la zona horaria al final de cada petición"""
        timezone.deactivate()
        return response
