#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROPUESTA DE MEJORAS AL SISTEMA CLÍNICO
=====================================

Basado en el flujo que describes:
1. Paciente llega con caries en diente 16
2. Se detecta (diagnóstico)
3. Se trata en cita
4. Cambia estado a sano/reparado
5. Todo con fechas y responsables

MODELOS PROPUESTOS PARA AGREGAR:
"""

from django.db import models
from django.utils import timezone

# MODELO NUEVO 1: Historial de Estados del Odontograma
class HistorialEstadoDiente(models.Model):
    """
    Registra TODOS los cambios de estado de cada diente
    Permite trazabilidad completa del tratamiento
    """
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    numero_diente = models.IntegerField()
    
    # ESTADO ANTERIOR
    diagnostico_anterior = models.ForeignKey(
        'Diagnostico', 
        on_delete=models.PROTECT,
        related_name='cambios_desde',
        null=True, blank=True,
        help_text="Estado previo del diente (null si es primer registro)"
    )
    
    # ESTADO NUEVO
    diagnostico_nuevo = models.ForeignKey(
        'Diagnostico',
        on_delete=models.PROTECT, 
        related_name='cambios_hacia',
        help_text="Nuevo estado del diente después del tratamiento"
    )
    
    # TRAZABILIDAD
    cita = models.ForeignKey(
        'Cita',
        on_delete=models.PROTECT,
        help_text="Cita donde se realizó el cambio"
    )
    dentista = models.ForeignKey(
        'PerfilDentista',
        on_delete=models.PROTECT,
        help_text="Dentista responsable del tratamiento" 
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    
    # DETALLES DEL TRATAMIENTO
    tratamiento_realizado = models.TextField(
        help_text="Descripción del tratamiento que generó el cambio"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Notas adicionales del dentista"
    )
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Historial de Estado de Diente'
        verbose_name_plural = 'Historial de Estados de Dientes'
    
    def __str__(self):
        anterior = self.diagnostico_anterior.nombre if self.diagnostico_anterior else "Inicial"
        return f"Diente {self.numero_diente}: {anterior} → {self.diagnostico_nuevo.nombre}"

# MODELO NUEVO 2: Tratamientos Realizados en Cita  
class TratamientoCita(models.Model):
    """
    Registra tratamientos específicos realizados en cada cita
    Vincula cita → tratamiento → dientes afectados
    """
    cita = models.ForeignKey('Cita', on_delete=models.CASCADE, related_name='tratamientos')
    
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
    
    # ESTADOS
    estado_inicial_descripcion = models.TextField(
        help_text="Descripción del estado de los dientes antes del tratamiento"
    )
    estado_final_descripcion = models.TextField(
        help_text="Descripción del estado de los dientes después del tratamiento" 
    )
    
    # PENDIENTES
    trabajo_pendiente = models.TextField(
        blank=True,
        help_text="Trabajo que queda pendiente para próximas citas"
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Tratamiento en cita {self.cita.id} - Dientes: {self.dientes_tratados}"

# MEJORAS AL MODELO EXISTENTE HistorialClinico
"""
El modelo actual YA TIENE lo que necesitas:
- paciente ✓
- fecha_evento ✓ (automática)
- descripcion_evento ✓ (puede ser llenado por recepcionista/dentista)
- registrado_por ✓ (dentista responsable)

