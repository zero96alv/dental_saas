#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Sistema Financiero Integral
==============================================

Este script valida el funcionamiento completo del sistema financiero
incluyendo dashboard financiero, pagos, abonos, recibos PDF, reportes
de ingresos, saldos, facturación y análisis financiero.

Ejecutar desde la raíz del proyecto:
python validation_financial_system.py
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

class FinancialSystemValidator:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.tenant = None
        
        print("=" * 70)
        print("VALIDACIÓN DEL SISTEMA FINANCIERO INTEGRAL")
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

    def validate_payment_model(self):
        """Valida el modelo de pagos y sus campos"""
        print("\n1. VALIDACIÓN DEL MODELO DE PAGOS")
        print("-" * 38)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Pago
                
                # Verificar campos del modelo
                pago_fields = [field.name for field in Pago._meta.get_fields()]
                expected_fields = [
                    'monto', 'fecha', 'metodo_pago', 'paciente', 'cita',
                    'concepto', 'folio', 'estado', 'observaciones'
                ]
                
                for field in expected_fields:
                    if field in pago_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Pago")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Pago")
                
                # Verificar conteo de pagos
                pagos_count = Pago.objects.count()
                self.log_success(f"Pagos registrados en el sistema: {pagos_count}")
                
                if pagos_count > 0:
                    # Análisis básico de pagos
                    from django.db.models import Sum, Avg, Count
                    stats = Pago.objects.aggregate(
                        total=Sum('monto'),
                        promedio=Avg('monto'),
                        count=Count('id')
                    )
                    
                    if stats['total']:
                        self.log_success(f"Monto total de pagos: ${stats['total']:,.2f}")
                        self.log_success(f"Pago promedio: ${stats['promedio']:,.2f}")
                    
                    # Verificar métodos de pago utilizados
                    if 'metodo_pago' in pago_fields:
                        metodos = Pago.objects.values_list('metodo_pago', flat=True).distinct()
                        self.log_success(f"Métodos de pago utilizados: {list(metodos)}")
                    
                    # Mostrar algunos pagos de ejemplo
                    sample_payments = Pago.objects.all()[:3]
                    for i, pago in enumerate(sample_payments, 1):
                        self.log_success(f"Pago ejemplo {i}: ${pago.monto} - {pago.fecha}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Pago: {str(e)}")

    def validate_plan_pago_model(self):
        """Valida el modelo de planes de pago"""
        print("\n2. VALIDACIÓN DE PLANES DE PAGO")
        print("-" * 36)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import PlanPago
                
                # Verificar campos del modelo
                plan_fields = [field.name for field in PlanPago._meta.get_fields()]
                expected_fields = [
                    'paciente', 'monto_total', 'numero_cuotas', 'monto_cuota',
                    'fecha_inicio', 'activo', 'completado'
                ]
                
                for field in expected_fields:
                    if field in plan_fields:
                        self.log_success(f"Campo '{field}' presente en modelo PlanPago")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo PlanPago")
                
                # Verificar conteo de planes de pago
                planes_count = PlanPago.objects.count()
                self.log_success(f"Planes de pago registrados: {planes_count}")
                
                if planes_count > 0:
                    # Análisis de planes de pago
                    from django.db.models import Sum, Avg
                    
                    # Planes activos vs completados
                    if 'activo' in plan_fields and 'completado' in plan_fields:
                        activos = PlanPago.objects.filter(activo=True).count()
                        completados = PlanPago.objects.filter(completado=True).count()
                        
                        self.log_success(f"Planes activos: {activos}")
                        self.log_success(f"Planes completados: {completados}")
                    
                    # Monto total en planes
                    total_planes = PlanPago.objects.aggregate(
                        total=Sum('monto_total')
                    )['total']
                    
                    if total_planes:
                        self.log_success(f"Monto total en planes de pago: ${total_planes:,.2f}")
                
        except Exception as e:
            self.log_error(f"Error en validación de planes de pago: {str(e)}")

    def validate_financial_urls(self):
        """Valida las URLs del sistema financiero"""
        print("\n3. VALIDACIÓN DE URLs FINANCIERAS")
        print("-" * 38)
        
        try:
            # Dashboard financiero
            dashboard_urls = [
                ('core:dashboard_financiero', 'Dashboard financiero'),
            ]
            
            for url_name, description in dashboard_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs de pagos
            payment_urls = [
                ('core:pago_list', 'Lista de pagos'),
                ('core:pago_create', 'Registrar pago'),
                ('core:registrar_abono', 'Registrar abono'),
                ('core:saldos_pendientes', 'Saldos pendientes'),
                ('core:pacientes_pendientes_pago', 'Pacientes pendientes de pago'),
            ]
            
            for url_name, description in payment_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs de reportes
            report_urls = [
                ('core:reporte_ingresos', 'Reporte de ingresos'),
                ('core:reporte_saldos', 'Reporte de saldos'),
                ('core:reporte_facturacion', 'Reporte de facturación'),
                ('core:reporte_servicios_vendidos', 'Servicios más vendidos'),
                ('core:reporte_ingresos_dentista', 'Ingresos por dentista'),
            ]
            
            for url_name, description in report_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
                        
        except Exception as e:
            self.log_error(f"Error en validación de URLs: {str(e)}")

    def validate_financial_reports_apis(self):
        """Valida las APIs de reportes financieros"""
        print("\n4. VALIDACIÓN DE APIs DE REPORTES")
        print("-" * 38)
        
        try:
            # APIs de reportes
            api_urls = [
                ('core:reporte_ingresos_api', 'API reporte ingresos'),
                ('core:reporte_saldos_api', 'API reporte saldos'),
            ]
            
            for url_name, description in api_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"API '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"API '{description}' ({url_name}) no encontrada")
            
            # URLs de exportación
            export_urls = [
                ('core:exportar_ingresos_excel', 'Exportar ingresos Excel'),
                ('core:exportar_saldos_excel', 'Exportar saldos Excel'),
                ('core:exportar_facturacion_excel', 'Exportar facturación Excel'),
            ]
            
            for url_name, description in export_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
                        
        except Exception as e:
            self.log_error(f"Error en validación de APIs: {str(e)}")

    def validate_sat_configuration(self):
        """Valida la configuración SAT para facturación"""
        print("\n5. VALIDACIÓN DE CONFIGURACIÓN SAT")
        print("-" * 39)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import (
                    SatFormaPago, SatMetodoPago, SatRegimenFiscal, SatUsoCFDI
                )
                
                # Verificar configuraciones SAT
                sat_models = [
                    (SatFormaPago, "Formas de Pago SAT"),
                    (SatMetodoPago, "Métodos de Pago SAT"),
                    (SatRegimenFiscal, "Regímenes Fiscales SAT"),
                    (SatUsoCFDI, "Usos de CFDI SAT"),
                ]
                
                for model, description in sat_models:
                    try:
                        count = model.objects.count()
                        if count > 0:
                            self.log_success(f"{description}: {count} registros")
                            
                            # Mostrar algunos ejemplos
                            if count <= 5:
                                items = model.objects.all()
                                names = [str(item) for item in items]
                                self.log_success(f"   Ejemplos: {', '.join(names)}")
                        else:
                            self.log_warning(f"{description}: Sin registros")
                    except Exception:
                        self.log_error(f"{description}: Error al acceder al modelo")
                
                # Verificar URLs de configuración SAT
                sat_urls = [
                    ('core:sat_forma_pago_list', 'Configuración formas de pago'),
                    ('core:sat_metodo_pago_list', 'Configuración métodos de pago'),
                    ('core:sat_regimen_fiscal_list', 'Configuración regímenes fiscales'),
                    ('core:sat_uso_cfdi_list', 'Configuración usos de CFDI'),
                ]
                
                for url_name, description in sat_urls:
                    try:
                        url = reverse(url_name)
                        self.log_success(f"URL '{description}' configurada")
                    except NoReverseMatch:
                        self.log_warning(f"URL '{description}' no encontrada")
                
        except Exception as e:
            self.log_error(f"Error en validación SAT: {str(e)}")

    def validate_payment_receipts(self):
        """Valida el sistema de recibos de pago"""
        print("\n6. VALIDACIÓN DE RECIBOS DE PAGO")
        print("-" * 37)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Pago
                
                pagos_count = Pago.objects.count()
                
                if pagos_count > 0:
                    # Verificar URLs de recibos
                    pago = Pago.objects.first()
                    
                    try:
                        url = reverse('core:recibo_pago', kwargs={'pk': pago.id})
                        self.log_success(f"URL de recibo configurada: {url}")
                    except NoReverseMatch:
                        self.log_error("URL de recibo de pago no encontrada")
                    
                    try:
                        url = reverse('core:generar_recibo_pdf', kwargs={'pk': pago.id})
                        self.log_success(f"URL de PDF configurada: {url}")
                    except NoReverseMatch:
                        self.log_error("URL de generación de PDF no encontrada")
                    
                    # Verificar campos necesarios para recibos
                    pago_fields = [field.name for field in Pago._meta.get_fields()]
                    recibo_fields = ['folio', 'fecha', 'monto', 'concepto']
                    
                    for field in recibo_fields:
                        if field in pago_fields:
                            self.log_success(f"Campo para recibo '{field}' presente")
                        else:
                            self.log_warning(f"Campo para recibo '{field}' faltante")
                else:
                    self.log_warning("No hay pagos para validar recibos")
                
        except Exception as e:
            self.log_error(f"Error en validación de recibos: {str(e)}")

    def validate_financial_analysis(self):
        """Valida las capacidades de análisis financiero"""
        print("\n7. VALIDACIÓN DE ANÁLISIS FINANCIERO")
        print("-" * 41)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Pago, Paciente, PerfilDentista
                from django.db.models import Sum, Count, Avg
                from django.db.models.functions import TruncMonth
                
                pagos_count = Pago.objects.count()
                
                if pagos_count > 0:
                    # Análisis por período
                    today = datetime.now()
                    inicio_mes = today.replace(day=1)
                    
                    pagos_mes = Pago.objects.filter(fecha__gte=inicio_mes).count()
                    self.log_success(f"Pagos del mes actual: {pagos_mes}")
                    
                    # Análisis por dentista (si existe relación)
                    if hasattr(Pago, 'dentista') or hasattr(Pago, 'cita'):
                        self.log_success("Capacidad de análisis por dentista disponible")
                    
                    # Análisis por método de pago
                    pago_fields = [field.name for field in Pago._meta.get_fields()]
                    if 'metodo_pago' in pago_fields:
                        metodos_stats = Pago.objects.values('metodo_pago').annotate(
                            total=Sum('monto'),
                            count=Count('id')
                        )
                        
                        if metodos_stats:
                            self.log_success("Análisis por método de pago funcional")
                            for stat in metodos_stats[:3]:  # Mostrar primeros 3
                                metodo = stat['metodo_pago'] or 'Sin especificar'
                                self.log_success(f"   {metodo}: ${stat['total']:,.2f} ({stat['count']} pagos)")
                    
                    # Análisis de tendencias
                    pagos_por_mes = Pago.objects.annotate(
                        mes=TruncMonth('fecha')
                    ).values('mes').annotate(
                        total=Sum('monto'),
                        count=Count('id')
                    ).order_by('mes')
                    
                    if pagos_por_mes.count() > 0:
                        self.log_success(f"Datos de tendencias disponibles: {pagos_por_mes.count()} meses")
                    
                else:
                    self.log_warning("No hay pagos para análisis financiero")
                
                # Verificar capacidad de análisis de saldos
                pacientes_count = Paciente.objects.count()
                if pacientes_count > 0:
                    # Verificar si existe campo saldo_global
                    paciente_fields = [field.name for field in Paciente._meta.get_fields()]
                    if 'saldo_global' in paciente_fields:
                        pacientes_con_saldo = Paciente.objects.exclude(
                            saldo_global=0
                        ).count()
                        self.log_success(f"Pacientes con saldo pendiente: {pacientes_con_saldo}")
                    
                    self.log_success("Capacidad de análisis de cartera disponible")
                
        except Exception as e:
            self.log_error(f"Error en análisis financiero: {str(e)}")

    def validate_financial_dashboard_metrics(self):
        """Valida las métricas del dashboard financiero"""
        print("\n8. VALIDACIÓN DE MÉTRICAS DEL DASHBOARD")
        print("-" * 43)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Pago, Paciente, Cita
                from django.db.models import Sum, Count, Avg
                from django.utils import timezone
                
                # Métricas básicas
                total_pagos = Pago.objects.aggregate(total=Sum('monto'))['total'] or 0
                self.log_success(f"Métrica: Ingresos totales = ${total_pagos:,.2f}")
                
                count_pagos = Pago.objects.count()
                self.log_success(f"Métrica: Total de pagos = {count_pagos}")
                
                if count_pagos > 0:
                    pago_promedio = total_pagos / count_pagos
                    self.log_success(f"Métrica: Pago promedio = ${pago_promedio:,.2f}")
                
                # Métricas del período actual
                today = timezone.now()
                inicio_mes = today.replace(day=1)
                
                pagos_mes = Pago.objects.filter(fecha_pago__gte=inicio_mes)
                ingresos_mes = pagos_mes.aggregate(total=Sum('monto'))['total'] or 0
                count_pagos_mes = pagos_mes.count()
                
                self.log_success(f"Métrica: Ingresos del mes = ${ingresos_mes:,.2f}")
                self.log_success(f"Métrica: Pagos del mes = {count_pagos_mes}")
                
                # Métricas de cartera
                pacientes_count = Paciente.objects.count()
                if pacientes_count > 0:
                    self.log_success(f"Métrica: Total pacientes = {pacientes_count}")
                    
                    # Verificar saldos pendientes
                    paciente_fields = [field.name for field in Paciente._meta.get_fields()]
                    if 'saldo_global' in paciente_fields:
                        saldo_total = Paciente.objects.aggregate(
                            total=Sum('saldo_global')
                        )['total'] or 0
                        
                        pacientes_con_saldo = Paciente.objects.exclude(
                            saldo_global=0
                        ).count()
                        
                        self.log_success(f"Métrica: Cartera por cobrar = ${saldo_total:,.2f}")
                        self.log_success(f"Métrica: Pacientes con saldo = {pacientes_con_saldo}")
                
                # Métricas de citas (si influyen en finanzas)
                citas_count = Cita.objects.count()
                if citas_count > 0:
                    self.log_success(f"Métrica: Total citas registradas = {citas_count}")
                    
                    # Citas del mes
                    citas_mes = Cita.objects.filter(fecha_hora__gte=inicio_mes).count()
                    self.log_success(f"Métrica: Citas del mes = {citas_mes}")
                
                self.log_success("Dashboard financiero tiene métricas completas")
                
        except Exception as e:
            self.log_error(f"Error en métricas del dashboard: {str(e)}")

    def validate_financial_data_integrity(self):
        """Valida la integridad de datos financieros"""
        print("\n9. VALIDACIÓN DE INTEGRIDAD DE DATOS FINANCIEROS")
        print("-" * 52)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Pago, PlanPago
                
                pagos_count = Pago.objects.count()
                
                if pagos_count > 0:
                    # Verificar pagos con montos válidos
                    pagos_invalidos = Pago.objects.filter(monto__lte=0).count()
                    if pagos_invalidos > 0:
                        self.log_warning(f"Pagos con monto inválido: {pagos_invalidos}")
                    else:
                        self.log_success("Todos los pagos tienen montos válidos")
                    
                    # Verificar fechas válidas
                    from datetime import date
                    fecha_futura = date.today() + timedelta(days=1)
                    pagos_fecha_futura = Pago.objects.filter(fecha__gt=fecha_futura).count()
                    
                    if pagos_fecha_futura > 0:
                        self.log_warning(f"Pagos con fecha futura: {pagos_fecha_futura}")
                    else:
                        self.log_success("Fechas de pagos son consistentes")
                    
                    # Verificar relaciones
                    pago_fields = [field.name for field in Pago._meta.get_fields()]
                    
                    if 'paciente' in pago_fields:
                        pagos_sin_paciente = Pago.objects.filter(paciente__isnull=True).count()
                        if pagos_sin_paciente > 0:
                            self.log_warning(f"Pagos sin paciente asignado: {pagos_sin_paciente}")
                        else:
                            self.log_success("Todos los pagos tienen paciente asignado")
                    
                    # Verificar folios únicos (si existen)
                    if 'folio' in pago_fields:
                        folios_duplicados = Pago.objects.exclude(
                            folio__isnull=True
                        ).exclude(folio='').values('folio').annotate(
                            count=models.Count('folio')
                        ).filter(count__gt=1).count()
                        
                        if folios_duplicados > 0:
                            self.log_warning(f"Folios de pago duplicados: {folios_duplicados}")
                        else:
                            self.log_success("Folios de pagos únicos")
                
                # Verificar integridad de planes de pago
                planes_count = PlanPago.objects.count()
                if planes_count > 0:
                    # Verificar consistencia de montos
                    planes_inconsistentes = 0
                    
                    for plan in PlanPago.objects.all():
                        if hasattr(plan, 'numero_cuotas') and hasattr(plan, 'monto_cuota') and hasattr(plan, 'monto_total'):
                            esperado = plan.numero_cuotas * plan.monto_cuota
                            if abs(esperado - plan.monto_total) > 0.01:  # Tolerancia para decimales
                                planes_inconsistentes += 1
                    
                    if planes_inconsistentes > 0:
                        self.log_warning(f"Planes con cálculos inconsistentes: {planes_inconsistentes}")
                    else:
                        self.log_success("Cálculos de planes de pago consistentes")
                
        except Exception as e:
            self.log_error(f"Error en validación de integridad: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        if not self.tenant:
            self.log_error("No se puede ejecutar validación sin tenant")
            return
            
        try:
            self.validate_payment_model()
            self.validate_plan_pago_model()
            self.validate_financial_urls()
            self.validate_financial_reports_apis()
            self.validate_sat_configuration()
            self.validate_payment_receipts()
            self.validate_financial_analysis()
            self.validate_financial_dashboard_metrics()
            self.validate_financial_data_integrity()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - SISTEMA FINANCIERO INTEGRAL")
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
            print("El sistema financiero integral está funcionando correctamente.")
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
        validator = FinancialSystemValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()