from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from core.permissions_utils import inicializar_permisos_por_defecto


class Command(BaseCommand):
    help = 'Inicializa módulos/submenús y permisos por defecto en TODOS los tenants (idempotente).'

    def add_arguments(self, parser):
        parser.add_argument('--only', type=str, help='Opcional: schema_name de un tenant específico a inicializar')

    def handle(self, *args, **options):
        target = options.get('only')
        tenants = Clinica.objects.all()
        if target:
            tenants = tenants.filter(schema_name=target)
            if not tenants.exists():
                self.stdout.write(self.style.ERROR(f"Tenant '{target}' no encontrado."))
                return

        for tenant in tenants:
            self.stdout.write(self.style.WARNING(f"Inicializando permisos en tenant: {tenant.schema_name}"))
            with tenant_context(tenant):
                try:
                    inicializar_permisos_por_defecto()
                    self.stdout.write(self.style.SUCCESS(f"✓ Permisos inicializados en {tenant.schema_name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error en {tenant.schema_name}: {e}"))
                    raise

        self.stdout.write(self.style.SUCCESS("Proceso completado."))
