from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
import datetime

# --- Base de Personas ---

class PersonaBase(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# --- Modelos de Personas ---

class Paciente(PersonaBase):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='paciente_perfil'
    )
    fecha_nacimiento = models.DateField()
    # Dirección estructurada
    calle = models.CharField(max_length=150, blank=True, null=True)
    numero_exterior = models.CharField(max_length=20, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    # Campo previo de dirección se conserva por compatibilidad
    direccion = models.TextField(blank=True, null=True)
    apto_para_plan_de_pago = models.BooleanField(default=False, help_text="Indica si el dentista ha autorizado un plan de pagos para este paciente.")
    consentimiento_cofepris = models.BooleanField(default=False, help_text="El paciente ha aceptado el aviso de privacidad y tratamiento de datos para COFEPRIS.")
    firma_consentimiento = models.ImageField(upload_to='firmas_consentimiento/', blank=True, null=True)
    saldo_global = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Saldo total pendiente del paciente.")

    @property
    def edad(self):
        """Calcula la edad del paciente"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    @property
    def datos_fiscales(self):
        try:
            return DatosFiscales.objects.filter(paciente=self).first()
        except Exception:
            return None

    def actualizar_saldo_global(self):
        from decimal import Decimal

        # Calcular total de cargos: primero intentar con servicios realizados, si no hay usar servicios planeados
        total_cargos = Decimal('0.00')

        # Citas atendidas o completadas
        citas_facturables = self.cita_set.filter(estado__in=['ATN', 'COM'])

        for cita in citas_facturables:
            # Primero intentar con servicios realizados
            servicios_realizados = cita.servicios_realizados.all()

            if servicios_realizados.exists():
                # Si tiene servicios realizados, usar esos
                subtotal = servicios_realizados.aggregate(total=Sum('precio'))['total'] or Decimal('0.00')
            else:
                # Si no tiene servicios realizados, usar los servicios planeados
                servicios_planeados = cita.servicios_planeados.all()
                subtotal = servicios_planeados.aggregate(total=Sum('precio'))['total'] or Decimal('0.00')

            total_cargos += subtotal

        # Total de pagos realizados
        total_pagos = self.pagos.all().aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')

        # Calcular saldo pendiente
        self.saldo_global = total_cargos - total_pagos
        self.save()
class SatFormaPago(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    descripcion = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'SAT Forma de Pago'
        verbose_name_plural = 'SAT Formas de Pago'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class SatMetodoPago(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    descripcion = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'SAT Método de Pago'
        verbose_name_plural = 'SAT Métodos de Pago'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class SatRegimenFiscal(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    descripcion = models.CharField(max_length=255)
    persona_fisica = models.BooleanField(default=True)
    persona_moral = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'SAT Régimen Fiscal'
        verbose_name_plural = 'SAT Regímenes Fiscales'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class SatUsoCFDI(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    descripcion = models.CharField(max_length=255)
    persona_fisica = models.BooleanField(default=True)
    persona_moral = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'SAT Uso CFDI'
        verbose_name_plural = 'SAT Usos CFDI'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

class DatosFiscales(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    rfc = models.CharField(max_length=13)
    razon_social = models.CharField(max_length=255)
    # Campo legacy (mantener por compatibilidad)
    domicilio_fiscal = models.TextField(blank=True, default='')
    # Dirección estructurada (preferida por SAT)
    calle = models.CharField(max_length=150, blank=True, default='')
    numero_exterior = models.CharField(max_length=20, blank=True, default='')
    numero_interior = models.CharField(max_length=20, blank=True, default='')
    colonia = models.CharField(max_length=100, blank=True, default='')
    municipio = models.CharField(max_length=100, blank=True, default='')
    estado = models.CharField(max_length=100, blank=True, default='')
    codigo_postal = models.CharField(max_length=10, blank=True, default='')
    regimen_fiscal = models.ForeignKey('SatRegimenFiscal', on_delete=models.SET_NULL, null=True, blank=True)
    uso_cfdi = models.ForeignKey('SatUsoCFDI', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def direccion_completa(self):
        partes = []
        if self.calle:
            num = (self.numero_exterior or '').strip()
            inter = (self.numero_interior or '').strip()
            linea = self.calle
            if num:
                linea += f" {num}"
            if inter:
                linea += f" Int {inter}"
            partes.append(linea)
        if self.colonia:
            partes.append(f"Col. {self.colonia}")
        loc = ' '.join(p for p in [self.municipio, self.estado] if p)
        if loc:
            partes.append(loc)
        if self.codigo_postal:
            partes.append(f"CP {self.codigo_postal}")
        # Fallback al legacy si no hay estructurada
        if not partes and self.domicilio_fiscal:
            return self.domicilio_fiscal
        return ', '.join(partes) if partes else ''

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    # NUEVO: Jerarquía de especialidades
    especialidades_incluidas = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        help_text="Especialidades cuyos servicios también puede realizar"
    )
    
    def __str__(self):
        return self.nombre
    
    def servicios_disponibles(self):
        """Obtener todos los servicios que puede realizar esta especialidad"""
        # Recopilar IDs de servicios propios y de especialidades incluidas
        servicios_ids = set()
        
        # Servicios propios
        servicios_ids.update(
            self.servicio_set.filter(activo=True).values_list('id', flat=True)
        )
        
        # Servicios de especialidades incluidas
        for esp_incluida in self.especialidades_incluidas.all():
            servicios_ids.update(
                esp_incluida.servicio_set.filter(activo=True).values_list('id', flat=True)
            )
        
        # Retornar queryset filtrado por IDs
        if servicios_ids:
            return Servicio.objects.filter(id__in=servicios_ids, activo=True).distinct()
        else:
            return Servicio.objects.none()

class PerfilDentista(PersonaBase):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_dentista')
    especialidades = models.ManyToManyField(Especialidad, blank=True)
    activo = models.BooleanField(default=True)
    # Nuevos campos opcionales
    foto = models.ImageField(upload_to='dentistas/fotos/', blank=True, null=True)
    titulo_profesional = models.FileField(upload_to='dentistas/titulos/', max_length=255, blank=True, null=True)
    cedula_profesional = models.FileField(upload_to='dentistas/cedulas/', max_length=255, blank=True, null=True)

class HorarioLaboral(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    dentista = models.ForeignKey(PerfilDentista, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('dentista', 'dia_semana', 'hora_inicio')
        ordering = ['dentista', 'dia_semana', 'hora_inicio']

    def __str__(self):
        return f"Horario de {self.dentista} el {self.get_dia_semana_display()} de {self.hora_inicio} a {self.hora_fin}"

# --- Modelos de Gestión Financiera ---

class Servicio(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(
        default=30,
        help_text="Duración estimada en minutos"
    )
    activo = models.BooleanField(default=True)
    especialidad = models.ForeignKey(
        'Especialidad', 
        on_delete=models.CASCADE,
        help_text="Especialidad requerida para realizar este servicio"
    )
    
    def __str__(self):
        return f"{self.nombre} ({self.especialidad.nombre})"
    
    class Meta:
        ordering = ['especialidad', 'nombre']


class Pago(models.Model):
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        related_name='pagos')
    cita = models.ForeignKey('Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, default='Efectivo')
    # Nuevos campos para facturación SAT
    forma_pago_sat = models.ForeignKey('SatFormaPago', on_delete=models.SET_NULL, null=True, blank=True)
    metodo_sat = models.ForeignKey('SatMetodoPago', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.cita:
            return f"Pago de ${self.monto} para la cita {self.cita.id}"
        return f"Abono de ${self.monto} para {self.paciente}"

class PlanPago(models.Model):
    FRECUENCIAS = [
        ('SEMANAL', 'Semanal'),
        ('MENSUAL', 'Mensual'),
    ]
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('CONCLUIDO', 'Concluido'),
        ('INCUMPLIDO', 'Incumplido'),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='planes_pago')
    cita = models.ForeignKey('Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name='planes_pago')
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIAS)
    numero_cuotas = models.PositiveIntegerField()
    fecha_inicio = models.DateField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ACTIVO')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        ref = f"Cita #{self.cita_id}" if self.cita_id else "Tratamiento"
        return f"Plan {ref} de {self.paciente} ({self.numero_cuotas} cuotas)"

    @property
    def total_pagado(self):
        return sum((c.monto for c in self.cuotas.filter(pagado=True)), start=0)

    @property
    def total_pendiente(self):
        return sum((c.monto for c in self.cuotas.filter(pagado=False)), start=0)

class CuotaPlan(models.Model):
    plan = models.ForeignKey(PlanPago, on_delete=models.CASCADE, related_name='cuotas')
    numero = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True, related_name='cuotas_asignadas')

    class Meta:
        unique_together = ('plan', 'numero')
        ordering = ['plan', 'numero']

    def __str__(self):
        return f"Cuota {self.numero} de {self.plan}"

# --- Modelos de Gestión de Inventario ---

class UnidadDental(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    dentistas_permitidos = models.ManyToManyField(
        PerfilDentista,
        blank=True,
        related_name='unidades_permitidas',
        help_text="Dentistas que pueden usar esta unidad"
    )

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre o Razón Social")
    rfc = models.CharField(max_length=13, unique=True, blank=True, null=True, verbose_name="RFC")
    nombre_contacto = models.CharField(max_length=100, blank=True, verbose_name="Nombre del Contacto")
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion_fiscal = models.TextField(blank=True, verbose_name="Dirección Fiscal")

    def __str__(self):
        return self.nombre
class Insumo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, editable=False, help_text="Este campo se calcula automáticamente a partir de los lotes.")
    stock_minimo = models.PositiveIntegerField(default=10, help_text="Nivel de stock global para generar alertas.")
    requiere_lote_caducidad = models.BooleanField(default=False, help_text="Marcar si este insumo necesita seguimiento por lote y caducidad (COFEPRIS).")
    registro_sanitario = models.CharField(max_length=100, blank=True, null=True, help_text="Registro COFEPRIS del insumo, si aplica.")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Precio unitario del insumo.")
    unidad_medida = models.CharField(max_length=50, blank=True, help_text="Unidad de medida del insumo (ej. pieza, litro, kg).")

    def __str__(self):
        return self.nombre

    def actualizar_stock_total(self):
        total = self.lotes.aggregate(total_cantidad=Sum('cantidad'))['total_cantidad'] or 0
        self.stock = total
        self.save(update_fields=['stock'])

class LoteInsumo(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='lotes')
    unidad_dental = models.ForeignKey(UnidadDental, on_delete=models.CASCADE, related_name='lotes_insumos')
    cantidad = models.PositiveIntegerField(default=0)
    numero_lote = models.CharField(max_length=100, blank=True, null=True)
    fecha_caducidad = models.DateField(blank=True, null=True)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad} de {self.insumo.nombre} (Lote: {self.numero_lote or 'N/A'}) en {self.unidad_dental.nombre}"

class ServicioInsumo(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.servicio.nombre} consume {self.cantidad} de {self.insumo.nombre}"

class Compra(models.Model):
    ESTADOS_COMPRA = [
        ('PENDIENTE', 'Pendiente'),
        ('RECIBIDA', 'Recibida'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    TIPOS_COMPRA = [
        ('EXTERNA', 'Compra Externa'),
        ('INTERNA', 'Transferencia Interna'),
        ('AJUSTE', 'Ajuste de Inventario'),
    ]
    
    # PROVEEDOR AHORA OPCIONAL
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Opcional para compras internas"
    )
    
    tipo_compra = models.CharField(
        max_length=10, 
        choices=TIPOS_COMPRA, 
        default='EXTERNA'
    )
    
    fecha_compra = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADOS_COMPRA, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    factura_adjunta = models.FileField(upload_to='facturas/', blank=True, null=True)
    notas = models.TextField(blank=True)
    
    def __str__(self):
        if self.proveedor:
            return f"Compra a {self.proveedor.nombre} - {self.fecha_compra.strftime('%d/%m/%Y')}"
        else:
            return f"Compra {self.get_tipo_compra_display()} - {self.fecha_compra.strftime('%d/%m/%Y')}"
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.insumo.nombre} en {self.compra}"

# --- Modelos de Gestión Clínica ---

class Cita(models.Model):
    ESTADOS_CITA = [
        ('PRO', 'Programada'),
        ('CON', 'Confirmada'),
        ('ATN', 'Atendida'),
        ('COM', 'Completada'),
        ('CAN', 'Cancelada'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    dentista = models.ForeignKey(PerfilDentista, on_delete=models.PROTECT)
    unidad_dental = models.ForeignKey(UnidadDental, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    
    # SERVICIOS PLANEADOS (al agendar)
    servicios_planeados = models.ManyToManyField(
        'Servicio',
        related_name='citas_planeadas',
        blank=True,
        help_text="Servicios que se planea realizar"
    )
    
    # SERVICIOS REALIZADOS (al finalizar cita) - CAMPO EXISTENTE
    servicios_realizados = models.ManyToManyField(
        'Servicio', 
        related_name='citas_realizadas',
        blank=True,
        help_text="Servicios que realmente se realizaron"
    )
    
    motivo = models.TextField(
        max_length=500, 
        blank=True,
        help_text="Síntomas específicos o notas adicionales"
    )
    
    estado = models.CharField(max_length=3, choices=ESTADOS_CITA, default='PRO')
    notas = models.TextField(blank=True)
    requiere_factura = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    
    
    @property
    def costo_estimado(self):
        return sum(servicio.precio for servicio in self.servicios_planeados.all())
    
    @property
    def costo_real(self):
        return sum(servicio.precio for servicio in self.servicios_realizados.all())
    
    @property
    def duracion_estimada(self):
        return sum(servicio.duracion_minutos for servicio in self.servicios_planeados.all())
    
    @property
    def total_pagado(self):
        return self.pagos.aggregate(total=models.Sum('monto'))['total'] or 0
    
    @property
    def saldo_pendiente(self):
        return self.costo_real - self.total_pagado
class Diagnostico(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color_hex = models.CharField(max_length=7, default='#FFFFFF', help_text="Color de fondo por defecto para este diagnóstico.")
    icono_svg = models.TextField(blank=True, help_text="Código SVG del icono para superponer en el diente.")
    
    def __str__(self):
        return self.nombre

class HistorialClinico(models.Model):
    TIPOS_REGISTRO = [
        ('CONSULTA', 'Consulta General'),
        ('DIAGNOSTICO', 'Diagnóstico'),
        ('TRATAMIENTO', 'Tratamiento Realizado'),
        ('SEGUIMIENTO', 'Seguimiento'),
        ('EMERGENCIA', 'Emergencia'),
        ('OBSERVACION', 'Observación General'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='historial_clinico')
    fecha_evento = models.DateTimeField(auto_now_add=True)
    tipo_registro = models.CharField(
        max_length=15,
        choices=TIPOS_REGISTRO,
        default='CONSULTA',
        help_text="Tipo de registro clínico"
    )
    descripcion_evento = models.TextField()
    registrado_por = models.ForeignKey(
        PerfilDentista,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Dentista o personal que registra la entrada"
    )
    # Opcional: vincular con cita específica
    cita = models.ForeignKey(
        'Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entradas_historial',
        help_text="Cita asociada a este registro (opcional)"
    )

    class Meta:
        ordering = ['-fecha_evento']
        verbose_name = 'Entrada de Historial Clínico'
        verbose_name_plural = 'Entradas de Historial Clínico'

    def __str__(self):
        return f"{self.get_tipo_registro_display()} - {self.paciente} ({self.fecha_evento.strftime('%d/%m/%Y %H:%M')})"

class EstadoDiente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='odontograma')
    numero_diente = models.IntegerField()
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.PROTECT)
    color_seleccionado = models.CharField(max_length=7, blank=True, help_text="Color personalizado para el fondo del diente (ej. resinas).")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('paciente', 'numero_diente')
        verbose_name = 'Estado Actual de Diente'
        verbose_name_plural = 'Estados Actuales de Dientes'

    def __str__(self):
        return f"Diente {self.numero_diente} de {self.paciente}: {self.diagnostico.nombre}"

# --- Modelos para Seguimiento Dental Completo ---

class HistorialEstadoDiente(models.Model):
    """
    Registra TODOS los cambios de estado de cada diente
    Permite trazabilidad completa del tratamiento dental
    
    Ejemplo de flujo:
    - Diente 16: Sano → Cariado (diagnóstico)
    - Diente 16: Cariado → Obturado (tratamiento)
    """
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='historial_dental'
    )
    numero_diente = models.IntegerField(
        help_text="Número del diente según sistema FDI (11-48)"
    )
    
    # ESTADO ANTERIOR
    diagnostico_anterior = models.ForeignKey(
        Diagnostico,
        on_delete=models.PROTECT,
        related_name='cambios_desde',
        null=True, blank=True,
        help_text="Estado previo del diente (null si es primer registro)"
    )
    
    # ESTADO NUEVO
    diagnostico_nuevo = models.ForeignKey(
        Diagnostico,
        on_delete=models.PROTECT,
        related_name='cambios_hacia',
        help_text="Nuevo estado del diente después del tratamiento"
    )
    
    # TRAZABILIDAD
    cita = models.ForeignKey(
        'Cita',
        on_delete=models.PROTECT,
        related_name='cambios_dentales',
        help_text="Cita donde se realizó el cambio"
    )
    dentista = models.ForeignKey(
        PerfilDentista,
        on_delete=models.PROTECT,
        help_text="Dentista responsable del tratamiento" 
    )
    fecha_cambio = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del cambio de estado"
    )
    
    # DETALLES DEL TRATAMIENTO
    tratamiento_realizado = models.TextField(
        help_text="Descripción detallada del tratamiento que generó el cambio"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Notas adicionales del dentista sobre el tratamiento"
    )
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Historial de Estado de Diente'
        verbose_name_plural = 'Historial de Estados de Dientes'
        indexes = [
            models.Index(fields=['paciente', 'numero_diente']),
            models.Index(fields=['fecha_cambio']),
        ]
    
    def __str__(self):
        anterior = self.diagnostico_anterior.nombre if self.diagnostico_anterior else "Inicial"
        return f"Diente {self.numero_diente}: {anterior} → {self.diagnostico_nuevo.nombre} ({self.fecha_cambio.strftime('%d/%m/%Y')})"

class TratamientoCita(models.Model):
    """
    Registra tratamientos específicos realizados en cada cita
    Vincula cita → tratamiento → dientes afectados → estados
    
    Permite registrar múltiples tratamientos por cita y el estado
    antes/después de cada diente tratado.
    """
    cita = models.ForeignKey(
        'Cita',
        on_delete=models.CASCADE,
        related_name='tratamientos_realizados'
    )
    
    # DIENTES TRATADOS
    dientes_tratados = models.CharField(
        max_length=200,
        help_text="Números de dientes tratados separados por comas (ej: 16,17,18)"
    )
    
    # DESCRIPCIÓN DEL TRATAMIENTO
    descripcion = models.TextField(
        help_text="Descripción detallada del tratamiento realizado"
    )
    
    # SERVICIOS APLICADOS
    servicios = models.ManyToManyField(
        'Servicio',
        blank=True,
        help_text="Servicios facturables aplicados en este tratamiento"
    )
    
    # ESTADOS DESCRIPTIVOS
    estado_inicial_descripcion = models.TextField(
        help_text="Descripción del estado de los dientes antes del tratamiento"
    )
    estado_final_descripcion = models.TextField(
        help_text="Descripción del estado de los dientes después del tratamiento" 
    )
    
    # PENDIENTES Y SEGUIMIENTO
    trabajo_pendiente = models.TextField(
        blank=True,
        help_text="Trabajo que queda pendiente para próximas citas"
    )
    requiere_seguimiento = models.BooleanField(
        default=False,
        help_text="Si este tratamiento requiere cita de seguimiento"
    )
    fecha_seguimiento_sugerida = models.DateField(
        null=True, blank=True,
        help_text="Fecha sugerida para cita de seguimiento"
    )
    
    # METADATOS
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        PerfilDentista,
        on_delete=models.PROTECT,
        help_text="Dentista que registra el tratamiento"
    )
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Tratamiento de Cita'
        verbose_name_plural = 'Tratamientos de Citas'
    
    def __str__(self):
        return f"Tratamiento en cita {self.cita.id} - Dientes: {self.dientes_tratados} ({self.fecha_registro.strftime('%d/%m/%Y')})"
    
    def get_dientes_list(self):
        """Devuelve lista de números de dientes tratados"""
        return [int(d.strip()) for d in self.dientes_tratados.split(',') if d.strip()]
    
    @property
    def dientes_formateados(self):
        """Devuelve los dientes en formato legible"""
        dientes = self.get_dientes_list()
        if len(dientes) == 1:
            return f"Diente {dientes[0]}"
        elif len(dientes) <= 3:
            return f"Dientes {', '.join(map(str, dientes))}"
        else:
            return f"Dientes {', '.join(map(str, dientes[:3]))} y {len(dientes)-3} más"

# --- Modelos de Gestión de Cumplimiento (COFEPRIS) ---

class AvisoFuncionamiento(models.Model):
    consultorio = models.ForeignKey('tenants.Clinica', on_delete=models.CASCADE, related_name='avisos_funcionamiento')
    responsable_sanitario = models.CharField(max_length=255)
    cedula_profesional = models.CharField(max_length=100)
    fecha_presentacion = models.DateField()
    certificado_pdf = models.FileField(upload_to='cofepris/avisos/', blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Aviso de Funcionamiento para {self.consultorio.nombre}"

class Equipo(models.Model):
    unidad_trabajo = models.ForeignKey(UnidadDental, on_delete=models.CASCADE, related_name='equipos')
    nombre = models.CharField(max_length=200)
    registro_sanitario = models.CharField(max_length=100, blank=True, null=True)
    certificado_bpm = models.FileField(upload_to='cofepris/equipos/', blank=True, null=True, verbose_name="Certificado de Buenas Prácticas de Fabricación")
    fecha_calibracion = models.DateField()
    fecha_vencimiento_calibracion = models.DateField()

    def __str__(self):
        return f"{self.nombre} en {self.unidad_trabajo.nombre}"

class Residuos(models.Model):
    consultorio = models.ForeignKey('tenants.Clinica', on_delete=models.CASCADE, related_name='recolecciones_residuos')
    unidad_trabajo = models.ForeignKey(UnidadDental, on_delete=models.CASCADE, related_name='recolecciones_residuos')
    proveedor_recoleccion = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Empresa de recolección de RPBI. Puede dejarse en blanco si es un proveedor no registrado."
    )
    fecha_recoleccion = models.DateField()
    manifiesto_pdf = models.FileField(upload_to='cofepris/residuos/', blank=True, null=True)
    cantidad_kg = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Recolección RPBI del {self.fecha_recoleccion} en {self.unidad_trabajo.nombre}"

# --- Modelos para Cuestionario de Historial Clínico ---

class CategoriaHistorial(models.Model):
    """Categorías para organizar preguntas del historial clínico según normativas mexicanas"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase de ícono CSS (ej: fas fa-heart)")
    color = models.CharField(max_length=7, default='#007bff', help_text="Color hexadecimal para la categoría")
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = 'Categoría de Historial'
        verbose_name_plural = 'Categorías de Historial'
    
    def __str__(self):
        return self.nombre

