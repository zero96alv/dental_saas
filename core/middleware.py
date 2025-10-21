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
            '/setup-tenants/',
            '/simple-setup/',
            '/tenants/',
            '/switch/',
            '/debug/',  # Vistas de debug
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
            # IMPORTANTE: Si ya estamos en una página de login, NO redirigir (evitar bucle infinito)
            if path.endswith('/accounts/login/') or '/accounts/login/' in path:
                logger.info(f"ForceAuth: Ya estamos en login ({path}), permitiendo acceso")
                return self.get_response(request)
            
            # Si estamos en una ruta de clínica, mantener el contexto
            clinic_slug = self._extract_clinic_from_path(path)
            if clinic_slug:
                # Estamos en una clínica, redirigir al login de esa clínica
                login_url = f'/{clinic_slug}/accounts/login/'
                logger.info(f"ForceAuth: Redirigiendo desde {path} al login de clínica: {login_url}")
            else:
                # Usar login estándar para rutas públicas
                login_url = settings.LOGIN_URL
                
                # Preservar parámetro tenant si existe
                tenant_param = request.GET.get('tenant')
                if tenant_param:
                    login_url += f'?tenant={tenant_param}'
                    logger.info(f"ForceAuth: Redirigiendo desde {path} a {login_url} (tenant={tenant_param})")
                else:
                    logger.info(f"ForceAuth: Redirigiendo desde {path} a {login_url}")
            
            return redirect(login_url)
        
        logger.info(f"ForceAuth: Permitiendo acceso autenticado a {path}")
        return self.get_response(request)
    
    def _extract_clinic_from_path(self, path):
        """
        Extrae slug de clínica de la URL para mantener contexto en redirects.
        Reutiliza la misma lógica que el ClinicRouteMiddleware.
        """
        # Limpiar la ruta
        path = path.strip('/')
        
        if not path:
            return None
        
        # Obtener el primer segmento
        first_segment = path.split('/')[0]
        
        # Excluir rutas especiales que NO son clínicas
        excluded_paths = {
            'admin', 'static', 'media', 'api', 'debug', 'accounts',
            'setup-tenants', 'simple-setup', 'tenants', 'switch'
        }
        
        if first_segment in excluded_paths:
            return None
        
        # Si es un slug válido, retornarlo
        if self._is_valid_clinic_slug(first_segment):
            return first_segment
        
        return None
    
    def _is_valid_clinic_slug(self, slug):
        """
        Valida que el slug sea un nombre válido de clínica.
        Misma lógica que ClinicRouteMiddleware.
        """
        import re
        
        if not slug or len(slug) < 3 or len(slug) > 20:
            return False
        
        # Patrón: letras, números y guiones, no empezar/terminar con guión
        pattern = r'^[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$'
        
        if len(slug) == 3:
            # Para slugs de 3 caracteres, permitir solo letras/números
            pattern = r'^[a-zA-Z0-9]+$'
        
        return bool(re.match(pattern, slug))

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
