# In dental_saas/urls_public.py
# These are the URL patterns for the public schema
from django.contrib import admin
from django.urls import path
from tenants.views import tenant_check_view
from core.setup_views import setup_tenants_migrations
from core.simple_setup import simple_setup
from core.setup_domains import setup_domains
from core.tenant_switch import tenant_switch_view, switch_to_tenant
from core.debug_views import tenant_debug, user_debug, force_tenant_switch
from core.landing_views import landing_page, clinic_not_found

urlpatterns = [
    # Landing page (página principal)
    path('', landing_page, name='landing_page'),
    
    # Admin y setup
    path('admin/', admin.site.urls),
    path('check/', tenant_check_view, name='tenant_check'),
    path('setup-tenants/', setup_tenants_migrations, name='setup_tenants'),
    path('simple-setup/', simple_setup, name='simple_setup'),
    path('setup-domains/', setup_domains, name='setup_domains'),
    
    # Herramientas de tenants
    path('tenants/', tenant_switch_view, name='tenant_switch'),
    path('switch/<str:tenant_schema>/', switch_to_tenant, name='switch_tenant'),
    
    # Debug views
    path('debug/tenant/', tenant_debug, name='tenant_debug'),
    path('debug/user/', user_debug, name='user_debug'),
    path('debug/force-tenant/', force_tenant_switch, name='force_tenant_switch'),
]