class PreguntaHistorial(models.Model):
    TIPO_PREGUNTA = [
        ('TEXT', 'Texto Corto'),
        ('TEXTAREA', 'Párrafo'),
        ('SI_NO', 'Sí / No'),
        ('MULTIPLE', 'Opción Múltiple'),
        ('FECHA', 'Fecha'),
        ('NUMERO', 'Número'),
        ('EMAIL', 'Email'),
        ('TELEFONO', 'Teléfono'),
    ]
    
    NIVEL_IMPORTANCIA = [
        ('BAJA', 'Informativa'),
        ('MEDIA', 'Importante'),
        ('ALTA', 'Crítica'),
        ('CRITICA', 'Emergencia Médica'),
    ]
    
    categoria = models.ForeignKey(CategoriaHistorial, on_delete=models.CASCADE, related_name='preguntas', null=True, blank=True)
    texto = models.CharField(max_length=500)
    subtitulo = models.CharField(max_length=300, blank=True, help_text="Explicación adicional o contexto")
    tipo = models.CharField(max_length=10, choices=TIPO_PREGUNTA, default='SI_NO')
    opciones = models.TextField(blank=True, help_text="Para opción múltiple, separar opciones con comas")
    orden = models.PositiveIntegerField(default=0)
    obligatoria = models.BooleanField(default=False)
    importancia = models.CharField(max_length=10, choices=NIVEL_IMPORTANCIA, default='MEDIA')
    activa = models.BooleanField(default=True)
    
    # Campos específicos para normativas mexicanas
    requiere_seguimiento = models.BooleanField(default=False, help_text="Si requiere seguimiento médico")
    alerta_cofepris = models.BooleanField(default=False, help_text="Si requiere reporte a COFEPRIS")
    
    class Meta:
        ordering = ['categoria__orden', 'orden']
        verbose_name = 'Pregunta de Historial'
        verbose_name_plural = 'Preguntas de Historial'
    
    def __str__(self):
        return f"{self.categoria.nombre}: {self.texto[:50]}..."
    
    def get_opciones_lista(self):
        """Retorna las opciones como lista"""
        if self.opciones:
            return [opcion.strip() for opcion in self.opciones.split(',')]
        return []

