from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet, modelformset_factory
from datetime import timedelta

# Importar modelos solo para type hinting si es necesario o dentro de los métodos
from . import models
from django.forms import BaseFormSet

class PacienteFiltroForm(forms.Form):
    """Formulario para filtrar la lista de pacientes"""
    ESTADO_HISTORIAL_CHOICES = [
        ('', 'Todos'),
        ('completo', 'Historial completo'),
        ('pendiente', 'Sin historial'),
        ('actualizar', 'Necesita actualización (>3 meses)'),
    ]
    
    ORDENAR_POR_CHOICES = [
        ('nombre', 'Nombre A-Z'),
        ('-nombre', 'Nombre Z-A'),
        ('apellido', 'Apellido A-Z'),
        ('-apellido', 'Apellido Z-A'),
        ('-creado_en', 'Más recientes'),
        ('creado_en', 'Más antiguos'),
        ('saldo_global', 'Menor saldo'),
        ('-saldo_global', 'Mayor saldo'),
    ]
    
    busqueda = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido, email o teléfono...',
            'autocomplete': 'off'
        }),
        label='Búsqueda'
    )
    
    estado_historial = forms.ChoiceField(
        choices=ESTADO_HISTORIAL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Estado del Historial'
    )
    
    ordenar_por = forms.ChoiceField(
        choices=ORDENAR_POR_CHOICES,
        required=False,
        initial='nombre',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Ordenar por'
    )
    
    con_saldo_pendiente = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Solo pacientes con saldo pendiente'
    )
    
    con_acceso_portal = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Solo pacientes con acceso al portal'
    )

class PacienteForm(forms.ModelForm):
    telefono = forms.RegexField(
        regex=r'^(\+?52)?\s?\d{2,3}?[-\s]?\d{3}[-\s]?\d{4}$',
        required=False,
        label='Teléfono',
        error_messages={'invalid': 'Ingrese un teléfono válido (ej. 55 1234 5678).'}
    )

    class Meta:
        model = models.Paciente
        fields = [
            'nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento',
            'calle', 'numero_exterior', 'codigo_postal', 'colonia', 'municipio', 'estado'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '55 1234 5678'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_exterior': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'pattern': '\\d{5}', 'title': '5 dígitos'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Forzar email requerido a nivel de formulario
        self.fields['email'].required = True
        # Asegurar formato de fecha compatible con input type=date
        self.fields['fecha_nacimiento'].input_formats = ['%Y-%m-%d']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('El email es obligatorio.')
        qs = models.Paciente.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un paciente con este email.')
        return email

class HistorialClinicoForm(forms.ModelForm):
    dientes_seleccionados = forms.CharField(widget=forms.HiddenInput(), required=False)
    diagnostico = forms.ModelChoiceField(queryset=models.Diagnostico.objects.all(), label="Nuevo Diagnóstico para Dientes Seleccionados")

    class Meta:
        model = models.HistorialClinico
        fields = ['descripcion_evento', 'diagnostico', 'dientes_seleccionados']
        widgets = {'descripcion_evento': forms.Textarea(attrs={'rows': 4})}

class UserForm(forms.ModelForm):
    rol = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.fields['rol'].initial = self.instance.groups.first()
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        # Diferir asignación de grupos si el usuario aún no tiene ID
        self._rol_to_set = self.cleaned_data.get('rol')
        if commit and self._rol_to_set:
            user.groups.set([self._rol_to_set])
        return user

    def save_m2m(self):
        super().save_m2m()
        # Asignar grupo cuando ya exista ID (después de save en la vista)
        if hasattr(self, '_rol_to_set') and self._rol_to_set and self.instance.pk:
            self.instance.groups.set([self._rol_to_set])

class PerfilDentistaForm(forms.ModelForm):
    class Meta:
        model = models.PerfilDentista
        fields = ['telefono', 'titulo_profesional', 'cedula_profesional', 'foto', 'especialidades', 'activo']
        widgets = {
            'especialidades': forms.CheckboxSelectMultiple(),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo_profesional': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg', 'data-allowed': 'application/pdf,image/jpeg'}),
            'cedula_profesional': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg', 'data-allowed': 'application/pdf,image/jpeg'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg', 'data-allowed': 'image/jpeg'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'especialidades': 'Especialidades del Dentista',
            'telefono': 'Teléfono',
            'titulo_profesional': 'Título Profesional',
            'cedula_profesional': 'Cédula Profesional',
            'foto': 'Foto del Dentista',
            'activo': 'Usuario Activo',
        }
        help_texts = {
            'especialidades': 'Seleccione una o más especialidades que maneja este dentista.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especialidades'].label_from_instance = lambda obj: obj.nombre
        
        # Ordenar especialidades alfabéticamente
        self.fields['especialidades'].queryset = self.fields['especialidades'].queryset.order_by('nombre')

    # Validaciones de tamaño y tipo de archivo
    def _validate_upload(self, f, allowed_content_types, allowed_exts, max_size_bytes, nombre_campo):
        # Si es un archivo subido (no un FieldFile existente), validarlo
        try:
            from django.core.files.uploadedfile import UploadedFile
            is_uploaded = isinstance(f, UploadedFile)
        except Exception:
            is_uploaded = hasattr(f, 'content_type') and hasattr(f, 'size')
        if not f or not is_uploaded:
            return f
        content_type = getattr(f, 'content_type', '') or ''
        name_lower = (getattr(f, 'name', '') or '').lower()
        # Validar tipo
        if content_type not in allowed_content_types and not any(name_lower.endswith(ext) for ext in allowed_exts):
            raise ValidationError(f"El archivo de '{nombre_campo}' debe ser de tipo: {', '.join(allowed_exts)}")
        # Validar tamaño
        size = getattr(f, 'size', 0) or 0
        if size > max_size_bytes:
            from math import ceil
            mb = ceil(max_size_bytes / (1024*1024))
            raise ValidationError(f"El archivo de '{nombre_campo}' es demasiado grande. Máximo {mb} MB.")
        return f

    def clean_titulo_profesional(self):
        f = self.cleaned_data.get('titulo_profesional')
        if not f:
            return f
        content_type = getattr(f, 'content_type', '') or ''
        max_size = 5 * 1024 * 1024 if content_type == 'application/pdf' else 3 * 1024 * 1024
        return self._validate_upload(
            f,
            allowed_content_types={'application/pdf', 'image/jpeg'},
            allowed_exts=['.pdf', '.jpg', '.jpeg'],
            max_size_bytes=max_size,
            nombre_campo='Título profesional'
        )

    def clean_cedula_profesional(self):
        f = self.cleaned_data.get('cedula_profesional')
        if not f:
            return f
        content_type = getattr(f, 'content_type', '') or ''
        max_size = 5 * 1024 * 1024 if content_type == 'application/pdf' else 3 * 1024 * 1024
        return self._validate_upload(
            f,
            allowed_content_types={'application/pdf', 'image/jpeg'},
            allowed_exts=['.pdf', '.jpg', '.jpeg'],
            max_size_bytes=max_size,
            nombre_campo='Cédula profesional'
        )

    def clean_foto(self):
        f = self.cleaned_data.get('foto')
        return self._validate_upload(
            f,
            allowed_content_types={'image/jpeg'},
            allowed_exts=['.jpg', '.jpeg'],
            max_size_bytes=3 * 1024 * 1024,  # 3 MB
            nombre_campo='Foto'
        )

