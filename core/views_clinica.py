#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vistas para Gestión Clínica Avanzada
===================================

Vistas para manejar el nuevo flujo clínico:
- Historial clínico con tipos de registro
- Seguimiento de cambios en odontograma
- Tratamientos realizados en citas
- APIs para integración con frontend

"""

import json
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView

from .models import (
    Paciente, Cita, HistorialClinico, EstadoDiente, HistorialEstadoDiente,
    TratamientoCita, Diagnostico, Servicio, PerfilDentista
)
from .models import (
    actualizar_estado_diente, procesar_tratamiento_cita,
    crear_entrada_historial_clinico, obtener_historial_diente,
    obtener_odontograma_completo, validar_numero_diente_fdi
)

# --- VISTAS DE HISTORIAL CLÍNICO ---

@login_required
def historial_clinico_paciente(request, paciente_id):
    """
    Vista principal del historial clínico de un paciente
    Muestra todo el historial organizado por tipo de registro
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener historial clínico con filtros
    historial_qs = HistorialClinico.objects.filter(
        paciente=paciente
    ).select_related(
        'registrado_por', 'cita'
    ).order_by('-fecha_evento')
    
    # Filtros opcionales
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        historial_qs = historial_qs.filter(tipo_registro=tipo_filtro)
    
    # Paginación
    paginator = Paginator(historial_qs, 10)
    page_number = request.GET.get('page')
    historial = paginator.get_page(page_number)
    
    # Estadísticas del historial
    stats = {
        'total_entradas': historial_qs.count(),
        'por_tipo': HistorialClinico.objects.filter(
            paciente=paciente
        ).values('tipo_registro').annotate(
            count=Count('id')
        ).order_by('-count'),
        'ultima_consulta': HistorialClinico.objects.filter(
            paciente=paciente,
            tipo_registro='CONSULTA'
        ).order_by('-fecha_evento').first(),
        'ultimo_tratamiento': HistorialClinico.objects.filter(
            paciente=paciente,
            tipo_registro='TRATAMIENTO'
        ).order_by('-fecha_evento').first(),
    }
    
    # Opciones para formularios
    tipos_registro = HistorialClinico.TIPOS_REGISTRO
    
    context = {
        'paciente': paciente,
        'historial': historial,
        'stats': stats,
        'tipos_registro': tipos_registro,
        'tipo_filtro': tipo_filtro,
    }
    
    return render(request, 'core/clinica/historial_clinico.html', context)

