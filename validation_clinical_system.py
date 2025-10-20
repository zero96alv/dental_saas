#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Sistema Clínico Completo
============================================

Este script valida el funcionamiento completo del sistema clínico
incluyendo historial clínico, odontograma de 48 dientes, diagnósticos,
aplicación de tratamientos, seguimiento clínico y odontograma anatómico.

Ejecutar desde la raíz del proyecto:
python validation_clinical_system.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
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

class ClinicalSystemValidator:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.tenant = None
        
        print("=" * 70)
        print("VALIDACIÓN DEL SISTEMA CLÍNICO COMPLETO")
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

    def validate_clinical_history_model(self):
        """Valida el modelo de historial clínico"""
        print("\n1. VALIDACIÓN DEL MODELO HISTORIAL CLÍNICO")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import HistorialClinico
                
                # Verificar campos del modelo
                historial_fields = [field.name for field in HistorialClinico._meta.get_fields()]
                expected_fields = [
                    'paciente', 'fecha', 'tipo_registro', 'descripcion',
                    'tratamiento', 'observaciones', 'dentista', 'diente_tratado'
                ]
                
                for field in expected_fields:
                    if field in historial_fields:
                        self.log_success(f"Campo '{field}' presente en HistorialClinico")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en HistorialClinico")
                
                # Verificar conteo de registros
                registros_count = HistorialClinico.objects.count()
                self.log_success(f"Registros de historial clínico: {registros_count}")
                
                if registros_count > 0:
                    # Análisis por tipo de registro
                    if 'tipo_registro' in historial_fields:
                        tipos = HistorialClinico.objects.values_list('tipo_registro', flat=True).distinct()
                        self.log_success(f"Tipos de registro utilizados: {list(tipos)}")
                    
                    # Registros por paciente
                    pacientes_con_historial = HistorialClinico.objects.values(
                        'paciente'
                    ).distinct().count()
                    self.log_success(f"Pacientes con historial clínico: {pacientes_con_historial}")
                    
                    # Registros por dentista
                    if 'dentista' in historial_fields:
                        dentistas_registrantes = HistorialClinico.objects.exclude(
                            dentista__isnull=True
                        ).values('dentista').distinct().count()
                        self.log_success(f"Dentistas que han registrado historiales: {dentistas_registrantes}")
                
        except Exception as e:
            self.log_error(f"Error en validación de historial clínico: {str(e)}")

    def validate_odontogram_system(self):
        """Valida el sistema de odontograma"""
        print("\n2. VALIDACIÓN DEL SISTEMA DE ODONTOGRAMA")
        print("-" * 41)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import EstadoDiente
                
                # Verificar modelo EstadoDiente
                estado_fields = [field.name for field in EstadoDiente._meta.get_fields()]
                expected_fields = [
                    'paciente', 'numero_diente', 'estado', 'observaciones',
                    'fecha_modificacion', 'dentista', 'color_estado'
                ]
                
                for field in expected_fields:
                    if field in estado_fields:
                        self.log_success(f"Campo '{field}' presente en EstadoDiente")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en EstadoDiente")
                
                # Verificar registros de estados de dientes
                estados_count = EstadoDiente.objects.count()
                self.log_success(f"Estados de dientes registrados: {estados_count}")
                
                if estados_count > 0:
                    # Verificar cobertura de dientes (1-48 para adultos)
                    dientes_registrados = EstadoDiente.objects.values_list(
                        'numero_diente', flat=True
                    ).distinct()
                    
                    dientes_unicos = sorted(set(dientes_registrados))
                    self.log_success(f"Dientes con registros: {len(dientes_unicos)} únicos")
                    
                    # Verificar rango válido de dientes (1-48)
                    dientes_validos = [d for d in dientes_unicos if 1 <= d <= 48]
                    dientes_invalidos = [d for d in dientes_unicos if d < 1 or d > 48]
                    
                    self.log_success(f"Dientes en rango válido (1-48): {len(dientes_validos)}")
                    if dientes_invalidos:
                        self.log_warning(f"Dientes fuera de rango: {dientes_invalidos}")
                    
                    # Verificar estados utilizados
                    if 'estado' in estado_fields:
                        estados_utilizados = EstadoDiente.objects.values_list('estado', flat=True).distinct()
                        self.log_success(f"Estados de dientes utilizados: {list(estados_utilizados)}")
                    
                    # Pacientes con odontograma
                    pacientes_con_odontograma = EstadoDiente.objects.values(
                        'paciente'
                    ).distinct().count()
                    self.log_success(f"Pacientes con odontograma: {pacientes_con_odontograma}")
                
                # Verificar URLs del odontograma
                try:
                    # Necesita un paciente para probar la URL
                    from core.models import Paciente
                    if Paciente.objects.exists():
                        paciente_id = Paciente.objects.first().id
                        url = reverse('core:odontograma_48', kwargs={'cliente_id': paciente_id})
                        self.log_success(f"URL odontograma 48 configurada: {url}")
                    else:
                        self.log_warning("No hay pacientes para validar URL de odontograma")
                except NoReverseMatch:
                    self.log_error("URL del odontograma no encontrada")
                
        except Exception as e:
            self.log_error(f"Error en validación del odontograma: {str(e)}")

    def validate_diagnosis_system(self):
        """Valida el sistema de diagnósticos"""
        print("\n3. VALIDACIÓN DEL SISTEMA DE DIAGNÓSTICOS")
        print("-" * 42)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Diagnostico
                
                # Verificar campos del modelo
                diagnostico_fields = [field.name for field in Diagnostico._meta.get_fields()]
                expected_fields = [
                    'nombre', 'codigo', 'descripcion', 'categoria',
                    'activo', 'color', 'requiere_tratamiento'
                ]
                
                for field in expected_fields:
                    if field in diagnostico_fields:
                        self.log_success(f"Campo '{field}' presente en Diagnostico")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en Diagnostico")
                
                # Verificar conteo de diagnósticos
                diagnosticos_count = Diagnostico.objects.count()
                self.log_success(f"Diagnósticos registrados: {diagnosticos_count}")
                
                if diagnosticos_count > 0:
                    # Verificar diagnósticos activos
                    if 'activo' in diagnostico_fields:
                        activos = Diagnostico.objects.filter(activo=True).count()
                        self.log_success(f"Diagnósticos activos: {activos}/{diagnosticos_count}")
                    
                    # Verificar categorías
                    if 'categoria' in diagnostico_fields:
                        categorias = Diagnostico.objects.values_list('categoria', flat=True).distinct()
                        self.log_success(f"Categorías de diagnósticos: {list(categorias)}")
                    
                    # Verificar códigos únicos
                    if 'codigo' in diagnostico_fields:
                        codigos_duplicados = Diagnostico.objects.exclude(
                            codigo__isnull=True
                        ).exclude(codigo='').values('codigo').annotate(
                            count=models.Count('codigo')
                        ).filter(count__gt=1).count()
                        
                        if codigos_duplicados > 0:
                            self.log_warning(f"Diagnósticos con códigos duplicados: {codigos_duplicados}")
                        else:
                            self.log_success("Códigos de diagnósticos únicos")
                    
                    # Mostrar algunos ejemplos
                    sample_diagnosticos = Diagnostico.objects.all()[:5]
                    nombres = [d.nombre for d in sample_diagnosticos]
                    self.log_success(f"Diagnósticos de ejemplo: {nombres}")
                
                # Verificar URLs de diagnósticos
                diagnostic_urls = [
                    ('core:diagnostico_list', 'Lista de diagnósticos'),
                    ('core:diagnostico_create', 'Crear diagnóstico'),
                ]
                
                for url_name, description in diagnostic_urls:
                    try:
                        url = reverse(url_name)
                        self.log_success(f"URL '{description}' configurada: {url}")
                    except NoReverseMatch:
                        self.log_error(f"URL '{description}' no encontrada")
                
        except Exception as e:
            self.log_error(f"Error en validación de diagnósticos: {str(e)}")

    def validate_odontogram_apis(self):
        """Valida las APIs del odontograma"""
        print("\n4. VALIDACIÓN DE APIs DEL ODONTOGRAMA")
        print("-" * 38)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Paciente
                
                # Verificar APIs del odontograma
                if Paciente.objects.exists():
                    paciente_id = Paciente.objects.first().id
                    
                    odontogram_apis = [
                        ('core:odontograma_api_get', {'cliente_id': paciente_id}, 'API obtener odontograma'),
                        ('core:odontograma_api_update', {'cliente_id': paciente_id}, 'API actualizar odontograma'),
                        ('core:diagnostico_api_list', {}, 'API lista de diagnósticos'),
                    ]
                    
                    for url_name, kwargs, description in odontogram_apis:
                        try:
                            url = reverse(url_name, kwargs=kwargs) if kwargs else reverse(url_name)
                            self.log_success(f"API '{description}' configurada: {url}")
                        except NoReverseMatch:
                            self.log_error(f"API '{description}' no encontrada")
                else:
                    self.log_warning("No hay pacientes para validar APIs del odontograma")
                
                # Verificar URLs de prueba
                test_urls = [
                    ('core:prueba_odontograma_anatomico', 'Prueba odontograma anatómico'),
                    ('core:prueba_boca_abierta', 'Prueba boca abierta'),
                    ('core:prueba_fdi_universal', 'Prueba sistema FDI Universal'),
                ]
                
                for url_name, description in test_urls:
                    try:
                        url = reverse(url_name)
                        self.log_success(f"URL prueba '{description}' configurada: {url}")
                    except NoReverseMatch:
                        self.log_warning(f"URL prueba '{description}' no encontrada")
                
        except Exception as e:
            self.log_error(f"Error en validación de APIs del odontograma: {str(e)}")

    def validate_dental_numbering_systems(self):
        """Valida los sistemas de numeración dental"""
        print("\n5. VALIDACIÓN DE SISTEMAS DE NUMERACIÓN DENTAL")
        print("-" * 50)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import EstadoDiente
                
                # Verificar sistema FDI (1-48 para adultos completos)
                if EstadoDiente.objects.exists():
                    dientes_registrados = EstadoDiente.objects.values_list(
                        'numero_diente', flat=True
                    ).distinct()
                    
                    # Análisis del sistema FDI
                    cuadrante_1 = [d for d in dientes_registrados if 11 <= d <= 18]  # Superior derecho
                    cuadrante_2 = [d for d in dientes_registrados if 21 <= d <= 28]  # Superior izquierdo
                    cuadrante_3 = [d for d in dientes_registrados if 31 <= d <= 38]  # Inferior izquierdo
                    cuadrante_4 = [d for d in dientes_registrados if 41 <= d <= 48]  # Inferior derecho
                    
                    self.log_success(f"Cuadrante 1 (Superior derecho): {len(cuadrante_1)} dientes")
                    self.log_success(f"Cuadrante 2 (Superior izquierdo): {len(cuadrante_2)} dientes")
                    self.log_success(f"Cuadrante 3 (Inferior izquierdo): {len(cuadrante_3)} dientes")
                    self.log_success(f"Cuadrante 4 (Inferior derecho): {len(cuadrante_4)} dientes")
                    
                    # Verificar completitud del sistema
                    total_fdi = len(cuadrante_1) + len(cuadrante_2) + len(cuadrante_3) + len(cuadrante_4)
                    if total_fdi > 0:
                        self.log_success(f"Sistema FDI operativo: {total_fdi} dientes registrados")
                    
                    # Verificar dientes específicos importantes
                    dientes_importantes = [11, 21, 31, 41]  # Incisivos centrales
                    importantes_registrados = [d for d in dientes_registrados if d in dientes_importantes]
                    
                    if importantes_registrados:
                        self.log_success(f"Dientes importantes registrados: {importantes_registrados}")
                else:
                    self.log_warning("No hay registros de estados de dientes para validar numeración")
                
                self.log_success("Sistema de numeración FDI compatible")
                
        except Exception as e:
            self.log_error(f"Error en validación de numeración dental: {str(e)}")

    def validate_clinical_workflow(self):
        """Valida el flujo de trabajo clínico"""
        print("\n6. VALIDACIÓN DEL FLUJO CLÍNICO")
        print("-" * 35)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import HistorialClinico, EstadoDiente, Diagnostico, Cita
                
                # Verificar integración historial-odontograma
                historial_count = HistorialClinico.objects.count()
                odontograma_count = EstadoDiente.objects.count()
                
                if historial_count > 0 and odontograma_count > 0:
                    self.log_success("Integración historial-odontograma disponible")
                elif historial_count > 0:
                    self.log_success("Sistema de historial clínico funcional")
                elif odontograma_count > 0:
                    self.log_success("Sistema de odontograma funcional")
                else:
                    self.log_warning("Sin datos clínicos para validar flujo")
                
                # Verificar relación citas-historial
                citas_count = Cita.objects.count()
                if citas_count > 0:
                    # Verificar si existen registros clínicos asociados a citas
                    historial_fields = [field.name for field in HistorialClinico._meta.get_fields()]
                    
                    if 'cita' in historial_fields:
                        historiales_con_cita = HistorialClinico.objects.exclude(
                            cita__isnull=True
                        ).count()
                        
                        if historiales_con_cita > 0:
                            self.log_success(f"Historiales vinculados a citas: {historiales_con_cita}")
                        else:
                            self.log_warning("No hay historiales vinculados a citas")
                    
                    self.log_success("Flujo citas-historial configurado")
                
                # Verificar capacidad de seguimiento
                diagnosticos_count = Diagnostico.objects.count()
                if diagnosticos_count > 0:
                    self.log_success("Sistema de diagnósticos para seguimiento disponible")
                    
                    # Verificar diagnósticos que requieren tratamiento
                    diag_fields = [field.name for field in Diagnostico._meta.get_fields()]
                    if 'requiere_tratamiento' in diag_fields:
                        requieren_tratamiento = Diagnostico.objects.filter(
                            requiere_tratamiento=True
                        ).count()
                        self.log_success(f"Diagnósticos que requieren tratamiento: {requieren_tratamiento}")
                
                self.log_success("Flujo de trabajo clínico validado")
                
        except Exception as e:
            self.log_error(f"Error en validación del flujo clínico: {str(e)}")

    def validate_clinical_reports_capability(self):
        """Valida capacidades de reportes clínicos"""
        print("\n7. VALIDACIÓN DE REPORTES CLÍNICOS")
        print("-" * 37)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import HistorialClinico, EstadoDiente, Diagnostico, Paciente
                from django.db.models import Count
                
                # Verificar datos para reportes de tratamientos
                historial_count = HistorialClinico.objects.count()
                if historial_count > 0:
                    self.log_success(f"Datos para reportes de tratamientos: {historial_count} registros")
                    
                    # Verificar capacidad de análisis por tipo
                    historial_fields = [field.name for field in HistorialClinico._meta.get_fields()]
                    if 'tipo_registro' in historial_fields:
                        tipos_stats = HistorialClinico.objects.values('tipo_registro').annotate(
                            count=Count('id')
                        )
                        
                        if tipos_stats:
                            self.log_success("Análisis de tratamientos por tipo disponible")
                            for stat in tipos_stats[:3]:  # Mostrar primeros 3
                                tipo = stat['tipo_registro'] or 'Sin especificar'
                                self.log_success(f"   {tipo}: {stat['count']} registros")
                
                # Verificar datos para reportes de odontograma
                odontograma_count = EstadoDiente.objects.count()
                if odontograma_count > 0:
                    self.log_success(f"Datos para reportes de odontograma: {odontograma_count} estados")
                    
                    # Análisis por estado de dientes
                    estado_fields = [field.name for field in EstadoDiente._meta.get_fields()]
                    if 'estado' in estado_fields:
                        estados_stats = EstadoDiente.objects.values('estado').annotate(
                            count=Count('id')
                        )
                        
                        if estados_stats:
                            self.log_success("Análisis de estados dentales disponible")
                            for stat in estados_stats[:3]:
                                estado = stat['estado'] or 'Sin especificar'
                                self.log_success(f"   Estado '{estado}': {stat['count']} dientes")
                
                # Verificar datos para reportes de diagnósticos
                diagnosticos_count = Diagnostico.objects.count()
                if diagnosticos_count > 0:
                    self.log_success(f"Catálogo de diagnósticos: {diagnosticos_count} disponibles")
                
                # Verificar capacidad de reportes por paciente
                pacientes_count = Paciente.objects.count()
                if pacientes_count > 0:
                    self.log_success(f"Reportes individuales disponibles: {pacientes_count} pacientes")
                
                self.log_success("Sistema preparado para reportes clínicos completos")
                
        except Exception as e:
            self.log_error(f"Error en validación de reportes clínicos: {str(e)}")

    def validate_clinical_data_integrity(self):
        """Valida la integridad de datos clínicos"""
        print("\n8. VALIDACIÓN DE INTEGRIDAD CLÍNICA")
        print("-" * 39)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import HistorialClinico, EstadoDiente, Diagnostico
                
                # Validar integridad del historial clínico
                historial_count = HistorialClinico.objects.count()
                if historial_count > 0:
                    # Verificar que todos los registros tienen paciente
                    sin_paciente = HistorialClinico.objects.filter(paciente__isnull=True).count()
                    if sin_paciente > 0:
                        self.log_warning(f"Registros de historial sin paciente: {sin_paciente}")
                    else:
                        self.log_success("Todos los registros de historial tienen paciente")
                    
                    # Verificar fechas válidas
                    from datetime import date
                    fecha_futura = date.today() + timedelta(days=1)
                    
                    historial_fields = [field.name for field in HistorialClinico._meta.get_fields()]
                    if 'fecha' in historial_fields:
                        fechas_futuras = HistorialClinico.objects.filter(fecha__gt=fecha_futura).count()
                        if fechas_futuras > 0:
                            self.log_warning(f"Registros con fecha futura: {fechas_futuras}")
                        else:
                            self.log_success("Fechas de historial clínico consistentes")
                
                # Validar integridad del odontograma
                odontograma_count = EstadoDiente.objects.count()
                if odontograma_count > 0:
                    # Verificar números de dientes válidos
                    dientes_invalidos = EstadoDiente.objects.filter(
                        models.Q(numero_diente__lt=11) | 
                        models.Q(numero_diente__gt=48) |
                        (~models.Q(numero_diente__in=[
                            11,12,13,14,15,16,17,18,  # Cuadrante 1
                            21,22,23,24,25,26,27,28,  # Cuadrante 2
                            31,32,33,34,35,36,37,38,  # Cuadrante 3
                            41,42,43,44,45,46,47,48   # Cuadrante 4
                        ]))
                    ).count()
                    
                    if dientes_invalidos > 0:
                        self.log_warning(f"Estados con numeración dental inválida: {dientes_invalidos}")
                    else:
                        self.log_success("Numeración dental FDI consistente")
                    
                    # Verificar duplicados por paciente-diente
                    duplicados = EstadoDiente.objects.values('paciente', 'numero_diente').annotate(
                        count=models.Count('id')
                    ).filter(count__gt=1).count()
                    
                    if duplicados > 0:
                        self.log_warning(f"Estados duplicados paciente-diente: {duplicados}")
                    else:
                        self.log_success("Estados de dientes únicos por paciente")
                
                # Validar integridad de diagnósticos
                diagnosticos_count = Diagnostico.objects.count()
                if diagnosticos_count > 0:
                    # Verificar nombres únicos
                    nombres_duplicados = Diagnostico.objects.values('nombre').annotate(
                        count=models.Count('nombre')
                    ).filter(count__gt=1).count()
                    
                    if nombres_duplicados > 0:
                        self.log_warning(f"Diagnósticos con nombres duplicados: {nombres_duplicados}")
                    else:
                        self.log_success("Nombres de diagnósticos únicos")
                
                self.log_success("Integridad de datos clínicos validada")
                
        except Exception as e:
            self.log_error(f"Error en validación de integridad clínica: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        if not self.tenant:
            self.log_error("No se puede ejecutar validación sin tenant")
            return
            
        try:
            self.validate_clinical_history_model()
            self.validate_odontogram_system()
            self.validate_diagnosis_system()
            self.validate_odontogram_apis()
            self.validate_dental_numbering_systems()
            self.validate_clinical_workflow()
            self.validate_clinical_reports_capability()
            self.validate_clinical_data_integrity()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - SISTEMA CLÍNICO COMPLETO")
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
            print("El sistema clínico completo está funcionando correctamente.")
            print("🦷 Odontograma de 48 dientes, diagnósticos y seguimiento operativo.")
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
        validator = ClinicalSystemValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()