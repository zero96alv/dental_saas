"""
Mixins personalizados para manejar autenticación con tenants path-based
"""
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps


class TenantLoginRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requiere autenticación pero mantiene el prefijo del tenant
    en las redirecciones. Reemplaza a LoginRequiredMixin estándar.
    """
    
    def get_login_url(self):
        """
        Obtiene la URL de login incluyendo el prefijo del tenant si existe
        """
        import logging
        logger = logging.getLogger(__name__)
        
        login_url = super().get_login_url()
        
        # Obtener el prefijo del tenant del request
        tenant_prefix = getattr(self.request, 'tenant_prefix', '')
        
        logger.info(f"[TenantLoginRequiredMixin] Original login_url: {login_url}")
        logger.info(f"[TenantLoginRequiredMixin] tenant_prefix: '{tenant_prefix}'")
        logger.info(f"[TenantLoginRequiredMixin] request.path: {self.request.path}")
        logger.info(f"[TenantLoginRequiredMixin] request.path_info: {self.request.path_info}")
        logger.info(f"[TenantLoginRequiredMixin] has tenant attr: {hasattr(self.request, 'tenant')}")
        
        # Si existe prefijo y la URL no lo incluye ya, agregarlo
        if tenant_prefix and not login_url.startswith(tenant_prefix):
            # Asegurar que login_url no tenga slash al inicio si tenant_prefix ya lo tiene
            if login_url.startswith('/'):
                login_url = login_url[1:]
            login_url = f'{tenant_prefix}/{login_url}'
            logger.info(f"[TenantLoginRequiredMixin] Modified login_url: {login_url}")
        else:
            logger.warning(f"[TenantLoginRequiredMixin] No tenant_prefix or already in URL")
        
        return login_url


def tenant_login_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorador que requiere autenticación pero mantiene el prefijo del tenant.
    Reemplaza a @login_required estándar para vistas basadas en funciones.
    
    Uso:
        @tenant_login_required
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Si el usuario está autenticado, continuar
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Usuario no autenticado, obtener prefijo del tenant
            tenant_prefix = getattr(request, 'tenant_prefix', '')
            
            # Construir URL de login con prefijo
            if login_url:
                resolved_login_url = login_url
            else:
                from django.conf import settings
                resolved_login_url = settings.LOGIN_URL
            
            # Agregar prefijo del tenant si existe
            if tenant_prefix and not resolved_login_url.startswith(tenant_prefix):
                if resolved_login_url.startswith('/'):
                    resolved_login_url = resolved_login_url[1:]
                resolved_login_url = f'{tenant_prefix}/{resolved_login_url}'
            
            # Agregar parámetro next si se especifica
            path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, resolved_login_url, redirect_field_name)
        
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator


class TenantAccessMixin(AccessMixin):
    """
    Mixin base para control de acceso que mantiene el prefijo del tenant
    """
    
    def get_login_url(self):
        """
        Obtiene la URL de login incluyendo el prefijo del tenant si existe
        """
        login_url = super().get_login_url()
        
        # Obtener el prefijo del tenant del request
        tenant_prefix = getattr(self.request, 'tenant_prefix', '')
        
        # Si existe prefijo y la URL no lo incluye ya, agregarlo
        if tenant_prefix and not login_url.startswith(tenant_prefix):
            if login_url.startswith('/'):
                login_url = login_url[1:]
            login_url = f'{tenant_prefix}/{login_url}'
        
        return login_url
