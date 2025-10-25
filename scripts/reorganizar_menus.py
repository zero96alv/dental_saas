#!/usr/bin/env python
"""
Script para reorganizar la estructura de menús del sistema
Agrega el módulo de Laboratorio Dental y reorganiza los existentes
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.db import connection, transaction
from tenants.models import Clinica
from core.models_permissions import ModuloSistema, SubmenuItem, PermisoRol
from django.contrib.auth.models import Group

def reorganizar_menus(schema_name='dev'):
    """Reorganiza los menús del sistema"""

    tenant = Clinica.objects.get(schema_name=schema_name)
    connection.set_tenant(tenant)

    print(f"=== REORGANIZANDO MENÚS PARA: {tenant.nombre} ===\n")

    with transaction.atomic():
        # --- NUEVA ESTRUCTURA DE MÓDULOS ---

        nueva_estructura = [
            {
                'nombre': 'Dashboard',
                'icono': 'bi bi-speedometer2',
                'orden': 1,
                'submenus': [
                    {'nombre': 'Panel Principal', 'url': 'core:dashboard', 'icono': 'bi bi-house-door', 'orden': 1},
                ]
            },
            {
                'nombre': 'Pacientes',
                'icono': 'bi bi-people-fill',
                'orden': 2,
                'submenus': [
                    {'nombre': 'Lista de Pacientes', 'url': 'core:paciente_list', 'icono': 'bi bi-list-ul', 'orden': 1},
                    {'nombre': 'Nuevo Paciente', 'url': 'core:paciente_create', 'icono': 'bi bi-person-plus', 'orden': 2},
                    {'nombre': 'Historial Clínico', 'url': 'core:cuestionario_list', 'icono': 'bi bi-file-medical', 'orden': 3},
                    {'nombre': 'Saldos Pendientes', 'url': 'core:saldos_pendientes', 'icono': 'bi bi-cash-stack', 'orden': 4},
                ]
            },
            {
                'nombre': 'Citas',
                'icono': 'bi bi-calendar-check',
                'orden': 3,
                'submenus': [
                    {'nombre': 'Agenda', 'url': 'core:agenda', 'icono': 'bi bi-calendar3', 'orden': 1},
                    {'nombre': 'Lista de Citas', 'url': 'core:cita_list', 'icono': 'bi bi-list-check', 'orden': 2},
                    {'nombre': 'Citas Pendientes de Pago', 'url': 'core:citas_pendientes_pago', 'icono': 'bi bi-exclamation-circle', 'orden': 3},
                ]
            },
            {
                'nombre': 'Clínica',
                'icono': 'bi bi-hospital',
                'orden': 4,
                'submenus': [
                    {'nombre': 'Servicios', 'url': 'core:service_list', 'icono': 'bi bi-clipboard-check', 'orden': 1},
                    {'nombre': 'Especialidades', 'url': 'core:especialidad_list', 'icono': 'bi bi-award', 'orden': 2},
                    {'nombre': 'Diagnósticos', 'url': 'core:diagnostico_list', 'icono': 'bi bi-clipboard-pulse', 'orden': 3},
                    {'nombre': 'Unidades Dentales', 'url': 'core:unidad_dental_list', 'icono': 'bi bi-activity', 'orden': 4},
                ]
            },
            {
                'nombre': 'Laboratorio Dental',
                'icono': 'bi bi-person-workspace',
                'orden': 5,
                'submenus': [
                    {'nombre': 'Trabajos de Laboratorio', 'url': 'core:trabajo_laboratorio_list', 'icono': 'bi bi-clipboard-data', 'orden': 1},
                    {'nombre': 'Nueva Solicitud', 'url': 'core:trabajo_laboratorio_create', 'icono': 'bi bi-plus-circle', 'orden': 2},
                ]
            },
            {
                'nombre': 'Personal',
                'icono': 'bi bi-person-badge',
                'orden': 6,
                'submenus': [
                    {'nombre': 'Lista de Personal', 'url': 'core:usuario_list', 'icono': 'bi bi-people', 'orden': 1},
                    {'nombre': 'Dentistas', 'url': 'core:dentista_list', 'icono': 'bi bi-person-check', 'orden': 2},
                ]
            },
            {
                'nombre': 'Finanzas',
                'icono': 'bi bi-graph-up-arrow',
                'orden': 7,
                'submenus': [
                    {'nombre': 'Dashboard Financiero', 'url': 'core:dashboard_financiero', 'icono': 'bi bi-bar-chart', 'orden': 1},
                    {'nombre': 'Pagos', 'url': 'core:pago_list', 'icono': 'bi bi-wallet2', 'orden': 2},
                    {'nombre': 'Reporte de Ingresos', 'url': 'core:reporte_ingresos', 'icono': 'bi bi-cash-coin', 'orden': 3},
                    {'nombre': 'Reporte de Saldos', 'url': 'core:reporte_saldos', 'icono': 'bi bi-file-earmark-text', 'orden': 4},
                    {'nombre': 'Facturación', 'url': 'core:reporte_facturacion', 'icono': 'bi bi-receipt', 'orden': 5},
                ]
            },
            {
                'nombre': 'Inventario',
                'icono': 'bi bi-box-seam',
                'orden': 8,
                'submenus': [
                    {'nombre': 'Insumos', 'url': 'core:insumo_list', 'icono': 'bi bi-boxes', 'orden': 1},
                    {'nombre': 'Proveedores', 'url': 'core:proveedor_list', 'icono': 'bi bi-truck', 'orden': 2},
                    {'nombre': 'Compras', 'url': 'core:compra_list', 'icono': 'bi bi-cart-check', 'orden': 3},
                ]
            },
            {
                'nombre': 'COFEPRIS',
                'icono': 'bi bi-shield-check',
                'orden': 9,
                'submenus': [
                    {'nombre': 'Panel COFEPRIS', 'url': 'core:dashboard_cofepris', 'icono': 'bi bi-clipboard-data', 'orden': 1},
                    {'nombre': 'Aviso de Funcionamiento', 'url': 'core:aviso_list', 'icono': 'bi bi-file-earmark-check', 'orden': 2},
                    {'nombre': 'Equipos', 'url': 'core:equipo_list', 'icono': 'bi bi-gear', 'orden': 3},
                    {'nombre': 'Residuos', 'url': 'core:residuos_list', 'icono': 'bi bi-trash', 'orden': 4},
                ]
            },
            {
                'nombre': 'Configuración',
                'icono': 'bi bi-gear-fill',
                'orden': 10,
                'submenus': [
                    {'nombre': 'Datos de la Clínica', 'url': 'core:configuracion_clinica', 'icono': 'bi bi-building', 'orden': 1},
                    {'nombre': 'Preguntas de Historial', 'url': 'core:pregunta_list', 'icono': 'bi bi-question-circle', 'orden': 2},
                    {'nombre': 'Gestión de Permisos', 'url': 'core:permisos_admin', 'icono': 'bi bi-shield-lock', 'orden': 3},
                ]
            },
        ]

        # Primero, desactivar todos los módulos y submenús existentes
        print("1. Desactivando estructura antigua...")
        ModuloSistema.objects.all().update(activo=False)
        SubmenuItem.objects.all().update(activo=False)

        # Crear/actualizar nueva estructura
        print("\n2. Creando nueva estructura de menús...\n")

        for modulo_data in nueva_estructura:
            # Crear o actualizar módulo
            modulo, created = ModuloSistema.objects.update_or_create(
                nombre=modulo_data['nombre'],
                defaults={
                    'icono': modulo_data['icono'],
                    'orden': modulo_data['orden'],
                    'activo': True,
                    'descripcion': f"Módulo de {modulo_data['nombre']}"
                }
            )

            status = "✓ Creado" if created else "↻ Actualizado"
            print(f"{status}: {modulo.nombre} ({modulo.icono})")

            # Crear/actualizar submenús
            for submenu_data in modulo_data['submenus']:
                submenu, sub_created = SubmenuItem.objects.update_or_create(
                    modulo=modulo,
                    url_name=submenu_data['url'],
                    defaults={
                        'nombre': submenu_data['nombre'],
                        'icono': submenu_data['icono'],
                        'orden': submenu_data['orden'],
                        'activo': True,
                        'requiere_ver': True,
                        'requiere_crear': False,
                        'requiere_editar': False,
                        'requiere_eliminar': False,
                    }
                )
                sub_status = "  + Nuevo" if sub_created else "  ↻ Actualizado"
                print(f"{sub_status}: {submenu.nombre}")

            print()

        # Asignar permisos a roles
        print("\n3. Asignando permisos a roles...\n")

        # Obtener roles
        admin_group = Group.objects.get(name='Administrador')
        dentista_group = Group.objects.get(name='Dentista')
        recepcionista_group = Group.objects.get(name='Recepcionista')

        # Limpiar permisos antiguos
        PermisoRol.objects.all().delete()

        # Configuración de permisos por rol
        permisos_config = {
            'Administrador': {
                'acceso_completo': True,  # Todos los módulos
            },
            'Dentista': {
                'modulos_completos': ['Dashboard', 'Pacientes', 'Citas', 'Clínica', 'Laboratorio Dental'],
                'modulos_solo_ver': ['Personal', 'Finanzas', 'Inventario'],
            },
            'Recepcionista': {
                'modulos_completos': ['Dashboard', 'Pacientes', 'Citas', 'Laboratorio Dental', 'Finanzas'],
                'modulos_solo_ver': ['Clínica', 'Personal', 'Inventario'],
            }
        }

        # Asignar permisos
        for modulo in ModuloSistema.objects.filter(activo=True):
            for submenu in modulo.submenus.filter(activo=True):

                # Administrador: acceso completo a todo
                PermisoRol.objects.create(
                    rol=admin_group,
                    submenu_item=submenu,
                    puede_ver=True,
                    puede_crear=True,
                    puede_editar=True,
                    puede_eliminar=True,
                    puede_exportar=True,
                    nivel_acceso='COMPLETO'
                )

                # Dentista
                if modulo.nombre in permisos_config['Dentista'].get('modulos_completos', []):
                    PermisoRol.objects.create(
                        rol=dentista_group,
                        submenu_item=submenu,
                        puede_ver=True,
                        puede_crear=True,
                        puede_editar=True,
                        puede_eliminar=False,  # Dentistas no eliminan (solo admin)
                        puede_exportar=True,
                        nivel_acceso='EDITAR'
                    )
                elif modulo.nombre in permisos_config['Dentista'].get('modulos_solo_ver', []):
                    PermisoRol.objects.create(
                        rol=dentista_group,
                        submenu_item=submenu,
                        puede_ver=True,
                        puede_crear=False,
                        puede_editar=False,
                        puede_eliminar=False,
                        puede_exportar=False,
                        nivel_acceso='VER'
                    )

                # Recepcionista
                if modulo.nombre in permisos_config['Recepcionista'].get('modulos_completos', []):
                    PermisoRol.objects.create(
                        rol=recepcionista_group,
                        submenu_item=submenu,
                        puede_ver=True,
                        puede_crear=True,
                        puede_editar=True,
                        puede_eliminar=False,  # Solo admin elimina
                        puede_exportar=True,
                        nivel_acceso='EDITAR'
                    )
                elif modulo.nombre in permisos_config['Recepcionista'].get('modulos_solo_ver', []):
                    PermisoRol.objects.create(
                        rol=recepcionista_group,
                        submenu_item=submenu,
                        puede_ver=True,
                        puede_crear=False,
                        puede_editar=False,
                        puede_eliminar=False,
                        puede_exportar=False,
                        nivel_acceso='VER'
                    )

        print(f"✓ Administrador: {PermisoRol.objects.filter(rol=admin_group).count()} permisos")
        print(f"✓ Dentista: {PermisoRol.objects.filter(rol=dentista_group).count()} permisos")
        print(f"✓ Recepcionista: {PermisoRol.objects.filter(rol=recepcionista_group).count()} permisos")

        # Estadísticas finales
        print("\n" + "="*60)
        print("✅ REORGANIZACIÓN COMPLETADA")
        print("="*60)
        print(f"📁 Módulos activos: {ModuloSistema.objects.filter(activo=True).count()}")
        print(f"📋 Submenús activos: {SubmenuItem.objects.filter(activo=True).count()}")
        print(f"🔐 Permisos asignados: {PermisoRol.objects.count()}")
        print("\n🎯 Nueva estructura aplicada con éxito!")
        print(f"🌐 Accede a: http://localhost:8000/{schema_name}/")

        return True

if __name__ == '__main__':
    import sys
    schema = sys.argv[1] if len(sys.argv) > 1 else 'dev'

    try:
        reorganizar_menus(schema)
    except Clinica.DoesNotExist:
        print(f"❌ Error: No existe el tenant '{schema}'")
        print("\nTenants disponibles:")
        for clinica in Clinica.objects.exclude(schema_name='public'):
            print(f"  • {clinica.schema_name} - {clinica.nombre}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
