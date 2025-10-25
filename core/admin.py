from django.contrib import admin
from .models import (
    Paciente, Servicio, PerfilDentista, Especialidad, Pago, Proveedor,
    Insumo, Compra, DetalleCompra, LoteInsumo, Cita, Diagnostico,
    HistorialClinico, EstadoDiente, UnidadDental, DatosFiscales,
    PreguntaHistorial, RespuestaHistorial, TipoTrabajoLaboratorio, TrabajoLaboratorio
)
from .models_permissions import ModuloSistema, SubmenuItem, PermisoRol, LogAcceso

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

# --- Administración de Permisos Dinámicos ---

class SubmenuItemInline(admin.TabularInline):
    model = SubmenuItem
    extra = 1
    fields = ('nombre', 'url_name', 'orden', 'activo', 'requiere_crear', 'requiere_editar', 'requiere_eliminar')

@admin.register(ModuloSistema)
class ModuloSistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden', 'activo', 'icono')
    list_editable = ('orden', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    inlines = [SubmenuItemInline]
    ordering = ('orden', 'nombre')

@admin.register(SubmenuItem)
class SubmenuItemAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modulo', 'url_name', 'orden', 'activo')
    list_editable = ('orden', 'activo')
    list_filter = ('modulo', 'activo', 'requiere_crear', 'requiere_editar', 'requiere_eliminar')
    search_fields = ('nombre', 'url_name', 'descripcion')
    ordering = ('modulo__orden', 'orden', 'nombre')

@admin.register(PermisoRol)
class PermisoRolAdmin(admin.ModelAdmin):
    list_display = ('rol', 'submenu_item', 'nivel_acceso', 'puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar')
    list_filter = ('rol', 'nivel_acceso', 'submenu_item__modulo', 'puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar')
    search_fields = ('rol__name', 'submenu_item__nombre')
    ordering = ('rol__name', 'submenu_item__modulo__orden', 'submenu_item__orden')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rol', 'submenu_item__modulo')

@admin.register(LogAcceso)
class LogAccesoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'submenu_item', 'fecha_acceso', 'ip_address')
    list_filter = ('fecha_acceso', 'submenu_item__modulo')
    search_fields = ('usuario__username', 'submenu_item__nombre', 'ip_address')
    readonly_fields = ('usuario', 'submenu_item', 'fecha_acceso', 'ip_address', 'user_agent')
    ordering = ('-fecha_acceso',)
    
    def has_add_permission(self, request):
        return False  # No permitir agregar logs manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # No permitir editar logs

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

# Modelos de Laboratorio Dental
@admin.register(TipoTrabajoLaboratorio)
class TipoTrabajoLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo_referencia', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)

@admin.register(TrabajoLaboratorio)
class TrabajoLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('tipo_trabajo', 'paciente', 'laboratorio', 'estado', 'fecha_solicitud', 'fecha_entrega_estimada', 'esta_retrasado')
    list_filter = ('estado', 'fecha_solicitud', 'laboratorio', 'tipo_trabajo')
    search_fields = ('paciente__nombre', 'paciente__apellido', 'dientes', 'observaciones')
    readonly_fields = ('fecha_solicitud', 'dias_transcurridos', 'margen', 'esta_retrasado')
    date_hierarchy = 'fecha_solicitud'

    fieldsets = (
        ('Información General', {
            'fields': ('paciente', 'cita_origen', 'tipo_trabajo', 'laboratorio', 'dentista_solicitante')
        }),
        ('Detalles del Trabajo', {
            'fields': ('dientes', 'material', 'color', 'observaciones')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_entrega_estimada', 'fecha_entrega_real', 'dias_transcurridos')
        }),
        ('Estado y Costos', {
            'fields': ('estado', 'costo_laboratorio', 'precio_paciente', 'margen', 'esta_retrasado')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
    )
