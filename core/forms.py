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
        widgets = {'especialidades': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'})}

class CitaForm(forms.ModelForm):
    class Meta:
        model = models.Cita
        fields = ['cliente', 'dentista', 'unidad_dental', 'fecha_hora', 'motivo', 'estado']
        widgets = {'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = models.Paciente.objects.order_by('apellido', 'nombre')
        self.fields['dentista'].queryset = models.PerfilDentista.objects.filter(activo=True).order_by('apellido', 'nombre')
        self.fields['unidad_dental'].queryset = models.UnidadDental.objects.all()
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get("fecha_hora")
        dentista = cleaned_data.get("dentista")

        if fecha_hora and dentista:
            hora_fin = fecha_hora + timedelta(minutes=30)
            citas_en_conflicto = models.Cita.objects.filter(
                dentista=dentista,
                fecha_hora__lt=hora_fin,
                fecha_hora__gte=fecha_hora
            )
            if self.instance and self.instance.pk:
                citas_en_conflicto = citas_en_conflicto.exclude(pk=self.instance.pk)
            if citas_en_conflicto.exists():
                raise ValidationError(f"El dentista {dentista} ya tiene una cita programada en este horario.")
        return cleaned_data

class PagoForm(forms.ModelForm):
    class Meta:
        model = models.Pago
        fields = ['cita', 'monto', 'metodo_pago']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class CompraForm(forms.ModelForm):
    class Meta:
        model = models.Compra
        fields = ['proveedor', 'fecha_compra', 'estado', 'total', 'factura_adjunta']
        widgets = {'fecha_compra': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['total'].widget.attrs['readonly'] = True
        self.fields['total'].widget.attrs['class'] = 'form-control'
        self.fields['proveedor'].widget.attrs['class'] = 'form-select'
        self.fields['fecha_compra'].widget.attrs['class'] = 'form-control'
        self.fields['estado'].widget.attrs['class'] = 'form-select'

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

class FinalizarCitaForm(forms.ModelForm):
    class Meta:
        model = models.Cita
        fields = ['servicios_realizados']
        widgets = {'servicios_realizados': forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['servicios_realizados'].queryset = models.Servicio.objects.filter(activo=True)
        self.fields['servicios_realizados'].help_text = "Seleccione los servicios que se realizaron durante la consulta."

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
            ]
        )

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