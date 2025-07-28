from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
# Al inicio del archivo views.py, agrega esta línea:
from django.db.models import Count, Sum, F, Q  # ← Agrega F aquí
import json
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView
)
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
import string
import random
from datetime import timedelta

# Importar forms y models de manera controlada para evitar ciclos
from . import forms
from . import models

class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        user = self.request.user
        if hasattr(user, 'paciente_perfil'):
            return ['core/portal/dashboard.html']
        
        if user.groups.filter(name='Administrador').exists() or user.is_superuser:
            return ['core/dashboards/admin_dashboard.html']
        elif user.groups.filter(name='Dentista').exists():
            return ['core/dashboards/dentista_dashboard.html']
        elif user.groups.filter(name='Recepcionista').exists():
            return ['core/dashboards/recepcionista_dashboard.html']
        else:
            return ['core/dashboards/admin_dashboard.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if hasattr(user, 'paciente_perfil'):
            paciente = user.paciente_perfil
            context['paciente'] = paciente
            context['proximas_citas'] = models.Cita.objects.filter(
                cliente=paciente, 
                fecha_hora__gte=timezone.now()
            ).order_by('fecha_hora')
            context['saldo_total_pendiente'] = paciente.saldo_global or 0
            return context

        periodo = self.request.GET.get('periodo', 'hoy')
        today = timezone.now().date()
        
        if periodo == 'semana':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            context['periodo_seleccionado'] = 'Esta Semana'
        elif periodo == 'mes':
            start_date = today.replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
            context['periodo_seleccionado'] = 'Este Mes'
        elif periodo == 'historico':
            start_date = None
            end_date = today
            context['periodo_seleccionado'] = 'Histórico'
        else:
            start_date = today
            end_date = today
            context['periodo_seleccionado'] = 'Hoy'
            
        context['periodo_param'] = periodo
        
        citas_periodo = models.Cita.objects.all()
        pagos_periodo = models.Pago.objects.all()
        pacientes_periodo = models.Paciente.objects.all()
        
        if start_date:
            citas_periodo = citas_periodo.filter(fecha_hora__date__gte=start_date, fecha_hora__date__lte=end_date)
            pagos_periodo = pagos_periodo.filter(fecha_pago__date__gte=start_date, fecha_pago__date__lte=end_date)
            pacientes_periodo = pacientes_periodo.filter(creado_en__date__gte=start_date, creado_en__date__lte=end_date)

        context['citas_total_periodo'] = citas_periodo.count()
        context['citas_pendientes_periodo'] = citas_periodo.filter(estado__in=['PRO', 'CON']).count()
        
        if user.groups.filter(name='Administrador').exists() or user.is_superuser:
            context['ingresos_periodo'] = pagos_periodo.aggregate(total=Sum('monto'))['total'] or 0
            
            # USAR SALDO_GLOBAL DE PACIENTES
            context['total_saldos_pendientes'] = models.Paciente.objects.filter(
                saldo_global__gt=0
            ).aggregate(total=Sum('saldo_global'))['total'] or 0
            
            from datetime import date
            alert_date = date.today()
            proximos_30_dias = alert_date + timedelta(days=30)
            context['stocks_bajos'] = models.Insumo.objects.filter(stock__lte=F('stock_minimo'))
            context['insumos_caducados'] = models.LoteInsumo.objects.filter(fecha_caducidad__lt=alert_date).order_by('fecha_caducidad')
            context['insumos_proximos_a_caducar'] = models.LoteInsumo.objects.filter(
                fecha_caducidad__gte=alert_date,
                fecha_caducidad__lte=proximos_30_dias
            ).order_by('fecha_caducidad')
            
        if user.groups.filter(name='Dentista').exists():
            perfil = get_object_or_404(models.PerfilDentista, usuario=user)
            citas_dentista_periodo = citas_periodo.filter(dentista=perfil)
            context['citas_dentista_periodo'] = citas_dentista_periodo.count()
            context['pacientes_atendidos_periodo'] = citas_dentista_periodo.filter(estado__in=['ATN', 'COM']).count()
            
        if user.groups.filter(name='Recepcionista').exists():
            context['citas_por_confirmar_periodo'] = citas_periodo.filter(estado='PRO').count()
            context['pacientes_nuevos_periodo'] = pacientes_periodo.count()
            
        return context
class UsuarioListView(ListView):
    model = User
    template_name = 'core/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 15

    def get_queryset(self):
        return User.objects.prefetch_related('groups').all().order_by('first_name', 'last_name')

class UsuarioCreateView(SuccessMessageMixin, CreateView):
    model = User
    form_class = forms.UserForm
    template_name = 'core/usuario_form.html'
    success_url = reverse_lazy('core:usuario_list')
    success_message = "Usuario '%(username)s' creado con éxito."

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password('password123')
        user.save()
        form.save_m2m()
        
        roles = set(form.cleaned_data['groups'].values_list('name', flat=True))
        if 'Administrador' in roles or 'Dentista' in roles:
            models.PerfilDentista.objects.create(
                usuario=user,
                nombre=user.first_name,
                apellido=user.last_name,
                email=user.email
            )
        messages.warning(self.request, "Se asignó la contraseña temporal 'password123'. El usuario debe cambiarla.")
        return super().form_valid(form)

class UsuarioUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = forms.UserForm
    template_name = 'core/usuario_form.html'
    success_url = reverse_lazy('core:usuario_list')
    success_message = "Usuario '%(username)s' actualizado con éxito."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        has_dentist_profile = hasattr(user, 'perfil_dentista')
        context['has_dentist_profile'] = has_dentist_profile

        if has_dentist_profile:
            if self.request.POST:
                context['perfil_form'] = forms.PerfilDentistaForm(self.request.POST, instance=user.perfil_dentista)
            else:
                context['perfil_form'] = forms.PerfilDentistaForm(instance=user.perfil_dentista)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user = form.save()

        if context.get('has_dentist_profile'):
            perfil_form = context['perfil_form']
            if perfil_form.is_valid():
                perfil = perfil_form.save(commit=False)
                perfil.usuario = user
                perfil.nombre = user.first_name
                perfil.apellido = user.last_name
                perfil.email = user.email
                perfil.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)

class PacienteListView(ListView):
    model = models.Paciente
    template_name = 'core/paciente_list.html'
    context_object_name = 'pacientes'

class PacienteDetailView(DetailView):
    model = models.Paciente
    template_name = 'core/paciente_detail.html'
    context_object_name = 'paciente'

class PacienteCreateView(SuccessMessageMixin, CreateView):
    model = models.Paciente
    template_name = 'core/paciente_form.html'
    fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'direccion']
    success_url = reverse_lazy('core:paciente_list')
    success_message = "Paciente '%(nombre)s %(apellido)s' creado con éxito."

class PacienteUpdateView(SuccessMessageMixin, UpdateView):
    model = models.Paciente
    template_name = 'core/paciente_form.html'
    fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'direccion']
    success_url = reverse_lazy('core:paciente_list')
    success_message = "Paciente '%(nombre)s %(apellido)s' actualizado con éxito."

