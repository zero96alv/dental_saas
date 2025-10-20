from django.conf import settings
from django.http import Http404
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

class TenantByParamMiddleware(TenantMainMiddleware):
    """
    Middleware que permite seleccionar tenant por parámetro GET
    Ejemplos:
    - http://192.168.100.4:8000/?tenant=demo
    - http://192.168.100.4:8000/agenda/?tenant=dev  
    """
    
    def get_tenant(self, domain_model, hostname):
        # Si hay parámetro tenant en la URL, usarlo
        request = getattr(self, 'current_request', None)
        if request and 'tenant' in request.GET:
            tenant_param = request.GET['tenant']
            return self._get_tenant_by_schema(tenant_param)
        
        # Si no hay parámetro, usar comportamiento normal o tenant por defecto
        try:
            return super().get_tenant(domain_model, hostname)
        except Http404:
            # Si no encuentra tenant por hostname, usar tenant por defecto
            if settings.DEBUG:
                return self._get_tenant_by_schema(getattr(settings, 'DEFAULT_TENANT_SCHEMA', 'dev'))
            raise
    
    def _get_tenant_by_schema(self, schema_name):
        """Obtiene tenant por schema_name"""
        tenant_model = get_tenant_model()
        try:
            return tenant_model.objects.get(schema_name=schema_name)
        except tenant_model.DoesNotExist:
            raise Http404(f"Tenant '{schema_name}' no encontrado")
    
    def __call__(self, request):
        # Guardar request para acceso en get_tenant
        self.current_request = request
        return super().__call__(request)