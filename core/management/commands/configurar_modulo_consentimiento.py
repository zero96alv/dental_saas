"""
Comando para configurar el módulo de Consentimiento Informado en el sistema de navegación dinámico.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import ModuloSistema, SubmenuItem, PermisoRol


class Command(BaseCommand):
    help = 'Configurar el módulo de Consentimiento Informado en el sistema de navegación'

    def handle(self, *args, **options):
        self.stdout.write('Configurando módulo de Consentimiento Informado...')

        # 1. Crear o actualizar el módulo principal
        modulo, created = ModuloSistema.objects.get_or_create(
            nombre='Consentimiento Informado',
            defaults={
                'descripcion': 'Gestión de documentos de consentimiento informado y firmas de pacientes',
                'icono': 'fas fa-file-contract',
                'orden': 110,
                'activo': True,
                'url_pattern': '/consentimientos/',
            }
        )

        if created:
            self.stdout.write(f'✓ Módulo creado: {modulo.nombre}')
        else:
            self.stdout.write(f'✓ Módulo existente: {modulo.nombre}')

        # 2. Crear submenús
        submenus = [
            {
                'nombre': 'Documentos PDF',
                'descripcion': 'Gestionar documentos PDF de consentimiento',
                'url_name': 'core:consentimiento_list',
                'icono': 'fas fa-file-pdf',
                'orden': 1,
                'requiere_ver': True,
            },
            {
                'nombre': 'Nuevo Documento',
                'descripcion': 'Crear nuevo documento de consentimiento',
                'url_name': 'core:consentimiento_create',
                'icono': 'fas fa-plus-circle',
                'orden': 2,
                'requiere_crear': True,
            },
            {
                'nombre': 'Firmas de Pacientes',
                'descripcion': 'Ver consentimientos firmados por pacientes',
                'url_name': 'core:paciente_consentimiento_list',
                'icono': 'fas fa-signature',
                'orden': 3,
                'requiere_ver': True,
            },
            {
                'nombre': 'Integración Cuestionarios',
                'descripcion': 'Pacientes con cuestionarios y consentimientos',
                'url_name': 'core:cuestionario_lista',
                'icono': 'fas fa-link',
                'orden': 4,
                'requiere_ver': True,
            },
        ]

        for submenu_data in submenus:
            submenu, created = SubmenuItem.objects.get_or_create(
                modulo=modulo,
                nombre=submenu_data['nombre'],
                defaults={
                    'descripcion': submenu_data['descripcion'],
                    'url_name': submenu_data['url_name'],
                    'icono': submenu_data['icono'],
                    'orden': submenu_data['orden'],
                    'activo': True,
                    'requiere_ver': submenu_data.get('requiere_ver', False),
                    'requiere_crear': submenu_data.get('requiere_crear', False),
                    'requiere_editar': submenu_data.get('requiere_editar', False),
                    'requiere_eliminar': submenu_data.get('requiere_eliminar', False),
                }
            )

            if created:
                self.stdout.write(f'  ✓ Submenú creado: {submenu.nombre}')
            else:
                self.stdout.write(f'  ✓ Submenú existente: {submenu.nombre}')

        # 3. Configurar permisos por rol
        roles_configuracion = {
            'Administrador': 'completo',
            'Dentista': 'escritura', 
            'Recepcionista': 'lectura',
        }

        # Obtener grupos existentes
        grupos_existentes = {}
        for rol_nombre in roles_configuracion.keys():
            try:
                grupo = Group.objects.get(name=rol_nombre)
                grupos_existentes[rol_nombre] = grupo
                self.stdout.write(f'✓ Grupo encontrado: {rol_nombre}')
            except Group.DoesNotExist:
                self.stdout.write(f'⚠ Grupo no encontrado: {rol_nombre}')

        # 4. Asignar permisos a roles para cada submenú
        permisos_creados = 0
        for submenu in modulo.submenus.all():
            for rol_nombre, nivel_acceso in roles_configuracion.items():
                if rol_nombre not in grupos_existentes:
                    continue

                grupo = grupos_existentes[rol_nombre]
                permiso_obj, created = PermisoRol.objects.get_or_create(
                    rol=grupo,
                    submenu_item=submenu,
                    defaults={
                        'nivel_acceso': nivel_acceso,
                    }
                )

                if created:
                    permisos_creados += 1

        self.stdout.write(f'✓ Permisos configurados: {permisos_creados} nuevos')

        # 5. Estadísticas finales
        total_submenus = modulo.submenus.count()
        total_permisos = PermisoRol.objects.filter(submenu_item__modulo=modulo).count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Configuración completada exitosamente!\n'
                f'📋 Módulo: {modulo.nombre}\n'
                f'📑 Submenús: {total_submenus}\n'
                f'🔐 Permisos configurados: {total_permisos}\n'
                f'👥 Roles con acceso: {len(grupos_existentes)}'
            )
        )

        # 6. Instrucciones adicionales
        self.stdout.write(
            self.style.WARNING(
                f'\n📝 SIGUIENTES PASOS:\n'
                f'1. Verificar que los templates estén creados\n'
                f'2. Probar el acceso desde el menú principal\n'
                f'3. Verificar permisos por rol\n'
                f'4. Crear documentos PDF de consentimiento\n'
                f'5. Probar la integración con cuestionarios'
            )
        )