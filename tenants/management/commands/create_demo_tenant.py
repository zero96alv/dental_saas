from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from tenants.models import Clinica, Domain


class Command(BaseCommand):
    help = 'Crea una clínica demo y su dominio para pruebas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--schema-name',
            type=str,
            default='demo',
            help='Nombre del schema para la clínica demo (default: demo)'
        )
        parser.add_argument(
            '--domain-name',
            type=str,
            default='demo.localhost',
            help='Dominio para la clínica demo (default: demo.localhost)'
        )
        parser.add_argument(
            '--clinic-name',
            type=str,
            default='Clinica Demo',
            help='Nombre de la clínica demo (default: Clinica Demo)'
        )
    
    def handle(self, *args, **options):
        schema_name = options['schema_name']
        domain_name = options['domain_name']
        clinic_name = options['clinic_name']
        
        self.stdout.write(f"Creando tenant demo: {schema_name}")
        
        with schema_context('public'):
            # Crear la clínica demo
            clinica, created = Clinica.objects.get_or_create(
                schema_name=schema_name,
                defaults={'nombre': clinic_name}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Tenant '{clinica.schema_name}' creado exitosamente.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"! Tenant '{clinica.schema_name}' ya existe.")
                )
            
            # Crear el dominio y asociarlo
            domain, created = Domain.objects.get_or_create(
                domain=domain_name,
                tenant=clinica,
                defaults={'is_primary': True}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Dominio '{domain.domain}' creado y vinculado a '{clinica.schema_name}'.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"! Dominio '{domain.domain}' ya existe.")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Tenant demo listo! Accede en: http://{domain_name}:8000/")
        )
