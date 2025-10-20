
import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)

class CustomLogoutView(DjangoLogoutView):
    """
    Vista de logout personalizada que maneja tanto GET como POST
    y limpia la sesión de forma segura.
    """
    
    def get(self, request, *args, **kwargs):
        """Manejar solicitudes GET de logout"""
        return self.post(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Manejar solicitudes POST de logout"""
        logger.info("Procesando logout para el usuario: %s", request.user)
        
        # Llamar al método de logout de Django
        logout(request)
        logger.info("Llamada a django.contrib.auth.logout() completada.")

        # Añadir mensaje de éxito
        messages.success(request, "Has cerrado sesión correctamente.")
        
        # Crear respuesta de redirección
        response = HttpResponseRedirect('/accounts/login/')
        
        # Eliminar cookies de sesión y CSRF
        logger.info("Eliminando cookies de sesión y CSRF.")
        response.delete_cookie(settings.SESSION_COOKIE_NAME, domain=settings.SESSION_COOKIE_DOMAIN)
        response.delete_cookie(settings.CSRF_COOKIE_NAME, domain=settings.SESSION_COOKIE_DOMAIN)

        return response

