# core/management/commands/init_permisos.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.permissions_utils import inicializar_permisos_por_defecto


class Command(BaseCommand):
    help = 'Inicializa el sistema de permisos dinámicos con configuración por defecto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la recreación de permisos existentes',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando configuración del sistema de permisos...'))
        
        try:
            # Verificar grupos básicos
            admin_group, admin_created = Group.objects.get_or_create(name='Administrador')
            dentista_group, dentista_created = Group.objects.get_or_create(name='Dentista')
            recepcionista_group, recepcionista_created = Group.objects.get_or_create(name='Recepcionista')
            
            if admin_created:
                self.stdout.write(self.style.SUCCESS('✓ Grupo "Administrador" creado'))
            if dentista_created:
                self.stdout.write(self.style.SUCCESS('✓ Grupo "Dentista" creado'))
            if recepcionista_created:
                self.stdout.write(self.style.SUCCESS('✓ Grupo "Recepcionista" creado'))
            
            # Inicializar permisos
            inicializar_permisos_por_defecto()
            
            self.stdout.write(
                self.style.SUCCESS(
                    '✓ Sistema de permisos inicializado correctamente'
                )
            )
            
            # Mostrar estadísticas
            from core.models_permissions import ModuloSistema, SubmenuItem, PermisoRol
            
            num_modulos = ModuloSistema.objects.count()
            num_submenus = SubmenuItem.objects.count()
            num_permisos = PermisoRol.objects.count()
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=== ESTADÍSTICAS ==='))
            self.stdout.write(f'Módulos creados: {num_modulos}')
            self.stdout.write(f'Submenús creados: {num_submenus}')
            self.stdout.write(f'Permisos asignados: {num_permisos}')
            self.stdout.write('')
            
            # Mostrar información de acceso
            self.stdout.write(self.style.WARNING('=== INFORMACIÓN IMPORTANTE ==='))
            self.stdout.write('Para acceder al panel de administración de permisos:')
            self.stdout.write('1. Accede como superusuario o con rol "Administrador"')
            self.stdout.write('2. Ve al menú "Configuración" > "Administrar Permisos"')
            self.stdout.write('3. Ahí podrás configurar qué puede ver cada rol')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('¡Configuración completada!'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la inicialización: {str(e)}')
            )
            raise e