# Comentados temporalmente para evitar conflictos de migración
# Se implementarán en la siguiente fase
"""
class AntecedenteFamiliar(models.Model):
    # ... modelo completo se agregará después de resolver migraciones ...
    pass

class MaloHabitoOral(models.Model):
    # ... modelo completo se agregará después de resolver migraciones ...
    pass

class EscalaDolor(models.Model):
    # ... modelo completo se agregará después de resolver migraciones ...
    pass
"""

class RespuestaHistorial(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='respuestas_historial')
    pregunta = models.ForeignKey(PreguntaHistorial, on_delete=models.CASCADE)
    respuesta = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='respuestas_actualizadas'
    )
    
    # Campo para marcar respuestas que requieren atención médica
    requiere_atencion = models.BooleanField(default=False)
    notas_medicas = models.TextField(blank=True, help_text="Notas del dentista sobre esta respuesta")
    
    class Meta:
        unique_together = ('paciente', 'pregunta')
        verbose_name = 'Respuesta de Historial'
        verbose_name_plural = 'Respuestas de Historial'
    
    def __str__(self):
        return f"Respuesta de {self.paciente} a '{self.pregunta.texto[:30]}...'"
    
    def es_respuesta_critica(self):
        """Determina si la respuesta indica una condición crítica"""
        if self.pregunta.importancia == 'CRITICA':
            # Para preguntas críticas, 'Sí' indica problema
            if self.pregunta.tipo == 'SI_NO' and self.respuesta.lower() in ['sí', 'si', 'yes', '1', 'true']:
                return True
        return False

