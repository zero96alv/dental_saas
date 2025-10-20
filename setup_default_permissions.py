#!/usr/bin/env python
"""
Script para configurar permisos por defecto en el tenant demo.
Versión definitiva que funciona con los modelos finales.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth.models import Group
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from core.models_permissions import ModuloSistema, SubmenuItem, PermisoRol

def configurar_permisos_por_defecto():
    """Configura los permisos por defecto para todos los roles en el tenant demo."""
    
    # Obtener el tenant demo
    try:
        clinica_demo = Clinica.objects.get(schema_name='demo')
        print(f"✅ Tenant demo encontrado: {clinica_demo.nombre}")
    except Clinica.DoesNotExist:
        print("❌ Error: No se encontró el tenant 'demo'")
        return False
    
    with tenant_context(clinica_demo):
        print("🔄 Configurando permisos por defecto...")
        
        # Verificar que existen los módulos y submenús
        modulos_count = ModuloSistema.objects.count()
        submenus_count = SubmenuItem.objects.count()
        print(f"📊 Módulos disponibles: {modulos_count}")
        print(f"📊 Submenús disponibles: {submenus_count}")
        
        if modulos_count == 0:
            print("⚠️  No hay módulos definidos. Ejecuta primero la inicialización de módulos.")
            return False
        
        # Obtener o crear grupos
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        dentista_group, _ = Group.objects.get_or_create(name='Dentista')
        recepcionista_group, _ = Group.objects.get_or_create(name='Recepcionista')
        
        print(f"👥 Grupos configurados: {Group.objects.count()}")
        
        # Configurar permisos para ADMINISTRADOR (acceso completo a todo)
        print("🔧 Configurando permisos para Administrador...")
        admin_count = 0
        for submenu in SubmenuItem.objects.all():
            permiso, created = PermisoRol.objects.get_or_create(
                rol=admin_group,
                submenu_item=submenu,
                defaults={
                    'nivel_acceso': 'completo',
                    'puede_ver': True,
                    'puede_crear': True,
                    'puede_editar': True,
                    'puede_eliminar': True,
                    'puede_exportar': True,
                    'solo_propios_registros': False
                }
            )
            if created:
                admin_count += 1
        print(f"✅ Permisos configurados para Administrador: {admin_count} nuevos")
        
        # Configurar permisos para DENTISTA
        print("🔧 Configurando permisos para Dentista...")
        dentista_modules = ['Pacientes', 'Agenda', 'Historial Clínico', 'Dashboard']
        dentista_count = 0
        
        for submenu in SubmenuItem.objects.filter(modulo__nombre__in=dentista_modules):
            # Permisos específicos según el tipo de submenu
            if 'Lista' in submenu.nombre or 'Ver' in submenu.nombre:
                nivel = 'lectura'
            elif submenu.modulo.nombre == 'Historial Clínico':
                nivel = 'escritura'  # Puede agregar notas clínicas
            elif 'Eliminar' in submenu.nombre:
                nivel = 'lectura'  # No puede eliminar
            else:
                nivel = 'escritura'
            
            permiso, created = PermisoRol.objects.get_or_create(
                rol=dentista_group,
                submenu_item=submenu,
                defaults={
                    'nivel_acceso': nivel,
                    'solo_propios_registros': submenu.modulo.nombre == 'Agenda'  # Solo sus citas
                }
            )
            if created:
                dentista_count += 1
        print(f"✅ Permisos configurados para Dentista: {dentista_count} nuevos")
        
        # Configurar permisos para RECEPCIONISTA
        print("🔧 Configurando permisos para Recepcionista...")
        recepcionista_modules = ['Pacientes', 'Agenda', 'Pagos', 'Dashboard']
        recepcionista_count = 0
        
        for submenu in SubmenuItem.objects.filter(modulo__nombre__in=recepcionista_modules):
            # Sin acceso a eliminar, pero sí crear y editar
            if 'Eliminar' in submenu.nombre:
                continue  # Sin permisos de eliminación
            
            nivel = 'escritura' if submenu.modulo.nombre in ['Pacientes', 'Agenda', 'Pagos'] else 'lectura'
            
            permiso, created = PermisoRol.objects.get_or_create(
                rol=recepcionista_group,
                submenu_item=submenu,
                defaults={
                    'nivel_acceso': nivel,
                    'solo_propios_registros': False
                }
            )
            if created:
                recepcionista_count += 1
        print(f"✅ Permisos configurados para Recepcionista: {recepcionista_count} nuevos")
        
        # Resumen final
        total_permisos = PermisoRol.objects.count()
        print(f"\n📊 RESUMEN:")
        print(f"   • Total permisos configurados: {total_permisos}")
        print(f"   • Administrador: acceso completo a {SubmenuItem.objects.count()} submenús")
        print(f"   • Dentista: acceso a {PermisoRol.objects.filter(rol=dentista_group).count()} submenús")
        print(f"   • Recepcionista: acceso a {PermisoRol.objects.filter(rol=recepcionista_group).count()} submenús")
        
        return True

if __name__ == '__main__':
    print("🚀 Iniciando configuración de permisos por defecto...")
    success = configurar_permisos_por_defecto()
    
    if success:
        print("\n✅ ¡Configuración de permisos completada exitosamente!")
        print("💡 Ahora puedes probar el sistema de permisos con diferentes roles.")
    else:
        print("\n❌ Error durante la configuración de permisos.")
        sys.exit(1)
