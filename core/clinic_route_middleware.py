from django.conf import settings
from django.http import Http404
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model

class ClinicRouteMiddleware(TenantMainMiddleware):
    """
    Middleware que permite acceso a tenants mediante rutas:
    
    /sgdental/ → tenant "sgdental"
    /cgdental/ → tenant "cgdental"  
    /demo/     → tenant "demo"
    /          → página de landing o tenant por defecto
    """
    
    def get_tenant(self, domain_model, hostname):
        request = getattr(self, 'current_request', None)
        
        if request:
            # PRIORIDAD 1: Parámetro ?tenant= (override todo)
            tenant_param = request.GET.get('tenant')
            if tenant_param:
                try:
                    tenant = self._get_tenant_by_schema(tenant_param)
                    print(f"🎯 Tenant por parámetro: {tenant.schema_name}")
                    return tenant
                except Http404:
                    print(f"❌ Tenant '{tenant_param}' no encontrado")
            
            # PRIORIDAD 2: Ruta de clínica (/sgdental/, /demo/)
            clinic_slug = self._extract_clinic_from_path(request.path)
            if clinic_slug:
                try:
                    tenant = self._get_tenant_by_schema(clinic_slug)
                    print(f"🏥 Tenant por ruta '{clinic_slug}': {tenant.schema_name}")
                    return tenant
                except Http404:
                    print(f"❌ Clínica '{clinic_slug}' no encontrada")
        
        # PRIORIDAD 3: Domain table lookup (estándar)
        try:
            tenant = super().get_tenant(domain_model, hostname)
            print(f"📋 Tenant por dominio: {tenant.schema_name}")
            return tenant
        except Http404:
            print(f"❌ Dominio '{hostname}' no encontrado en tabla")
        
        # PRIORIDAD 4: Tenant por defecto para landing
        default_schema = getattr(settings, 'DEFAULT_TENANT_SCHEMA', 'public')
        try:
            tenant = self._get_tenant_by_schema(default_schema)
            print(f"🏠 Tenant por defecto: {tenant.schema_name}")
            return tenant
        except Http404:
            raise Http404(f"No se pudo determinar tenant para '{hostname}'")
    
    def _extract_clinic_from_path(self, path):
        """
        Extrae slug de clínica de la URL.
        
        Ejemplos:
        /sgdental/ → "sgdental"
        /cgdental/dashboard/ → "cgdental"
        /demo/pacientes/ → "demo"
        / → None
        /admin/ → None (excluido)
        /static/ → None (excluido)
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
        
        Criterios:
        - Solo letras, números, guiones
        - Longitud entre 3-20 caracteres
        - No empezar/terminar con guión
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