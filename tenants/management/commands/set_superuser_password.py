from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context


class Command(BaseCommand):
    help = 'Establece la contraseña para el superusuario global'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='superadmin',
            help='Username del superusuario (default: superadmin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Nueva contraseña para el superusuario'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        self.stdout.write(f"Estableciendo contraseña para el usuario '{username}'...")
        
        with schema_context('public'):
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Contraseña actualizada para '{username}'")
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"✗ Usuario '{username}' no encontrado.")
                )
                self.stdout.write("Usuarios disponibles:")
                for user in User.objects.all():
                    self.stdout.write(f"  - {user.username}")
