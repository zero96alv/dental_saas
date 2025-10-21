#!/usr/bin/env python
"""
Script para inicializar módulos del sistema y permisos en un tenant específico.
Uso: python manage.py shell < scripts/setup_tenant_modules.py
"""

from django.db import connection
from tenants.models import Clinica
from core.permissions_utils import inicializar_permisos_por_defecto

def setup_tenant_modules(schema_name='demo'):
    """
    Inicializa módulos y permisos para un tenant específico
    """
    print(f"\n{'='*60}")
    print(f"INICIALIZANDO MÓDULOS Y PERMISOS PARA TENANT: {schema_name}")
    print(f"{'='*60}\n")
    
    # Cambiar al tenant
    try:
        tenant = Clinica.objects.get(schema_name=schema_name)
        connection.set_tenant(tenant)
        print(f"✓ Conectado al tenant: {tenant.nombre}")
    except Clinica.DoesNotExist:
        print(f"✗ ERROR: No existe el tenant con schema_name='{schema_name}'")
        return
    
    # Inicializar permisos y módulos
    try:
        print(f"\n➤ Inicializando módulos del sistema...")
        inicializar_permisos_por_defecto()
        print(f"✓ Módulos y permisos inicializados correctamente")
    except Exception as e:
        print(f"✗ ERROR al inicializar: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Verificar resultados
    from core.models import ModuloSistema, SubmenuItem, PermisoRol
    from django.contrib.auth.models import Group
    
    num_modulos = ModuloSistema.objects.filter(activo=True).count()
    num_submenus = SubmenuItem.objects.filter(activo=True).count()
    num_permisos = PermisoRol.objects.count()
    num_grupos = Group.objects.count()
    
    print(f"\n{'='*60}")
    print(f"RESUMEN DE INICIALIZACIÓN")
    print(f"{'='*60}")
    print(f"  Módulos activos:    {num_modulos}")
    print(f"  Submenús activos:   {num_submenus}")
    print(f"  Permisos creados:   {num_permisos}")
    print(f"  Grupos existentes:  {num_grupos}")
    
    # Listar grupos
    print(f"\nGrupos disponibles:")
    for grupo in Group.objects.all():
        permisos_count = PermisoRol.objects.filter(rol=grupo).count()
        print(f"  - {grupo.name}: {permisos_count} permisos asignados")
    
    # Listar módulos
    print(f"\nMódulos creados:")
    for modulo in ModuloSistema.objects.filter(activo=True).order_by('orden'):
        submenus_count = modulo.submenus.filter(activo=True).count()
        print(f"  {modulo.orden}. {modulo.nombre} ({submenus_count} submenús)")
    
    print(f"\n{'='*60}")
    print(f"✓ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
    print(f"{'='*60}\n")

# Ejecutar
if __name__ == '__main__':
    setup_tenant_modules('demo')
else:
    # Si se ejecuta desde shell interactivo
    setup_tenant_modules('demo')
