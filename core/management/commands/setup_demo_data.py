import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from core.models import (
    Paciente, PerfilDentista, Especialidad, Servicio, Cita, Pago,
    Proveedor, Insumo, Compra, DetalleCompra, LoteInsumo, UnidadDental,
    Diagnostico, EstadoDiente, HistorialClinico, DatosFiscales
)
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Crea un conjunto de datos de demostración robusto para un tenant específico.'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', required=True, type=str, help='El schema_name del tenant para poblar.')
        parser.add_argument('--clean', action='store_true', help='Borra los datos existentes antes de crear nuevos datos.')

    @transaction.atomic
    def handle(self, *args, **options):
        from django_tenants.utils import tenant_context
        from tenants.models import Clinica

        try:
            tenant = Clinica.objects.get(schema_name=options['tenant'])
        except Clinica.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tenant "{options["tenant"]}" no encontrado.'))
            return

        with tenant_context(tenant):
            self.stdout.write(f'Operando en el tenant: {tenant.nombre} ({tenant.schema_name})')
            
            if options['clean']:
                self.stdout.write(self.style.WARNING('Limpiando datos existentes...'))
                self._clean_data()

            self.faker = Faker('es_MX')
            self._create_all_data()

            self.stdout.write(self.style.SUCCESS('¡Los datos de demostración mejorados se han creado con éxito!'))

    def _clean_data(self):
        # El orden es importante para respetar las restricciones de FK
        EstadoDiente.objects.all().delete()
        HistorialClinico.objects.all().delete()
        Pago.objects.all().delete()
        Cita.objects.all().delete()
        DetalleCompra.objects.all().delete()
        Compra.objects.all().delete()
        LoteInsumo.objects.all().delete()
        Insumo.objects.all().delete()
        Proveedor.objects.all().delete()
        Servicio.objects.all().delete()
        Especialidad.objects.all().delete()
        DatosFiscales.objects.all().delete()
        Paciente.objects.all().delete()
        UnidadDental.objects.all().delete()
        # No borramos usuarios/grupos para no perder el acceso

    def _create_all_data(self):
        self.stdout.write("1. Creando entidades base (roles, unidades, servicios)...")
        self._create_base_entities()
        
        self.stdout.write("2. Creando un conjunto de pacientes...")
        self._create_pacientes(50)
        
        self.stdout.write("3. Creando flujo histórico de citas y pagos...")
        self._create_citas_flow(150, historical=True)
        
        self.stdout.write("4. Asegurando actividad para el día de HOY...")
        self._create_today_activity(5)

        self.stdout.write("5. Creando casos especiales para demostración...")
        self._create_special_cases()

        self.stdout.write("6. Simulando compras y poblando el stock de inventario...")
        self._simulate_compras(8)

    def _create_base_entities(self):
        # Roles
        Group.objects.get_or_create(name='Administrador')
        Group.objects.get_or_create(name='Dentista')
        Group.objects.get_or_create(name='Recepcionista')

        # Unidades Dentales
        UnidadDental.objects.get_or_create(nombre='Consultorio 1')
        UnidadDental.objects.get_or_create(nombre='Consultorio 2')
        UnidadDental.objects.get_or_create(nombre='Quirofano')

        # Especialidades
        especialidades = ['General', 'Ortodoncia', 'Endodoncia', 'Periodoncia', 'Cirugía Maxilofacial']
        for nombre in especialidades:
            Especialidad.objects.get_or_create(nombre=nombre)

        # Diagnósticos
        Diagnostico.objects.get_or_create(nombre='SANO', defaults={'color_hex': '#C8E6C9'})
        Diagnostico.objects.get_or_create(nombre='CARIES', defaults={'color_hex': '#FFCDD2', 'icono_svg': '<circle cx="12" cy="12" r="4" fill="red"/>'})
        Diagnostico.objects.get_or_create(nombre='RESTAURACIÓN', defaults={'color_hex': '#BBDEFB'})
        Diagnostico.objects.get_or_create(nombre='AUSENTE', defaults={'color_hex': '#BDBDBD', 'icono_svg': '<line x1="4" y1="4" x2="20" y2="20" stroke="black" stroke-width="2"/><line x1="4" y1="20" x2="20" y2="4" stroke="black" stroke-width="2"/>'})
        Diagnostico.objects.get_or_create(nombre='ENDODONCIA', defaults={'color_hex': '#F8BBD0'})

        # Servicios
        servicios_data = [
            ('Consulta de Diagnóstico', 350.00, 'General'), ('Limpieza Dental', 700.00, 'General'),
            ('Resina Simple', 950.00, 'General'), ('Consulta de Ortodoncia', 500.00, 'Ortodoncia'),
            ('Ajuste Mensual Brackets', 800.00, 'Ortodoncia'), ('Tratamiento de Endodoncia', 3500.00, 'Endodoncia'),
            ('Extracción Simple', 1200.00, 'Cirugía Maxilofacial'),
        ]
        for nombre, precio, esp_nombre in servicios_data:
            esp = Especialidad.objects.get(nombre=esp_nombre)
            Servicio.objects.get_or_create(nombre=nombre, defaults={'precio': precio, 'especialidad': esp})

        # Proveedores e Insumos
        proveedores = ['Depósito Dental Villa de Cortés', '3M México', 'Dentsply Sirona', 'Henry Schein']
        for nombre in proveedores:
            Proveedor.objects.get_or_create(nombre=nombre, defaults={'rfc': self.faker.rfc()})
        
        insumos_data = [
            ('Resina A2', 10, True), ('Anestesia Local', 20, True), ('Guantes de Latex (Caja)', 5, False),
            ('Eyector de Saliva (Paquete)', 15, False), ('Bracket Metálico (Kit)', 50, True), ('Ácido Grabador', 25, True)
        ]
        for nombre, stock_min, req_lote in insumos_data:
            Insumo.objects.get_or_create(nombre=nombre, defaults={'stock_minimo': stock_min, 'requiere_lote_caducidad': req_lote, 'proveedor': Proveedor.objects.order_by('?').first()})

    def _create_pacientes(self, count):
        for _ in range(count):
            paciente = Paciente.objects.create(
                nombre=self.faker.first_name(), apellido=self.faker.last_name(),
                email=self.faker.unique.email(), telefono=self.faker.phone_number(),
                fecha_nacimiento=self.faker.date_of_birth(minimum_age=5, maximum_age=90),
                direccion=self.faker.address()
            )
            if random.random() < 0.3:
                DatosFiscales.objects.create(paciente=paciente, rfc=self.faker.rfc(), razon_social=self.faker.company(), domicilio_fiscal=self.faker.address())

    def _create_citas_flow(self, count, historical=False):
        pacientes = list(Paciente.objects.all())
        dentistas = list(PerfilDentista.objects.all())
        servicios = list(Servicio.objects.all())
        unidades = list(UnidadDental.objects.all())
        now = timezone.now()

        for _ in range(count):
            if historical:
                fecha = now - timedelta(days=random.randint(1, 365), hours=random.randint(0, 8))
            else: # Para actividad de hoy
                fecha = now.replace(hour=random.randint(9, 17), minute=random.choice([0, 30]))
            
            estado = random.choices(['PRO', 'CON', 'ATN', 'CAN', 'COM'], weights=[0.1, 0.1, 0.1, 0.1, 0.6], k=1)[0]
            
            cita = Cita.objects.create(
                paciente=random.choice(pacientes), dentista=random.choice(dentistas),
                unidad_dental=random.choice(unidades), fecha_hora=fecha,
                motivo=self.faker.sentence(nb_words=4), estado=estado
            )

            if estado in ['ATN', 'COM']:
                servicios_realizados = random.sample(servicios, k=random.randint(1, 2))
                cita.servicios_realizados.set(servicios_realizados)
                # Actualizar saldo del paciente en función de servicios y pagos
                if cita.saldo_pendiente > 0:
                    pago_total = (estado == 'COM') or (random.random() < 0.5)
                    monto_pago = cita.saldo_pendiente if pago_total else cita.saldo_pendiente * Decimal(str(random.uniform(0.2, 0.8)))
                    Pago.objects.create(cita=cita, paciente=cita.paciente, monto=monto_pago, fecha_pago=fecha + timedelta(minutes=30))
                # Recalcular saldo del paciente
                cita.paciente.actualizar_saldo_global()

    def _create_today_activity(self, count):
        self._create_citas_flow(count, historical=False)

    def _create_special_cases(self):
        self.stdout.write("  - Creando paciente con deuda significativa...")
        deudor, _ = Paciente.objects.get_or_create(
            nombre="Juan", apellido="Deudor Moroso",
            defaults={'email': 'juan.deudor@example.com', 'telefono': '5512345678', 'fecha_nacimiento': '1980-01-01'}
        )
        
        dentista = PerfilDentista.objects.order_by('?').first()
        unidad = UnidadDental.objects.order_by('?').first()
        servicio_caro = Servicio.objects.get(nombre='Tratamiento de Endodoncia')
        
        for i in range(3):
            cita = Cita.objects.create(
                paciente=deudor, dentista=dentista, unidad_dental=unidad,
                fecha_hora=timezone.now() - timedelta(days=45 * (i+1)),
                motivo="Revisión y tratamiento complejo", estado='COM'
            )
            cita.servicios_realizados.add(servicio_caro)
            # Pagar solo una pequeña parte y recalcular saldo
            Pago.objects.create(cita=cita, paciente=deudor, monto=Decimal('500.00'))
            deudor.actualizar_saldo_global()

    def _simulate_compras(self, count):
        proveedores = list(Proveedor.objects.all())
        insumos = list(Insumo.objects.all())
        unidades = list(UnidadDental.objects.all())

        for _ in range(count):
            compra = Compra.objects.create(proveedor=random.choice(proveedores), fecha_compra=timezone.now() - timedelta(days=random.randint(1, 90)))
            total_compra = 0
            for _ in range(random.randint(2, 5)):
                insumo = random.choice(insumos)
                cantidad = random.randint(5, 50)
                precio = Decimal(str(round(random.uniform(50.0, 500.0), 2)))
                total_compra += cantidad * precio
                DetalleCompra.objects.create(compra=compra, insumo=insumo, cantidad=cantidad, precio_unitario=precio)
            
            compra.total = total_compra
            compra.estado = 'RECIBIDA'
            compra.save()

            for detalle in compra.detalles.all():
                LoteInsumo.objects.create(
                    insumo=detalle.insumo, unidad_dental=random.choice(unidades),
                    cantidad=detalle.cantidad,
                    numero_lote=self.faker.ean(length=8) if detalle.insumo.requiere_lote_caducidad else None,
                    fecha_caducidad=self.faker.future_date(end_date='+2y') if detalle.insumo.requiere_lote_caducidad else None
                )
                detalle.insumo.actualizar_stock_total()