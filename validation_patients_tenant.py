#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Módulo de Pacientes con Contexto Tenant
===========================================================

Este script valida el funcionamiento completo del módulo de pacientes
en el contexto del tenant demo.

Ejecutar desde la raíz del proyecto:
python validation_patients_tenant.py
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
from django.db import transaction, connection
from django.test import RequestFactory, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import Group
from tenants.models import Clinica
from django_tenants.utils import schema_context

User = get_user_model()

class PatientsModuleValidatorTenant:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.tenant = None
        
        print("=" * 70)
        print("VALIDACIÓN COMPLETA DEL MÓDULO DE PACIENTES (TENANT)")
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

    def validate_patient_model_tenant(self):
        """Valida el modelo de paciente en el contexto del tenant"""
        print("\n1. VALIDACIÓN DEL MODELO PACIENTE (TENANT)")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                # Importar modelos dentro del contexto del tenant
                from core.models import Paciente
                
                # Verificar campos del modelo
                paciente_fields = [field.name for field in Paciente._meta.get_fields()]
                expected_fields = [
                    'nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento',
                    'direccion'
                ]
                
                for field in expected_fields:
                    if field in paciente_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Paciente")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Paciente")
                
                # Verificar cuenta de pacientes
                pacientes_count = Paciente.objects.count()
                self.log_success(f"Pacientes registrados en el tenant: {pacientes_count}")
                
                # Verificar estructura de datos
                if pacientes_count > 0:
                    # Verificar emails únicos
                    from django.db import models
                    emails_duplicados = Paciente.objects.values('email').annotate(
                        count=models.Count('email')
                    ).filter(count__gt=1)
                    
                    if emails_duplicados.exists():
                        self.log_warning(f"Emails duplicados encontrados: {emails_duplicados.count()}")
                    else:
                        self.log_success("Emails únicos por paciente validados")
                        
                    # Mostrar algunos pacientes de ejemplo
                    sample_patients = Paciente.objects.all()[:3]
                    self.log_success(f"Pacientes de muestra: {[f'{p.nombre} {p.apellido}' for p in sample_patients]}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Paciente: {str(e)}")

    def validate_patient_data_integrity_tenant(self):
        """Valida la integridad de datos en el contexto del tenant"""
        print("\n2. VALIDACIÓN DE INTEGRIDAD DE DATOS (TENANT)")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Paciente
                
                if Paciente.objects.exists():
                    # Verificar pacientes con datos básicos completos
                    pacientes_completos = Paciente.objects.filter(
                        nombre__isnull=False,
                        apellido__isnull=False,
                        email__isnull=False
                    ).exclude(
                        nombre='',
                        apellido='',
                        email=''
                    ).count()
                    
                    total_pacientes = Paciente.objects.count()
                    porcentaje = (pacientes_completos / total_pacientes * 100) if total_pacientes > 0 else 0
                    
                    self.log_success(f"Pacientes con datos básicos completos: {pacientes_completos}/{total_pacientes} ({porcentaje:.1f}%)")
                    
                    # Verificar emails válidos
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    
                    pacientes_email_valido = 0
                    for paciente in Paciente.objects.filter(email__isnull=False).exclude(email=''):
                        if re.match(email_pattern, paciente.email):
                            pacientes_email_valido += 1
                    
                    self.log_success(f"Pacientes con email válido: {pacientes_email_valido}/{total_pacientes}")
                    
                    # Verificar teléfonos
                    pacientes_con_telefono = Paciente.objects.exclude(
                        telefono__isnull=True
                    ).exclude(telefono='').count()
                    
                    self.log_success(f"Pacientes con teléfono: {pacientes_con_telefono}/{total_pacientes}")
                    
                else:
                    self.log_warning("No hay pacientes para validar integridad de datos")
                
        except Exception as e:
            self.log_error(f"Error en validación de integridad: {str(e)}")

    def validate_patient_clinical_history_tenant(self):
        """Valida el historial clínico en el contexto del tenant"""
        print("\n3. VALIDACIÓN DEL HISTORIAL CLÍNICO (TENANT)")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import HistorialClinico, Paciente
                
                # Verificar registros de historial clínico
                historial_count = HistorialClinico.objects.count()
                self.log_success(f"Registros de historial clínico: {historial_count}")
                
                if historial_count > 0:
                    # Verificar pacientes con historial
                    pacientes_con_historial = HistorialClinico.objects.values(
                        'paciente'
                    ).distinct().count()
                    
                    self.log_success(f"Pacientes con historial clínico: {pacientes_con_historial}")
                    
                    # Verificar tipos de registros si existe el campo
                    try:
                        tipos_registro = HistorialClinico.objects.values(
                            'tipo_registro'
                        ).distinct()
                        if tipos_registro:
                            tipos_count = len(list(tipos_registro))
                            self.log_success(f"Tipos de registro clínico diferentes: {tipos_count}")
                    except Exception:
                        self.log_warning("Campo 'tipo_registro' no encontrado en HistorialClinico")
                
        except Exception as e:
            self.log_error(f"Error en validación de historial clínico: {str(e)}")

    def validate_patient_payments_tenant(self):
        """Valida el sistema de pagos en el contexto del tenant"""
        print("\n4. VALIDACIÓN DEL SISTEMA DE PAGOS (TENANT)")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Pago, Paciente
                
                # Verificar pagos registrados
                pagos = Pago.objects.count()
                self.log_success(f"Pagos registrados: {pagos}")
                
                if pagos > 0:
                    # Verificar pagos por paciente
                    field_name = 'paciente' if hasattr(Pago, 'paciente') else 'cliente'
                    pacientes_con_pagos = Pago.objects.values(field_name).distinct().count()
                    self.log_success(f"Pacientes con pagos registrados: {pacientes_con_pagos}")
                    
                    # Verificar métodos de pago
                    if hasattr(Pago, 'metodo_pago'):
                        metodos_pago = Pago.objects.values('metodo_pago').distinct().count()
                        if metodos_pago > 0:
                            self.log_success(f"Métodos de pago utilizados: {metodos_pago}")
                    
                    # Verificar montos totales
                    from django.db.models import Sum
                    total_pagos = Pago.objects.aggregate(total=Sum('monto'))['total']
                    if total_pagos:
                        self.log_success(f"Monto total de pagos: ${total_pagos:,.2f}")
                
        except Exception as e:
            self.log_error(f"Error en validación de pagos: {str(e)}")

    def validate_appointments_system_tenant(self):
        """Valida el sistema de citas en el contexto del tenant"""
        print("\n5. VALIDACIÓN DEL SISTEMA DE CITAS (TENANT)")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Cita, Paciente, PerfilDentista
                
                # Verificar citas registradas
                citas = Cita.objects.count()
                self.log_success(f"Citas registradas: {citas}")
                
                if citas > 0:
                    # Verificar estados de citas
                    if hasattr(Cita, 'estado'):
                        estados = Cita.objects.values_list('estado', flat=True).distinct()
                        self.log_success(f"Estados de cita utilizados: {list(estados)}")
                    
                    # Verificar citas por paciente
                    field_name = 'paciente' if hasattr(Cita, 'paciente') else 'cliente'
                    pacientes_con_citas = Cita.objects.values(field_name).distinct().count()
                    self.log_success(f"Pacientes con citas: {pacientes_con_citas}")
                    
                    # Verificar citas por dentista
                    dentistas_con_citas = Cita.objects.values('dentista').distinct().count()
                    self.log_success(f"Dentistas con citas asignadas: {dentistas_con_citas}")
                    
                    # Citas del mes actual
                    from datetime import datetime
                    inicio_mes = datetime.now().replace(day=1)
                    citas_mes = Cita.objects.filter(fecha_hora__gte=inicio_mes).count()
                    self.log_success(f"Citas del mes actual: {citas_mes}")
                
                # Verificar perfiles de dentista
                dentistas = PerfilDentista.objects.count()
                self.log_success(f"Perfiles de dentista registrados: {dentistas}")
                
        except Exception as e:
            self.log_error(f"Error en validación de citas: {str(e)}")

    def validate_services_system_tenant(self):
        """Valida el sistema de servicios en el contexto del tenant"""
        print("\n6. VALIDACIÓN DEL SISTEMA DE SERVICIOS (TENANT)")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio, Especialidad
                
                # Verificar servicios registrados
                servicios = Servicio.objects.count()
                self.log_success(f"Servicios registrados: {servicios}")
                
                if servicios > 0:
                    # Verificar precios de servicios
                    from django.db.models import Min, Max, Avg
                    precio_stats = Servicio.objects.aggregate(
                        min_precio=Min('precio'),
                        max_precio=Max('precio'),
                        avg_precio=Avg('precio')
                    )
                    
                    if precio_stats['min_precio']:
                        self.log_success(f"Rango de precios: ${precio_stats['min_precio']:,.2f} - ${precio_stats['max_precio']:,.2f}")
                        self.log_success(f"Precio promedio: ${precio_stats['avg_precio']:,.2f}")
                    
                    # Verificar servicios activos vs inactivos
                    if hasattr(Servicio, 'activo'):
                        activos = Servicio.objects.filter(activo=True).count()
                        inactivos = servicios - activos
                        self.log_success(f"Servicios activos: {activos}, Inactivos: {inactivos}")
                
                # Verificar especialidades
                especialidades = Especialidad.objects.count()
                self.log_success(f"Especialidades registradas: {especialidades}")
                
        except Exception as e:
            self.log_error(f"Error en validación de servicios: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        if not self.tenant:
            self.log_error("No se puede ejecutar validación sin tenant")
            return
            
        try:
            self.validate_patient_model_tenant()
            self.validate_patient_data_integrity_tenant()
            self.validate_patient_clinical_history_tenant()
            self.validate_patient_payments_tenant()
            self.validate_appointments_system_tenant()
            self.validate_services_system_tenant()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - MÓDULO DE PACIENTES (TENANT)")
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
            print("El módulo de pacientes está funcionando correctamente en el tenant.")
        elif success_rate >= 70:
            print(f"\n⚠️  VALIDACIÓN CON ADVERTENCIAS")
            print("El módulo funciona, pero hay aspectos que necesitan atención.")
        else:
            print(f"\n❌ VALIDACIÓN FALLIDA")
            print("Se encontraron errores críticos que deben ser corregidos.")
        
        print(f"\nFin de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

def main():
    """Función principal"""
    try:
        validator = PatientsModuleValidatorTenant()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()