class PacienteDeleteView(DeleteView):
    model = models.Paciente
    template_name = 'core/paciente_confirm_delete.html'
    success_url = reverse_lazy('core:paciente_list')
    context_object_name = 'paciente'

    def form_valid(self, form):
        messages.success(self.request, f"Paciente '{self.object.nombre} {self.object.apellido}' eliminado con éxito.")
        return super().form_valid(form)

class ServicioListView(ListView):
    model = models.Servicio
    template_name = 'core/service_list.html'
    context_object_name = 'servicios'

class ServicioCreateView(SuccessMessageMixin, CreateView):
    model = models.Servicio
    template_name = 'core/service_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'activo', 'especialidad']
    success_url = reverse_lazy('core:service_list')
    success_message = "Servicio '%(nombre)s' creado con éxito."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.ServicioInsumoFormSet(self.request.POST, prefix='insumos')
        else:
            context['formset'] = forms.ServicioInsumoFormSet(prefix='insumos')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class ServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = models.Servicio
    template_name = 'core/service_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'activo', 'especialidad']
    success_url = reverse_lazy('core:service_list')
    success_message = "Servicio '%(nombre)s' actualizado con éxito."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.ServicioInsumoFormSet(self.request.POST, instance=self.object, prefix='insumos')
        else:
            context['formset'] = forms.ServicioInsumoFormSet(instance=self.object, prefix='insumos')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class ServicioDeleteView(DeleteView):
    model = models.Servicio
    template_name = 'core/service_confirm_delete.html'
    success_url = reverse_lazy('core:service_list')
    context_object_name = 'servicio'

    def form_valid(self, form):
        messages.success(self.request, f"Servicio '{self.object.nombre}' eliminado con éxito.")
        return super().form_valid(form)

class PerfilDentistaListView(ListView):
    model = models.PerfilDentista
    template_name = 'core/dentista_list.html'
    context_object_name = 'dentistas'
    paginate_by = 15

    def get_queryset(self):
        return models.PerfilDentista.objects.prefetch_related('especialidades').order_by('apellido', 'nombre')

class EspecialidadListView(ListView):
    model = models.Especialidad
    template_name = 'core/especialidad_list.html'
    context_object_name = 'especialidades'
    paginate_by = 10

class EspecialidadCreateView(SuccessMessageMixin, CreateView):
    model = models.Especialidad
    template_name = 'core/especialidad_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('core:especialidad_list')
    success_message = "Especialidad '%(nombre)s' creada con éxito."

class EspecialidadUpdateView(SuccessMessageMixin, UpdateView):
    model = models.Especialidad
    template_name = 'core/especialidad_form.html'
    fields = ['nombre']
    success_url = reverse_lazy('core:especialidad_list')
    success_message = "Especialidad '%(nombre)s' actualizada con éxito."

class EspecialidadDeleteView(DeleteView):
    model = models.Especialidad
    template_name = 'core/especialidad_confirm_delete.html'
    success_url = reverse_lazy('core:especialidad_list')
    context_object_name = 'especialidad'

    def form_valid(self, form):
        messages.success(self.request, f"Especialidad '{self.object.nombre}' eliminada con éxito.")
        return super().form_valid(form)

# REEMPLAZA tu PagoCreateView existente por:
class PagoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Pago  # ← Corregido: era 'mode'
    form_class = forms.PagoForm  # ✅ Este formulario existe
    template_name = 'core/pago_form.html'
    success_url = reverse_lazy('core:pago_list')
    success_message = "Pago creado exitosamente."
    
class PagoListView(ListView):
    model = models.Pago
    template_name = 'core/pago_list.html'
    context_object_name = 'pagos'
    paginate_by = 20

    def get_queryset(self):
        return models.Pago.objects.select_related('cita__cliente').order_by('-fecha_pago')

class PagoUpdateView(SuccessMessageMixin, UpdateView):
    model = models.Pago
    form_class = forms.PagoForm
    template_name = 'core/pago_form.html'
    success_url = reverse_lazy('core:pago_list')
    success_message = "Pago actualizado con éxito."

class PagoDeleteView(DeleteView):
    model = models.Pago
    template_name = 'core/pago_confirm_delete.html'
    success_url = reverse_lazy('core:pago_list')
    context_object_name = 'pago'

    def form_valid(self, form):
        messages.success(self.request, f"Pago de {self.object.monto} eliminado con éxito.")
        return super().form_valid(form)

class CompraListView(ListView):
    model = models.Compra
    template_name = 'core/compra_list.html'
    context_object_name = 'compras'
    paginate_by = 15

    def get_queryset(self):
        return models.Compra.objects.select_related('proveedor').order_by('-fecha_compra')

class CompraCreateView(SuccessMessageMixin, CreateView):
    model = models.Compra
    form_class = forms.CompraForm
    template_name = 'core/compra_form.html'
    success_url = reverse_lazy('core:compra_list')
    success_message = "Compra creada con éxito."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.DetalleCompraFormSet(self.request.POST, prefix='detalles')
        else:
            context['formset'] = forms.DetalleCompraFormSet(prefix='detalles')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            
            total = 0
            for detalle_form in formset.cleaned_data:
                if detalle_form and not detalle_form.get('DELETE'):
                    cantidad = detalle_form.get('cantidad', 0)
                    precio = detalle_form.get('precio_unitario', 0)
                    total += cantidad * precio
            self.object.total = total
            
            self.object.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class CompraUpdateView(SuccessMessageMixin, UpdateView):
    model = models.Compra
    form_class = forms.CompraForm
    template_name = 'core/compra_form.html'
    success_url = reverse_lazy('core:compra_list')
    success_message = "Compra actualizada con éxito."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.DetalleCompraFormSet(self.request.POST, instance=self.object, prefix='detalles')
        else:
            context['formset'] = forms.DetalleCompraFormSet(instance=self.object, prefix='detalles')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            
            total = 0
            for detalle_form in formset.cleaned_data:
                if detalle_form and not detalle_form.get('DELETE'):
                    cantidad = detalle_form.get('cantidad', 0)
                    precio = detalle_form.get('precio_unitario', 0)
                    total += cantidad * precio
            self.object.total = total

            self.object.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class CompraDeleteView(DeleteView):
    model = models.Compra
    template_name = 'core/compra_confirm_delete.html'
    success_url = reverse_lazy('core:compra_list')
    context_object_name = 'compra'

    def form_valid(self, form):
        messages.success(self.request, f"Compra a '{self.object.proveedor.nombre}' eliminada con éxito.")
        return super().form_valid(form)