class CuestionarioCompletado(models.Model):
    """Registro de cuestionarios completados por pacientes"""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='cuestionarios_completados')
    fecha_completado = models.DateTimeField(auto_now_add=True)
    completado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Usuario que ayudó a completar el cuestionario (si aplica)"
    )
    
    # Campos para seguimiento
    tiempo_completado_minutos = models.PositiveIntegerField(null=True, blank=True)
    revision_medica = models.BooleanField(default=False, help_text="¿Ha sido revisado por el dentista?")
    revisado_por = models.ForeignKey(
        PerfilDentista,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuestionarios_revisados'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    notas_revision = models.TextField(blank=True)
    
    # Campos para alertas automáticas
    tiene_alertas = models.BooleanField(default=False)
    alertas_generadas = models.TextField(blank=True, help_text="Alertas automáticas generadas")
    
    # NUEVA INTEGRACIÓN CON CONSENTIMIENTO INFORMADO
    consentimiento_requerido = models.BooleanField(
        default=True,
        help_text="¿Se requiere consentimiento informado después del cuestionario?"
    )
    consentimiento_presentado = models.ForeignKey(
        'PacienteConsentimiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuestionarios_relacionados',
        help_text="Consentimiento informado presentado al paciente"
    )
    
    class Meta:
        ordering = ['-fecha_completado']
        verbose_name = 'Cuestionario Completado'
        verbose_name_plural = 'Cuestionarios Completados'
    
    def __str__(self):
        return f"Cuestionario de {self.paciente} - {self.fecha_completado.strftime('%d/%m/%Y')}"
    
    def generar_alertas(self):
        """Genera alertas basadas en las respuestas del paciente"""
        alertas = []
        
        for respuesta in self.paciente.respuestas_historial.all():
            if respuesta.es_respuesta_critica():
                alertas.append(f"⚠️ {respuesta.pregunta.categoria.nombre}: {respuesta.pregunta.texto}")
            
            if respuesta.pregunta.requiere_seguimiento and respuesta.respuesta.lower() in ['sí', 'si']:
                alertas.append(f"📋 Seguimiento: {respuesta.pregunta.texto}")
        
        self.alertas_generadas = '\n'.join(alertas)
        self.tiene_alertas = len(alertas) > 0
        self.save()
    
    def requiere_consentimiento_informado(self):
        """Determina si se requiere consentimiento informado basado en las respuestas"""
        if not self.consentimiento_requerido:
            return False
            
        # Si ya se presentó un consentimiento, verificar su estado
        if self.consentimiento_presentado:
            return self.consentimiento_presentado.estado == 'PENDIENTE'
        
        return True
    
    def determinar_tipo_consentimiento(self):
        """Determina qué tipo de consentimiento se necesita según las respuestas"""
        # Analizar respuestas para determinar el tipo de consentimiento más apropiado
        respuestas_criticas = self.paciente.respuestas_historial.filter(
            pregunta__importancia__in=['ALTA', 'CRITICA']
        )
        
        # Lógica para determinar tipo de consentimiento
        tipos_detectados = set()
        
        for respuesta in respuestas_criticas:
            texto_respuesta = respuesta.respuesta.lower()
            texto_pregunta = respuesta.pregunta.texto.lower()
            
            # Detectar tipos de procedimientos basados en las respuestas
            if any(keyword in texto_pregunta for keyword in ['cirugía', 'extracción', 'implante']):
                tipos_detectados.add('CIRUGIA')
            elif any(keyword in texto_pregunta for keyword in ['ortodoncia', 'brackets', 'alineadores']):
                tipos_detectados.add('ORTODONTICA')
            elif any(keyword in texto_pregunta for keyword in ['endodoncia', 'conducto']):
                tipos_detectados.add('ENDODONCIA')
            elif any(keyword in texto_pregunta for keyword in ['blanqueamiento', 'estética']):
                tipos_detectados.add('ESTETICA')
        
        # Si no se detectó un tipo específico, usar general
        if not tipos_detectados:
            return 'GENERAL'
        
        # Si hay múltiples tipos, priorizar cirugía
        if 'CIRUGIA' in tipos_detectados:
            return 'CIRUGIA'
        
        # Retornar el primer tipo detectado
        return list(tipos_detectados)[0]
    
    def presentar_consentimiento(self, tipo_documento=None, dentista=None):
        """Presenta un consentimiento informado al paciente"""
        if not self.consentimiento_requerido:
            return None
            
        # Si ya existe un consentimiento pendiente, retornarlo
        if self.consentimiento_presentado and self.consentimiento_presentado.estado == 'PENDIENTE':
            return self.consentimiento_presentado
        
        # Determinar tipo de consentimiento si no se especifica
        if not tipo_documento:
            tipo_documento = self.determinar_tipo_consentimiento()
        
        # Buscar documento vigente
        documento_consentimiento = ConsentimientoInformado.get_documento_vigente(tipo_documento)
        
        if not documento_consentimiento:
            # Si no hay documento vigente, usar el general
            documento_consentimiento = ConsentimientoInformado.get_documento_vigente('GENERAL')
        
        if documento_consentimiento:
            # Crear registro de consentimiento para el paciente
            paciente_consentimiento = PacienteConsentimiento.objects.create(
                paciente=self.paciente,
                consentimiento=documento_consentimiento,
                presentado_por=dentista
            )
            
            # Asociar con este cuestionario
            self.consentimiento_presentado = paciente_consentimiento
            self.save()
            
            return paciente_consentimiento
        
        return None
    
    def estado_consentimiento(self):
        """Retorna el estado del consentimiento asociado"""
        if not self.consentimiento_requerido:
            return 'NO_REQUERIDO'
            
        if not self.consentimiento_presentado:
            return 'PENDIENTE_PRESENTACION'
            
        return self.consentimiento_presentado.estado
    
    def puede_proceder_con_tratamiento(self):
        """Verifica si se puede proceder con el tratamiento"""
        # Cuestionario debe estar revisado médicamente
        if not self.revision_medica:
            return False, "El cuestionario debe ser revisado por un dentista"
            
        # Si se requiere consentimiento, debe estar firmado
        if self.consentimiento_requerido:
            if not self.consentimiento_presentado:
                return False, "Se requiere presentar consentimiento informado"
            
            if self.consentimiento_presentado.estado != 'FIRMADO':
                return False, "El consentimiento informado debe estar firmado"
        
        return True, "Puede proceder con el tratamiento"

# --- Modelo para Consentimiento Informado ---

class ConsentimientoInformado(models.Model):
    """Modelo para gestionar documentos PDF de consentimiento informado"""
    TIPOS_DOCUMENTO = [
        ('GENERAL', 'Consentimiento General'),
        ('CIRUGIA', 'Consentimiento Cirugía Oral'),
        ('ORTODONTICA', 'Consentimiento Ortodoncia'),
        ('ENDODONCIA', 'Consentimiento Endodoncia'),
        ('IMPLANTES', 'Consentimiento Implantes'),
        ('ESTETICA', 'Consentimiento Estética Dental'),
        ('PERIODONCIA', 'Consentimiento Periodoncia'),
        ('PROTESIS', 'Consentimiento Prótesis'),
        ('PEDIATRICA', 'Consentimiento Odontología Pediátrica'),
        ('OTROS', 'Otros Procedimientos'),
    ]
    
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('ARCHIVADO', 'Archivado'),
    ]
    
    titulo = models.CharField(max_length=200, help_text="Título descriptivo del documento")
    tipo_documento = models.CharField(max_length=20, choices=TIPOS_DOCUMENTO, default='GENERAL')
    descripcion = models.TextField(blank=True, help_text="Descripción del contenido del documento")
    
    # Archivo PDF
    archivo_pdf = models.FileField(
        upload_to='consentimientos/',
        help_text="Documento PDF del consentimiento informado"
    )
    
    # Metadatos del archivo
    nombre_archivo_original = models.CharField(max_length=255, blank=True)
    tamaño_archivo = models.PositiveIntegerField(null=True, blank=True, help_text="Tamaño en bytes")
    
    # Control de versiones
    version = models.CharField(max_length=20, default='1.0')
    version_anterior = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versiones_posteriores',
        help_text="Versión anterior de este documento"
    )
    
    # Estado y validez
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO')
    fecha_vigencia_inicio = models.DateField(help_text="Fecha de inicio de vigencia")
    fecha_vigencia_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de fin de vigencia (opcional)"
    )
    
    # Información legal y regulatoria
    cumple_cofepris = models.BooleanField(
        default=True,
        help_text="Cumple con normativas COFEPRIS"
    )
    requiere_testigos = models.BooleanField(
        default=False,
        help_text="Requiere firma de testigos"
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consentimientos_creados'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consentimientos_actualizados'
    )
    
    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Consentimiento Informado'
        verbose_name_plural = 'Consentimientos Informados'
    
    def __str__(self):
        return f"{self.titulo} v{self.version} ({self.get_tipo_documento_display()})"
    
    def esta_vigente(self):
        """Verifica si el documento está vigente en la fecha actual"""
        from datetime import date
        today = date.today()
        
        if self.estado != 'ACTIVO':
            return False
            
        if today < self.fecha_vigencia_inicio:
            return False
            
        if self.fecha_vigencia_fin and today > self.fecha_vigencia_fin:
            return False
            
        return True
    
    def save(self, *args, **kwargs):
        """Override save para almacenar metadatos del archivo"""
        if self.archivo_pdf:
            self.nombre_archivo_original = self.archivo_pdf.name
            # Intentar obtener el tamaño del archivo
            try:
                self.tamaño_archivo = self.archivo_pdf.size
            except (AttributeError, ValueError):
                pass
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_documento_vigente(cls, tipo_documento='GENERAL'):
        """Obtiene el documento vigente para un tipo específico"""
        from datetime import date
        today = date.today()
        
        return cls.objects.filter(
            tipo_documento=tipo_documento,
            estado='ACTIVO',
            fecha_vigencia_inicio__lte=today
        ).filter(
            models.Q(fecha_vigencia_fin__isnull=True) |
            models.Q(fecha_vigencia_fin__gte=today)
        ).order_by('-version', '-creado_en').first()