@login_required
@require_http_methods(["POST"])
def agregar_entrada_historial(request, paciente_id):
    """
    Agregar nueva entrada al historial clínico
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    tipo_registro = request.POST.get('tipo_registro', 'CONSULTA')
    descripcion = request.POST.get('descripcion', '').strip()
    cita_id = request.POST.get('cita_id', '')
    
    if not descripcion:
        messages.error(request, "La descripción es obligatoria")
        return redirect('core:historial_clinico_paciente', paciente_id=paciente_id)
    
    try:
        # Obtener dentista del usuario actual
        dentista = PerfilDentista.objects.get(usuario=request.user)
        
        # Obtener cita si se especifica
        cita = None
        if cita_id:
            try:
                cita = Cita.objects.get(id=cita_id, paciente=paciente)
            except Cita.DoesNotExist:
                pass
        
        # Crear entrada
        entrada = crear_entrada_historial_clinico(
            paciente=paciente,
            tipo_registro=tipo_registro,
            descripcion=descripcion,
            dentista=dentista,
            cita=cita
        )
        
        messages.success(request, f"Entrada de {entrada.get_tipo_registro_display().lower()} agregada correctamente")
        
    except PerfilDentista.DoesNotExist:
        messages.error(request, "No tienes permisos para registrar entradas clínicas")
    except Exception as e:
        messages.error(request, f"Error al crear entrada: {str(e)}")
    
    return redirect('core:historial_clinico_paciente', paciente_id=paciente_id)

# --- VISTAS DE SEGUIMIENTO DENTAL ---

@login_required
def historial_dental_paciente(request, paciente_id):
    """
    Vista del historial dental completo (odontograma + cambios)
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener odontograma actual
    odontograma_actual = obtener_odontograma_completo(paciente)
    
    # Obtener historial de cambios
    historial_dental = HistorialEstadoDiente.objects.filter(
        paciente=paciente
    ).select_related(
        'diagnostico_anterior', 'diagnostico_nuevo', 'dentista', 'cita'
    ).order_by('-fecha_cambio')
    
    # Filtro por diente específico
    diente_filtro = request.GET.get('diente', '')
    if diente_filtro:
        try:
            numero_diente = int(diente_filtro)
            if validar_numero_diente_fdi(numero_diente):
                historial_dental = historial_dental.filter(numero_diente=numero_diente)
            else:
                messages.warning(request, f"Número de diente inválido: {diente_filtro}")
        except ValueError:
            messages.warning(request, f"Número de diente inválido: {diente_filtro}")
    
    # Paginación
    paginator = Paginator(historial_dental, 15)
    page_number = request.GET.get('page')
    historial_page = paginator.get_page(page_number)
    
    # Estadísticas dentales
    stats_dentales = {
        'total_cambios': historial_dental.count(),
        'dientes_tratados': HistorialEstadoDiente.objects.filter(
            paciente=paciente
        ).values('numero_diente').distinct().count(),
        'ultimo_tratamiento': historial_dental.first(),
        'tratamientos_por_cuadrante': {
            'cuadrante_1': historial_dental.filter(numero_diente__in=range(11, 19)).count(),
            'cuadrante_2': historial_dental.filter(numero_diente__in=range(21, 29)).count(), 
            'cuadrante_3': historial_dental.filter(numero_diente__in=range(31, 39)).count(),
            'cuadrante_4': historial_dental.filter(numero_diente__in=range(41, 49)).count(),
        }
    }
    
    # Diagnósticos disponibles para quick actions
    diagnosticos = Diagnostico.objects.all().order_by('nombre')
    
    context = {
        'paciente': paciente,
        'odontograma_actual': odontograma_actual,
        'historial_dental': historial_page,
        'stats_dentales': stats_dentales,
        'diente_filtro': diente_filtro,
        'diagnosticos': diagnosticos,
    }
    
    return render(request, 'core/clinica/historial_dental.html', context)