class RecibirCompraView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Compra
    template_name = 'core/compra_recibir.html'
    fields = []
    success_url = reverse_lazy('core:compra_list')
    success_message = "La compra ha sido marcada como 'Recibida' y el stock ha sido actualizado."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.DetalleCompraRecepcionFormSet(self.request.POST, instance=self.object, prefix='detalles')
        else:
            context['formset'] = forms.DetalleCompraRecepcionFormSet(instance=self.object, prefix='detalles')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            with transaction.atomic():
                for detalle_form in formset:
                    detalle = detalle_form.instance
                    unidad_dental = detalle_form.cleaned_data.get('unidad_dental')
                    
                    if not unidad_dental:
                        messages.error(self.request, f"Debe seleccionar una unidad de destino para {detalle.insumo.nombre}.")
                        return self.form_invalid(form)

                    lote, created = models.LoteInsumo.objects.get_or_create(
                        insumo=detalle.insumo,
                        unidad_dental=unidad_dental,
                        numero_lote=detalle_form.cleaned_data.get('numero_lote'),
                        fecha_caducidad=detalle_form.cleaned_data.get('fecha_caducidad'),
                        defaults={'cantidad': detalle.cantidad}
                    )
                    if not created:
                        lote.cantidad += detalle.cantidad
                        lote.save()

                self.object.estado = 'RECIBIDA'
                self.object.save()
            
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class AgendaView(TemplateView):
    template_name = 'core/agenda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cita_form'] = forms.CitaForm()
        context['dentistas'] = models.PerfilDentista.objects.filter(activo=True)
        return context

