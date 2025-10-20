from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from tenants.models import Clinica

class Command(BaseCommand):
    help = 'Ejecuta migraciones en todos los tenants existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant', 
            type=str, 
            help='Ejecutar migraciones solo en un tenant específico'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando migraciones en tenants...")
        
        if options['tenant']:
            # Migrar solo un tenant específico
            try:
                tenant = Clinica.objects.get(schema_name=options['tenant'])
                self._migrate_tenant(tenant)
            except Clinica.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Tenant '{options['tenant']}' no encontrado")
                )
        else:
            # Migrar todos los tenants excepto 'public'
            tenants = Clinica.objects.exclude(schema_name='public')
            
            if not tenants.exists():
                self.stdout.write(
                    self.style.WARNING("⚠️ No se encontraron tenants para migrar")
                )
                return
            
            for tenant in tenants:
                self._migrate_tenant(tenant)
        
        self.stdout.write(
            self.style.SUCCESS("✅ Migraciones completadas en todos los tenants")
        )

    def _migrate_tenant(self, tenant):
        """Ejecuta migraciones en un tenant específico"""
        self.stdout.write(f"📊 Migrando tenant: {tenant.nombre} ({tenant.schema_name})")
        
        try:
            # Cambiar al esquema del tenant
            connection.set_tenant(tenant)
            
            # Ejecutar migraciones
            call_command('migrate', verbosity=1, interactive=False)
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Migraciones completadas para {tenant.schema_name}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error migrando {tenant.schema_name}: {str(e)}")
            )