class PacienteConsentimiento(models.Model):
    """Registro de consentimientos firmados por pacientes"""
    ESTADOS_FIRMA = [
        ('PENDIENTE', 'Pendiente'),
        ('FIRMADO', 'Firmado'),
        ('RECHAZADO', 'Rechazado'),
        ('VENCIDO', 'Vencido'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='consentimientos')
    consentimiento = models.ForeignKey(ConsentimientoInformado, on_delete=models.PROTECT)
    cita = models.ForeignKey(
        'Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Cita asociada al consentimiento"
    )
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADOS_FIRMA, default='PENDIENTE')
    fecha_presentado = models.DateTimeField(auto_now_add=True)
    fecha_firmado = models.DateTimeField(null=True, blank=True)
    
    # Firmas digitales
    firma_paciente = models.ImageField(
        upload_to='firmas_consentimiento/',
        null=True,
        blank=True,
        help_text="Firma digital del paciente"
    )
    firma_testigo1 = models.ImageField(
        upload_to='firmas_consentimiento/',
        null=True,
        blank=True,
        help_text="Firma del primer testigo"
    )
    firma_testigo2 = models.ImageField(
        upload_to='firmas_consentimiento/',
        null=True,
        blank=True,
        help_text="Firma del segundo testigo"
    )
    
    # Información de testigos
    nombre_testigo1 = models.CharField(max_length=200, blank=True)
    nombre_testigo2 = models.CharField(max_length=200, blank=True)
    
    # Dentista que presenta el consentimiento
    presentado_por = models.ForeignKey(
        PerfilDentista,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consentimientos_presentados'
    )
    
    # Notas adicionales
    notas = models.TextField(
        blank=True,
        help_text="Observaciones sobre el proceso de consentimiento"
    )
    
    class Meta:
        ordering = ['-fecha_presentado']
        verbose_name = 'Consentimiento de Paciente'
        verbose_name_plural = 'Consentimientos de Pacientes'
    
    def __str__(self):
        return f"{self.paciente} - {self.consentimiento.titulo} ({self.estado})"
    
    def esta_completo(self):
        """Verifica si el consentimiento está completamente firmado"""
        if not self.firma_paciente:
            return False
            
        if self.consentimiento.requiere_testigos:
            return bool(self.firma_testigo1 and self.nombre_testigo1)
            
        return True
    
    def marcar_como_firmado(self):
        """Marca el consentimiento como firmado si está completo"""
        if self.esta_completo() and self.estado == 'PENDIENTE':
            self.estado = 'FIRMADO'
            self.fecha_firmado = timezone.now()
            self.save()
            return True
        return False

