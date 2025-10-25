# core/views_laboratorio.py
"""
Vistas para gestión de trabajos de laboratorio dental
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Sum, Avg
from datetime import date, timedelta
from decimal import Decimal

from .mixins import TenantLoginRequiredMixin, TenantSuccessUrlMixin, tenant_reverse
from . import models
from . import forms


# --- VISTAS DE LISTADO Y DETALLE ---

class TrabajoLaboratorioListView(TenantLoginRequiredMixin, ListView):
    """Vista de listado de trabajos de laboratorio con filtros"""
    model = models.TrabajoLaboratorio
    template_name = 'core/trabajo_laboratorio_list.html'
    context_object_name = 'trabajos'
    paginate_by = 20

    def get_queryset(self):
        queryset = models.TrabajoLaboratorio.objects.select_related(
            'tipo_trabajo',
            'laboratorio',
            'paciente',
            'cita_origen',
            'dentista_solicitante'
        ).order_by('-fecha_solicitud')

        # Si es dentista, solo mostrar sus trabajos
        if not self.request.user.is_superuser:
            if self.request.user.groups.filter(name='Dentista').exists():
                try:
                    perfil_dentista = self.request.user.perfil_dentista
                    queryset = queryset.filter(dentista_solicitante=perfil_dentista)
                except:
                    queryset = queryset.none()

        # Aplicar filtros del formulario
        form = forms.TrabajoLaboratorioFiltroForm(self.request.GET)
        if form.is_valid():
            # Búsqueda general
            busqueda = form.cleaned_data.get('busqueda')
            if busqueda:
                queryset = queryset.filter(
                    Q(paciente__nombre__icontains=busqueda) |
                    Q(paciente__apellido__icontains=busqueda) |
                    Q(dientes__icontains=busqueda) |
                    Q(material__icontains=busqueda) |
                    Q(observaciones__icontains=busqueda)
                )

            # Filtro por estado
            estado = form.cleaned_data.get('estado')
            if estado:
                queryset = queryset.filter(estado=estado)

            # Filtro por laboratorio
            laboratorio = form.cleaned_data.get('laboratorio')
            if laboratorio:
                queryset = queryset.filter(laboratorio=laboratorio)

            # Filtro por tipo de trabajo
            tipo_trabajo = form.cleaned_data.get('tipo_trabajo')
            if tipo_trabajo:
                queryset = queryset.filter(tipo_trabajo=tipo_trabajo)

            # Filtro por rango de fechas
            fecha_desde = form.cleaned_data.get('fecha_desde')
            fecha_hasta = form.cleaned_data.get('fecha_hasta')
            if fecha_desde:
                queryset = queryset.filter(fecha_solicitud__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fecha_solicitud__lte=fecha_hasta)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = forms.TrabajoLaboratorioFiltroForm(self.request.GET)

        # Estadísticas generales
        trabajos_qs = self.get_queryset()
        context['total_trabajos'] = trabajos_qs.count()
        context['trabajos_pendientes'] = trabajos_qs.filter(
            estado__in=['SOLICITADO', 'EN_PROCESO']
        ).count()
        context['trabajos_retrasados'] = sum(
            1 for t in trabajos_qs if t.esta_retrasado
        )

        # Estadísticas financieras
        stats = trabajos_qs.aggregate(
            total_costos=Sum('costo_laboratorio'),
            total_ingresos=Sum('precio_paciente')
        )
        context['total_costos'] = stats['total_costos'] or Decimal('0.00')
        context['total_ingresos'] = stats['total_ingresos'] or Decimal('0.00')
        context['total_margen'] = context['total_ingresos'] - context['total_costos']

        return context


class TrabajoLaboratorioDetailView(TenantLoginRequiredMixin, DetailView):
    """Vista de detalle de trabajo de laboratorio"""
    model = models.TrabajoLaboratorio
    template_name = 'core/trabajo_laboratorio_detail.html'
    context_object_name = 'trabajo'

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'tipo_trabajo',
            'laboratorio',
            'paciente',
            'cita_origen',
            'dentista_solicitante'
        )

        # Si es dentista, solo puede ver sus trabajos
        if not self.request.user.is_superuser:
            if self.request.user.groups.filter(name='Dentista').exists():
                try:
                    perfil_dentista = self.request.user.perfil_dentista
                    queryset = queryset.filter(dentista_solicitante=perfil_dentista)
                except:
                    queryset = queryset.none()

        return queryset


# --- VISTAS DE CREACIÓN Y EDICIÓN ---

class TrabajoLaboratorioCreateView(TenantSuccessUrlMixin, TenantLoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para crear solicitud de trabajo de laboratorio"""
    model = models.TrabajoLaboratorio
    form_class = forms.TrabajoLaboratorioForm
    template_name = 'core/trabajo_laboratorio_form.html'
    success_message = 'Trabajo de laboratorio solicitado exitosamente'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # Obtener paciente y cita del contexto
        paciente_id = self.kwargs.get('paciente_id')
        cita_id = self.kwargs.get('cita_id')

        if paciente_id:
            kwargs['paciente'] = get_object_or_404(models.Paciente, pk=paciente_id)

        if cita_id:
            kwargs['cita'] = get_object_or_404(models.Cita, pk=cita_id)
            # Si viene de cita, auto-asignar paciente
            if not paciente_id:
                kwargs['paciente'] = kwargs['cita'].paciente

        # Obtener dentista actual
        try:
            kwargs['dentista'] = self.request.user.perfil_dentista
        except:
            kwargs['dentista'] = None

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar info del paciente y cita al contexto
        if 'paciente_id' in self.kwargs:
            context['paciente'] = get_object_or_404(
                models.Paciente,
                pk=self.kwargs['paciente_id']
            )

        if 'cita_id' in self.kwargs:
            context['cita'] = get_object_or_404(
                models.Cita,
                pk=self.kwargs['cita_id']
            )

        return context

    def get_success_url(self):
        # Si viene de cita, regresar a gestión de cita
        if 'cita_id' in self.kwargs:
            return reverse('core:cita_manage', kwargs={'pk': self.kwargs['cita_id']})

        # Si no, ir a detalle del trabajo
        return reverse('core:trabajo_laboratorio_detail', kwargs={'pk': self.object.pk})