SOLO necesita un campo adicional:
"""

# Campo a AGREGAR al HistorialClinico existente:
# tipo_registro = models.CharField(
#     max_length=20,
#     choices=[
#         ('CONSULTA', 'Consulta General'),
#         ('DIAGNOSTICO', 'Diagnóstico'),
#         ('TRATAMIENTO', 'Tratamiento Realizado'),
#         ('SEGUIMIENTO', 'Seguimiento'),
#         ('EMERGENCIA', 'Emergencia'),
#     ],
#     default='CONSULTA'
# )

# FUNCIÓN HELPER para actualizar odontograma automáticamente
def actualizar_estado_diente(paciente, numero_diente, diagnostico_nuevo, cita, tratamiento_descripcion):
    """
    Función helper para actualizar estado de diente manteniendo historial
    """
    from .models import EstadoDiente, HistorialEstadoDiente, Diagnostico
    
    # Obtener estado actual (si existe)
    estado_actual, created = EstadoDiente.objects.get_or_create(
        paciente=paciente,
        numero_diente=numero_diente,
        defaults={'diagnostico': diagnostico_nuevo}
    )
    
    diagnostico_anterior = None if created else estado_actual.diagnostico
    
    # Solo crear historial si realmente cambió
    if not created and diagnostico_anterior != diagnostico_nuevo:
        # Crear registro en historial
        HistorialEstadoDiente.objects.create(
            paciente=paciente,
            numero_diente=numero_diente,
            diagnostico_anterior=diagnostico_anterior,
            diagnostico_nuevo=diagnostico_nuevo,
            cita=cita,
            dentista=cita.dentista,
            tratamiento_realizado=tratamiento_descripcion
        )
        
        # Actualizar estado actual
        estado_actual.diagnostico = diagnostico_nuevo
        estado_actual.save()

"""
FLUJO PROPUESTO COMPLETO:

1. PACIENTE LLEGA:
   - Recepcionista/Dentista crea entrada en HistorialClinico
   - tipo_registro='CONSULTA'
   - descripcion_evento='Paciente refiere dolor en diente 16'
   - registrado_por=dentista

2. DIAGNÓSTICO:
   - Dentista examina y encuentra caries
   - Se crea entrada en HistorialClinico:
     * tipo_registro='DIAGNOSTICO' 
     * descripcion_evento='Caries profunda en diente 16'
   - Se actualiza EstadoDiente (16) a 'Cariado'
   - Se crea HistorialEstadoDiente (Sano → Cariado)

3. TRATAMIENTO:
   - Durante la cita se realiza obturación
   - Se crea TratamientoCita:
     * dientes_tratados='16'
     * descripcion='Obturación con resina compuesta'
     * estado_inicial_descripcion='Caries profunda oclusal'
     * estado_final_descripcion='Obturación terminada, sellado completo'
   - Se actualiza EstadoDiente (16) a 'Obturado'
   - Se crea HistorialEstadoDiente (Cariado → Obturado)
   - Se crea entrada en HistorialClinico:
     * tipo_registro='TRATAMIENTO'
     * descripcion_evento='Obturación completada en diente 16'

4. RESULTADO:
   - Trazabilidad completa: Sano → Cariado → Obturado
   - Fechas y responsables en cada paso
   - Odontograma visual actualizado
   - Historial médico-legal completo
"""

# EJEMPLO DE USO EN VISTA:
"""
# En views.py - al finalizar tratamiento en cita:

def finalizar_tratamiento_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Datos del formulario
    dientes = request.POST.get('dientes_tratados')  # '16,17'
    tratamiento_desc = request.POST.get('tratamiento_descripcion')
    diagnostico_final_id = request.POST.get('diagnostico_final')
    
    # Crear registro de tratamiento
    tratamiento = TratamientoCita.objects.create(
        cita=cita,
        dientes_tratados=dientes,
        descripcion=tratamiento_desc,
        estado_inicial_descripcion=request.POST.get('estado_inicial'),
        estado_final_descripcion=request.POST.get('estado_final')
    )
    
    # Actualizar estado de cada diente tratado
    diagnostico_final = Diagnostico.objects.get(id=diagnostico_final_id)
    for numero_diente in dientes.split(','):
        actualizar_estado_diente(
            paciente=cita.paciente,
            numero_diente=int(numero_diente.strip()),
            diagnostico_nuevo=diagnostico_final,
            cita=cita,
            tratamiento_descripcion=tratamiento_desc
        )
    
    # Crear entrada en historial clínico
    HistorialClinico.objects.create(
        paciente=cita.paciente,
        descripcion_evento=f"Tratamiento completado: {tratamiento_desc} en dientes {dientes}",
        registrado_por=cita.dentista,
        tipo_registro='TRATAMIENTO'
    )
    
    return redirect('cita_completada')
"""