# Importar modelos de permisos dinámicos
from .models_permissions import ModuloSistema, SubmenuItem, PermisoRol, LogAcceso

# --- FUNCIONES HELPER PARA GESTIÓN CLÍNICA ---

def actualizar_estado_diente(paciente, numero_diente, diagnostico_nuevo, cita, tratamiento_descripcion, observaciones=''):
    """
    Función helper para actualizar estado de diente manteniendo historial completo
    
    Args:
        paciente: Instancia del modelo Paciente
        numero_diente: Número del diente (sistema FDI)
        diagnostico_nuevo: Instancia del modelo Diagnostico
        cita: Instancia del modelo Cita
        tratamiento_descripcion: Descripción del tratamiento realizado
        observaciones: Observaciones adicionales (opcional)
    
    Returns:
        tuple: (estado_diente, historial_creado)
    """
    # Obtener estado actual (si existe)
    estado_actual, created = EstadoDiente.objects.get_or_create(
        paciente=paciente,
        numero_diente=numero_diente,
        defaults={'diagnostico': diagnostico_nuevo}
    )
    
    diagnostico_anterior = None if created else estado_actual.diagnostico
    historial_creado = False
    
    # Solo crear historial si realmente cambió el estado
    if not created and diagnostico_anterior != diagnostico_nuevo:
        # Crear registro en historial
        HistorialEstadoDiente.objects.create(
            paciente=paciente,
            numero_diente=numero_diente,
            diagnostico_anterior=diagnostico_anterior,
            diagnostico_nuevo=diagnostico_nuevo,
            cita=cita,
            dentista=cita.dentista,
            tratamiento_realizado=tratamiento_descripcion,
            observaciones=observaciones
        )
        
        # Actualizar estado actual
        estado_actual.diagnostico = diagnostico_nuevo
        estado_actual.save()
        historial_creado = True
    
    elif created:
        # Es el primer estado del diente, crear historial inicial
        HistorialEstadoDiente.objects.create(
            paciente=paciente,
            numero_diente=numero_diente,
            diagnostico_anterior=None,
            diagnostico_nuevo=diagnostico_nuevo,
            cita=cita,
            dentista=cita.dentista,
            tratamiento_realizado=tratamiento_descripcion,
            observaciones=f"Estado inicial del diente. {observaciones}".strip()
        )
        historial_creado = True
    
    return estado_actual, historial_creado

