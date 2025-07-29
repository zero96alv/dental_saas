from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet, modelformset_factory
from datetime import timedelta

# Importar modelos solo para type hinting si es necesario o dentro de los métodos
from . import models

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
        user.groups.set([self.cleaned_data['rol']])
        return user

class PerfilDentistaForm(forms.ModelForm):
    class Meta:
        model = models.PerfilDentista
        fields = ['telefono', 'especialidades', 'activo']
        widgets = {
            'especialidades': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['especialidades'].label_from_instance = lambda obj: obj.nombre

# En forms.py - REEMPLAZAR CitaForm existente
class CitaForm(forms.ModelForm):
    class Meta:
        model = models.Cita
        fields = [
            'cliente', 'dentista', 'unidad_dental', 'fecha_hora', 
            'servicios_planeados', 'motivo'
        ]
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
            })
        }
    
    def __init__(self, *args, **kwargs):
        # Pasar el usuario actual para filtrar dentistas por especialidad
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configuracion básica
        self.fields['cliente'].queryset = models.Paciente.objects.order_by('apellido', 'nombre')
        self.fields['dentista'].queryset = models.PerfilDentista.objects.filter(activo=True)
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
        servicios = models.Servicio.objects.none()
        
        for especialidad in dentista.especialidades.all():
            # Servicios de la especialidad + servicios de especialidades incluidas
            servicios = servicios.union(especialidad.servicios_disponibles())
        
        return servicios.filter(activo=True).distinct()
    
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
            
            if duracion_total > 0:
                hora_fin = fecha_hora + timedelta(minutes=duracion_total)
                
                # Verificar conflictos de horario (incluyendo tiempo estimado)
                citas_en_conflicto = models.Cita.objects.filter(
                    dentista=dentista,
                    fecha_hora__lt=hora_fin,
                    fecha_hora__gte=fecha_hora
                ).exclude(estado='CAN')  # No considerar canceladas
                
                if self.instance.pk:
                    citas_en_conflicto = citas_en_conflicto.exclude(pk=self.instance.pk)
                
                if citas_en_conflicto.exists():
                    raise ValidationError(
                        f"El dentista {dentista} ya tiene una cita en este horario. "
                        f"Duración estimada: {duracion_total} minutos (hasta {hora_fin.strftime('%H:%M')})."
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
        fields = ['cita', 'monto', 'metodo_pago', 'desea_factura']
        widgets = {
            'cita': forms.HiddenInput(),  # La cita se pasa por URL
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metodo_pago'].choices = [
            ('EFECTIVO', 'Efectivo'),
            ('TARJETA', 'Tarjeta'),
            ('TRANSFERENCIA', 'Transferencia'),
        ]

# En forms.py - REEMPLAZAR CompraForm existente
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
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
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
        fields = ['rfc', 'razon_social', 'domicilio_fiscal', 'uso_cfdi']
        widgets = {'domicilio_fiscal': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uso_cfdi'].widget = forms.Select(
            choices=[
                ('G01', 'Adquisición de mercancías'),
                ('G03', 'Gastos en general'),
                ('I04', 'Equipo de computo y accesorios'),
                ('D01', 'Honorarios médicos, dentales y gastos hospitalarios.'),
            ],
            attrs={'class': 'form-select'}
        )
        for field_name, field in self.fields.items():
            if field_name != 'uso_cfdi':
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
        widgets = {'fecha_recoleccion': forms.DateInput(attrs={'type': 'date'})}

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
        self.fields['metodo_pago'].widget.attrs.update({'class': 'form-select'})

class ReporteIngresosDentistaForm(forms.Form):
    dentista = forms.ModelChoiceField(
        queryset=models.PerfilDentista.objects.filter(activo=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Filtrar por Dentista"
    )
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)