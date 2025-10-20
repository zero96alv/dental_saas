# In dental_saas/urls_public.py
# These are the URL patterns for the public schema
from django.contrib import admin
from django.urls import path
from tenants.views import tenant_check_view
from core.setup_views import setup_tenants_migrations
from core.simple_setup import simple_setup
from core.tenant_switch import tenant_switch_view, switch_to_tenant

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', tenant_check_view, name='tenant_check'),
    path('setup-tenants/', setup_tenants_migrations, name='setup_tenants'),
    path('simple-setup/', simple_setup, name='simple_setup'),
    path('tenants/', tenant_switch_view, name='tenant_switch'),
    path('switch/<str:tenant_schema>/', switch_to_tenant, name='switch_tenant'),
]
