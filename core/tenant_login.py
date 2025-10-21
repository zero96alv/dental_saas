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
        
        # Obtener el prefijo del tenant desde el path actual
        current_path = self.request.path
        if current_path.startswith('/'):
            parts = current_path.split('/')
            if len(parts) > 1 and parts[1]:  # Ej: ['', 'demo', 'accounts', 'login', '']
                tenant_slug = parts[1]
                # Verificar que no sea 'accounts' (para evitar falsos positivos)
                if tenant_slug != 'accounts':
                    tenant_prefix = f"/{tenant_slug}"
                    # Asegurarse de que la URL empiece con el prefijo
                    if not url.startswith(tenant_prefix):
                        url = f"{tenant_prefix}{url}"
        
        return url
    
    def get_context_data(self, **kwargs):
        """Agregar información del tenant al contexto"""
        context = super().get_context_data(**kwargs)
        
        if hasattr(self.request, 'tenant') and self.request.tenant:
            context['tenant'] = self.request.tenant
            context['tenant_nombre'] = self.request.tenant.nombre
        
        return context
