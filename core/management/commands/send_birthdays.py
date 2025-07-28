import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from core.models import Paciente

class Command(BaseCommand):
    help = 'Envía emails de felicitación a los pacientes que cumplen años mañana.'

    def handle(self, *args, **options):
        tenants = Clinica.objects.exclude(schema_name='public')
        self.stdout.write(f'Encontrados {len(tenants)} tenants (clínicas). Iniciando proceso de felicitaciones...')

        for tenant in tenants:
            with tenant_context(tenant):
                self.stdout.write(self.style.SUCCESS(f'--- Procesando tenant: {tenant.nombre} ---'))
                self.enviar_felicitaciones_por_tenant(tenant)
        
        self.stdout.write(self.style.SUCCESS('Proceso de felicitaciones finalizado para todos los tenants.'))

    def enviar_felicitaciones_por_tenant(self, tenant):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        
        pacientes_cumpleaneros = Paciente.objects.filter(
            fecha_nacimiento__day=tomorrow.day,
            fecha_nacimiento__month=tomorrow.month
        )

        if not pacientes_cumpleaneros.exists():
            self.stdout.write('No hay pacientes que cumplan años mañana en este tenant.')
            return

        self.stdout.write(f'Encontrados {pacientes_cumpleaneros.count()} cumpleañeros. Enviando emails...')

        for paciente in pacientes_cumpleaneros:
            if not paciente.email:
                self.stdout.write(self.style.WARNING(f'Paciente {paciente} no tiene email. Saltando.'))
                continue

            subject = f'¡Feliz Cumpleaños de parte de {tenant.nombre}!'
            message = (
                f'Hola {paciente.nombre},\n\n'
                f'Todo el equipo de {tenant.nombre} te desea un muy feliz cumpleaños.\n\n'
                f'Esperamos que tengas un día excelente.\n\n'
                f'¡Muchas felicidades!'
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [paciente.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Felicitación enviada a {paciente.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al enviar email a {paciente.email}: {e}'))