class CitaListView(LoginRequiredMixin, ListView):
    model = models.Cita
    template_name = 'core/cita_list.html'
    context_object_name = 'citas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = models.Cita.objects.select_related(
            'cliente', 'dentista', 'unidad_dental'
        ).prefetch_related(
            'servicios_planeados', 'servicios_realizados', 'pagos'
        ).order_by('-fecha_hora')
        
        user = self.request.user
        
        # FILTRO POR ROL: Si es dentista, solo ver sus citas
        if user.groups.filter(name='Dentista').exists():
            try:
                perfil_dentista = models.PerfilDentista.objects.get(usuario=user)
                queryset = queryset.filter(dentista=perfil_dentista)
            except models.PerfilDentista.DoesNotExist:
                messages.warning(self.request, 'No tienes un perfil de dentista asignado.')
                queryset = queryset.none()
        
        # FILTROS ADICIONALES
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        dentista_id = self.request.GET.get('dentista')
        if dentista_id and user.groups.filter(name__in=['Administrador', 'Recepcionista']).exists():
            queryset = queryset.filter(dentista_id=dentista_id)
        
        fecha = self.request.GET.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha_hora__date=fecha)
        
        # Filtro por paciente
        paciente = self.request.GET.get('paciente')
        if paciente:
            queryset = queryset.filter(
                models.Q(cliente__nombre__icontains=paciente) |
                models.Q(cliente__apellido__icontains=paciente)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Estados disponibles
        context['estados'] = [
            ('PRO', 'Programada'),
            ('CON', 'Confirmada'),
            ('ATN', 'Atendida'),
            ('COM', 'Completada'),
            ('CAN', 'Cancelada'),
        ]
        
        # Solo admin y recepción pueden filtrar por dentista
        context['puede_filtrar_dentista'] = user.groups.filter(
            name__in=['Administrador', 'Recepcionista']
        ).exists()
        
        if context['puede_filtrar_dentista']:
            context['dentistas'] = models.PerfilDentista.objects.filter(activo=True)
        
        # Estadísticas del queryset filtrado
        queryset = self.get_queryset()
        context['stats'] = {
            'programadas': queryset.filter(estado='PRO').count(),
            'confirmadas': queryset.filter(estado='CON').count(),
            'atendidas': queryset.filter(estado='ATN').count(),
            'completadas': queryset.filter(estado='COM').count(),
            'canceladas': queryset.filter(estado='CAN').count(),
            'total': queryset.count(),
        }
        
        # Añadir datos calculados a cada cita
        for cita in context['citas']:
            # Calcular costos
            cita.costo_estimado_calc = sum(s.precio for s in cita.servicios_planeados.all())
            cita.costo_real_calc = sum(s.precio for s in cita.servicios_realizados.all()) 
            cita.total_pagado_calc = cita.pagos.aggregate(total=Sum('monto'))['total'] or 0
            cita.saldo_pendiente_calc = cita.costo_real_calc - cita.total_pagado_calc
            
            # Calcular duración estimada  
            cita.duracion_estimada_calc = sum(s.duracion_minutos for s in cita.servicios_planeados.all())
        
        # Filtros aplicados (para mantener en los links de paginación)
        context['filtros_actuales'] = {
            'estado': self.request.GET.get('estado', ''),
            'dentista': self.request.GET.get('dentista', ''),
            'fecha': self.request.GET.get('fecha', ''),
            'paciente': self.request.GET.get('paciente', ''),
        }
        
        return context
    
class CambiarEstadoCitaView(LoginRequiredMixin, UpdateView):
    model = models.Cita
    template_name = 'core/cita_cambiar_estado.html'
    fields = ['estado', 'notas']
    success_url = reverse_lazy('core:cita_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estados permitidos según rol
        user = self.request.user
        cita = self.object
        
        if user.groups.filter(name='Recepcionista').exists():
            # Recepción puede: Programada → Confirmada, Confirma → Cancelada
            if cita.estado == 'PRO':
                context['estados_permitidos'] = [('CON', 'Confirmada'), ('CAN', 'Cancelada')]
            elif cita.estado == 'CON':
                context['estados_permitidos'] = [('CAN', 'Cancelada')]
            else:
                context['estados_permitidos'] = []
                
        elif user.groups.filter(name='Dentista').exists():
            # Dentista puede: Confirmada → Atendida (a través de "Finalizar Cita")
            context['estados_permitidos'] = []  # Usan vista especial
            
        else:  # Administrador
            # Admin puede todo
            context['estados_permitidos'] = [
                ('PRO', 'Programada'),
                ('CON', 'Confirmada'), 
                ('ATN', 'Atendida'),
                ('COM', 'Completada'),
                ('CAN', 'Cancelada'),
            ]
        
        return context
    
    def form_valid(self, form):
        cita = form.save()
        
        # Mensajes personalizados
        estado_msgs = {
            'CON': f'Cita de {cita.cliente} confirmada para {cita.fecha_hora.strftime("%d/%m/%Y %H:%M")}',
            'CAN': f'Cita de {cita.cliente} cancelada',
            'ATN': f'Cita de {cita.cliente} marcada como atendida',
            'COM': f'Cita de {cita.cliente} completada',
        }
        
        if cita.estado in estado_msgs:
            messages.success(self.request, estado_msgs[cita.estado])
        
        return super().form_valid(form)
class CitasPendientesPagoListView(LoginRequiredMixin, ListView):
    model = models.Cita
    template_name = 'core/citas_pendientes_pago.html'
    context_object_name = 'citas'

    def get_queryset(self):
        return models.Cita.objects.filter(estado='ATN').select_related('cliente', 'dentista').order_by('fecha_hora')

class FinalizarCitaView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Cita
    form_class = forms.FinalizarCitaForm
    template_name = 'core/cita_finalizar.html'
    success_url = reverse_lazy('core:agenda')
    success_message = "La cita ha sido marcada como 'Atendida' y enviada a caja."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['paciente_form'] = forms.PacientePlanPagoForm(self.request.POST, instance=self.object.cliente)
        else:
            context['paciente_form'] = forms.PacientePlanPagoForm(instance=self.object.cliente)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        paciente_form = context['paciente_form']
        
        if paciente_form.is_valid():
            with transaction.atomic():
                paciente = paciente_form.save()
                
                cita = form.save(commit=False)
                
                servicios = form.cleaned_data['servicios_realizados']
                consumo_descripcion = []

                for servicio in servicios:
                    for item in servicio.servicioinsumo_set.all():
                        insumo_a_consumir = item.insumo
                        cantidad_necesaria = item.cantidad
                        
                        lotes_disponibles = models.LoteInsumo.objects.filter(
                            insumo=insumo_a_consumir,
                            unidad_dental=cita.unidad_dental,
                            cantidad__gt=0
                        ).order_by('fecha_caducidad')

                        for lote in lotes_disponibles:
                            if cantidad_necesaria <= 0:
                                break
                            
                            cantidad_a_tomar = min(lote.cantidad, cantidad_necesaria)
                            
                            lote.cantidad -= cantidad_a_tomar
                            lote.save()
                            
                            cantidad_necesaria -= cantidad_a_tomar
                            
                            consumo_descripcion.append(
                                f"{cantidad_a_tomar} de {insumo_a_consumir.nombre} (Lote: {lote.numero_lote or 'N/A'}, Cad: {lote.fecha_caducidad or 'N/A'})"
                            )
                
                if consumo_descripcion:
                    descripcion_evento = "Consumo de insumos para la cita: " + ", ".join(consumo_descripcion) + "."
                    models.HistorialClinico.objects.create(
                        cliente=cita.cliente,
                        descripcion_evento=descripcion_evento,
                        registrado_por=self.request.user.perfil_dentista
                    )
                
                dentista = self.request.user.perfil_dentista
                models.HistorialClinico.objects.create(
                    cliente=cita.cliente,
                    descripcion_evento=f"Cita atendida por Dr. {dentista}. Servicios: {', '.join(s.nombre for s in servicios)}.",
                    registrado_por=dentista
                )

                cita.estado = 'ATN'
                cita.save()
                form.save_m2m()
                
                paciente.actualizar_saldo_global()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class HistorialPacienteView(DetailView):
    model = models.Paciente
    template_name = 'core/historial_paciente.html'
    context_object_name = 'paciente'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.HistorialClinicoForm()

        import math
        
        def calcular_posiciones_arco(num_dientes, radio_x, radio_y, centro_x, centro_y, angulo_inicio, angulo_fin, es_inferior=False):
            dientes = []
            total_angulos = angulo_fin - angulo_inicio
            paso_angulo = total_angulos / (num_dientes - 1)
            
            for i in range(num_dientes):
                angulo_actual = angulo_inicio + (i * paso_angulo)
                angulo_rad = math.radians(angulo_actual)
                
                x = centro_x + radio_x * math.cos(angulo_rad)
                y = centro_y + radio_y * math.sin(angulo_rad)
                
                rotacion = angulo_actual + 90
                if es_inferior:
                    rotacion += 180

                dientes.append({'x': x, 'y': y, 'rotacion': rotacion})
            return dientes

        dientes_sup_data = [
            {'visual': 1, 'fdi': 18}, {'visual': 2, 'fdi': 17}, {'visual': 3, 'fdi': 16}, {'visual': 4, 'fdi': 15},
            {'visual': 5, 'fdi': 14}, {'visual': 6, 'fdi': 13}, {'visual': 7, 'fdi': 12}, {'visual': 8, 'fdi': 11},
            {'visual': 9, 'fdi': 21}, {'visual': 10, 'fdi': 22}, {'visual': 11, 'fdi': 23}, {'visual': 12, 'fdi': 24},
            {'visual': 13, 'fdi': 25}, {'visual': 14, 'fdi': 26}, {'visual': 15, 'fdi': 27}, {'visual': 16, 'fdi': 28},
        ]
        dientes_inf_data = [
            {'visual': 32, 'fdi': 48}, {'visual': 31, 'fdi': 47}, {'visual': 30, 'fdi': 46}, {'visual': 29, 'fdi': 45},
            {'visual': 28, 'fdi': 44}, {'visual': 27, 'fdi': 43}, {'visual': 26, 'fdi': 42}, {'visual': 25, 'fdi': 41},
            {'visual': 24, 'fdi': 31}, {'visual': 23, 'fdi': 32}, {'visual': 22, 'fdi': 33}, {'visual': 21, 'fdi': 34},
            {'visual': 20, 'fdi': 35}, {'visual': 19, 'fdi': 36}, {'visual': 18, 'fdi': 37}, {'visual': 17, 'fdi': 38},
        ]

        pos_sup = calcular_posiciones_arco(16, 420, 120, 460, 200, 195, 345)
        pos_inf = calcular_posiciones_arco(16, 420, 120, 460, 200, 165, 15, es_inferior=True)
        
        context['dientes_superiores'] = [{**d, **p} for d, p in zip(dientes_sup_data, pos_sup)]
        context['dientes_inferiores'] = [{**d, **p} for d, p in zip(dientes_inf_data, reversed(pos_inf))]

        return context

class HistorialClinicoCreateView(CreateView):
    model = models.HistorialClinico
    form_class = forms.HistorialClinicoForm

    def form_valid(self, form):
        cliente = models.Paciente.objects.get(pk=self.kwargs['cliente_id'])
        form.instance.cliente = cliente
        form.instance.registrado_por = self.request.user.perfil_dentista
        
        dientes_seleccionados = form.cleaned_data['dientes_seleccionados'].split(',')
        diagnostico = form.cleaned_data['diagnostico']
        
        for diente_num in dientes_seleccionados:
            if diente_num:
                models.EstadoDiente.objects.update_or_create(
                    cliente=cliente,
                    numero_diente=int(diente_num),
                    defaults={'diagnostico': diagnostico}
                )
        
        messages.success(self.request, f"Se guardó la nota de evolución y se actualizaron {len(dientes_seleccionados)} dientes.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('core:cliente_history', kwargs={'pk': self.kwargs['cliente_id']})

def agenda_events(request):
    dentista_id = request.GET.get('dentista_id')
    citas = models.Cita.objects.all()
    if dentista_id:
        citas = citas.filter(dentista_id=dentista_id)
    
    eventos = []
    for cita in citas:
        eventos.append({
            'id': cita.id,
            'title': f"{cita.cliente.nombre} {cita.cliente.apellido}",
            'start': cita.fecha_hora.isoformat(),
        })
    return JsonResponse(eventos, safe=False)

def cita_create_api(request):
    if request.method == 'POST':
        form = forms.CitaForm(request.POST)
        if form.is_valid():
            cita = form.save()
            return JsonResponse({'status': 'success', 'message': 'Cita creada con éxito.', 'cita_id': cita.id})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def cita_detail_api(request, pk):
    try:
        cita = models.Cita.objects.get(pk=pk)
        data = {
            'cliente': cita.cliente.id,
            'dentista': cita.dentista.id if cita.dentista else '',
            'fecha_hora': cita.fecha_hora.strftime('%Y-%m-%dT%H:%M'),
            'motivo': cita.motivo,
            'estado': cita.estado,
        }
        return JsonResponse(data)
    except models.Cita.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cita no encontrada'}, status=404)

@csrf_exempt
@require_POST
def cita_update_api(request, pk):
    try:
        cita = models.Cita.objects.get(pk=pk)
        form = forms.CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Cita actualizada con éxito.'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except models.Cita.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cita no encontrada'}, status=404)

@csrf_exempt
@require_POST
def cita_delete_api(request, pk):
    try:
        cita = models.Cita.objects.get(pk=pk)
        cita.delete()
        return JsonResponse({'status': 'success', 'message': 'Cita eliminada con éxito.'})
    except models.Cita.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cita no encontrada'}, status=404)

def odontograma_api_get(request, cliente_id):
    try:
        cliente = models.Paciente.objects.get(pk=cliente_id)
        sano = models.Diagnostico.objects.get(nombre='SANO')
        
        dientes_estandar = list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))
        data = {
            diente: {
                'diagnostico_id': sano.id,
                'diagnostico_nombre': sano.nombre,
                'diagnostico_color': sano.color_hex,
                'diagnostico_icono': sano.icono_svg,
                'color_seleccionado': ''
            } for diente in dientes_estandar
        }

        estados_guardados = cliente.odontograma.select_related('diagnostico')
        for estado in estados_guardados:
            data[estado.numero_diente] = {
                'diagnostico_id': estado.diagnostico.id,
                'diagnostico_nombre': estado.diagnostico.nombre,
                'diagnostico_color': estado.diagnostico.color_hex,
                'diagnostico_icono': estado.diagnostico.icono_svg,
                'color_seleccionado': estado.color_seleccionado
            }
        
        return JsonResponse(data)

    except models.Paciente.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Paciente no encontrado'}, status=404)
    except models.Diagnostico.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Diagnóstico "SANO" no encontrado. Ejecute las migraciones.'}, status=500)