@login_required
def detalle_diente(request, paciente_id, numero_diente):
    """
    Vista detallada del historial de un diente específico
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if not validar_numero_diente_fdi(numero_diente):
        messages.error(request, f"Número de diente inválido: {numero_diente}")
        return redirect('core:historial_dental_paciente', paciente_id=paciente_id)
    
    # Obtener historial completo del diente
    historial_diente = obtener_historial_diente(paciente, numero_diente)
    
    # Estado actual del diente
    try:
        estado_actual = EstadoDiente.objects.get(
            paciente=paciente,
            numero_diente=numero_diente
        )
    except EstadoDiente.DoesNotExist:
        estado_actual = None
    
    # Diagnósticos disponibles
    diagnosticos = Diagnostico.objects.all().order_by('nombre')
    
    context = {
        'paciente': paciente,
        'numero_diente': numero_diente,
        'historial_diente': historial_diente,
        'estado_actual': estado_actual,
        'diagnosticos': diagnosticos,
    }
    
    return render(request, 'core/clinica/detalle_diente.html', context)

# --- VISTAS DE TRATAMIENTOS EN CITAS ---

@login_required
def tratamientos_cita(request, cita_id):
    """
    Vista para gestionar tratamientos de una cita específica
    """
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Verificar permisos (el dentista de la cita o admin)
    try:
        perfil_dentista = PerfilDentista.objects.get(usuario=request.user)
        if cita.dentista != perfil_dentista and not request.user.is_superuser:
            messages.error(request, "No tienes permisos para modificar esta cita")
            return redirect('core:cita_detail', pk=cita_id)
    except PerfilDentista.DoesNotExist:
        messages.error(request, "No tienes permisos para acceder a esta función")
        return redirect('core:cita_detail', pk=cita_id)
    
    # Obtener tratamientos existentes
    tratamientos_existentes = TratamientoCita.objects.filter(
        cita=cita
    ).select_related('registrado_por').prefetch_related('servicios')
    
    # Obtener odontograma actual del paciente
    odontograma_actual = obtener_odontograma_completo(cita.paciente)
    
    # Servicios y diagnósticos disponibles
    servicios = Servicio.objects.filter(activo=True).order_by('nombre')
    diagnosticos = Diagnostico.objects.all().order_by('nombre')
    
    context = {
        'cita': cita,
        'tratamientos_existentes': tratamientos_existentes,
        'odontograma_actual': odontograma_actual,
        'servicios': servicios,
        'diagnosticos': diagnosticos,
    }
    
    return render(request, 'core/clinica/tratamientos_cita.html', context)

@login_required
@require_http_methods(["POST"])
def registrar_tratamiento_cita(request, cita_id):
    """
    Registrar un nuevo tratamiento realizado en una cita
    """
    cita = get_object_or_404(Cita, id=cita_id)
    
    try:
        # Verificar permisos
        perfil_dentista = PerfilDentista.objects.get(usuario=request.user)
        if cita.dentista != perfil_dentista and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
        
        # Obtener datos del formulario
        dientes_tratados = request.POST.get('dientes_tratados', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        estado_inicial = request.POST.get('estado_inicial', '').strip()
        estado_final = request.POST.get('estado_final', '').strip()
        diagnostico_final_id = request.POST.get('diagnostico_final_id')
        servicios_ids = request.POST.getlist('servicios_ids')
        trabajo_pendiente = request.POST.get('trabajo_pendiente', '').strip()
        requiere_seguimiento = request.POST.get('requiere_seguimiento') == 'on'
        fecha_seguimiento = request.POST.get('fecha_seguimiento', '').strip()
        
        # Validaciones
        if not all([dientes_tratados, descripcion, estado_inicial, estado_final, diagnostico_final_id]):
            return JsonResponse({'success': False, 'error': 'Faltan campos obligatorios'}, status=400)
        
        # Validar dientes
        try:
            dientes_list = [int(d.strip()) for d in dientes_tratados.split(',') if d.strip()]
            for diente in dientes_list:
                if not validar_numero_diente_fdi(diente):
                    return JsonResponse({'success': False, 'error': f'Diente inválido: {diente}'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Formato de dientes inválido'}, status=400)
        
        # Obtener diagnóstico final
        try:
            diagnostico_final = Diagnostico.objects.get(id=diagnostico_final_id)
        except Diagnostico.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Diagnóstico no encontrado'}, status=400)
        
        # Procesar fecha de seguimiento
        fecha_seguimiento_obj = None
        if fecha_seguimiento:
            try:
                fecha_seguimiento_obj = datetime.strptime(fecha_seguimiento, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Fecha de seguimiento inválida'}, status=400)
        
        # Procesar tratamiento usando la función helper
        with transaction.atomic():
            tratamiento, estados_actualizados, cambios_realizados = procesar_tratamiento_cita(
                cita=cita,
                dientes_tratados_str=dientes_tratados,
                descripcion_tratamiento=descripcion,
                estado_inicial_desc=estado_inicial,
                estado_final_desc=estado_final,
                diagnostico_final=diagnostico_final,
                servicios_ids=servicios_ids if servicios_ids else None,
                trabajo_pendiente=trabajo_pendiente,
                requiere_seguimiento=requiere_seguimiento,
                fecha_seguimiento=fecha_seguimiento_obj
            )
        
        # Respuesta exitosa
        response_data = {
            'success': True,
            'message': f'Tratamiento registrado correctamente. {cambios_realizados} dientes actualizados.',
            'tratamiento_id': tratamiento.id,
            'dientes_tratados': len(dientes_list),
            'cambios_realizados': cambios_realizados
        }
        
        # Si es AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response_data)
        
        # Si no es AJAX, redirigir con mensaje
        messages.success(request, response_data['message'])
        return redirect('core:tratamientos_cita', cita_id=cita_id)
        
    except PerfilDentista.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# --- APIs PARA FRONTEND ---

@login_required
def api_odontograma_paciente(request, paciente_id):
    """
    API para obtener el odontograma completo de un paciente
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    odontograma = obtener_odontograma_completo(paciente)
    
    # Convertir datetime a string para JSON
    for diente_data in odontograma.values():
        if 'actualizado_en' in diente_data:
            diente_data['actualizado_en'] = diente_data['actualizado_en'].isoformat()
    
    return JsonResponse({
        'success': True,
        'paciente_id': paciente_id,
        'paciente_nombre': str(paciente),
        'odontograma': odontograma
    })