def procesar_tratamiento_cita(cita, dientes_tratados_str, descripcion_tratamiento, 
                             estado_inicial_desc, estado_final_desc, diagnostico_final,
                             servicios_ids=None, trabajo_pendiente='', requiere_seguimiento=False,
                             fecha_seguimiento=None):
    """
    Función helper para procesar un tratamiento completo en una cita
    
    Args:
        cita: Instancia del modelo Cita
        dientes_tratados_str: String con números de dientes separados por comas (ej: '16,17,18')
        descripcion_tratamiento: Descripción del tratamiento realizado
        estado_inicial_desc: Descripción del estado inicial de los dientes
        estado_final_desc: Descripción del estado final de los dientes
        diagnostico_final: Instancia del modelo Diagnostico (estado final)
        servicios_ids: Lista de IDs de servicios aplicados (opcional)
        trabajo_pendiente: Descripción del trabajo pendiente (opcional)
        requiere_seguimiento: Si requiere cita de seguimiento
        fecha_seguimiento: Fecha sugerida para seguimiento (opcional)
    
    Returns:
        tuple: (tratamiento_cita, estados_actualizados, historial_creado)
    """
    # Crear registro de tratamiento
    tratamiento = TratamientoCita.objects.create(
        cita=cita,
        dientes_tratados=dientes_tratados_str,
        descripcion=descripcion_tratamiento,
        estado_inicial_descripcion=estado_inicial_desc,
        estado_final_descripcion=estado_final_desc,
        trabajo_pendiente=trabajo_pendiente,
        requiere_seguimiento=requiere_seguimiento,
        fecha_seguimiento_sugerida=fecha_seguimiento,
        registrado_por=cita.dentista
    )
    
    # Agregar servicios si se especifican
    if servicios_ids:
        from .models import Servicio
        servicios = Servicio.objects.filter(id__in=servicios_ids)
        tratamiento.servicios.set(servicios)
    
    # Actualizar estado de cada diente tratado
    dientes_list = [int(d.strip()) for d in dientes_tratados_str.split(',') if d.strip()]
    estados_actualizados = []
    historial_entries = []
    
    for numero_diente in dientes_list:
        estado, historial_creado = actualizar_estado_diente(
            paciente=cita.paciente,
            numero_diente=numero_diente,
            diagnostico_nuevo=diagnostico_final,
            cita=cita,
            tratamiento_descripcion=descripcion_tratamiento
        )
        estados_actualizados.append(estado)
        if historial_creado:
            historial_entries.append(numero_diente)
    
    # Crear entrada en historial clínico general
    dientes_formateados = ', '.join(map(str, dientes_list))
    HistorialClinico.objects.create(
        paciente=cita.paciente,
        tipo_registro='TRATAMIENTO',
        descripcion_evento=f"Tratamiento completado en dientes {dientes_formateados}: {descripcion_tratamiento}",
        registrado_por=cita.dentista,
        cita=cita
    )
    
    return tratamiento, estados_actualizados, len(historial_entries)

