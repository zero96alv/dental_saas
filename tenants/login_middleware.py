from django.conf import settings

class TenantLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Si hay tenant, ajustar LOGIN_URL con el prefijo
        if hasattr(request, 'tenant_prefix'):
            settings.LOGIN_URL = f"{request.tenant_prefix}/accounts/login/"
        else:
            settings.LOGIN_URL = '/accounts/login/'
        
        response = self.get_response(request)
        return response
