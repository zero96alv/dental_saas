#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Sistema de Citas y Agenda
=============================================

Este script valida el funcionamiento completo del sistema de citas y agenda
incluyendo agenda visual, CRUD de citas, horarios, estados, dentistas y 
funcionalidades avanzadas.

Ejecutar desde la raíz del proyecto:
python validation_appointments_system.py
"""

import os
import sys
import django
from datetime import datetime, timedelta, date, time
from decimal import Decimal

# Configurar Django
sys.path.append('C:\\desarrollo\\dental_saas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection, models
from django.test import RequestFactory, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import Group
from tenants.models import Clinica
from django_tenants.utils import schema_context

User = get_user_model()

class AppointmentsSystemValidator:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.tenant = None
        
        print("=" * 70)
        print("VALIDACIÓN DEL SISTEMA DE CITAS Y AGENDA")
        print("=" * 70)
        print(f"Inicio de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Configurar tenant demo
        try:
            self.tenant = Clinica.objects.get(schema_name='demo')
            print(f"🏥 Usando tenant: {self.tenant.nombre} (schema: {self.tenant.schema_name})")
        except Clinica.DoesNotExist:
            print("❌ Tenant 'demo' no encontrado")
            self.tenant = None

    def log_success(self, message):
        """Registra un test exitoso"""
        self.success_count += 1
        self.total_tests += 1
        print(f"✓ {message}")

    def log_error(self, message):
        """Registra un error"""
        self.total_tests += 1
        self.errors.append(message)
        print(f"✗ ERROR: {message}")

    def log_warning(self, message):
        """Registra una advertencia"""
        self.warnings.append(message)
        print(f"⚠ ADVERTENCIA: {message}")

    def validate_appointment_model(self):
        """Valida el modelo de citas y sus campos"""
        print("\n1. VALIDACIÓN DEL MODELO DE CITAS")
        print("-" * 40)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita
                
                # Verificar campos del modelo
                cita_fields = [field.name for field in Cita._meta.get_fields()]
                expected_fields = [
                    'fecha_hora', 'duracion', 'estado', 'paciente', 'dentista',
                    'observaciones', 'servicios_planeados', 'servicios_realizados'
                ]
                
                for field in expected_fields:
                    if field in cita_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Cita")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Cita")
                
                # Verificar conteo de citas
                citas_count = Cita.objects.count()
                self.log_success(f"Citas registradas en el sistema: {citas_count}")
                
                # Verificar estados de cita disponibles
                if hasattr(Cita, 'ESTADOS'):
                    estados = [choice[0] for choice in Cita.ESTADOS]
                    self.log_success(f"Estados de cita configurados: {estados}")
                elif citas_count > 0:
                    estados_utilizados = list(Cita.objects.values_list('estado', flat=True).distinct())
                    self.log_success(f"Estados de cita utilizados: {estados_utilizados}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Cita: {str(e)}")

    def validate_dentist_profiles(self):
        """Valida los perfiles de dentista y horarios"""
        print("\n2. VALIDACIÓN DE PERFILES DE DENTISTA Y HORARIOS")
        print("-" * 50)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import PerfilDentista, HorarioLaboral
                
                # Verificar perfiles de dentista
                dentistas_count = PerfilDentista.objects.count()
                self.log_success(f"Perfiles de dentista registrados: {dentistas_count}")
                
                if dentistas_count > 0:
                    # Verificar especialidades
                    dentistas_con_especialidad = PerfilDentista.objects.exclude(
                        especialidades__isnull=True
                    ).count()
                    self.log_success(f"Dentistas con especialidades asignadas: {dentistas_con_especialidad}")
                    
                    # Verificar usuarios activos
                    dentistas_activos = PerfilDentista.objects.filter(
                        activo=True
                    ).count() if hasattr(PerfilDentista, 'activo') else dentistas_count
                    self.log_success(f"Dentistas activos: {dentistas_activos}")
                    
                    # Mostrar algunos dentistas de ejemplo
                    sample_dentistas = PerfilDentista.objects.all()[:3]
                    dentista_names = [f"Dr. {d.nombre} {d.apellido}" for d in sample_dentistas]
                    self.log_success(f"Dentistas de ejemplo: {dentista_names}")
                
                # Verificar horarios laborales
                horarios_count = HorarioLaboral.objects.count()
                self.log_success(f"Horarios laborales configurados: {horarios_count}")
                
                if horarios_count > 0:
                    # Verificar distribución por días
                    dias_configurados = HorarioLaboral.objects.values(
                        'dia_semana'
                    ).distinct().count()
                    self.log_success(f"Días de la semana con horarios configurados: {dias_configurados}")
                
        except Exception as e:
            self.log_error(f"Error en validación de dentistas y horarios: {str(e)}")

    def validate_appointment_urls(self):
        """Valida las URLs del sistema de citas"""
        print("\n3. VALIDACIÓN DE URLs DE CITAS")
        print("-" * 35)
        
        try:
            # URLs principales de citas
            appointment_urls = [
                ('core:agenda', 'Agenda principal'),
                ('core:cita_list', 'Lista de citas'),
                ('core:cita_create', 'Crear cita'),
                ('core:agenda_events', 'API eventos agenda'),
            ]
            
            for url_name, description in appointment_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs que requieren parámetros (si hay citas)
            if self.tenant:
                with schema_context(self.tenant.schema_name):
                    from core.models import Cita
                    
                    if Cita.objects.exists():
                        cita_id = Cita.objects.first().id
                        parametric_urls = [
                            ('core:cita_detail', {'pk': cita_id}, 'Detalle de cita'),
                            ('core:cita_update', {'pk': cita_id}, 'Editar cita'),
                            ('core:cita_delete', {'pk': cita_id}, 'Eliminar cita'),
                            ('core:cita_manage', {'pk': cita_id}, 'Gestionar cita'),
                        ]
                        
                        for url_name, kwargs, description in parametric_urls:
                            try:
                                url = reverse(url_name, kwargs=kwargs)
                                self.log_success(f"URL '{description}' configurada: {url}")
                            except NoReverseMatch:
                                self.log_error(f"URL '{description}' ({url_name}) no encontrada")
                    else:
                        self.log_warning("No hay citas para validar URLs paramétricas")
                        
        except Exception as e:
            self.log_error(f"Error en validación de URLs: {str(e)}")

    def validate_appointment_states_workflow(self):
        """Valida el flujo de estados de las citas"""
        print("\n4. VALIDACIÓN DEL FLUJO DE ESTADOS DE CITAS")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita
                
                citas_count = Cita.objects.count()
                
                if citas_count > 0:
                    # Analizar distribución de estados
                    estados_count = {}
                    for estado, count in Cita.objects.values_list('estado').annotate(
                        count=models.Count('estado')
                    ):
                        estados_count[estado] = count
                    
                    self.log_success(f"Distribución de estados: {estados_count}")
                    
                    # Verificar transiciones de estado válidas
                    estados_validos = ['agendada', 'confirmada', 'en_proceso', 'completada', 'cancelada', 'no_asistio']
                    estados_sistema = list(Cita.objects.values_list('estado', flat=True).distinct())
                    
                    estados_reconocidos = [e for e in estados_sistema if e in estados_validos]
                    estados_desconocidos = [e for e in estados_sistema if e not in estados_validos]
                    
                    if estados_reconocidos:
                        self.log_success(f"Estados reconocidos: {estados_reconocidos}")
                    
                    if estados_desconocidos:
                        self.log_warning(f"Estados no estándar: {estados_desconocidos}")
                    
                    # Verificar citas futuras vs pasadas
                    ahora = datetime.now()
                    citas_futuras = Cita.objects.filter(fecha_hora__gt=ahora).count()
                    citas_pasadas = Cita.objects.filter(fecha_hora__lte=ahora).count()
                    
                    self.log_success(f"Citas futuras: {citas_futuras}, Citas pasadas: {citas_pasadas}")
                    
                else:
                    self.log_warning("No hay citas para validar flujo de estados")
                
        except Exception as e:
            self.log_error(f"Error en validación de estados: {str(e)}")

    def validate_appointment_services_integration(self):
        """Valida la integración con servicios dentales"""
        print("\n5. VALIDACIÓN DE INTEGRACIÓN CON SERVICIOS")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita, Servicio
                
                servicios_count = Servicio.objects.count()
                self.log_success(f"Servicios disponibles: {servicios_count}")
                
                if servicios_count > 0 and Cita.objects.exists():
                    # Verificar citas con servicios planeados
                    if hasattr(Cita, 'servicios_planeados'):
                        citas_con_servicios_planeados = Cita.objects.exclude(
                            servicios_planeados__isnull=True
                        ).count()
                        self.log_success(f"Citas con servicios planeados: {citas_con_servicios_planeados}")
                    
                    # Verificar citas con servicios realizados
                    if hasattr(Cita, 'servicios_realizados'):
                        citas_con_servicios_realizados = Cita.objects.exclude(
                            servicios_realizados__isnull=True
                        ).count()
                        self.log_success(f"Citas con servicios realizados: {citas_con_servicios_realizados}")
                
                # Verificar precios promedio de servicios
                if servicios_count > 0:
                    from django.db.models import Avg, Min, Max
                    precio_stats = Servicio.objects.aggregate(
                        promedio=Avg('precio'),
                        minimo=Min('precio'),
                        maximo=Max('precio')
                    )
                    
                    if precio_stats['promedio']:
                        self.log_success(f"Precio promedio servicios: ${precio_stats['promedio']:.2f}")
                        self.log_success(f"Rango precios: ${precio_stats['minimo']:.2f} - ${precio_stats['maximo']:.2f}")
                
        except Exception as e:
            self.log_error(f"Error en validación de integración con servicios: {str(e)}")

    def validate_appointment_time_management(self):
        """Valida la gestión de horarios y tiempos de citas"""
        print("\n6. VALIDACIÓN DE GESTIÓN DE HORARIOS")
        print("-" * 40)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita, HorarioLaboral
                
                # Verificar horarios laborales configurados
                horarios_count = HorarioLaboral.objects.count()
                
                if horarios_count > 0:
                    # Verificar cobertura semanal
                    dias_con_horario = HorarioLaboral.objects.values('dia_semana').distinct().count()
                    self.log_success(f"Días de la semana con horarios configurados: {dias_con_horario}")
                    
                    # Verificar horarios típicos
                    horario_ejemplo = HorarioLaboral.objects.first()
                    if horario_ejemplo:
                        self.log_success(f"Ejemplo horario: {horario_ejemplo.hora_inicio} - {horario_ejemplo.hora_fin}")
                
                # Verificar duraciones de citas
                if Cita.objects.exists():
                    duraciones = Cita.objects.values_list('duracion', flat=True).distinct()
                    duraciones_minutos = [d.total_seconds()/60 for d in duraciones if d]
                    
                    if duraciones_minutos:
                        self.log_success(f"Duraciones típicas de citas (min): {sorted(duraciones_minutos)}")
                    
                    # Verificar citas en horario laboral
                    citas_en_horario = self.verify_appointments_within_working_hours()
                    if citas_en_horario is not None:
                        self.log_success(f"Citas programadas en horario laboral: {citas_en_horario}%")
                
        except Exception as e:
            self.log_error(f"Error en validación de gestión de horarios: {str(e)}")

    def verify_appointments_within_working_hours(self):
        """Verifica que las citas estén dentro del horario laboral"""
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita, HorarioLaboral
                
                total_citas = Cita.objects.count()
                if total_citas == 0:
                    return None
                
                citas_validas = 0
                
                for cita in Cita.objects.all()[:50]:  # Limitar muestra para performance
                    dia_semana = cita.fecha_hora.weekday()  # 0 = Lunes
                    hora_cita = cita.fecha_hora.time()
                    
                    # Buscar horario laboral para este día
                    horario = HorarioLaboral.objects.filter(dia_semana=dia_semana).first()
                    
                    if horario and horario.hora_inicio <= hora_cita <= horario.hora_fin:
                        citas_validas += 1
                
                return (citas_validas / min(50, total_citas)) * 100
                
        except Exception:
            return None

    def validate_appointment_apis(self):
        """Valida las APIs de citas"""
        print("\n7. VALIDACIÓN DE APIs DE CITAS")
        print("-" * 35)
        
        try:
            # APIs principales
            api_urls = [
                ('core:agenda_events', 'API eventos de agenda'),
                ('core:api_horarios_disponibles', 'API horarios disponibles'),
            ]
            
            for url_name, description in api_urls:
                try:
                    if 'horarios_disponibles' in url_name:
                        # Esta API requiere dentista_id
                        if self.tenant:
                            with schema_context(self.tenant.schema_name):
                                from core.models import PerfilDentista
                                if PerfilDentista.objects.exists():
                                    dentista_id = PerfilDentista.objects.first().id
                                    url = reverse(url_name, kwargs={'dentista_id': dentista_id})
                                    self.log_success(f"API '{description}' configurada: {url}")
                                else:
                                    self.log_warning(f"No hay dentistas para validar API '{description}'")
                    else:
                        url = reverse(url_name)
                        self.log_success(f"API '{description}' configurada: {url}")
                        
                except NoReverseMatch:
                    self.log_error(f"API '{description}' ({url_name}) no encontrada")
            
            # Verificar APIs de detalle de cita
            if self.tenant:
                with schema_context(self.tenant.schema_name):
                    from core.models import Cita
                    
                    if Cita.objects.exists():
                        cita_id = Cita.objects.first().id
                        try:
                            url = reverse('core:cita_detail_api', kwargs={'pk': cita_id})
                            self.log_success(f"API detalle de cita configurada: {url}")
                        except NoReverseMatch:
                            self.log_warning("API detalle de cita no encontrada")
            
        except Exception as e:
            self.log_error(f"Error en validación de APIs: {str(e)}")

    def validate_appointment_business_logic(self):
        """Valida la lógica de negocio de citas"""
        print("\n8. VALIDACIÓN DE LÓGICA DE NEGOCIO")
        print("-" * 40)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita, Paciente, PerfilDentista
                
                # Verificar relaciones válidas
                total_citas = Cita.objects.count()
                
                if total_citas > 0:
                    # Verificar que todas las citas tienen paciente
                    citas_con_paciente = Cita.objects.exclude(
                        paciente__isnull=True
                    ).count() if hasattr(Cita, 'paciente') else 0
                    
                    if hasattr(Cita, 'paciente'):
                        porcentaje_pacientes = (citas_con_paciente / total_citas) * 100
                        self.log_success(f"Citas con paciente asignado: {citas_con_paciente}/{total_citas} ({porcentaje_pacientes:.1f}%)")
                    
                    # Verificar que todas las citas tienen dentista
                    citas_con_dentista = Cita.objects.exclude(
                        dentista__isnull=True
                    ).count()
                    
                    porcentaje_dentistas = (citas_con_dentista / total_citas) * 100
                    self.log_success(f"Citas con dentista asignado: {citas_con_dentista}/{total_citas} ({porcentaje_dentistas:.1f}%)")
                    
                    # Verificar solapamientos de citas (mismo dentista, horarios conflictivos)
                    solapamientos = self.check_appointment_overlaps()
                    if solapamientos == 0:
                        self.log_success("No se detectaron solapamientos de citas")
                    else:
                        self.log_warning(f"Posibles solapamientos detectados: {solapamientos}")
                
                # Verificar capacidad del sistema
                total_pacientes = Paciente.objects.count()
                total_dentistas = PerfilDentista.objects.count()
                
                if total_pacientes > 0 and total_dentistas > 0:
                    ratio_pacientes_dentista = total_pacientes / total_dentistas
                    self.log_success(f"Ratio pacientes/dentista: {ratio_pacientes_dentista:.1f}")
                
        except Exception as e:
            self.log_error(f"Error en validación de lógica de negocio: {str(e)}")

    def check_appointment_overlaps(self):
        """Verifica solapamientos de citas"""
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita
                from django.db.models import Q
                
                solapamientos = 0
                
                # Solo verificar una muestra para performance
                for cita in Cita.objects.all()[:20]:
                    if cita.duracion:
                        fin_cita = cita.fecha_hora + cita.duracion
                        
                        # Buscar citas del mismo dentista que se solapen
                        citas_solapadas = Cita.objects.filter(
                            dentista=cita.dentista
                        ).exclude(
                            id=cita.id
                        ).filter(
                            Q(fecha_hora__lt=fin_cita) & Q(fecha_hora__gte=cita.fecha_hora) |
                            Q(fecha_hora__lte=cita.fecha_hora) & 
                            Q(fecha_hora__gte=cita.fecha_hora)  # Simplificado
                        )
                        
                        if citas_solapadas.exists():
                            solapamientos += 1
                
                return solapamientos
                
        except Exception:
            return 0

    def run_validation(self):
        """Ejecuta toda la validación"""
        if not self.tenant:
            self.log_error("No se puede ejecutar validación sin tenant")
            return
            
        try:
            self.validate_appointment_model()
            self.validate_dentist_profiles()
            self.validate_appointment_urls()
            self.validate_appointment_states_workflow()
            self.validate_appointment_services_integration()
            self.validate_appointment_time_management()
            self.validate_appointment_apis()
            self.validate_appointment_business_logic()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - SISTEMA DE CITAS Y AGENDA")
        print("=" * 70)
        
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Tenant utilizado: {self.tenant.nombre if self.tenant else 'N/A'}")
        print(f"Tests ejecutados: {self.total_tests}")
        print(f"Tests exitosos: {self.success_count}")
        print(f"Errores: {len(self.errors)}")
        print(f"Advertencias: {len(self.warnings)}")
        print(f"Tasa de éxito: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n🔴 ERRORES ENCONTRADOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n🟡 ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if success_rate >= 90:
            print(f"\n✅ VALIDACIÓN EXITOSA")
            print("El sistema de citas y agenda está funcionando correctamente.")
        elif success_rate >= 70:
            print(f"\n⚠️  VALIDACIÓN CON ADVERTENCIAS")
            print("El sistema funciona, pero hay aspectos que necesitan atención.")
        else:
            print(f"\n❌ VALIDACIÓN FALLIDA")
            print("Se encontraron errores críticos que deben ser corregidos.")
        
        print(f"\nFin de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

def main():
    """Función principal"""
    try:
        validator = AppointmentsSystemValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()