from django.contrib import admin
from .models import (
    Paciente, Servicio, PerfilDentista, Especialidad, Pago, Proveedor, 
    Insumo, Compra, DetalleCompra, LoteInsumo, Cita, Diagnostico, 
    HistorialClinico, EstadoDiente, UnidadDental, DatosFiscales,
    PreguntaHistorial, RespuestaHistorial
)

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    inlines = [DetalleCompraInline]
    list_display = ('proveedor', 'fecha_compra', 'estado', 'total')
    list_filter = ('estado', 'fecha_compra')

@admin.register(PreguntaHistorial)
class PreguntaHistorialAdmin(admin.ModelAdmin):
    list_display = ('texto', 'tipo', 'orden', 'activa')
    list_editable = ('orden', 'activa')

@admin.register(RespuestaHistorial)
class RespuestaHistorialAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'pregunta', 'respuesta')
    list_filter = ('paciente', 'pregunta')

# Registrar otros modelos para que aparezcan en el admin
admin.site.register(Paciente)
admin.site.register(Servicio)
admin.site.register(PerfilDentista)
admin.site.register(Especialidad)
admin.site.register(Pago)
admin.site.register(Proveedor)
admin.site.register(Insumo)
admin.site.register(LoteInsumo)
admin.site.register(Cita)
admin.site.register(Diagnostico)
admin.site.register(HistorialClinico)
admin.site.register(EstadoDiente)
admin.site.register(UnidadDental)
admin.site.register(DatosFiscales)