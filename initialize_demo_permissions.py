#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append('.')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Clinica
from django.contrib.auth.models import User, Group
from core.models import ModuloSistema, SubmenuItem, PermisoRol

def initialize_demo_permissions():
    """Inicializar sistema de permisos y submenús en el tenant demo."""
    
    print("=== INICIALIZANDO SISTEMA DE PERMISOS EN TENANT DEMO ===")
    
    try:
        # Obtener el tenant demo
        demo_tenant = Clinica.objects.get(schema_name='demo')
        print(f"✅ Tenant demo encontrado: {demo_tenant.nombre}")
        
        # Conectar al tenant demo
        with tenant_context(demo_tenant):
            from django.db import connection
            print(f"📍 Conectado al schema: {connection.schema_name}")
            
            # 1. Crear módulos del sistema
            print("\n1. Creando módulos del sistema...")
            modulos_data = [
                {'nombre': 'Dashboard', 'icono': 'fas fa-tachometer-alt', 'orden': 1, 'activo': True},
                {'nombre': 'Pacientes', 'icono': 'fas fa-users', 'orden': 2, 'activo': True},
                {'nombre': 'Citas', 'icono': 'fas fa-calendar-alt', 'orden': 3, 'activo': True},
                {'nombre': 'Servicios', 'icono': 'fas fa-tooth', 'orden': 4, 'activo': True},
                {'nombre': 'Inventario', 'icono': 'fas fa-boxes', 'orden': 5, 'activo': True},
                {'nombre': 'Finanzas', 'icono': 'fas fa-money-bill', 'orden': 6, 'activo': True},
                {'nombre': 'Reportes', 'icono': 'fas fa-chart-bar', 'orden': 7, 'activo': True},
                {'nombre': 'Administración', 'icono': 'fas fa-cogs', 'orden': 8, 'activo': True},
            ]
            
            modulos = {}
            for modulo_data in modulos_data:
                modulo, created = ModuloSistema.objects.get_or_create(
                    nombre=modulo_data['nombre'],
                    defaults=modulo_data
                )
                modulos[modulo.nombre] = modulo
                print(f"  {'✅' if created else '⚠️'} Módulo '{modulo.nombre}' {'creado' if created else 'ya existe'}")
            
            # 2. Crear submenús
            print("\n2. Creando submenús...")
            submenus_data = [
                # Dashboard
                {'modulo': 'Dashboard', 'nombre': 'Panel Principal', 'url': 'core:dashboard', 'orden': 1},
                
                # Pacientes
                {'modulo': 'Pacientes', 'nombre': 'Lista de Pacientes', 'url': 'core:paciente_list', 'orden': 1},
                {'modulo': 'Pacientes', 'nombre': 'Agregar Paciente', 'url': 'core:paciente_create', 'orden': 2},
                {'modulo': 'Pacientes', 'nombre': 'Saldos Pendientes', 'url': 'core:saldos_pendientes', 'orden': 3},
                
                # Citas
                {'modulo': 'Citas', 'nombre': 'Agenda', 'url': 'core:agenda', 'orden': 1},
                {'modulo': 'Citas', 'nombre': 'Lista de Citas', 'url': 'core:cita_list', 'orden': 2},
                {'modulo': 'Citas', 'nombre': 'Citas Pendientes', 'url': 'core:citas_pendientes_pago', 'orden': 3},
                
                # Servicios
                {'modulo': 'Servicios', 'nombre': 'Lista de Servicios', 'url': 'core:service_list', 'orden': 1},
                {'modulo': 'Servicios', 'nombre': 'Agregar Servicio', 'url': 'core:service_create', 'orden': 2},
                {'modulo': 'Servicios', 'nombre': 'Especialidades', 'url': 'core:especialidad_list', 'orden': 3},
                
                # Inventario
                {'modulo': 'Inventario', 'nombre': 'Insumos', 'url': 'core:insumo_list', 'orden': 1},
                {'modulo': 'Inventario', 'nombre': 'Proveedores', 'url': 'core:proveedor_list', 'orden': 2},
                {'modulo': 'Inventario', 'nombre': 'Compras', 'url': 'core:compra_list', 'orden': 3},
                
                # Finanzas
                {'modulo': 'Finanzas', 'nombre': 'Pagos', 'url': 'core:pago_list', 'orden': 1},
                {'modulo': 'Finanzas', 'nombre': 'Registrar Pago', 'url': 'core:pago_create', 'orden': 2},
                
                # Reportes
                {'modulo': 'Reportes', 'nombre': 'Ingresos', 'url': 'core:reporte_ingresos', 'orden': 1},
                {'modulo': 'Reportes', 'nombre': 'Saldos', 'url': 'core:reporte_saldos', 'orden': 2},
                {'modulo': 'Reportes', 'nombre': 'Facturación', 'url': 'core:reporte_facturacion', 'orden': 3},
                
                # Administración
                {'modulo': 'Administración', 'nombre': 'Usuarios', 'url': 'core:usuario_list', 'orden': 1},
                {'modulo': 'Administración', 'nombre': 'Permisos', 'url': 'core:admin_permisos', 'orden': 2},
            ]
            
            for submenu_data in submenus_data:
                modulo = modulos.get(submenu_data['modulo'])
                if modulo:
                    submenu, created = SubmenuItem.objects.get_or_create(
                        modulo=modulo,
                        nombre=submenu_data['nombre'],
                        defaults={
                            'url_name': submenu_data['url'],
                            'orden': submenu_data['orden'],
                            'activo': True
                        }
                    )
                    print(f"  {'✅' if created else '⚠️'} Submenú '{submenu.nombre}' {'creado' if created else 'ya existe'}")
            
            # 3. Configurar permisos por rol
            print("\n3. Configurando permisos por rol...")
            
            # Obtener grupos
            admin_group = Group.objects.get(name='Administrador')
            dentista_group = Group.objects.get(name='Dentista')
            recepcionista_group = Group.objects.get(name='Recepcionista')
            
            # Permisos para Administrador (acceso completo)
            for modulo in modulos.values():
                for submenu in modulo.submenus.all():
                    permiso, created = PermisoRol.objects.get_or_create(
                        rol=admin_group,
                        submenu_item=submenu,
                        defaults={'nivel_acceso': 'completo'}
                    )
            print("  ✅ Permisos de Administrador configurados (acceso completo)")
            
            # Permisos para Dentista (acceso limitado)
            permisos_dentista = ['Dashboard', 'Pacientes', 'Citas', 'Servicios', 'Reportes']
            for modulo_nombre in permisos_dentista:
                modulo = modulos.get(modulo_nombre)
                if modulo:
                    for submenu in modulo.submenus.all():
                        permiso, created = PermisoRol.objects.get_or_create(
                            rol=dentista_group,
                            submenu_item=submenu,
                            defaults={'nivel_acceso': 'escritura'}
                        )
            print("  ✅ Permisos de Dentista configurados (acceso limitado)")
            
            # Permisos para Recepcionista (acceso básico)
            permisos_recepcionista = ['Dashboard', 'Pacientes', 'Citas']
            for modulo_nombre in permisos_recepcionista:
                modulo = modulos.get(modulo_nombre)
                if modulo:
                    for submenu in modulo.submenus.all():
                        permiso, created = PermisoRol.objects.get_or_create(
                            rol=recepcionista_group,
                            submenu_item=submenu,
                            defaults={'nivel_acceso': 'lectura'}
                        )
            print("  ✅ Permisos de Recepcionista configurados (acceso básico)")
            
            print("\n=== SISTEMA DE PERMISOS INICIALIZADO EXITOSAMENTE ===")
            print("Resumen:")
            print(f"  📁 Módulos creados: {len(modulos)}")
            print(f"  📄 Submenús creados: {SubmenuItem.objects.count()}")
            print(f"  🔐 Permisos configurados: {PermisoRol.objects.count()}")
            print("\n¡Los submenús ya deberían aparecer en la navbar!")
                    
    except Clinica.DoesNotExist:
        print("❌ Tenant demo no encontrado")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    initialize_demo_permissions()
