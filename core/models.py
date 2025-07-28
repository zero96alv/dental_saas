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
    direccion = models.TextField(blank=True, null=True)
    apto_para_plan_de_pago = models.BooleanField(default=False, help_text="Indica si el dentista ha autorizado un plan de pagos para este paciente.")
    consentimiento_cofepris = models.BooleanField(default=False, help_text="El paciente ha aceptado el aviso de privacidad y tratamiento de datos para COFEPRIS.")
    firma_consentimiento = models.ImageField(upload_to='firmas_consentimiento/', blank=True, null=True)
    saldo_global = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Saldo total pendiente del paciente.")

    def actualizar_saldo_global(self):
        from decimal import Decimal
        total_cargos = self.citas.filter(estado__in=['ATN', 'COM']).aggregate(
            total=Sum('servicios_realizados__precio')
        )['total'] or Decimal('0.00')
        
        total_pagos = self.pagos.all().aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')
        
        self.saldo_global = total_cargos - total_pagos
        self.save()

class DatosFiscales(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='datos_fiscales')
    rfc = models.CharField(max_length=13)
    razon_social = models.CharField(max_length=255)
    domicilio_fiscal = models.TextField()
    uso_cfdi = models.CharField(max_length=50, default='Gastos en General')

    def __str__(self):
        return f"Datos Fiscales de {self.paciente}"

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    # NUEVO: Jerarquía de especialidades
    especialidades_incluidas = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        help_text="Especialidades cuyos servicios también puede realizar"
    )
    
    def servicios_disponibles(self):
        """Obtener todos los servicios que puede realizar esta especialidad"""
        # Servicios propios
        servicios = self.servicio_set.filter(activo=True)
        
        # Servicios de especialidades incluidas
        for esp_incluida in self.especialidades_incluidas.all():
            servicios = servicios.union(esp_incluida.servicio_set.filter(activo=True))
        
        return servicios.distinct()

class PerfilDentista(PersonaBase):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_dentista')
    especialidades = models.ManyToManyField(Especialidad, blank=True)
    activo = models.BooleanField(default=True)

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

    def __str__(self):
        if self.cita:
            return f"Pago de ${self.monto} para la cita {self.cita.id}"
        return f"Abono de ${self.monto} para {self.paciente}"

# --- Modelos de Gestión de Inventario ---

class UnidadDental(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

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
    
    cliente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    dentista = models.ForeignKey(PerfilDentista, on_delete=models.CASCADE)
    unidad_dental = models.ForeignKey(UnidadDental, on_delete=models.CASCADE)
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
    cliente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='historial_clinico', null=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    descripcion_evento = models.TextField()
    registrado_por = models.ForeignKey(PerfilDentista, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"Entrada de historial para {self.cliente} el {self.fecha_evento.strftime('%Y-%m-%d')}"

class EstadoDiente(models.Model):
    cliente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='odontograma')
    numero_diente = models.IntegerField()
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.PROTECT)
    color_seleccionado = models.CharField(max_length=7, blank=True, help_text="Color personalizado para el fondo del diente (ej. resinas).")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cliente', 'numero_diente')

    def __str__(self):
        return f"Diente {self.numero_diente} de {self.cliente}: {self.diagnostico.nombre}"

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
    proveedor_recoleccion = models.CharField(max_length=255, help_text="Nombre de la empresa de recolección de RPBI.")
    fecha_recoleccion = models.DateField()
    manifiesto_pdf = models.FileField(upload_to='cofepris/residuos/')
    cantidad_kg = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Recolección RPBI del {self.fecha_recoleccion} en {self.unidad_trabajo.nombre}"

# --- Modelos para Cuestionario de Historial Clínico ---

class PreguntaHistorial(models.Model):
    TIPO_PREGUNTA = [
        ('TEXT', 'Texto Corto'),
        ('TEXTAREA', 'Párrafo'),
        ('SI_NO', 'Sí / No'),
        ('MULTIPLE', 'Opción Múltiple'),
    ]
    texto = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_PREGUNTA, default='SI_NO')
    opciones = models.CharField(max_length=500, blank=True, help_text="Para opción múltiple, separar opciones con comas (ej. A,B,C)")
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.texto

class RespuestaHistorial(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='respuestas_historial')
    pregunta = models.ForeignKey(PreguntaHistorial, on_delete=models.CASCADE)
    respuesta = models.TextField()
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('paciente', 'pregunta')

    def __str__(self):
        return f"Respuesta de {self.paciente} a '{self.pregunta}'"