@login_required
def api_historial_diente(request, paciente_id, numero_diente):
    """
    API para obtener el historial completo de un diente
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if not validar_numero_diente_fdi(numero_diente):
        return JsonResponse({'success': False, 'error': 'Número de diente inválido'}, status=400)
    
    historial = obtener_historial_diente(paciente, numero_diente)
    
    historial_data = []
    for entrada in historial:
        historial_data.append({
            'id': entrada.id,
            'fecha_cambio': entrada.fecha_cambio.isoformat(),
            'diagnostico_anterior': entrada.diagnostico_anterior.nombre if entrada.diagnostico_anterior else None,
            'diagnostico_nuevo': entrada.diagnostico_nuevo.nombre,
            'tratamiento_realizado': entrada.tratamiento_realizado,
            'observaciones': entrada.observaciones,
            'dentista': str(entrada.dentista),
            'cita_id': entrada.cita.id if entrada.cita else None
        })
    
    return JsonResponse({
        'success': True,
        'paciente_id': paciente_id,
        'numero_diente': numero_diente,
        'historial': historial_data
    })

@login_required
def api_diagnosticos_disponibles(request):
    """
    API para obtener lista de diagnósticos disponibles
    """
    diagnosticos = Diagnostico.objects.all().order_by('nombre')
    
    diagnosticos_data = []
    for diagnostico in diagnosticos:
        diagnosticos_data.append({
            'id': diagnostico.id,
            'nombre': diagnostico.nombre,
            'color_hex': diagnostico.color_hex,
            'icono_svg': diagnostico.icono_svg
        })
    
    return JsonResponse({
        'success': True,
        'diagnosticos': diagnosticos_data
    })

# --- REPORTES CLÍNICOS ---

@login_required
def reporte_tratamientos_paciente(request, paciente_id):
    """
    Reporte completo de tratamientos de un paciente
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener rango de fechas
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Tratamientos realizados
    tratamientos_qs = TratamientoCita.objects.filter(
        cita__paciente=paciente
    ).select_related('cita', 'registrado_por').prefetch_related('servicios')
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            tratamientos_qs = tratamientos_qs.filter(fecha_registro__date__gte=fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            tratamientos_qs = tratamientos_qs.filter(fecha_registro__date__lte=fecha_hasta_obj)
        except ValueError:
            pass
    
    tratamientos = tratamientos_qs.order_by('-fecha_registro')
    
    # Estadísticas del período
    stats_periodo = {
        'total_tratamientos': tratamientos.count(),
        'total_citas': tratamientos.values('cita').distinct().count(),
        'dientes_tratados_total': sum(len(t.get_dientes_list()) for t in tratamientos),
        'tratamientos_con_seguimiento': tratamientos.filter(requiere_seguimiento=True).count(),
    }
    
    context = {
        'paciente': paciente,
        'tratamientos': tratamientos,
        'stats_periodo': stats_periodo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'core/clinica/reporte_tratamientos.html', context)