"""
URL configuration for dental_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from core.auth_views import CustomLogoutView, CustomLoginView
from core.debug_views import tenant_debug, user_debug, force_tenant_switch

urlpatterns = [
    # URLs de Autenticación
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    # Usar nuestra vista de logout personalizada
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Debug views (también en tenant para pruebas)
    path('debug/tenant/', tenant_debug, name='tenant_debug_tenant'),
    path('debug/user/', user_debug, name='user_debug_tenant'),
    path('debug/force-tenant/', force_tenant_switch, name='force_tenant_switch_tenant'),
    
    # URLs de la aplicación core (incluye la raíz) - DEBE IR ANTES del admin
    path('', include('core.urls', namespace='core')),
    
    # URLs del admin de Django - DEBE IR DESPUÉS para evitar conflictos
    path('admin/', admin.site.urls),
]

# Servir archivos estáticos y multimedia en dev/local sin depender de DEBUG
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()  # Sirve archivos desde STATICFILES_DIRS y app/static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
