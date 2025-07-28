import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from core.models import Cita

class Command(BaseCommand):
    help = 'Envía recordatorios por email para las citas del día siguiente para todos los tenants.'

    def handle(self, *args, **options):
        tenants = Clinica.objects.exclude(schema_name='public')
        self.stdout.write(f'Encontrados {len(tenants)} tenants (clínicas). Iniciando proceso de recordatorios...')

        for tenant in tenants:
            with tenant_context(tenant):
                self.stdout.write(self.style.SUCCESS(f'--- Procesando tenant: {tenant.nombre} ---'))
                self.enviar_recordatorios_por_tenant(tenant)
        
        self.stdout.write(self.style.SUCCESS('Proceso de recordatorios finalizado para todos los tenants.'))

    def enviar_recordatorios_por_tenant(self, tenant):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        
        citas_de_manana = Cita.objects.filter(
            fecha_hora__date=tomorrow,
            estado__in=['PRO', 'CON']
        ).select_related('cliente')

        if not citas_de_manana.exists():
            self.stdout.write('No hay citas programadas para mañana en este tenant.')
            return

        self.stdout.write(f'Encontradas {citas_de_manana.count()} citas. Enviando emails...')

        for cita in citas_de_manana:
            paciente = cita.cliente
            if not paciente.email:
                self.stdout.write(self.style.WARNING(f'Paciente {paciente} no tiene email. Saltando.'))
                continue

            subject = f'Recordatorio de tu cita en {tenant.nombre}'
            message = (
                f'Hola {paciente.nombre},\n\n'
                f'Te recordamos tu cita programada para mañana, {tomorrow.strftime("%d/%m/%Y")}, '
                f'a las {cita.fecha_hora.strftime("%H:%M")} horas.\n\n'
                f'Motivo: {cita.motivo}\n\n'
                f'¡Te esperamos!\n\n'
                f'Atentamente,\n'
                f'El equipo de {tenant.nombre}'
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [paciente.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Recordatorio enviado a {paciente.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al enviar email a {paciente.email}: {e}'))