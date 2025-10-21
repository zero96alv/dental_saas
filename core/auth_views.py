
import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView as DjangoLogoutView, LoginView as DjangoLoginView
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        
        # Obtener el prefijo del tenant antes del logout
        tenant_prefix = getattr(request, 'tenant_prefix', '')
        logger.info(f"Tenant prefix detectado: '{tenant_prefix}'")
        
        # Llamar al método de logout de Django
        logout(request)
        logger.info("Llamada a django.contrib.auth.logout() completada.")

        # Añadir mensaje de éxito
        messages.success(request, "Has cerrado sesión correctamente.")
        
        # Crear respuesta de redirección con el prefijo del tenant
        redirect_url = f'{tenant_prefix}/accounts/login/' if tenant_prefix else '/accounts/login/'
        logger.info(f"Redirigiendo logout a: {redirect_url}")
        response = HttpResponseRedirect(redirect_url)
        
        # Eliminar cookies de sesión y CSRF
        logger.info("Eliminando cookies de sesión y CSRF.")
        response.delete_cookie(settings.SESSION_COOKIE_NAME, domain=settings.SESSION_COOKIE_DOMAIN)
        response.delete_cookie(settings.CSRF_COOKIE_NAME, domain=settings.SESSION_COOKIE_DOMAIN)

        return response


class CustomLoginView(DjangoLoginView):
    """
    Vista de login personalizada que preserva el parámetro tenant
    en la redirección después del login exitoso.
    """
    template_name = 'core/login.html'
    
    def get_success_url(self):
        """Redirigión después del login exitoso preservando tenant"""
        # Obtener URL de redirección por defecto
        success_url = super().get_success_url()
        
        # Preservar parámetro tenant si existe
        tenant_param = self.request.GET.get('tenant')
        if tenant_param:
            # Si la URL ya tiene parámetros, agregar con &, si no con ?
            separator = '&' if '?' in success_url else '?'
            success_url += f'{separator}tenant={tenant_param}'
            logger.info(f"Login exitoso: Redirigiendo a {success_url} con tenant={tenant_param}")
        
        return success_url