@csrf_exempt
@require_POST
def odontograma_api_update(request, cliente_id):
    try:
        data = json.loads(request.body)
        numero_diente = data.get('numero_diente')
        diagnostico_id = data.get('diagnostico_id')
        color_seleccionado = data.get('color_seleccionado', '')

        cliente = models.Paciente.objects.get(pk=cliente_id)
        diagnostico = models.Diagnostico.objects.get(pk=diagnostico_id)
        dentista = models.PerfilDentista.objects.filter(usuario=request.user).first()

        obj, created = models.EstadoDiente.objects.update_or_create(
            cliente=cliente,
            numero_diente=numero_diente,
            defaults={
                'diagnostico': diagnostico,
                'color_seleccionado': color_seleccionado
            }
        )

        descripcion = (
            f"Se {'asignó' if created else 'actualizó'} el diagnóstico '{diagnostico.nombre}' "
            f"al diente {numero_diente}."
        )
        if color_seleccionado:
            descripcion += f" Se asignó el color {color_seleccionado}."

        models.HistorialClinico.objects.create(
            cliente=cliente,
            descripcion_evento=descripcion,
            registrado_por=dentista
        )

        return JsonResponse({'status': 'success', 'message': 'Odontograma actualizado.'})

    except (models.Paciente.DoesNotExist, models.Diagnostico.DoesNotExist) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def diagnostico_api_list(request):
    diagnosticos = models.Diagnostico.objects.all().order_by('nombre')
    data = [{'id': d.id, 'nombre': d.nombre, 'color_hex': d.color_hex, 'icono_svg': d.icono_svg} for d in diagnosticos]
    return JsonResponse(data, safe=False)

def reporte_ingresos_api(request):
    form = forms.ReporteIngresosForm(request.GET or None)
    data = {'labels': [], 'values': []}
    if form.is_valid():
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
        ingresos = models.Pago.objects.filter(
            fecha_pago__date__gte=fecha_inicio,
            fecha_pago__date__lte=fecha_fin
        ).values('fecha_pago__date').annotate(total_dia=Sum('monto')).order_by('fecha_pago__date')
        
        for item in ingresos:
            data['labels'].append(item['fecha_pago__date'].strftime('%d/%m/%Y'))
            data['values'].append(float(item['total_dia']))
            
    return JsonResponse(data)

def reporte_saldos_api(request):
    # USAR SALDO_GLOBAL DE PACIENTES
    saldos = models.Paciente.objects.filter(
        saldo_global__gt=0
    ).values('nombre', 'apellido', 'saldo_global').order_by('-saldo_global')[:10]
    
    data = {
        'labels': [f"{item['nombre']} {item['apellido']}" for item in saldos],
        'values': [float(item['saldo_global']) for item in saldos]
    }
    return JsonResponse(data)

class ReciboPagoView(LoginRequiredMixin, DetailView):
    model = models.Pago
    template_name = 'core/recibo_pago.html'
    context_object_name = 'pago'

def generar_recibo_pdf(request, pk):
    pago = get_object_or_404(models.Pago, pk=pk)
    formato = request.GET.get('formato', 'carta')
    response = HttpResponse(content_type='application/pdf')
    filename = f"recibo_{pago.id}_{formato}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    if formato == 'ticket':
        width, height = 80 * mm, 200 * mm
        _generar_recibo_ticket(response, pago, width, height)
    else:
        _generar_recibo_carta(response, pago)
    
    return response