class TrabajoLaboratorioUpdateView(TenantSuccessUrlMixin, TenantLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista para actualizar estado de trabajo de laboratorio"""
    model = models.TrabajoLaboratorio
    form_class = forms.TrabajoLaboratorioUpdateForm
    template_name = 'core/trabajo_laboratorio_update.html'
    success_message = 'Trabajo de laboratorio actualizado exitosamente'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()

        # Si es dentista, solo puede editar sus trabajos
        if not self.request.user.is_superuser:
            if self.request.user.groups.filter(name='Dentista').exists():
                try:
                    perfil_dentista = self.request.user.perfil_dentista
                    queryset = queryset.filter(dentista_solicitante=perfil_dentista)
                except:
                    queryset = queryset.none()

        return queryset

    def get_success_url(self):
        return reverse('core:trabajo_laboratorio_detail', kwargs={'pk': self.object.pk})


class TrabajoLaboratorioDeleteView(TenantSuccessUrlMixin, TenantLoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Vista para eliminar trabajo de laboratorio"""
    model = models.TrabajoLaboratorio
    template_name = 'core/trabajo_laboratorio_confirm_delete.html'
    success_message = 'Trabajo de laboratorio eliminado exitosamente'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Solo administradores y dentistas dueños pueden eliminar
        if not self.request.user.is_superuser:
            if self.request.user.groups.filter(name='Dentista').exists():
                try:
                    perfil_dentista = self.request.user.perfil_dentista
                    queryset = queryset.filter(dentista_solicitante=perfil_dentista)
                except:
                    queryset = queryset.none()
            else:
                # Recepcionistas no pueden eliminar
                queryset = queryset.none()

        return queryset

    def get_success_url(self):
        return reverse('core:trabajo_laboratorio_list')

    def delete(self, request, *args, **kwargs):
        # Solo permitir eliminar si está en estado SOLICITADO
        self.object = self.get_object()
        if self.object.estado != 'SOLICITADO':
            messages.error(
                request,
                'Solo se pueden eliminar trabajos en estado SOLICITADO'
            )
            return redirect(tenant_reverse('core:trabajo_laboratorio_detail', request=request, kwargs={'pk': self.object.pk}))

        return super().delete(request, *args, **kwargs)


# --- API VIEWS (AJAX) ---

def trabajo_laboratorio_cambiar_estado_api(request, pk):
    """API para cambiar estado de trabajo (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

    trabajo = get_object_or_404(models.TrabajoLaboratorio, pk=pk)
    nuevo_estado = request.POST.get('estado')

    # Validar permisos
    if not request.user.is_superuser:
        es_dentista = request.user.groups.filter(name='Dentista').exists()
        es_recepcion = request.user.groups.filter(name='Recepcionista').exists()

        if es_dentista:
            # Verificar que sea su trabajo
            try:
                if trabajo.dentista_solicitante != request.user.perfil_dentista:
                    return JsonResponse({
                        'success': False,
                        'message': 'No tiene permisos para modificar este trabajo'
                    }, status=403)
            except:
                return JsonResponse({
                    'success': False,
                    'message': 'Usuario no tiene perfil de dentista'
                }, status=403)

        elif not es_recepcion:
            return JsonResponse({
                'success': False,
                'message': 'No tiene permisos suficientes'
            }, status=403)

    # Validar estado
    estados_validos = [e[0] for e in models.TrabajoLaboratorio.ESTADOS]
    if nuevo_estado not in estados_validos:
        return JsonResponse({
            'success': False,
            'message': 'Estado no válido'
        }, status=400)

    # Cambiar estado
    trabajo.estado = nuevo_estado

    # Si se marca como ENTREGADO, registrar fecha
    if nuevo_estado == 'ENTREGADO' and not trabajo.fecha_entrega_real:
        trabajo.fecha_entrega_real = date.today()

    trabajo.save()

    return JsonResponse({
        'success': True,
        'message': 'Estado actualizado exitosamente',
        'nuevo_estado': trabajo.get_estado_display(),
        'fecha_entrega_real': trabajo.fecha_entrega_real.strftime('%d/%m/%Y') if trabajo.fecha_entrega_real else None
    })


def trabajo_laboratorio_obtener_costo_api(request):
    """API para obtener costo de referencia de tipo de trabajo (AJAX)"""
    tipo_trabajo_id = request.GET.get('tipo_trabajo_id')

    if not tipo_trabajo_id:
        return JsonResponse({'success': False, 'message': 'Falta ID de tipo de trabajo'}, status=400)

    try:
        tipo_trabajo = models.TipoTrabajoLaboratorio.objects.get(pk=tipo_trabajo_id)
        return JsonResponse({
            'success': True,
            'costo_referencia': float(tipo_trabajo.costo_referencia),
            'nombre': tipo_trabajo.nombre
        })
    except models.TipoTrabajoLaboratorio.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Tipo de trabajo no encontrado'}, status=404)


def obtener_citas_paciente_api(request):
    """API para obtener las citas de un paciente (AJAX)"""
    paciente_id = request.GET.get('paciente_id')

    if not paciente_id:
        return JsonResponse({'success': False, 'message': 'Falta ID de paciente'}, status=400)

    try:
        paciente = models.Paciente.objects.get(pk=paciente_id)

        # Obtener citas del paciente ordenadas por fecha (más recientes primero)
        citas = models.Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')[:20]

        citas_data = []
        for cita in citas:
            # Construir descripción de la cita
            servicios = ', '.join([s.nombre for s in cita.servicios_planeados.all()[:2]])
            if cita.servicios_planeados.count() > 2:
                servicios += '...'

            citas_data.append({
                'id': cita.id,
                'fecha_hora': cita.fecha_hora.strftime('%d/%m/%Y %H:%M'),
                'estado': cita.get_estado_display(),
                'servicios': servicios or 'Sin servicios',
                'dentista': f'Dr. {cita.dentista.nombre} {cita.dentista.apellido}' if cita.dentista else 'Sin asignar'
            })

        return JsonResponse({
            'success': True,
            'citas': citas_data,
            'paciente_nombre': f'{paciente.nombre} {paciente.apellido}'
        })

    except models.Paciente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Paciente no encontrado'}, status=404)
