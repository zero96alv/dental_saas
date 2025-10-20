from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class CustomLogoutView(DjangoLogoutView):
    """
    Vista personalizada de logout que asegura limpieza completa de sesión
    """
    
    def dispatch(self, request, *args, **kwargs):
        # Log del estado antes del logout
        user = request.user
        session_key = request.session.session_key
        logger.info(f"CustomLogout: Usuario {user} (authenticated={user.is_authenticated}) iniciando logout, session_key={session_key}")
        
        # Si no hay usuario autenticado, redirigir directamente
        if not request.user.is_authenticated:
            logger.info("CustomLogout: Usuario ya no autenticado, redirigiendo a login")
            return HttpResponseRedirect(reverse('login'))
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Manejar POST logout"""
        return self.logout_and_redirect(request)
    
    def get(self, request, *args, **kwargs):
        """Manejar GET logout"""
        return self.logout_and_redirect(request)
    
    def logout_and_redirect(self, request):
        """Realizar logout y redirección con limpieza explícita"""
        user = request.user
        session_key = request.session.session_key
        
        logger.info(f"CustomLogout: Ejecutando logout para {user}, session_key={session_key}")
        
        # Limpiar sesión explícitamente
        if hasattr(request, 'session'):
            request.session.flush()  # Elimina todos los datos de sesión y regenera la clave
            logger.info("CustomLogout: Sesión eliminada con flush()")
        
        # Ejecutar logout de Django
        logout(request)
        logger.info("CustomLogout: Django logout() ejecutado")
        
        # Verificar que realmente se hizo logout
        logger.info(f"CustomLogout: Post-logout - Usuario: {request.user}, Authenticated: {request.user.is_authenticated}")
        
        # Agregar mensaje de confirmación
        messages.success(request, "Has cerrado sesión exitosamente.")
        
        # Redirigir al login
        redirect_url = reverse('login')
        logger.info(f"CustomLogout: Redirigiendo a {redirect_url}")
        
        return HttpResponseRedirect(redirect_url)