# En forms.py - REEMPLAZAR CitaForm existente
class CitaForm(forms.ModelForm):
    class Meta:
        model = models.Cita
        fields = ['paciente', 'dentista', 'unidad_dental', 'servicios_planeados', 'motivo', 'notas',
            'fecha_hora']
        widgets = {
            
            'fecha_hora': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control'
            }),
            'servicios_planeados': forms.SelectMultiple(attrs={
                'class': 'form-control select2',  # Clase para Select2
                'multiple': 'multiple'
            }),
            'motivo': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Síntomas, observaciones adicionales...'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Pasar el usuario actual para filtrar dentistas por especialidad
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configuracion básica
        self.fields['paciente'].queryset = models.Paciente.objects.order_by('apellido', 'nombre')
        # Filtrar dentistas: solo perfiles activos con usuario que tenga grupo Dentista
        self.fields['dentista'].queryset = models.PerfilDentista.objects.filter(
            activo=True,
            usuario__groups__name='Dentista'
        ).distinct().select_related('usuario').order_by('usuario__last_name', 'usuario__first_name')
        self.fields['unidad_dental'].queryset = models.UnidadDental.objects.all()
        
        # FILTRAR SERVICIOS POR ESPECIALIDAD DEL DENTISTA
        if self.instance.pk and self.instance.dentista:
            # Si estamos editando y ya hay dentista seleccionado
            dentista = self.instance.dentista
            servicios_disponibles = self._get_servicios_para_dentista(dentista)
            self.fields['servicios_planeados'].queryset = servicios_disponibles
        else:
            # Si es nuevo, mostrar todos los servicios activos
            self.fields['servicios_planeados'].queryset = models.Servicio.objects.filter(activo=True)
        
        # Estilos CSS
        for field_name, field in self.fields.items():
            if field_name != 'servicios_planeados':  # Excepto checkboxes
                field.widget.attrs['class'] = 'form-control'
        
        # Labels personalizados
        self.fields['servicios_planeados'].label = "Servicios Planeados"
        self.fields['motivo'].label = "Síntomas / Observaciones"
        self.fields['motivo'].required = False
    
    def _get_servicios_para_dentista(self, dentista):
        """Obtener servicios que puede realizar el dentista según sus especialidades"""
        # Recopilar IDs de servicios de todas las especialidades del dentista
        servicios_ids = set()
        
        for especialidad in dentista.especialidades.all():
            # Obtener servicios de la especialidad
            especialidad_servicios = especialidad.servicios_disponibles()
            servicios_ids.update(especialidad_servicios.values_list('id', flat=True))
        
        # Retornar queryset filtrado por IDs y activo=True
        if servicios_ids:
            return models.Servicio.objects.filter(id__in=servicios_ids, activo=True).distinct()
        else:
            return models.Servicio.objects.none()
    
    def clean_fecha_hora(self):
        """Procesar fecha/hora asegurando zona horaria correcta"""
        fecha_hora = self.cleaned_data.get('fecha_hora')
        if not fecha_hora:
            return fecha_hora
            
        # Importar utilidades de timezone
        from django.utils import timezone
        from django.conf import settings
        
        # Si la fecha viene sin timezone info, asumirla como local
        if not timezone.is_aware(fecha_hora):
            # Activar zona horaria local temporalmente
            current_tz = timezone.get_current_timezone()
            timezone.activate(settings.TIME_ZONE)
            try:
                fecha_hora = timezone.make_aware(fecha_hora)
            finally:
                timezone.activate(current_tz)
        
        return fecha_hora

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get("fecha_hora")
        dentista = cleaned_data.get("dentista")
        servicios_planeados = cleaned_data.get("servicios_planeados")
        
        if fecha_hora and dentista:
            # Validar que el dentista puede realizar los servicios seleccionados
            if servicios_planeados:
                servicios_dentista = self._get_servicios_para_dentista(dentista)
                servicios_invalidos = []
                
                for servicio in servicios_planeados:
                    if servicio not in servicios_dentista:
                        servicios_invalidos.append(servicio.nombre)
                
                if servicios_invalidos:
                    raise ValidationError(
                        f"El Dr. {dentista} no puede realizar estos servicios: {', '.join(servicios_invalidos)}"
                    )
            
            # Calcular duración total estimada
            duracion_total = sum(
                s.duracion_minutos for s in servicios_planeados or []
            )

            # Asegurar hora_fin definida siempre para evitar errores cuando no hay servicios
            hora_fin = fecha_hora + timedelta(minutes=(duracion_total or 0))
            
            # Verificar conflictos de horario (incluyendo tiempo estimado)
            citas_en_conflicto = models.Cita.objects.filter(
                dentista=dentista,
                fecha_hora__lt=hora_fin,
                fecha_hora__gte=fecha_hora
            ).exclude(estado='CAN')  # No considerar canceladas
            
            if self.instance.pk:
                citas_en_conflicto = citas_en_conflicto.exclude(pk=self.instance.pk)
            
            if citas_en_conflicto.exists() and duracion_total > 0:
                raise ValidationError(
                    f"El dentista {dentista} ya tiene una cita en este horario. "
                    f"Duración estimada: {duracion_total} minutos (hasta {hora_fin.strftime('%H:%M')})."
                )
            
            # NUEVA VALIDACIÓN: Verificar que la cita caiga dentro del horario laboral del dentista
            dia_semana_cita = fecha_hora.weekday()
            horarios_laborales = models.HorarioLaboral.objects.filter(
                dentista=dentista,
                dia_semana=dia_semana_cita,
                activo=True
            )

            cita_dentro_horario = False
            for horario in horarios_laborales:
                horario_inicio_dt = fecha_hora.replace(
                    hour=horario.hora_inicio.hour,
                    minute=horario.hora_inicio.minute,
                    second=0, microsecond=0
                )
                horario_fin_dt = fecha_hora.replace(
                    hour=horario.hora_fin.hour,
                    minute=horario.hora_fin.minute,
                    second=0, microsecond=0
                )

                # Ajustar si el horario de fin es al día siguiente (ej. 23:00 a 01:00)
                if horario.hora_fin <= horario.hora_inicio: # Si termina al día siguiente
                    horario_fin_dt += timedelta(days=1)

                # Verificar si la cita está completamente contenida en este horario laboral
                if fecha_hora >= horario_inicio_dt and hora_fin <= horario_fin_dt:
                    cita_dentro_horario = True
                    break
            
            if not cita_dentro_horario:
                raise ValidationError(
                    f"La cita ({fecha_hora.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}) "
                    f"está fuera del horario laboral del Dr. {dentista} para este día."
                )
        
        return cleaned_data

