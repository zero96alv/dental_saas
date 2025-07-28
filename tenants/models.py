from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Clinica(TenantMixin):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos_clinicas/', blank=True, null=True)
    documento_consentimiento = models.FileField(upload_to='consentimientos/', blank=True, null=True, help_text="PDF con el aviso de privacidad y consentimiento de COFEPRIS.")
    creado_en = models.DateTimeField(auto_now_add=True)

    # auto_create_schema se activa automáticamente para crear 
    # el esquema de la base de datos para cada nueva clínica.
    auto_create_schema = True

    def __str__(self):
        return self.nombre

class Domain(DomainMixin):
    pass