from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Clinica, Domain

@admin.register(Clinica)
class ClinicaAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('nombre', 'creado_en')
    # Añadir 'logo' al fieldset para que aparezca en el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('nombre', 'logo', 'documento_consentimiento', 'schema_name')
        }),
    )

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant')