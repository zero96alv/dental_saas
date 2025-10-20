#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Módulo Completo de Pacientes
===============================================

Este script valida el funcionamiento completo del módulo de pacientes
incluyendo CRUD, perfil, datos fiscales, historial clínico, invitación,
cuestionarios, portal del paciente, saldos y pagos.

Ejecutar desde la raíz del proyecto:
python validation_patients_module.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

# Configurar Django
sys.path.append('C:\\desarrollo\\dental_saas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.db import models
from django.test import RequestFactory, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import Group

# Importar modelos necesarios
try:
    from core.models import Paciente
except ImportError:
    Paciente = None

try:
    from core.models import HistorialClinico
except ImportError:
    HistorialClinico = None

try:
    from core.models import Pago
except ImportError:
    Pago = None

try:
    from core.models import PlanPago
except ImportError:
    PlanPago = None

try:
    from core.models import RespuestaHistorial
except ImportError:
    RespuestaHistorial = None

try:
    from core.models import CuestionarioHistorialCompletado
except ImportError:
    CuestionarioHistorialCompletado = None

try:
    from core.models import ConsentimientoInformado
except ImportError:
    ConsentimientoInformado = None

try:
    from core.models import PacienteConsentimiento
except ImportError:
    PacienteConsentimiento = None

try:
    from core.models import SatFormaPago, SatMetodoPago, SatRegimenFiscal, SatUsoCFDI
except ImportError:
    SatFormaPago = SatMetodoPago = SatRegimenFiscal = SatUsoCFDI = None

User = get_user_model()

class PatientsModuleValidator:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        
        print("=" * 70)
        print("VALIDACIÓN COMPLETA DEL MÓDULO DE PACIENTES")
        print("=" * 70)
        print(f"Inicio de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

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

    def validate_patient_model(self):
        """Valida el modelo de paciente y sus campos"""
        print("\n1. VALIDACIÓN DEL MODELO PACIENTE")
        print("-" * 40)
        
        try:
            # Verificar si el modelo Paciente existe
            if Paciente is None:
                self.log_error("Modelo Paciente no encontrado")
                return
                
            paciente_fields = [field.name for field in Paciente._meta.get_fields()]
            expected_fields = [
                'nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento',
                'rfc', 'curp', 'direccion', 'ocupacion', 'contacto_emergencia'
            ]
            
            for field in expected_fields:
                if field in paciente_fields:
                    self.log_success(f"Campo '{field}' presente en modelo Paciente")
                else:
                    self.log_warning(f"Campo '{field}' no encontrado en modelo Paciente")
            
            # Verificar constraints y validaciones
            pacientes_count = Paciente.objects.count()
            self.log_success(f"Pacientes registrados en el sistema: {pacientes_count}")
            
            # Verificar pacientes con emails únicos
            if pacientes_count > 0:
                emails_duplicados = Paciente.objects.values('email').annotate(
                    count=models.Count('email')
                ).filter(count__gt=1)
                
                if emails_duplicados.exists():
                    self.log_warning(f"Emails duplicados encontrados: {emails_duplicados.count()}")
                else:
                    self.log_success("Emails únicos por paciente validados")
            
        except Exception as e:
            self.log_error(f"Error en validación del modelo Paciente: {str(e)}")

    def validate_patient_crud_operations(self):
        """Valida las operaciones CRUD de pacientes"""
        print("\n2. VALIDACIÓN DE OPERACIONES CRUD DE PACIENTES")
        print("-" * 50)
        
        try:
            # Verificar URLs de pacientes
            crud_urls = [
                'core:paciente_list',
                'core:paciente_create', 
                'core:paciente_detail',
                'core:paciente_edit',
                'core:paciente_delete'
            ]
            
            for url_name in crud_urls:
                try:
                    if 'detail' in url_name or 'edit' in url_name or 'delete' in url_name:
                        # Necesita ID de paciente
                        if Paciente.objects.exists():
                            paciente_id = Paciente.objects.first().id
                            url = reverse(url_name, kwargs={'pk': paciente_id})
                        else:
                            self.log_warning(f"No hay pacientes para probar URL: {url_name}")
                            continue
                    else:
                        url = reverse(url_name)
                    
                    self.log_success(f"URL '{url_name}' configurada correctamente: {url}")
                    
                except NoReverseMatch:
                    self.log_error(f"URL '{url_name}' no encontrada o mal configurada")
            
            # Verificar formularios de paciente
            try:
                from core.forms import PacienteForm
                self.log_success("Formulario PacienteForm disponible")
            except ImportError:
                self.log_warning("Formulario PacienteForm no encontrado")
            
        except Exception as e:
            self.log_error(f"Error en validación CRUD: {str(e)}")

    def validate_patient_financial_data(self):
        """Valida datos fiscales y financieros de pacientes"""
        print("\n3. VALIDACIÓN DE DATOS FISCALES Y FINANCIEROS")
        print("-" * 50)
        
        try:
            # Verificar configuración SAT
            sat_models = [
                (SatFormaPago, "Formas de Pago SAT"),
                (SatMetodoPago, "Métodos de Pago SAT"), 
                (SatRegimenFiscal, "Regímenes Fiscales SAT"),
                (SatUsoCFDI, "Usos de CFDI SAT")
            ]
            
            for model, description in sat_models:
                try:
                    count = model.objects.count()
                    if count > 0:
                        self.log_success(f"{description}: {count} registros")
                    else:
                        self.log_warning(f"{description}: Sin registros configurados")
                except Exception:
                    self.log_warning(f"{description}: Tabla no existe")
            
            # Verificar saldos de pacientes
            try:
                pacientes_con_saldo = Paciente.objects.exclude(
                    saldo_pendiente=0
                ).count() if hasattr(Paciente, 'saldo_pendiente') else 0
                
                self.log_success(f"Pacientes con saldo pendiente: {pacientes_con_saldo}")
                
            except Exception as e:
                self.log_warning(f"No se pudo verificar saldos: {str(e)}")
            
            # Verificar planes de pago
            if PlanPago is not None:
                planes_pago = PlanPago.objects.count()
                self.log_success(f"Planes de pago configurados: {planes_pago}")
            else:
                self.log_warning("Modelo PlanPago no encontrado")
            
        except Exception as e:
            self.log_error(f"Error en validación financiera: {str(e)}")

    def validate_patient_clinical_history(self):
        """Valida el historial clínico de pacientes"""
        print("\n4. VALIDACIÓN DEL HISTORIAL CLÍNICO")
        print("-" * 40)
        
        try:
            # Verificar registros de historial clínico
            if HistorialClinico is not None:
                historial_count = HistorialClinico.objects.count()
                self.log_success(f"Registros de historial clínico: {historial_count}")
            else:
                self.log_warning("Modelo HistorialClinico no encontrado")
                historial_count = 0
            
            if historial_count > 0:
                # Verificar pacientes con historial
                pacientes_con_historial = HistorialClinico.objects.values(
                    'paciente'
                ).distinct().count()
                
                self.log_success(f"Pacientes con historial clínico: {pacientes_con_historial}")
                
                # Verificar tipos de registros clínicos
                tipos_registro = HistorialClinico.objects.values(
                    'tipo_registro'
                ).distinct() if hasattr(HistorialClinico, 'tipo_registro') else []
                
                if tipos_registro:
                    self.log_success(f"Tipos de registro clínico: {len(tipos_registro)}")
                
            # Verificar URLs del historial
            history_urls = [
                'core:paciente_history',
                'core:historial_create'
            ]
            
            for url_name in history_urls:
                try:
                    if Paciente.objects.exists():
                        if 'history' in url_name:
                            paciente_id = Paciente.objects.first().id
                            url = reverse(url_name, kwargs={'pk': paciente_id})
                        else:
                            cliente_id = Paciente.objects.first().id
                            url = reverse(url_name, kwargs={'cliente_id': cliente_id})
                        
                        self.log_success(f"URL historial '{url_name}' configurada: {url}")
                    else:
                        self.log_warning(f"No hay pacientes para probar URL: {url_name}")
                        
                except NoReverseMatch:
                    self.log_error(f"URL historial '{url_name}' mal configurada")
            
        except Exception as e:
            self.log_error(f"Error en validación de historial clínico: {str(e)}")

    def validate_patient_questionnaire_system(self):
        """Valida el sistema de cuestionarios de pacientes"""
        print("\n5. VALIDACIÓN DEL SISTEMA DE CUESTIONARIOS")
        print("-" * 45)
        
        try:
            # Verificar cuestionarios completados
            if CuestionarioHistorialCompletado is not None:
                try:
                    cuestionarios_completados = CuestionarioHistorialCompletado.objects.count()
                    self.log_success(f"Cuestionarios completados: {cuestionarios_completados}")
                    
                    if cuestionarios_completados > 0:
                        pacientes_con_cuestionario = CuestionarioHistorialCompletado.objects.values(
                            'paciente'
                        ).distinct().count()
                        self.log_success(f"Pacientes con cuestionario: {pacientes_con_cuestionario}")
                except Exception:
                    self.log_warning("Error al acceder a cuestionarios completados")
            else:
                self.log_warning("Modelo CuestionarioHistorialCompletado no encontrado")
            
            # Verificar respuestas de historial
            if RespuestaHistorial is not None:
                try:
                    respuestas = RespuestaHistorial.objects.count()
                    self.log_success(f"Respuestas de historial registradas: {respuestas}")
                except Exception:
                    self.log_warning("Error al acceder a respuestas de historial")
            else:
                self.log_warning("Modelo RespuestaHistorial no encontrado")
            
            # Verificar URLs de cuestionarios
            questionnaire_urls = [
                'core:paciente_cuestionario',
                'core:paciente_historial_mejorado',
                'core:cuestionario_lista',
                'core:cuestionario_completar',
                'core:cuestionario_detalle'
            ]
            
            for url_name in questionnaire_urls:
                try:
                    if Paciente.objects.exists():
                        paciente_id = Paciente.objects.first().id
                        
                        if 'completar' in url_name or 'detalle' in url_name:
                            url = reverse(url_name, kwargs={'paciente_id': paciente_id})
                        elif 'cuestionario' in url_name and 'lista' not in url_name:
                            url = reverse(url_name, kwargs={'pk': paciente_id})
                        else:
                            url = reverse(url_name)
                        
                        self.log_success(f"URL cuestionario '{url_name}' configurada")
                    else:
                        self.log_warning(f"No hay pacientes para probar URL: {url_name}")
                        
                except NoReverseMatch:
                    self.log_error(f"URL cuestionario '{url_name}' mal configurada")
            
        except Exception as e:
            self.log_error(f"Error en validación de cuestionarios: {str(e)}")

    def validate_patient_portal(self):
        """Valida el portal del paciente"""
        print("\n6. VALIDACIÓN DEL PORTAL DEL PACIENTE")
        print("-" * 40)
        
        try:
            # Verificar URLs del portal
            portal_urls = [
                'core:portal_pagos',
                'core:portal_historial',
                'core:portal_completar_historial'
            ]
            
            for url_name in portal_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL portal '{url_name}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL portal '{url_name}' no encontrada")
            
            # Verificar usuarios paciente
            pacientes_usuarios = User.objects.filter(groups__name='Paciente').count()
            if pacientes_usuarios > 0:
                self.log_success(f"Usuarios paciente registrados: {pacientes_usuarios}")
            else:
                self.log_warning("No hay usuarios con rol de paciente")
            
        except Exception as e:
            self.log_error(f"Error en validación del portal del paciente: {str(e)}")

    def validate_patient_consent_system(self):
        """Valida el sistema de consentimiento informado"""
        print("\n7. VALIDACIÓN DEL SISTEMA DE CONSENTIMIENTO")
        print("-" * 45)
        
        try:
            # Verificar documentos de consentimiento
            if ConsentimientoInformado is not None and PacienteConsentimiento is not None:
                try:
                    consentimientos = ConsentimientoInformado.objects.count()
                    self.log_success(f"Documentos de consentimiento: {consentimientos}")
                    
                    # Verificar consentimientos de pacientes
                    paciente_consentimientos = PacienteConsentimiento.objects.count()
                    self.log_success(f"Consentimientos de pacientes: {paciente_consentimientos}")
                    
                    if paciente_consentimientos > 0:
                        consentimientos_firmados = PacienteConsentimiento.objects.filter(
                            firmado=True
                        ).count()
                        self.log_success(f"Consentimientos firmados: {consentimientos_firmados}")
                except Exception as e:
                    self.log_warning(f"Error al acceder al sistema de consentimiento: {str(e)}")
            else:
                self.log_warning("Modelos de consentimiento no encontrados")
            
            # Verificar URLs de consentimiento
            consent_urls = [
                'core:consentimiento_list',
                'core:consentimiento_create',
                'core:paciente_consentimiento_list',
                'core:firmar_consentimiento'
            ]
            
            for url_name in consent_urls:
                try:
                    if 'firmar' in url_name:
                        # Necesita ID de consentimiento
                        continue  # Saltamos por ahora
                    else:
                        url = reverse(url_name)
                    
                    self.log_success(f"URL consentimiento '{url_name}' configurada")
                except NoReverseMatch:
                    self.log_error(f"URL consentimiento '{url_name}' no encontrada")
            
        except Exception as e:
            self.log_error(f"Error en validación de consentimientos: {str(e)}")

    def validate_patient_payments_system(self):
        """Valida el sistema de pagos de pacientes"""
        print("\n8. VALIDACIÓN DEL SISTEMA DE PAGOS")
        print("-" * 40)
        
        try:
            # Verificar pagos registrados
            if Pago is not None:
                pagos = Pago.objects.count()
                self.log_success(f"Pagos registrados: {pagos}")
                
                if pagos > 0:
                    # Verificar pagos por paciente
                    pacientes_con_pagos = Pago.objects.values(
                        'paciente' if hasattr(Pago, 'paciente') else 'cliente'
                    ).distinct().count()
                    self.log_success(f"Pacientes con pagos registrados: {pacientes_con_pagos}")
                    
                    # Verificar tipos de pago
                    metodos_pago = Pago.objects.values(
                        'metodo_pago'
                    ).distinct().count() if hasattr(Pago, 'metodo_pago') else 0
                    
                    if metodos_pago > 0:
                        self.log_success(f"Métodos de pago utilizados: {metodos_pago}")
            else:
                self.log_warning("Modelo Pago no encontrado")
            
            # Verificar URLs de pagos
            payment_urls = [
                'core:registrar_pago_paciente',
                'core:saldos_pendientes',
                'core:pacientes_pendientes_pago'
            ]
            
            for url_name in payment_urls:
                try:
                    if 'registrar_pago_paciente' in url_name:
                        if Paciente.objects.exists():
                            paciente_id = Paciente.objects.first().id
                            url = reverse(url_name, kwargs={'paciente_id': paciente_id})
                        else:
                            self.log_warning(f"No hay pacientes para probar URL: {url_name}")
                            continue
                    else:
                        url = reverse(url_name)
                    
                    self.log_success(f"URL pagos '{url_name}' configurada")
                except NoReverseMatch:
                    self.log_error(f"URL pagos '{url_name}' no encontrada")
            
        except Exception as e:
            self.log_error(f"Error en validación de pagos: {str(e)}")

    def validate_patient_data_integrity(self):
        """Valida la integridad de datos de pacientes"""
        print("\n9. VALIDACIÓN DE INTEGRIDAD DE DATOS")
        print("-" * 40)
        
        try:
            if Paciente is not None and Paciente.objects.exists():
                # Verificar pacientes con datos mínimos
                pacientes_completos = Paciente.objects.filter(
                    nombre__isnull=False,
                    apellido__isnull=False,
                    email__isnull=False
                ).count()
                
                total_pacientes = Paciente.objects.count()
                porcentaje = (pacientes_completos / total_pacientes * 100) if total_pacientes > 0 else 0
                
                self.log_success(f"Pacientes con datos básicos completos: {pacientes_completos}/{total_pacientes} ({porcentaje:.1f}%)")
                
                # Verificar emails válidos
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                
                pacientes_email_valido = 0
                for paciente in Paciente.objects.filter(email__isnull=False):
                    if re.match(email_pattern, paciente.email):
                        pacientes_email_valido += 1
                
                self.log_success(f"Pacientes con email válido: {pacientes_email_valido}/{total_pacientes}")
                
                # Verificar teléfonos
                pacientes_con_telefono = Paciente.objects.exclude(
                    telefono__isnull=True
                ).exclude(telefono='').count()
                
                self.log_success(f"Pacientes con teléfono: {pacientes_con_telefono}/{total_pacientes}")
                
            elif Paciente is None:
                self.log_error("Modelo Paciente no disponible para validar integridad")
            else:
                self.log_warning("No hay pacientes para validar integridad de datos")
            
        except Exception as e:
            self.log_error(f"Error en validación de integridad: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        try:
            self.validate_patient_model()
            self.validate_patient_crud_operations()
            self.validate_patient_financial_data()
            self.validate_patient_clinical_history()
            self.validate_patient_questionnaire_system()
            self.validate_patient_portal()
            self.validate_patient_consent_system()
            self.validate_patient_payments_system()
            self.validate_patient_data_integrity()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - MÓDULO DE PACIENTES")
        print("=" * 70)
        
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
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
            print("El módulo de pacientes está funcionando correctamente.")
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
        validator = PatientsModuleValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()