def _generar_recibo_carta(response, pago):
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    if pago.cita.cliente.tenant.logo:
        try:
            logo = Image(pago.cita.cliente.tenant.logo.path, width=50, height=50)
            logo.hAlign = 'LEFT'
            story.append(logo)
        except Exception:
            story.append(Paragraph(f"<h1>{pago.cita.cliente.tenant.nombre}</h1>", styles['h1']))
    else:
        story.append(Paragraph(f"<h1>{pago.cita.cliente.tenant.nombre}</h1>", styles['h1']))

    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Recibo de Pago #{pago.id}</b>", styles['h2']))
    story.append(Paragraph(f"Fecha: {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 24))

    story.append(Paragraph("<b>Paciente:</b>", styles['h4']))
    story.append(Paragraph(f"{pago.cita.cliente.nombre} {pago.cita.cliente.apellido}", styles['Normal']))
    if pago.cita.cliente.email:
        story.append(Paragraph(f"{pago.cita.cliente.email}", styles['Normal']))
    story.append(Spacer(1, 24))

    story.append(Paragraph("<b>Detalles del Pago:</b>", styles['h4']))
    
    data = [['Descripción', 'Monto']]
    total_servicios = 0
    for servicio in pago.cita.servicios_realizados.all():
        data.append([servicio.nombre, f"${servicio.precio:,.2f}"])
        total_servicios += servicio.precio

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    
    tbl = Table(data, colWidths=[300, 100])
    tbl.setStyle(style)
    story.append(tbl)
    
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Total Servicios:</b> ${total_servicios:,.2f}", styles['Right']))
    story.append(Paragraph(f"<b>Monto Pagado ({pago.metodo_pago}):</b> ${pago.monto:,.2f}", styles['Right']))
    story.append(Paragraph(f"<b>Saldo Pendiente del paciente:</b> ${pago.cita.cliente.saldo_global:,.2f}", styles['Right']))

    doc.build(story)

def _generar_recibo_ticket(response, pago, width, height):
    from reportlab.pdfgen import canvas
    
    c = canvas.Canvas(response, pagesize=(width, height))
    
    x_pos = 3 * mm
    y_pos = height - (10 * mm)
    line_height = 5 * mm

    if pago.cita.cliente.tenant.logo:
        try:
            c.drawImage(pago.cita.cliente.tenant.logo.path, x_pos, y_pos - 10*mm, width=20*mm, height=20*mm, preserveAspectRatio=True)
            y_pos -= 25 * mm
        except Exception:
            pass
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_pos, y_pos, pago.cita.cliente.tenant.nombre)
    y_pos -= line_height * 2

    c.setFont("Helvetica", 9)
    c.drawString(x_pos, y_pos, f"Recibo de Pago #{pago.id}")
    y_pos -= line_height
    c.drawString(x_pos, y_pos, f"Fecha: {pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}")
    y_pos -= line_height * 1.5
    
    c.drawString(x_pos, y_pos, f"Paciente: {pago.cita.cliente}")
    y_pos -= line_height * 2

    c.line(x_pos, y_pos, width - x_pos, y_pos)
    y_pos -= line_height

    c.setFont("Helvetica-Bold", 9)
    c.drawString(x_pos, y_pos, "Servicios:")
    y_pos -= line_height
    c.setFont("Helvetica", 8)
    total_servicios = 0
    for servicio in pago.cita.servicios_realizados.all():
        c.drawString(x_pos + 2*mm, y_pos, f"- {servicio.nombre}")
        c.drawRightString(width - x_pos, y_pos, f"${servicio.precio:,.2f}")
        total_servicios += servicio.precio
        y_pos -= line_height

    y_pos -= line_height
    
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(width - x_pos, y_pos, f"Total: ${total_servicios:,.2f}")
    y_pos -= line_height
    c.drawRightString(width - x_pos, y_pos, f"Pagado: ${pago.monto:,.2f}")
    y_pos -= line_height
    c.drawRightString(width - x_pos, y_pos, f"Saldo: ${pago.cita.saldo_pendiente:,.2f}")
    y_pos -= line_height * 2

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, y_pos, "Gracias por su preferencia")

    c.showPage()
    c.save()

class DashboardCofeprisView(LoginRequiredMixin, TemplateView):
    template_name = 'core/cofepris/dashboard_cofepris.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date, timedelta
        hoy = date.today()
        proximos_60_dias = hoy + timedelta(days=60)

        context['aviso_vencimiento'] = models.AvisoFuncionamiento.objects.filter(
            consultorio=self.request.tenant,
            fecha_vencimiento__lte=proximos_60_dias
        ).first()

        context['equipos_proximos_a_vencer'] = models.Equipo.objects.filter(
            unidad_trabajo__in=models.UnidadDental.objects.all(),
            fecha_vencimiento_calibracion__lte=proximos_60_dias
        ).order_by('fecha_vencimiento_calibracion')

        return context

class DiagnosticoListView(LoginRequiredMixin, ListView):
    model = models.Diagnostico
    template_name = 'core/diagnostico_list.html'
    context_object_name = 'diagnosticos'

class DiagnosticoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Diagnostico
    template_name = 'core/diagnostico_form.html'
    fields = ['nombre', 'color_hex', 'icono_svg']
    success_url = reverse_lazy('core:diagnostico_list')
    success_message = "Diagnóstico '%(nombre)s' creado con éxito."

class DiagnosticoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Diagnostico
    template_name = 'core/diagnostico_form.html'
    fields = ['nombre', 'color_hex', 'icono_svg']
    success_url = reverse_lazy('core:diagnostico_list')
    success_message = "Diagnóstico '%(nombre)s' actualizado con éxito."

class DiagnosticoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.Diagnostico
    template_name = 'core/diagnostico_confirm_delete.html'
    success_url = reverse_lazy('core:diagnostico_list')
    context_object_name = 'diagnostico'
    success_message = "Diagnóstico eliminado con éxito."

class AvisoFuncionamientoListView(LoginRequiredMixin, ListView):
    model = models.AvisoFuncionamiento
    template_name = 'core/cofepris/aviso_funcionamiento_list.html'
    context_object_name = 'avisos'

    def get_queryset(self):
        return models.AvisoFuncionamiento.objects.filter(consultorio=self.request.tenant)

class AvisoFuncionamientoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.AvisoFuncionamiento
    form_class = forms.AvisoFuncionamientoForm
    template_name = 'core/cofepris/aviso_funcionamiento_form.html'
    success_url = reverse_lazy('core:aviso_list')
    success_message = "Aviso de Funcionamiento creado con éxito."

    def form_valid(self, form):
        form.instance.consultorio = self.request.tenant
        return super().form_valid(form)

class AvisoFuncionamientoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.AvisoFuncionamiento
    form_class = forms.AvisoFuncionamientoForm
    template_name = 'core/cofepris/aviso_funcionamiento_form.html'
    success_url = reverse_lazy('core:aviso_list')
    success_message = "Aviso de Funcionamiento actualizado con éxito."

class EquipoListView(LoginRequiredMixin, ListView):
    model = models.Equipo
    template_name = 'core/cofepris/equipo_list.html'
    context_object_name = 'equipos'

class EquipoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Equipo
    form_class = forms.EquipoForm
    template_name = 'core/cofepris/equipo_form.html'
    success_url = reverse_lazy('core:equipo_list')
    success_message = "Equipo '%(nombre)s' registrado con éxito."

class EquipoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Equipo
    form_class = forms.EquipoForm
    template_name = 'core/cofepris/equipo_form.html'
    success_url = reverse_lazy('core:equipo_list')
    success_message = "Equipo '%(nombre)s' actualizado con éxito."

class EquipoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.Equipo
    template_name = 'core/cofepris/equipo_confirm_delete.html'
    success_url = reverse_lazy('core:equipo_list')
    context_object_name = 'equipo'
    success_message = "Equipo eliminado con éxito."

class ResiduosListView(LoginRequiredMixin, ListView):
    model = models.Residuos
    template_name = 'core/cofepris/residuos_list.html'
    context_object_name = 'recolecciones'

class ResiduosCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Residuos
    form_class = forms.ResiduosForm
    template_name = 'core/cofepris/residuos_form.html'
    success_url = reverse_lazy('core:residuos_list')
    success_message = "Recolección de residuos registrada con éxito."

    def form_valid(self, form):
        form.instance.consultorio = self.request.tenant
        return super().form_valid(form)

class ResiduosUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Residuos
    form_class = forms.ResiduosForm
    template_name = 'core/cofepris/residuos_form.html'
    success_url = reverse_lazy('core:residuos_list')
    success_message = "Recolección de residuos actualizada con éxito."

class ResiduosDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.Residuos
    template_name = 'core/cofepris/residuos_confirm_delete.html'
    success_url = reverse_lazy('core:residuos_list')
    context_object_name = 'recoleccion'
    success_message = "Registro de recolección eliminado con éxito."

def exportar_ingresos_excel(request):
    form = forms.ReporteIngresosForm(request.GET or None)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_ingresos.xlsx"'
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Ingresos'
    headers = ['Fecha de Pago', 'Paciente', 'Cita', 'Método de Pago', 'Monto']
    worksheet.append(headers)
    if form.is_valid():
        pagos = models.Pago.objects.filter(
            fecha_pago__date__gte=form.cleaned_data['fecha_inicio'],
            fecha_pago__date__lte=form.cleaned_data['fecha_fin']
        ).select_related('cita__cliente')
        for pago in pagos:
            worksheet.append([
                pago.fecha_pago.strftime('%Y-%m-%d %H:%M'),
                str(pago.cita.cliente),
                f"Cita #{pago.cita.id}",
                pago.metodo_pago,
                pago.monto
            ])
    workbook.save(response)
    return response

def exportar_saldos_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_saldos.xlsx"'
    
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Saldos Pendientes'
    
    headers = ['Paciente', 'Saldo Pendiente']
    worksheet.append(headers)
    
    # USAR SALDO_GLOBAL DE PACIENTES
    pacientes = models.Paciente.objects.filter(saldo_global__gt=0).order_by('-saldo_global')
    for paciente in pacientes:
        worksheet.append([
            f"{paciente.nombre} {paciente.apellido}", 
            float(paciente.saldo_global)
        ])
    
    workbook.save(response)
    return response

