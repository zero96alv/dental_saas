from django.core.management.base import BaseCommand
from tenants.models import Domain

class Command(BaseCommand):
    help = 'Lista todos los dominios de los tenants.'

    def handle(self, *args, **options):
        domains = Domain.objects.all()
        if not domains:
            self.stdout.write(self.style.WARNING('No se encontraron dominios.'))
            return
        
        self.stdout.write(self.style.SUCCESS('Dominios registrados:'))
        for domain in domains:
            self.stdout.write(f'- {domain.domain} (Tenant: {domain.tenant.schema_name})')
