import datetime
from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from tenants.models import Clinica
from core.models import Paciente, Cita, Servicio, Proveedor

class Command(BaseCommand):
    help = 'Crea un conjunto de datos de prueba para validar los recordatorios.'

    def handle(self, *args, **options):
        tenants = Clinica.objects.exclude(schema_name='public')
        if not tenants:
            self.stdout.write(self.style.ERROR('No se encontró ninguna clínica para crear datos de prueba.'))
            return

        for tenant in tenants:
            with tenant_context(tenant):
                self.stdout.write(self.style.SUCCESS(f'--- Creando datos de prueba en el tenant: {tenant.nombre} ---'))
                self.crear_datos(tenant)
        
        self.stdout.write(self.style.WARNING('\n¡IMPORTANTE! Para recibir los emails, revisa el paciente "Usuario De Prueba" en CADA clínica y cambia "test@example.com" por tu email real.'))

    def crear_datos(self, tenant):
        # --- 1. Crear Proveedores de Prueba ---
        proveedores_data = [
            {'nombre': 'Depósito Dental Nacional S.A. de C.V.', 'contacto': 'Ana García', 'telefono': '5512345678', 'email': 'ventas@ddnacional.com'},
            {'nombre': 'OrthoSolutions México', 'contacto': 'Carlos Reyes', 'telefono': '8187654321', 'email': 'info@orthosolutions.mx'},
            {'nombre': 'Insumos Odontológicos del Caribe', 'contacto': 'Laura Pérez', 'telefono': '9981234567', 'email': 'pedidos@ioccaribe.com'},
        ]
        for data in proveedores_data:
            proveedor, created = Proveedor.objects.update_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Proveedor "{proveedor.nombre}" creado.'))
        
        # --- 2. Crear Paciente de Prueba ---
        test_email = 'test@example.com'
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        
        paciente, created = Paciente.objects.update_or_create(
            nombre='Usuario',
            apellido='De Prueba',
            defaults={
                'email': test_email,
                'fecha_nacimiento': tomorrow.replace(year=tomorrow.year - 30), # Cumpleaños mañana
                'telefono': '5551234567'
            }
        )
        
        # Asegurarse de que el cumpleaños sea mañana
        paciente.fecha_nacimiento = tomorrow.replace(year=paciente.fecha_nacimiento.year)
        paciente.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Paciente de prueba "{paciente}" con email "{test_email}" creado.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Paciente de prueba "{paciente}" con email "{test_email}" encontrado y actualizado.'))

        # --- 3. Crear Cita para Recordatorio ---
        cita_recordatorio, created = Cita.objects.update_or_create(
            paciente=paciente,
            motivo='Prueba de Recordatorio de Cita',
            defaults={
                'fecha_hora': datetime.datetime.combine(tomorrow, datetime.time(11, 30)),
                'estado': 'PRO'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Cita de prueba para mañana creada.'))
        else:
            self.stdout.write(self.style.SUCCESS('Cita de prueba para mañana actualizada.'))

        # --- 4. Crear Cita con Saldo Pendiente ---
        servicio, _ = Servicio.objects.get_or_create(
            nombre='Consulta de Prueba',
            defaults={'precio': 100.00}
        )
        
        cita_con_saldo, created = Cita.objects.update_or_create(
            paciente=paciente,
            motivo='Prueba de Saldo Pendiente',
            defaults={
                'fecha_hora': datetime.datetime.now() - datetime.timedelta(days=5),
                'estado': 'COM',
                'saldo_pendiente': servicio.precio
            }
        )
        cita_con_saldo.servicios_realizados.add(servicio)
        
        if created:
            self.stdout.write(self.style.SUCCESS('Cita completada con saldo pendiente creada.'))
        else:
            self.stdout.write(self.style.SUCCESS('Cita completada con saldo pendiente actualizada.'))
