from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from core.models import Cita

class Command(BaseCommand):
    help = 'Envía recordatorios de pago para citas completadas con saldo pendiente.'

    def handle(self, *args, **options):
        tenants = Clinica.objects.exclude(schema_name='public')
        self.stdout.write(f'Encontrados {len(tenants)} tenants (clínicas). Iniciando proceso de recordatorios de pago...')

        for tenant in tenants:
            with tenant_context(tenant):
                self.stdout.write(self.style.SUCCESS(f'--- Procesando tenant: {tenant.nombre} ---'))
                self.enviar_recordatorios_por_tenant(tenant)
        
        self.stdout.write(self.style.SUCCESS('Proceso de recordatorios de pago finalizado para todos los tenants.'))

    def enviar_recordatorios_por_tenant(self, tenant):
        citas_con_saldo = Cita.objects.filter(
            estado='COM', # Solo citas completadas
            saldo_pendiente__gt=0
        ).select_related('cliente')

        if not citas_con_saldo.exists():
            self.stdout.write('No hay citas con saldos pendientes en este tenant.')
            return

        self.stdout.write(f'Encontradas {citas_con_saldo.count()} citas con saldo pendiente. Enviando emails...')

        for cita in citas_con_saldo:
            paciente = cita.cliente
            if not paciente.email:
                self.stdout.write(self.style.WARNING(f'Paciente {paciente} no tiene email. Saltando.'))
                continue

            subject = f'Recordatorio de Saldo Pendiente en {tenant.nombre}'
            message = (
                f'Hola {paciente.nombre},\n\n'
                f'Te escribimos para recordarte que tienes un saldo pendiente de ${cita.saldo_pendiente:,.2f} '
                f'correspondiente a tu cita del día {cita.fecha_hora.strftime("%d/%m/%Y")}.\n\n'
                f'Puedes pasar por la clínica para saldar tu cuenta.\n\n'
                f'Gracias,\n'
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
                self.stdout.write(self.style.SUCCESS(f'Recordatorio de pago enviado a {paciente.email}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al enviar email a {paciente.email}: {e}'))