# In dental_saas/urls_public.py
# These are the URL patterns for the public schema
from django.contrib import admin
from django.urls import path
from tenants.views import tenant_check_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', tenant_check_view, name='tenant_check'),
]