def crear_entrada_historial_clinico(paciente, tipo_registro, descripcion, dentista, cita=None):
    """
    Función helper para crear entradas en el historial clínico
    
    Args:
        paciente: Instancia del modelo Paciente
        tipo_registro: Tipo de registro ('CONSULTA', 'DIAGNOSTICO', etc.)
        descripcion: Descripción del evento
        dentista: Instancia del modelo PerfilDentista
        cita: Instancia del modelo Cita (opcional)
    
    Returns:
        HistorialClinico: La entrada creada
    """
    return HistorialClinico.objects.create(
        paciente=paciente,
        tipo_registro=tipo_registro,
        descripcion_evento=descripcion,
        registrado_por=dentista,
        cita=cita
    )

def obtener_historial_diente(paciente, numero_diente):
    """
    Obtiene el historial completo de cambios de un diente específico
    
    Args:
        paciente: Instancia del modelo Paciente
        numero_diente: Número del diente
    
    Returns:
        QuerySet: Historial de cambios ordenado cronológicamente
    """
    return HistorialEstadoDiente.objects.filter(
        paciente=paciente,
        numero_diente=numero_diente
    ).order_by('fecha_cambio')

def obtener_odontograma_completo(paciente):
    """
    Obtiene el estado actual completo del odontograma de un paciente
    
    Args:
        paciente: Instancia del modelo Paciente
    
    Returns:
        dict: Diccionario con número_diente como key y estado como value
    """
    estados = EstadoDiente.objects.filter(paciente=paciente).select_related('diagnostico')
    
    odontograma = {}
    for estado in estados:
        odontograma[estado.numero_diente] = {
            'diagnostico': estado.diagnostico.nombre,
            'color': estado.color_seleccionado or estado.diagnostico.color_hex,
            'icono': estado.diagnostico.icono_svg,
            'actualizado_en': estado.actualizado_en
        }
    
    return odontograma

def validar_numero_diente_fdi(numero_diente):
    """
    Valida que un número de diente sea válido según el sistema FDI
    
    Args:
        numero_diente: Número del diente a validar
    
    Returns:
        bool: True si es válido, False si no
    """
    dientes_validos = [
        # Cuadrante 1 (Superior derecho)
        11, 12, 13, 14, 15, 16, 17, 18,
        # Cuadrante 2 (Superior izquierdo) 
        21, 22, 23, 24, 25, 26, 27, 28,
        # Cuadrante 3 (Inferior izquierdo)
        31, 32, 33, 34, 35, 36, 37, 38,
        # Cuadrante 4 (Inferior derecho)
        41, 42, 43, 44, 45, 46, 47, 48
    ]
    
    return numero_diente in dientes_validos
