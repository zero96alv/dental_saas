"""
Middleware personalizado para enrutamiento de tenants por PATH
En vez de subdominios (demo.example.com), usa paths (/demo/)
"""
from django.conf import settings
from django.http import Http404
from django.db import connection
from tenants.models import Clinica


class PathBasedTenantMiddleware:
    """
    Middleware que identifica el tenant desde la URL path
    Ejemplo: /demo/ -> tenant 'demo'
             /sgdental/ -> tenant 'sgdental'
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Lista de paths que NO son tenants (solo esquema público)
        self.excluded_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/setup/',
            '/simple-setup/',
            '/api/',
            '/__debug__/',
        ]
    
    def __call__(self, request):
        # Obtener el path
        path = request.path_info
        
        # Verificar si es un path excluido (admin, static, etc.)
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            # Usar esquema público para estos paths
            connection.set_schema_to_public()
            response = self.get_response(request)
            return response
        
        # Extraer el tenant del path
        # Formato esperado: /tenant_name/resto/del/path
        path_parts = [p for p in path.split('/') if p]
        
        if len(path_parts) > 0:
            tenant_slug = path_parts[0]
            
            # Primero asegurarse de estar en esquema público para buscar
            connection.set_schema_to_public()
            
            try:
                # Buscar el tenant
                tenant = Clinica.objects.get(schema_name=tenant_slug)
                
                # Establecer el tenant
                connection.set_tenant(tenant)
                
                # Guardar el tenant y el prefijo en el request para uso posterior
                request.tenant = tenant
                request.tenant_prefix = f'/{tenant_slug}'
                
                # Ajustar el path para que Django resuelva correctamente las URLs
                # /demo/pacientes/ -> /pacientes/
                # /demo/accounts/login/ -> /accounts/login/
                request.path_info = '/' + '/'.join(path_parts[1:])
                if request.path_info != '/' and not request.path_info.endswith('/'):
                    request.path_info += '/'
                if request.path_info == '':
                    request.path_info = '/'
                    
            except Clinica.DoesNotExist:
                # Si no existe el tenant, usar esquema público
                connection.set_schema_to_public()
                request.tenant = None
        else:
            # Path raíz (/), usar esquema público
            connection.set_schema_to_public()
            request.tenant = None
        
        response = self.get_response(request)
        return response