class PagoForm(forms.ModelForm):
    desea_factura = forms.BooleanField(
        label="¿Desea facturar este pago?",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = models.Pago
        fields = ['paciente', 'cita', 'monto', 'metodo_pago']
        widgets = {
            'cita': forms.HiddenInput(),  # La cita se pasa por URL
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        # Permitir pasar la instancia de 'paciente' para pagos directos
        self.paciente_instance = kwargs.pop('paciente', None)
        # Controlar si se permite solicitar factura en este formulario
        self.permitir_factura = kwargs.pop('permitir_factura', True)
        # Controlar si se muestra selector de destino (saldo vs cita)
        self.permitir_destino = kwargs.pop('permitir_destino', True)
        super().__init__(*args, **kwargs)
        # Asegurar queryset ordenado para selector de paciente (si se muestra)
        if 'paciente' in self.fields:
            self.fields['paciente'].queryset = models.Paciente.objects.order_by('apellido', 'nombre')
            self.fields['paciente'].widget.attrs.update({'class': 'form-select'})
            self.fields['paciente'].required = False  # coherente con blank=True en el modelo
        # Unificar métodos de pago como ChoiceField explícito para asegurar <select>
        met_label = self.fields['metodo_pago'].label if 'metodo_pago' in self.fields else 'Método de pago'
        self.fields['metodo_pago'] = forms.ChoiceField(
            choices=[
                ('Efectivo', 'Efectivo'),
                ('Tarjeta de crédito', 'Tarjeta de crédito'),
                ('Tarjeta de débito', 'Tarjeta de débito'),
                ('Transferencia', 'Transferencia'),
            ],
            initial='Efectivo',
            widget=forms.Select(attrs={'class': 'form-select'}),
            label=met_label,
            required=True,
        )
        # Si se pasa una instancia de paciente, establecerla como inicial para el campo paciente
        if self.paciente_instance and 'paciente' in self.fields:
            self.fields['paciente'].initial = self.paciente_instance
            self.fields['paciente'].widget = forms.HiddenInput()  # Ocultar si ya está preestablecido
            # Mostrar límite máximo en el campo monto según saldo del paciente
            try:
                saldo = float(self.paciente_instance.saldo_global or 0)
                self.fields['monto'].widget.attrs.update({'max': f"{saldo:.2f}", 'step': '0.01'})
                self.fields['monto'].help_text = f"Saldo actual del paciente: ${saldo:.2f}"
            except Exception:
                pass
            # Selector de destino (aplicar a saldo o a cita específica con adeudo)
            if self.permitir_destino:
                from django.db.models import Sum as _Sum
                opciones = [('saldo', 'Saldo general del paciente')]
                citas = models.Cita.objects.filter(paciente=self.paciente_instance, estado__in=['ATN', 'COM']).prefetch_related('servicios_realizados', 'pagos').order_by('-fecha_hora')
                for c in citas:
                    total_serv = sum(s.precio for s in c.servicios_realizados.all())
                    pagado = c.pagos.aggregate(total=_Sum('monto'))['total'] or 0
                    saldo_cita = float(total_serv) - float(pagado)
                    if saldo_cita > 0.005:
                        opciones.append((f'cita:{c.id}', f"Cita #{c.id} del {c.fecha_hora.strftime('%d/%m/%Y')} - Saldo ${saldo_cita:.2f}"))
                if len(opciones) > 1:
                    self.fields['aplicar_a'] = forms.ChoiceField(
                        choices=opciones,
                        label='Aplicar pago a',
                        widget=forms.Select(attrs={'class': 'form-select'}),
                        required=True
                    )
        # Ocultar o eliminar el campo desea_factura según contexto
        if not self.permitir_factura and 'desea_factura' in self.fields:
            # Opción 1: eliminar el campo para que no se muestre ni valide
            self.fields.pop('desea_factura')

    def clean(self):
        cleaned_data = super().clean()
        monto = cleaned_data.get('monto')
        cita = cleaned_data.get('cita')
        paciente = cleaned_data.get('paciente')  # Obtener paciente de los datos del formulario o de la instancia

        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto del pago debe ser un valor positivo.")

        if cita:
            # Si el pago es para una cita específica, validar contra su saldo_pendiente
            if monto is not None and monto > cita.saldo_pendiente:
                raise forms.ValidationError(
                    f"El monto del pago (${monto:.2f}) excede el saldo pendiente de la cita (${cita.saldo_pendiente:.2f})."
                )
        elif paciente:
            # Validar contra saldo global del paciente
            try:
                # Asegurar saldo actualizado (opcional): el llamado puede hacerse en la vista antes
                saldo_actual = float(paciente.saldo_global or 0)
            except Exception:
                saldo_actual = 0.0

            if monto is not None and saldo_actual > 0 and monto > saldo_actual:
                raise forms.ValidationError(
                    f"El monto del pago (${monto:.2f}) excede el saldo pendiente del paciente (${saldo_actual:.2f})."
                )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        # Aplicar mapeo SAT automático solo si desea facturar
        desea_factura = self.cleaned_data.get('desea_factura')
        if desea_factura:
            try:
                from .services import SatMappingService
                SatMappingService.aplicar_mapeo_automatico(instance)
            except Exception:
                pass
        return instance

# En forms.py - REEMPLAZAR CompraForm existente
class UnidadDentalForm(forms.ModelForm):
    class Meta:
        model = models.UnidadDental
        fields = ['nombre', 'descripcion', 'dentistas_permitidos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'dentistas_permitidos': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'dentistas_permitidos': 'Dentistas Permitidos',
        }

class CompraForm(forms.ModelForm):
    class Meta:
        model = models.Compra
        fields = ['proveedor', 'tipo_compra', 'fecha_compra', 'estado', 'total', 'factura_adjunta', 'notas']
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total'].widget.attrs['readonly'] = True
        self.fields['total'].widget.attrs['class'] = 'form-control'
        
        # Hacer proveedor opcional según el tipo
        self.fields['proveedor'].required = False
        self.fields['proveedor'].widget.attrs['class'] = 'form-select'
        self.fields['tipo_compra'].widget.attrs['class'] = 'form-select'
        self.fields['fecha_compra'].widget.attrs['class'] = 'form-control'
        self.fields['estado'].widget.attrs['class'] = 'form-select'
        
        # Labels personalizados
        self.fields['proveedor'].help_text = "Opcional para compras internas o ajustes de inventario"
        self.fields['tipo_compra'].label = "Tipo de Movimiento"
    
    def clean(self):
        cleaned_data = super().clean()
        proveedor = cleaned_data.get('proveedor')
        tipo_compra = cleaned_data.get('tipo_compra')
        
        # Validar que compras externas tengan proveedor
        if tipo_compra == 'EXTERNA' and not proveedor:
            raise ValidationError("Las compras externas requieren un proveedor.")
        
        return cleaned_data

DetalleCompraFormSet = inlineformset_factory(
    models.Compra, 
    models.DetalleCompra,
    fields=('insumo', 'cantidad', 'precio_unitario'),
    extra=1,
    can_delete=True,
    widgets={
        'insumo': forms.Select(attrs={'class': 'form-select'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

class BaseDetalleCompraRecepcionFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        
        form.fields['unidad_dental'] = forms.ModelChoiceField(
            queryset=models.UnidadDental.objects.all(),
            label="Unidad de Destino",
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        
        insumo = form.instance.insumo
        if insumo and insumo.requiere_lote_caducidad:
            form.fields['numero_lote'] = forms.CharField(
                label="Número de Lote",
                required=True,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            form.fields['fecha_caducidad'] = forms.DateField(
                label="Fecha de Caducidad",
                required=True,
                widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
            )

DetalleCompraRecepcionFormSet = inlineformset_factory(
    models.Compra,
    models.DetalleCompra,
    formset=BaseDetalleCompraRecepcionFormSet,
    fields=('insumo', 'cantidad'),
    extra=0,
    can_delete=False,
    widgets={
        'insumo': forms.HiddenInput(),
        'cantidad': forms.HiddenInput(),
    }
)

ServicioInsumoFormSet = inlineformset_factory(
    models.Servicio,
    models.ServicioInsumo,
    fields=('insumo', 'cantidad'),
    extra=1,
    can_delete=True,
    widgets={
        'insumo': forms.Select(attrs={'class': 'form-select'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

class ReporteIngresosForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

class ReporteServiciosForm(forms.Form):
    PERIODO_CHOICES = [
        ('semana', 'Semanal'),
        ('mes', 'Mensual'),
    ]
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, initial='semana', widget=forms.Select(attrs={'class': 'form-select'}))
    fecha_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    dentista = forms.ModelChoiceField(
        queryset=models.PerfilDentista.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Filtrar por Dentista"
    )

# En forms.py - REEMPLAZAR FinalizarCitaForm existente
# En forms.py - REEMPLAZAR FinalizarCitaForm existente
class FinalizarCitaForm(forms.ModelForm):
    confirmar_finalizacion = forms.BooleanField(
        required=True,
        label="Confirmo que he completado la atención del paciente",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = models.Cita
        fields = ['servicios_realizados', 'notas', 'confirmar_finalizacion']
        widgets = {
            'servicios_realizados': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'notas': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Notas sobre el tratamiento realizado...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.dentista = kwargs.pop('dentista', None)
        super().__init__(*args, **kwargs)
        
        # Solo mostrar servicios que el dentista puede realizar
        if self.dentista and self.instance.pk:
            servicios_disponibles = self._get_servicios_para_dentista(self.dentista)
            self.fields['servicios_realizados'].queryset = servicios_disponibles
            
            # Sugerir los servicios planeados como preseleccionados
            if not self.instance.servicios_realizados.exists():
                self.initial['servicios_realizados'] = self.instance.servicios_planeados.all()
        else:
            self.fields['servicios_realizados'].queryset = models.Servicio.objects.filter(activo=True)
        
        # Labels y help text
        self.fields['servicios_realizados'].label = "Servicios Realmente Realizados"
        self.fields['servicios_realizados'].help_text = "Seleccione solo los servicios que efectivamente se realizaron"
        self.fields['notas'].label = "Notas del Tratamiento"
        self.fields['notas'].required = False
    
    def _get_servicios_para_dentista(self, dentista):
        """Obtener servicios que puede realizar el dentista"""
        servicios = models.Servicio.objects.none()
        for especialidad in dentista.especialidades.all():
            servicios = servicios.union(especialidad.servicios_disponibles())
        return servicios.filter(activo=True).distinct()
    
    def clean_servicios_realizados(self):
        servicios = self.cleaned_data.get('servicios_realizados')
        if not servicios:
            raise ValidationError("Debe seleccionar al menos un servicio realizado.")
        return servicios
class PacientePlanPagoForm(forms.ModelForm):
    class Meta:
        model = models.Paciente
        fields = ['apto_para_plan_de_pago']
        labels = {'apto_para_plan_de_pago': "Paciente es apto para plan de pagos"}

class DatosFiscalesForm(forms.ModelForm):
    class Meta:
        model = models.DatosFiscales
        fields = [
            'rfc', 'razon_social',
            'calle', 'numero_exterior', 'numero_interior', 'colonia', 'municipio', 'estado', 'codigo_postal',
            'regimen_fiscal', 'uso_cfdi'
        ]
        widgets = {
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_exterior': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_interior': forms.TextInput(attrs={'class': 'form-control'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'pattern': '\\d{5}', 'title': '5 dígitos'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Poblar selects desde catálogos SAT
        self.fields['regimen_fiscal'].queryset = models.SatRegimenFiscal.objects.filter(activo=True).order_by('codigo')
        self.fields['regimen_fiscal'].widget.attrs.update({'class': 'form-select'})
        self.fields['uso_cfdi'].queryset = models.SatUsoCFDI.objects.filter(activo=True).order_by('codigo')
        self.fields['uso_cfdi'].widget.attrs.update({'class': 'form-select'})
        for field_name, field in self.fields.items():
            if field_name not in ('uso_cfdi', 'regimen_fiscal'):
                field.widget.attrs.update({'class': 'form-control'})

class AvisoFuncionamientoForm(forms.ModelForm):
    class Meta:
        model = models.AvisoFuncionamiento
        fields = ['responsable_sanitario', 'cedula_profesional', 'fecha_presentacion', 'certificado_pdf', 'fecha_vencimiento']
        widgets = {
            'fecha_presentacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class EquipoForm(forms.ModelForm):
    class Meta:
        model = models.Equipo
        fields = ['unidad_trabajo', 'nombre', 'registro_sanitario', 'certificado_bpm', 'fecha_calibracion', 'fecha_vencimiento_calibracion']
        widgets = {
            'fecha_calibracion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento_calibracion': forms.DateInput(attrs={'type': 'date'}),
        }

class ResiduosForm(forms.ModelForm):
    class Meta:
        model = models.Residuos
        fields = ['unidad_trabajo', 'proveedor_recoleccion', 'fecha_recoleccion', 'manifiesto_pdf', 'cantidad_kg']
        widgets = {
            'fecha_recoleccion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'unidad_trabajo': forms.Select(attrs={'class': 'form-select'}),
            'proveedor_recoleccion': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'manifiesto_pdf': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proveedor_recoleccion'].queryset = models.Proveedor.objects.all()
        self.fields['proveedor_recoleccion'].label = "Proveedor de Recolección"
        self.fields['manifiesto_pdf'].required = False


class RespuestaHistorialForm(forms.ModelForm):
    class Meta:
        model = models.RespuestaHistorial
        fields = ['pregunta', 'respuesta']
        widgets = {'pregunta': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pregunta = self.instance.pregunta
        
        if pregunta.tipo == 'SI_NO':
            self.fields['respuesta'] = forms.ChoiceField(
                choices=[('SI', 'Sí'), ('NO', 'No')],
                widget=forms.RadioSelect,
                label=pregunta.texto
            )
        elif pregunta.tipo == 'MULTIPLE':
            choices = [(op.strip(), op.strip()) for op in pregunta.opciones.split(',')]
            self.fields['respuesta'] = forms.ChoiceField(
                choices=choices,
                widget=forms.Select(attrs={'class': 'form-select'}),
                label=pregunta.texto
            )
        elif pregunta.tipo == 'TEXTAREA':
            self.fields['respuesta'].widget = forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
            self.fields['respuesta'].label = pregunta.texto
        else: # TEXT
            self.fields['respuesta'].widget = forms.TextInput(attrs={'class': 'form-control'})
            self.fields['respuesta'].label = pregunta.texto

RespuestaHistorialFormSet = modelformset_factory(
    models.RespuestaHistorial,
    form=RespuestaHistorialForm,
    extra=0,
    can_delete=False
)

class AbonoForm(forms.ModelForm):
    class Meta:
        model = models.Pago
        fields = ['paciente', 'monto', 'metodo_pago']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = models.Paciente.objects.order_by('apellido', 'nombre')
        self.fields['paciente'].widget.attrs.update({'class': 'form-select'})
        self.fields['monto'].widget.attrs.update({'class': 'form-control'})
        # Unificar opciones de método también aquí para consistencia
        self.fields['metodo_pago'] = forms.ChoiceField(
            choices=[
                ('Efectivo', 'Efectivo'),
                ('Tarjeta de crédito', 'Tarjeta de crédito'),
                ('Tarjeta de débito', 'Tarjeta de débito'),
                ('Transferencia', 'Transferencia'),
            ],
            initial='Efectivo',
            widget=forms.Select(attrs={'class': 'form-select'}),
            label=self.fields['metodo_pago'].label if 'metodo_pago' in self.fields else 'Método de pago',
            required=True,
        )

class ReporteIngresosDentistaForm(forms.Form):
    PERIODO_CHOICES = [
        ('semana', 'Semanal'),
        ('mes', 'Mensual'),
    ]
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, initial='semana', widget=forms.Select(attrs={'class': 'form-select'}))
    dentista = forms.ModelChoiceField(
        queryset=models.PerfilDentista.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Filtrar por Dentista"
    )
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)

class HorarioLaboralForm(forms.ModelForm):
    class Meta:
        model = models.HorarioLaboral
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

from django.forms import BaseModelFormSet

class BaseHorarioLaboralFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        # Reglas: no traslapes por día, turnos máximo 8h, dentro de 09:00–21:00
        import datetime as _dt
        inicio_permitido = _dt.time(9, 0)
        fin_permitido = _dt.time(21, 0)
        by_day = {}
        for i, form in enumerate(self.forms):
            if not hasattr(form, 'cleaned_data'):
                continue
            cd = form.cleaned_data
            if not cd or cd.get('DELETE'):
                continue
            dia = cd.get('dia_semana')
            hi = cd.get('hora_inicio')
            hf = cd.get('hora_fin')
            activo = cd.get('activo')
            if not (dia is not None and hi and hf and activo is not None):
                # Saltar filas incompletas
                continue
            # Validar rango permitido
            if hi < inicio_permitido or hf > fin_permitido:
                raise ValidationError("Los horarios deben estar entre 09:00 y 21:00.")
            # Validar duración
            dt0 = _dt.datetime.combine(_dt.date.today(), hi)
            dt1 = _dt.datetime.combine(_dt.date.today(), hf)
            if dt1 <= dt0:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            dur = (dt1 - dt0).seconds / 3600.0
            if dur > 8.0:
                raise ValidationError("Cada turno no debe exceder 8 horas.")
            lista = by_day.setdefault(dia, [])
            # Verificar traslapes con existentes del mismo día
            for (e_hi, e_hf) in lista:
                if hi < e_hf and hf > e_hi:
                    raise ValidationError("No puede haber horarios que se traslapen el mismo día.")
            lista.append((hi, hf))

HorarioLaboralFormSet = modelformset_factory(
    models.HorarioLaboral,
    form=HorarioLaboralForm,
    formset=BaseHorarioLaboralFormSet,
    extra=1,
    can_delete=True,
    edit_only=False
)

class ServicioForm(forms.ModelForm):
    class Meta:
        model = models.Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion_minutos', 'activo', 'especialidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar especialidades por nombre para mejor experiencia de usuario
        self.fields['especialidad'].queryset = models.Especialidad.objects.all().order_by('nombre')
        self.fields['especialidad'].empty_label = "Seleccione una especialidad"
        
        # Labels mejorados
        self.fields['nombre'].label = "Nombre del Servicio"
        self.fields['descripcion'].label = "Descripción"
        self.fields['precio'].label = "Precio (MXN)"
        self.fields['duracion_minutos'].label = "Duración Estimada (minutos)"
        self.fields['especialidad'].label = "Especialidad Requerida"
        
        # Help texts
        self.fields['duracion_minutos'].help_text = "Tiempo estimado que toma realizar este servicio"
        self.fields['especialidad'].help_text = "Solo dentistas con esta especialidad podrán realizar este servicio"
        
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
        return precio
        
    def clean_duracion_minutos(self):
        duracion = self.cleaned_data.get('duracion_minutos')
        if duracion is not None and duracion <= 0:
            raise ValidationError("La duración debe ser mayor que cero.")
        return duracion

# === FORMULARIOS PARA CUESTIONARIO DE HISTORIAL CLÍNICO ===

class CategoriaHistorialForm(forms.ModelForm):
    class Meta:
        model = models.CategoriaHistorial
        fields = ['nombre', 'descripcion', 'icono', 'color', 'orden', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icono': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'ej: fas fa-heart-pulse'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color', 
                'class': 'form-control form-control-color'
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PreguntaHistorialMejoradaForm(forms.ModelForm):
    class Meta:
        model = models.PreguntaHistorial
        fields = [
            'categoria', 'texto', 'subtitulo', 'tipo', 'opciones', 
            'orden', 'obligatoria', 'importancia', 'activa',
            'requiere_seguimiento', 'alerta_cofepris'
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'subtitulo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Explicación adicional (opcional)'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'opciones': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Para opción múltiple, separar con comas: Opción A, Opción B, Opción C'
            }),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'importancia': forms.Select(attrs={'class': 'form-select'}),
            'obligatoria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requiere_seguimiento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alerta_cofepris': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = models.CategoriaHistorial.objects.filter(activa=True).order_by('orden')
        
        # Labels mejorados
        self.fields['texto'].label = "Pregunta"
        self.fields['subtitulo'].label = "Explicación adicional"
        self.fields['opciones'].label = "Opciones (solo para opción múltiple)"
        self.fields['importancia'].label = "Nivel de importancia médica"
        self.fields['requiere_seguimiento'].label = "¿Requiere seguimiento médico?"
        self.fields['alerta_cofepris'].label = "¿Requiere reporte a COFEPRIS?"
        
        # Help texts
        self.fields['importancia'].help_text = "Determina qué tan crítica es esta pregunta para la salud del paciente"
        self.fields['requiere_seguimiento'].help_text = "Si la respuesta es 'Sí', se generará una alerta para seguimiento"
        self.fields['alerta_cofepris'].help_text = "Para condiciones que requieren reporte a autoridades sanitarias"

class CuestionarioHistorialForm(forms.Form):
    """Formulario dinámico para completar cuestionario de historial clínico"""
    
    def __init__(self, paciente, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paciente = paciente
        
        # Obtener todas las preguntas activas organizadas por categoría
        categorias = models.CategoriaHistorial.objects.filter(
            activa=True, 
            preguntas__activa=True
        ).prefetch_related('preguntas').distinct().order_by('orden')
        
        for categoria in categorias:
            preguntas = categoria.preguntas.filter(activa=True).order_by('orden')
            
            for pregunta in preguntas:
                field_name = f'pregunta_{pregunta.id}'
                
                # Obtener respuesta existente si la hay
                respuesta_existente = ''
                try:
                    respuesta_obj = models.RespuestaHistorial.objects.get(
                        paciente=paciente, pregunta=pregunta
                    )
                    respuesta_existente = respuesta_obj.respuesta
                except models.RespuestaHistorial.DoesNotExist:
                    pass
                
                # Crear el campo según el tipo de pregunta
                if pregunta.tipo == 'SI_NO':
                    self.fields[field_name] = forms.ChoiceField(
                        choices=[('', 'Seleccione...'), ('Sí', 'Sí'), ('No', 'No')],
                        widget=forms.Select(attrs={'class': 'form-select'}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                elif pregunta.tipo == 'MULTIPLE':
                    opciones = [('', 'Seleccione...')] + [
                        (op.strip(), op.strip()) for op in pregunta.get_opciones_lista()
                    ]
                    self.fields[field_name] = forms.ChoiceField(
                        choices=opciones,
                        widget=forms.Select(attrs={'class': 'form-select'}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                elif pregunta.tipo == 'TEXTAREA':
                    self.fields[field_name] = forms.CharField(
                        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                elif pregunta.tipo == 'FECHA':
                    self.fields[field_name] = forms.DateField(
                        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                elif pregunta.tipo == 'NUMERO':
                    self.fields[field_name] = forms.IntegerField(
                        widget=forms.NumberInput(attrs={'class': 'form-control'}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                elif pregunta.tipo == 'EMAIL':
                    self.fields[field_name] = forms.EmailField(
                        widget=forms.EmailInput(attrs={'class': 'form-control'}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                elif pregunta.tipo == 'TELEFONO':
                    self.fields[field_name] = forms.CharField(
                        widget=forms.TextInput(attrs={
                            'class': 'form-control', 
                            'placeholder': '55 1234 5678'
                        }),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                else:  # TEXT por defecto
                    self.fields[field_name] = forms.CharField(
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        required=pregunta.obligatoria,
                        initial=respuesta_existente,
                        label=pregunta.texto
                    )
                
                # Agregar subtítulo como help_text si existe
                if pregunta.subtitulo:
                    self.fields[field_name].help_text = pregunta.subtitulo
                
                # Agregar clase CSS según importancia
                css_class = self.fields[field_name].widget.attrs.get('class', '')
                if pregunta.importancia == 'CRITICA':
                    css_class += ' border-danger'
                elif pregunta.importancia == 'ALTA':
                    css_class += ' border-warning'
                
                self.fields[field_name].widget.attrs['class'] = css_class
                
                # Guardar metadatos de la pregunta para procesamiento posterior
                self.fields[field_name]._pregunta_obj = pregunta
    
    def save(self, completado_por=None):
        """Guarda las respuestas del cuestionario"""
        respuestas_guardadas = []
        alertas_generadas = []
        
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('pregunta_') and value:
                pregunta_id = int(field_name.replace('pregunta_', ''))
                pregunta = models.PreguntaHistorial.objects.get(id=pregunta_id)
                
                # Guardar o actualizar respuesta
                respuesta, created = models.RespuestaHistorial.objects.update_or_create(
                    paciente=self.paciente,
                    pregunta=pregunta,
                    defaults={
                        'respuesta': str(value),
                        'actualizado_por': completado_por
                    }
                )
                respuestas_guardadas.append(respuesta)
                
                # Verificar si genera alertas
                if respuesta.es_respuesta_critica():
                    alertas_generadas.append(
                        f"⚠️ {pregunta.categoria.nombre}: {pregunta.texto}"
                    )
                
                if pregunta.requiere_seguimiento and value.lower() in ['sí', 'si']:
                    alertas_generadas.append(
                        f"📋 Seguimiento: {pregunta.texto}"
                    )
        
        # Crear registro de cuestionario completado
        cuestionario_completado = models.CuestionarioCompletado.objects.create(
            paciente=self.paciente,
            completado_por=completado_por,
            alertas_generadas='\n'.join(alertas_generadas),
            tiene_alertas=len(alertas_generadas) > 0
        )
        
        return cuestionario_completado, respuestas_guardadas