def exportar_facturacion_excel(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_facturacion.xlsx"'
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Facturación'
    headers = ['Fecha Cita', 'Paciente', 'RFC', 'Domicilio Fiscal', 'Uso CFDI', 'Servicios', 'Monto Pagado']
    worksheet.append(headers)
    citas = models.Cita.objects.filter(requiere_factura=True).select_related('cliente', 'cliente__datos_fiscales').prefetch_related('servicios_realizados', 'pagos')
    for cita in citas:
        servicios = ", ".join([s.nombre for s in cita.servicios_realizados.all()])
        monto_pagado = cita.pagos.aggregate(total=Sum('monto'))['total'] or 0
        worksheet.append([
            cita.fecha_hora.strftime('%Y-%m-%d'),
            str(cita.cliente),
            getattr(getattr(cita.cliente, 'datos_fiscales', None), 'rfc', 'N/A'),
            getattr(getattr(cita.cliente, 'datos_fiscales', None), 'domicilio_fiscal', 'N/A'),
            getattr(getattr(cita.cliente, 'datos_fiscales', None), 'uso_cfdi', 'N/A'),
            servicios,
            monto_pagado
        ])
    workbook.save(response)
    return response

class InvitarPacienteView(LoginRequiredMixin, TemplateView):
    template_name = 'core/paciente_invitar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paciente'] = get_object_or_404(models.Paciente, pk=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        paciente = get_object_or_404(models.Paciente, pk=self.kwargs['pk'])
        if paciente.usuario:
            messages.error(request, 'Este paciente ya tiene una cuenta de usuario.')
            return redirect('core:paciente_detail', pk=paciente.pk)

        username = paciente.email or f'{paciente.nombre.lower()}.{paciente.apellido.lower()}{paciente.pk}'
        if User.objects.filter(username=username).exists():
            username = f'{username}{random.randint(10,99)}'
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        user = User.objects.create_user(username=username, email=paciente.email, password=password)
        user.first_name = paciente.nombre
        user.last_name = paciente.apellido
        
        paciente_group, _ = Group.objects.get_or_create(name='Paciente')
        user.groups.add(paciente_group)
        user.save()

        paciente.usuario = user
        paciente.save()

        messages.success(request, f'Se creó la cuenta para {paciente}. Usuario: {username}, Contraseña: {password}')
        return redirect('core:paciente_detail', pk=paciente.pk)

class PacientePagosListView(LoginRequiredMixin, ListView):
    model = models.Pago
    template_name = 'core/portal/pago_list.html'
    context_object_name = 'pagos'
    paginate_by = 10

    def get_queryset(self):
        return models.Pago.objects.filter(cita__cliente__usuario=self.request.user).order_by('-fecha_pago')

class ResetPasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'core/usuario_reset_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_a_resetear'] = get_object_or_404(User, pk=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        usuario = get_object_or_404(User, pk=self.kwargs['pk'])
        
        if not request.user.groups.filter(name='Administrador').exists() and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para realizar esta acción.')
            return redirect('core:usuario_list')

        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        usuario.set_password(new_password)
        usuario.save()

        messages.success(request, f'La contraseña para {usuario.username} ha sido restablecida a: {new_password}')
        return redirect('core:usuario_edit', pk=usuario.pk)

class CuestionarioHistorialView(LoginRequiredMixin, TemplateView):
    template_name = 'core/cuestionario_historial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente = get_object_or_404(models.Paciente, pk=self.kwargs['pk'])
        context['paciente'] = paciente
        
        preguntas = models.PreguntaHistorial.objects.filter(activa=True)
        for pregunta in preguntas:
            models.RespuestaHistorial.objects.get_or_create(paciente=paciente, pregunta=pregunta, defaults={'respuesta': ''})
            
        if self.request.POST:
            context['formset'] = forms.RespuestaHistorialFormSet(self.request.POST, queryset=paciente.respuestas_historial.all())
        else:
            context['formset'] = forms.RespuestaHistorialFormSet(queryset=paciente.respuestas_historial.all())
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        formset = context['formset']
        
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Cuestionario de historial clínico guardado con éxito.')
            return redirect('core:paciente_detail', pk=self.kwargs['pk'])
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
            return self.render_to_response(context)

class PreguntaHistorialListView(LoginRequiredMixin, ListView):
    model = models.PreguntaHistorial
    template_name = 'core/configuracion/pregunta_list.html'
    context_object_name = 'preguntas'

class PreguntaHistorialCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.PreguntaHistorial
    fields = ['texto', 'tipo', 'opciones', 'orden', 'activa']
    template_name = 'core/configuracion/pregunta_form.html'
    success_url = reverse_lazy('core:pregunta_list')
    success_message = "Pregunta creada con éxito."

class PreguntaHistorialUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.PreguntaHistorial
    fields = ['texto', 'tipo', 'opciones', 'orden', 'activa']
    template_name = 'core/configuracion/pregunta_form.html'
    success_url = reverse_lazy('core:pregunta_list')
    success_message = "Pregunta actualizada con éxito."

class PreguntaHistorialDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.PreguntaHistorial
    template_name = 'core/configuracion/pregunta_confirm_delete.html'
    success_url = reverse_lazy('core:pregunta_list')
    context_object_name = 'pregunta'
    success_message = "Pregunta eliminada con éxito."

class ReporteServiciosMasVendidosView(LoginRequiredMixin, ListView):
    model = models.Servicio
    template_name = 'core/reportes/reporte_servicios_vendidos.html'
    context_object_name = 'servicios'

    def get_queryset(self):
        return models.Servicio.objects.annotate(
            cantidad_vendida=Count('cita'),
            ingresos_generados=Sum('cita__servicios_realizados__precio')
        ).filter(cantidad_vendida__gt=0).order_by('-cantidad_vendida')

class ReporteIngresosPorDentistaView(LoginRequiredMixin, ListView):
    model = models.Pago
    template_name = 'core/reportes/reporte_ingresos_dentista.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        queryset = models.Pago.objects.select_related('paciente', 'cita__dentista').order_by('-fecha_pago')
        form = forms.ReporteIngresosDentistaForm(self.request.GET)

        if form.is_valid():
            dentista = form.cleaned_data.get('dentista')
            if dentista:
                queryset = queryset.filter(cita__dentista=dentista)
            
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            if fecha_inicio:
                queryset = queryset.filter(fecha_pago__date__gte=fecha_inicio)

            fecha_fin = form.cleaned_data.get('fecha_fin')
            if fecha_fin:
                queryset = queryset.filter(fecha_pago__date__lte=fecha_fin)
        
        return queryset
# REEMPLAZA la clase ReporteIngresosView existente por:
class ReporteIngresosView(LoginRequiredMixin, ListView):
    model = models.Pago
    template_name = 'core/reportes/reporte_ingresos.html'
    context_object_name = 'pagos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = models.Pago.objects.select_related('cita__cliente').order_by('-fecha_pago')
        form = forms.ReporteIngresosForm(self.request.GET)
        if form.is_valid():
            fecha_inicio = form.cleaned_data.get('fecha_inicio')
            fecha_fin = form.cleaned_data.get('fecha_fin')
            if fecha_inicio:
                queryset = queryset.filter(fecha_pago__date__gte=fecha_inicio)
            if fecha_fin:
                queryset = queryset.filter(fecha_pago__date__lte=fecha_fin)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.ReporteIngresosForm(self.request.GET or None)
        context['total_ingresos'] = self.get_queryset().aggregate(total=Sum('monto'))['total'] or 0
        return context
# ==================== VISTAS FALTANTES ====================

# --- PROVEEDORES ---
class ProveedorListView(LoginRequiredMixin, ListView):
    model = models.Proveedor
    template_name = 'core/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 15

class ProveedorCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Proveedor
    template_name = 'core/proveedor_form.html'
    fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion']
    success_url = reverse_lazy('core:proveedor_list')
    success_message = "Proveedor '%(nombre)s' creado con éxito."

class ProveedorUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Proveedor
    template_name = 'core/proveedor_form.html'
    fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion']
    success_url = reverse_lazy('core:proveedor_list')
    success_message = "Proveedor '%(nombre)s' actualizado con éxito."

class ProveedorDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Proveedor
    template_name = 'core/proveedor_confirm_delete.html'
    success_url = reverse_lazy('core:proveedor_list')
    context_object_name = 'proveedor'
    
    def form_valid(self, form):
        messages.success(self.request, f"Proveedor '{self.object.nombre}' eliminado con éxito.")
        return super().form_valid(form)

# --- INSUMOS ---
class InsumoListView(LoginRequiredMixin, ListView):
    model = models.Insumo
    template_name = 'core/insumo_list.html'
    context_object_name = 'insumos'
    paginate_by = 15

class InsumoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Insumo
    template_name = 'core/insumo_form.html'
    fields = ['nombre', 'descripcion', 'unidad_medida', 'stock_minimo', 'precio_unitario']
    success_url = reverse_lazy('core:insumo_list')
    success_message = "Insumo '%(nombre)s' creado con éxito."

class InsumoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Insumo
    template_name = 'core/insumo_form.html'
    fields = ['nombre', 'descripcion', 'unidad_medida', 'stock_minimo', 'precio_unitario']
    success_url = reverse_lazy('core:insumo_list')
    success_message = "Insumo '%(nombre)s' actualizado con éxito."

class InsumoDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Insumo
    template_name = 'core/insumo_confirm_delete.html'
    success_url = reverse_lazy('core:insumo_list')
    context_object_name = 'insumo'
    
    def form_valid(self, form):
        messages.success(self.request, f"Insumo '{self.object.nombre}' eliminado con éxito.")
        return super().form_valid(form)

# --- PAGOS ---
class RegistrarPagoView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Pago
    form_class = forms.PagoForm
    template_name = 'core/pago_registrar.html'
    success_url = reverse_lazy('core:pago_list')
    success_message = "Pago registrado con éxito."
    
    def get_initial(self):
        initial = super().get_initial()
        if 'paciente_id' in self.kwargs:
            paciente = get_object_or_404(models.Paciente, pk=self.kwargs['paciente_id'])
            initial['cliente'] = paciente
        elif 'cita_id' in self.kwargs:
            cita = get_object_or_404(models.Cita, pk=self.kwargs['cita_id'])
            initial['cita'] = cita
        return initial

class ProcesarPagoView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Cita
    form_class = forms.FinalizarCitaForm  # ✅ Este formulario SÍ existe
    template_name = 'core/cita_procesar_pago.html'
    success_url = reverse_lazy('core:citas_pendientes_pago')
    success_message = "Pago procesado con éxito."

# --- REPORTES ---
class ReporteSaldosView(LoginRequiredMixin, ListView):
    model = models.Cita
    template_name = 'core/reportes/reporte_saldos.html'
    context_object_name = 'citas_con_saldo'
    
    def get_queryset(self):
        return models.Cita.objects.filter(
            saldo_pendiente__gt=0
        ).select_related('cliente').order_by('-saldo_pendiente')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_saldos'] = self.get_queryset().aggregate(
            total=Sum('saldo_pendiente')
        )['total'] or 0
        return context

class ReporteFacturacionView(LoginRequiredMixin, ListView):
    model = models.Cita
    template_name = 'core/reportes/reporte_facturacion.html'
    context_object_name = 'citas_facturacion'
    
    def get_queryset(self):
        return models.Cita.objects.filter(
            requiere_factura=True
        ).select_related('cliente').order_by('-fecha_hora')