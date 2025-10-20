import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from core.models import PerfilDentista

class Command(BaseCommand):
    help = 'Crea usuarios de desarrollo (admin.dev, recep.dev, dentista.dev) y los asigna a sus grupos. Las contraseñas se toman de una variable de entorno.'

    def add_arguments(self, parser):
        parser.add_argument('--password-env', type=str, default='DEV_USER_PASSWORD', help='Nombre de la variable de entorno con la contraseña (default: DEV_USER_PASSWORD)')
        parser.add_argument('--tenant', type=str, default=None, help='Schema del tenant donde crear los usuarios (opcional)')

    def handle(self, *args, **options):
        env_name = options['password_env']
        password = os.environ.get(env_name)
        if not password:
            self.stdout.write(self.style.ERROR(f"La variable de entorno {env_name} no está definida. Define una contraseña segura y reintenta."))
            return

        tenant_schema = options.get('tenant')
        if tenant_schema:
            try:
                from django_tenants.utils import tenant_context
                from tenants.models import Clinica
                tenant = Clinica.objects.get(schema_name=tenant_schema)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"No se pudo ubicar el tenant '{tenant_schema}': {e}"))
                return
            with tenant_context(tenant):
                self._create_users(password)
        else:
            self._create_users(password)

    def _create_users(self, password):

        # Asegurar grupos
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        recep_group, _ = Group.objects.get_or_create(name='Recepcionista')
        dent_group, _ = Group.objects.get_or_create(name='Dentista')

        created = []
        updated = []

        # Admin
        admin_user, created_flag = User.objects.get_or_create(username='admin.dev', defaults={'email': 'admin.dev@example.com', 'first_name': 'Admin', 'last_name': 'Dev', 'is_staff': True, 'is_superuser': True})
        admin_user.set_password(password)
        admin_user.save()
        admin_user.groups.add(admin_group)
        (created if created_flag else updated).append('admin.dev')

        # Recepcionista
        recep_user, created_flag = User.objects.get_or_create(username='recep.dev', defaults={'email': 'recepcion.dev@example.com', 'first_name': 'Recep', 'last_name': 'Dev', 'is_staff': True})
        recep_user.set_password(password)
        recep_user.save()
        recep_user.groups.add(recep_group)
        (created if created_flag else updated).append('recep.dev')

        # Dentista
        dent_user, created_flag = User.objects.get_or_create(username='dentista.dev', defaults={'email': 'dentista.dev@example.com', 'first_name': 'Dr.', 'last_name': 'Dev', 'is_staff': True})
        dent_user.set_password(password)
        dent_user.save()
        dent_user.groups.add(dent_group)
        (created if created_flag else updated).append('dentista.dev')

        # PerfilDentista para dentista
        PerfilDentista.objects.get_or_create(usuario=dent_user, defaults={'nombre': dent_user.first_name or 'Dentista', 'apellido': dent_user.last_name or 'Dev', 'email': dent_user.email})

        if created:
            self.stdout.write(self.style.SUCCESS(f"Usuarios creados: {', '.join(created)}"))
        if updated:
            self.stdout.write(self.style.WARNING(f"Usuarios actualizados: {', '.join(updated)}"))

        self.stdout.write(self.style.SUCCESS("Contraseñas establecidas desde variable de entorno. Cambie las contraseñas tras la prueba."))
