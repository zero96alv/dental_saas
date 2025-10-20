# core/models_permissions.py
"""
Sistema de permisos dinámicos y granulares para el sistema dental SaaS.
Versión definitiva con campos timestamp.
"""

from django.db import models
from django.contrib.auth.models import Group

class ModuloSistema(models.Model):
    """
    Define los módulos principales del sistema.
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase CSS del ícono (ej: fas fa-users)")
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición en el menú")
    activo = models.BooleanField(default=True)
    url_pattern = models.CharField(max_length=200, blank=True, help_text="Patrón de URL para acceso directo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_modulosistema'
        ordering = ['orden', 'nombre']
        verbose_name = "Módulo del Sistema"
        verbose_name_plural = "Módulos del Sistema"
        
    def __str__(self):
        return self.nombre

class SubmenuItem(models.Model):
    """
    Define los elementos del submenú dentro de cada módulo.
    """
    modulo = models.ForeignKey(ModuloSistema, on_delete=models.CASCADE, related_name='submenus')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    url_name = models.CharField(max_length=100, help_text="Nombre de la URL de Django (ej: core:paciente_list)")
    url_pattern = models.CharField(max_length=200, blank=True, help_text="Patrón de URL (ej: /pacientes/)")
    icono = models.CharField(max_length=50, blank=True, help_text="Clase CSS del ícono")
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    
    # Permisos granulares para este submenu
    requiere_crear = models.BooleanField(default=False, help_text="¿Requiere permiso de creación?")
    requiere_editar = models.BooleanField(default=False, help_text="¿Requiere permiso de edición?")
    requiere_eliminar = models.BooleanField(default=False, help_text="¿Requiere permiso de eliminación?")
    requiere_ver = models.BooleanField(default=True, help_text="¿Requiere permiso de visualización?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_submenuitem'
        ordering = ['modulo', 'orden', 'nombre']
        unique_together = ('modulo', 'nombre')
        verbose_name = "Elemento de Submenú"
        verbose_name_plural = "Elementos de Submenú"
        
    def __str__(self):
        return f"{self.modulo.nombre} - {self.nombre}"

class PermisoRol(models.Model):
    """
    Define qué permisos tiene cada rol (grupo) sobre cada elemento del submenú.
    """
    NIVEL_ACCESO = [
        ('lectura', 'Solo Lectura'),
        ('escritura', 'Lectura y Escritura'),
        ('completo', 'Acceso Completo'),
    ]
    
    rol = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='permisos_dinamicos')
    submenu_item = models.ForeignKey(SubmenuItem, on_delete=models.CASCADE, related_name='permisos')
    nivel_acceso = models.CharField(max_length=20, choices=NIVEL_ACCESO, default='lectura')
    
    # Permisos específicos (opcional, para casos especiales)
    puede_ver = models.BooleanField(default=False)
    puede_crear = models.BooleanField(default=False)
    puede_editar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)
    puede_exportar = models.BooleanField(default=False)
    
    # Condiciones adicionales
    solo_propios_registros = models.BooleanField(default=False, help_text="¿Solo puede ver sus propios registros?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_permisorol'
        unique_together = ('rol', 'submenu_item')
        verbose_name = "Permiso de Rol"
        verbose_name_plural = "Permisos de Roles"
        
    def __str__(self):
        return f"{self.rol.name} - {self.submenu_item} ({self.get_nivel_acceso_display()})"
    
    def save(self, *args, **kwargs):
        """
        Auto-asigna permisos específicos basados en el nivel de acceso.
        """
        if self.nivel_acceso == 'lectura':
            self.puede_ver = True
            self.puede_crear = False
            self.puede_editar = False
            self.puede_eliminar = False
        elif self.nivel_acceso == 'escritura':
            self.puede_ver = True
            self.puede_crear = True
            self.puede_editar = True
            self.puede_eliminar = False
        elif self.nivel_acceso == 'completo':
            self.puede_ver = True
            self.puede_crear = True
            self.puede_editar = True
            self.puede_eliminar = True
        
        super().save(*args, **kwargs)

class LogAcceso(models.Model):
    """
    Registro de accesos a los módulos para auditoría.
    """
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    submenu_item = models.ForeignKey(SubmenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    modulo_accedido = models.CharField(max_length=100, blank=True)
    accion_realizada = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    user_agent = models.TextField(blank=True)
    detalles = models.TextField(blank=True)
    fecha_acceso = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_logacceso'
        ordering = ['-fecha_acceso']
        verbose_name = "Log de Acceso"
        verbose_name_plural = "Logs de Acceso"
        
    def __str__(self):
        return f"{self.usuario.username if self.usuario else 'Anónimo'} - {self.modulo_accedido} - {self.fecha_acceso}"
