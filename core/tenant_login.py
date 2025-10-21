"""
Vista de login personalizada que maneja correctamente los redirects
cuando se usa enrutamiento por path (path-based tenants)
"""
from django.contrib.auth.views import LoginView
from django.conf import settings


class TenantAwareLoginView(LoginView):
    """
    Vista de login que preserva el prefijo del tenant en los redirects.
    
    Cuando se usa path-based tenants (/demo/, /sgdental/, etc.),
    esta vista asegura que después del login el usuario sea redirigido
    a la URL correcta que incluye el prefijo del tenant.
    """
    template_name = 'core/login.html'  # Usar el template existente
    
    def get_success_url(self):
        """
        Sobrescribir para incluir el prefijo del tenant en la URL de éxito.
        """
        # Obtener la URL de éxito por defecto (settings.LOGIN_REDIRECT_URL)
        url = super().get_success_url()
        
        # Intentar obtener el prefijo del tenant desde diferentes fuentes
        tenant_prefix = None
        
        # 1. Desde el atributo tenant_prefix si existe
        if hasattr(self.request, 'tenant_prefix'):
            tenant_prefix = self.request.tenant_prefix
        
        # 2. Desde el HTTP_REFERER (URL de donde vino el request)
        elif 'HTTP_REFERER' in self.request.META:
            referer = self.request.META['HTTP_REFERER']
            # Extraer el path del referer: http://example.com/demo/accounts/login/ -> /demo/accounts/login/
            from urllib.parse import urlparse
            referer_path = urlparse(referer).path
            if referer_path.startswith('/'):
                parts = referer_path.split('/')
                if len(parts) > 2 and parts[1] and parts[1] != 'accounts':
                    tenant_prefix = f"/{parts[1]}"
        
        # 3. Desde el tenant actual si existe
        elif hasattr(self.request, 'tenant') and self.request.tenant:
            tenant_prefix = f"/{self.request.tenant.schema_name}"
        
        # Aplicar el prefijo si se encontró
        if tenant_prefix and not url.startswith(tenant_prefix):
            url = f"{tenant_prefix}{url}"
        
        return url
    
    def get_context_data(self, **kwargs):
        """Agregar información del tenant al contexto"""
        context = super().get_context_data(**kwargs)
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            context['tenant'] = self.request.tenant
            context['tenant_nombre'] = self.request.tenant.nombre
        
        return context
