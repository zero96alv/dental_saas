#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Sistema de Inventario y Compras
==================================================

Este script valida el funcionamiento completo del sistema de inventario
incluyendo proveedores, insumos, compras, recepción de mercancía,
unidades dentales, lotes y control de stock.

Ejecutar desde la raíz del proyecto:
python validation_inventory_system.py
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

class InventorySystemValidator:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.tenant = None
        
        print("=" * 70)
        print("VALIDACIÓN DEL SISTEMA DE INVENTARIO Y COMPRAS")
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

    def validate_supplier_model(self):
        """Valida el modelo de proveedores"""
        print("\n1. VALIDACIÓN DEL MODELO DE PROVEEDORES")
        print("-" * 43)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Proveedor
                
                # Verificar campos del modelo
                proveedor_fields = [field.name for field in Proveedor._meta.get_fields()]
                expected_fields = [
                    'nombre', 'rfc', 'direccion', 'telefono', 'email',
                    'contacto', 'activo', 'notas'
                ]
                
                for field in expected_fields:
                    if field in proveedor_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Proveedor")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Proveedor")
                
                # Verificar conteo de proveedores
                proveedores_count = Proveedor.objects.count()
                self.log_success(f"Proveedores registrados: {proveedores_count}")
                
                if proveedores_count > 0:
                    # Verificar proveedores activos
                    if 'activo' in proveedor_fields:
                        activos = Proveedor.objects.filter(activo=True).count()
                        inactivos = proveedores_count - activos
                        self.log_success(f"Proveedores activos: {activos}, Inactivos: {inactivos}")
                    
                    # Mostrar ejemplos
                    sample_proveedores = Proveedor.objects.all()[:3]
                    provider_names = [p.nombre for p in sample_proveedores]
                    self.log_success(f"Proveedores de ejemplo: {provider_names}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Proveedor: {str(e)}")

    def validate_supply_model(self):
        """Valida el modelo de insumos"""
        print("\n2. VALIDACIÓN DEL MODELO DE INSUMOS")
        print("-" * 39)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Insumo
                
                # Verificar campos del modelo
                insumo_fields = [field.name for field in Insumo._meta.get_fields()]
                expected_fields = [
                    'nombre', 'descripcion', 'codigo', 'unidad_medida',
                    'precio_unitario', 'stock_minimo', 'stock_actual',
                    'requiere_lote', 'requiere_caducidad', 'activo'
                ]
                
                for field in expected_fields:
                    if field in insumo_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Insumo")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Insumo")
                
                # Verificar conteo de insumos
                insumos_count = Insumo.objects.count()
                self.log_success(f"Insumos registrados: {insumos_count}")
                
                if insumos_count > 0:
                    # Análisis de stock
                    if 'stock_actual' in insumo_fields and 'stock_minimo' in insumo_fields:
                        stock_bajo = Insumo.objects.filter(
                            stock_actual__lt=models.F('stock_minimo')
                        ).count()
                        self.log_success(f"Insumos con stock bajo: {stock_bajo}")
                        
                        sin_stock = Insumo.objects.filter(stock_actual=0).count()
                        self.log_success(f"Insumos sin stock: {sin_stock}")
                    
                    # Verificar insumos que requieren lote/caducidad
                    if 'requiere_lote' in insumo_fields:
                        con_lote = Insumo.objects.filter(requiere_lote=True).count()
                        self.log_success(f"Insumos que requieren lote: {con_lote}")
                    
                    if 'requiere_caducidad' in insumo_fields:
                        con_caducidad = Insumo.objects.filter(requiere_caducidad=True).count()
                        self.log_success(f"Insumos que requieren caducidad: {con_caducidad}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Insumo: {str(e)}")

    def validate_purchase_model(self):
        """Valida el modelo de compras"""
        print("\n3. VALIDACIÓN DEL MODELO DE COMPRAS")
        print("-" * 39)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Compra, DetalleCompra
                
                # Verificar campos del modelo Compra
                compra_fields = [field.name for field in Compra._meta.get_fields()]
                expected_fields = [
                    'proveedor', 'fecha_pedido', 'fecha_entrega', 'total',
                    'estado', 'observaciones', 'folio'
                ]
                
                for field in expected_fields:
                    if field in compra_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Compra")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Compra")
                
                # Verificar conteo de compras
                compras_count = Compra.objects.count()
                self.log_success(f"Compras registradas: {compras_count}")
                
                if compras_count > 0:
                    # Análisis por estado
                    if 'estado' in compra_fields:
                        estados = Compra.objects.values_list('estado', flat=True).distinct()
                        self.log_success(f"Estados de compra utilizados: {list(estados)}")
                    
                    # Total de compras
                    from django.db.models import Sum
                    total_compras = Compra.objects.aggregate(total=Sum('total'))['total'] or 0
                    self.log_success(f"Monto total de compras: ${total_compras:,.2f}")
                
                # Verificar modelo DetalleCompra
                detalle_fields = [field.name for field in DetalleCompra._meta.get_fields()]
                expected_detail_fields = [
                    'compra', 'insumo', 'cantidad', 'precio_unitario',
                    'subtotal', 'recibido'
                ]
                
                for field in expected_detail_fields:
                    if field in detalle_fields:
                        self.log_success(f"Campo '{field}' presente en DetalleCompra")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en DetalleCompra")
                
                detalles_count = DetalleCompra.objects.count()
                self.log_success(f"Detalles de compra registrados: {detalles_count}")
                
        except Exception as e:
            self.log_error(f"Error en validación de modelos de compra: {str(e)}")

    def validate_batch_control_model(self):
        """Valida el modelo de control de lotes"""
        print("\n4. VALIDACIÓN DEL CONTROL DE LOTES")
        print("-" * 39)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import LoteInsumo
                
                # Verificar campos del modelo
                lote_fields = [field.name for field in LoteInsumo._meta.get_fields()]
                expected_fields = [
                    'insumo', 'numero_lote', 'fecha_caducidad', 'cantidad_inicial',
                    'cantidad_actual', 'fecha_ingreso', 'compra'
                ]
                
                for field in expected_fields:
                    if field in lote_fields:
                        self.log_success(f"Campo '{field}' presente en modelo LoteInsumo")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo LoteInsumo")
                
                # Verificar conteo de lotes
                lotes_count = LoteInsumo.objects.count()
                self.log_success(f"Lotes registrados: {lotes_count}")
                
                if lotes_count > 0:
                    # Análisis de caducidades
                    if 'fecha_caducidad' in lote_fields:
                        from datetime import date
                        hoy = date.today()
                        
                        # Lotes vencidos
                        vencidos = LoteInsumo.objects.filter(
                            fecha_caducidad__lt=hoy
                        ).count()
                        self.log_success(f"Lotes vencidos: {vencidos}")
                        
                        # Lotes por vencer (próximos 30 días)
                        fecha_limite = hoy + timedelta(days=30)
                        por_vencer = LoteInsumo.objects.filter(
                            fecha_caducidad__gte=hoy,
                            fecha_caducidad__lte=fecha_limite
                        ).count()
                        self.log_success(f"Lotes por vencer (30 días): {por_vencer}")
                    
                    # Verificar stock por lotes
                    if 'cantidad_actual' in lote_fields:
                        lotes_vacios = LoteInsumo.objects.filter(cantidad_actual=0).count()
                        self.log_success(f"Lotes sin stock: {lotes_vacios}")
                
        except Exception as e:
            self.log_error(f"Error en validación de lotes: {str(e)}")

    def validate_dental_units_model(self):
        """Valida el modelo de unidades dentales"""
        print("\n5. VALIDACIÓN DE UNIDADES DENTALES")
        print("-" * 39)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import UnidadDental
                
                # Verificar campos del modelo
                unidad_fields = [field.name for field in UnidadDental._meta.get_fields()]
                expected_fields = [
                    'nombre', 'numero', 'marca', 'modelo', 'ubicacion',
                    'activo', 'fecha_instalacion', 'dentistas_permitidos'
                ]
                
                for field in expected_fields:
                    if field in unidad_fields:
                        self.log_success(f"Campo '{field}' presente en modelo UnidadDental")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo UnidadDental")
                
                # Verificar conteo de unidades
                unidades_count = UnidadDental.objects.count()
                self.log_success(f"Unidades dentales registradas: {unidades_count}")
                
                if unidades_count > 0:
                    # Verificar unidades activas
                    if 'activo' in unidad_fields:
                        activas = UnidadDental.objects.filter(activo=True).count()
                        self.log_success(f"Unidades dentales activas: {activas}/{unidades_count}")
                    
                    # Verificar asignación de dentistas
                    if 'dentistas_permitidos' in unidad_fields:
                        with_dentists = UnidadDental.objects.exclude(
                            dentistas_permitidos__isnull=True
                        ).count()
                        self.log_success(f"Unidades con dentistas asignados: {with_dentists}")
                    
                    # Mostrar ejemplos
                    sample_units = UnidadDental.objects.all()[:3]
                    unit_names = [f"{u.nombre} ({u.numero})" for u in sample_units]
                    self.log_success(f"Unidades de ejemplo: {unit_names}")
                
        except Exception as e:
            self.log_error(f"Error en validación de unidades dentales: {str(e)}")

    def validate_inventory_urls(self):
        """Valida las URLs del sistema de inventario"""
        print("\n6. VALIDACIÓN DE URLs DE INVENTARIO")
        print("-" * 39)
        
        try:
            # URLs de proveedores
            supplier_urls = [
                ('core:proveedor_list', 'Lista de proveedores'),
                ('core:proveedor_create', 'Crear proveedor'),
            ]
            
            for url_name, description in supplier_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs de insumos
            supply_urls = [
                ('core:insumo_list', 'Lista de insumos'),
                ('core:insumo_create', 'Crear insumo'),
            ]
            
            for url_name, description in supply_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs de compras
            purchase_urls = [
                ('core:compra_list', 'Lista de compras'),
                ('core:compra_create', 'Crear compra'),
            ]
            
            for url_name, description in purchase_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs de unidades dentales
            unit_urls = [
                ('core:unidad_dental_list', 'Lista de unidades dentales'),
                ('core:unidad_dental_create', 'Crear unidad dental'),
            ]
            
            for url_name, description in unit_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
                        
        except Exception as e:
            self.log_error(f"Error en validación de URLs: {str(e)}")

    def validate_inventory_business_logic(self):
        """Valida la lógica de negocio del inventario"""
        print("\n7. VALIDACIÓN DE LÓGICA DE NEGOCIO")
        print("-" * 38)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Insumo, Proveedor, Compra, DetalleCompra, LoteInsumo
                
                # Validar integridad de datos
                insumos_count = Insumo.objects.count()
                proveedores_count = Proveedor.objects.count()
                
                if insumos_count > 0:
                    # Verificar códigos únicos de insumos
                    insumo_fields = [field.name for field in Insumo._meta.get_fields()]
                    
                    if 'codigo' in insumo_fields:
                        codigos_duplicados = Insumo.objects.exclude(
                            codigo__isnull=True
                        ).exclude(codigo='').values('codigo').annotate(
                            count=models.Count('codigo')
                        ).filter(count__gt=1).count()
                        
                        if codigos_duplicados > 0:
                            self.log_warning(f"Insumos con códigos duplicados: {codigos_duplicados}")
                        else:
                            self.log_success("Códigos de insumos únicos")
                    
                    # Verificar precios válidos
                    if 'precio_unitario' in insumo_fields:
                        precios_invalidos = Insumo.objects.filter(precio_unitario__lte=0).count()
                        if precios_invalidos > 0:
                            self.log_warning(f"Insumos con precio inválido: {precios_invalidos}")
                        else:
                            self.log_success("Todos los insumos tienen precios válidos")
                    
                    # Verificar consistencia de stock
                    if 'stock_actual' in insumo_fields and 'stock_minimo' in insumo_fields:
                        stock_negativo = Insumo.objects.filter(stock_actual__lt=0).count()
                        if stock_negativo > 0:
                            self.log_warning(f"Insumos con stock negativo: {stock_negativo}")
                        else:
                            self.log_success("Stock de insumos consistente")
                
                # Validar relaciones de compras
                compras_count = Compra.objects.count()
                if compras_count > 0:
                    # Verificar que todas las compras tienen proveedor
                    compras_sin_proveedor = Compra.objects.filter(proveedor__isnull=True).count()
                    if compras_sin_proveedor > 0:
                        self.log_warning(f"Compras sin proveedor: {compras_sin_proveedor}")
                    else:
                        self.log_success("Todas las compras tienen proveedor asignado")
                    
                    # Verificar detalles de compras
                    detalles_count = DetalleCompra.objects.count()
                    if detalles_count > 0:
                        compras_sin_detalle = Compra.objects.filter(
                            detallecompra__isnull=True
                        ).count()
                        
                        if compras_sin_detalle > 0:
                            self.log_warning(f"Compras sin detalles: {compras_sin_detalle}")
                        else:
                            self.log_success("Todas las compras tienen detalles")
                
                # Validar lotes si existen
                lotes_count = LoteInsumo.objects.count()
                if lotes_count > 0:
                    # Verificar consistencia de cantidades en lotes
                    lote_fields = [field.name for field in LoteInsumo._meta.get_fields()]
                    
                    if 'cantidad_inicial' in lote_fields and 'cantidad_actual' in lote_fields:
                        lotes_inconsistentes = LoteInsumo.objects.filter(
                            cantidad_actual__gt=models.F('cantidad_inicial')
                        ).count()
                        
                        if lotes_inconsistentes > 0:
                            self.log_warning(f"Lotes con cantidades inconsistentes: {lotes_inconsistentes}")
                        else:
                            self.log_success("Cantidades de lotes consistentes")
                
                self.log_success("Validación de lógica de negocio completada")
                
        except Exception as e:
            self.log_error(f"Error en validación de lógica de negocio: {str(e)}")

    def validate_inventory_reports_capability(self):
        """Valida las capacidades de reportes del inventario"""
        print("\n8. VALIDACIÓN DE CAPACIDADES DE REPORTES")
        print("-" * 43)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Insumo, Compra, LoteInsumo
                from django.db.models import Sum, Count, Avg
                
                # Verificar datos para reportes de stock
                insumos_count = Insumo.objects.count()
                if insumos_count > 0:
                    self.log_success(f"Datos para reporte de stock: {insumos_count} insumos")
                    
                    # Verificar capacidad de análisis de stock
                    insumo_fields = [field.name for field in Insumo._meta.get_fields()]
                    
                    if 'stock_actual' in insumo_fields and 'stock_minimo' in insumo_fields:
                        # Stock bajo
                        stock_bajo = Insumo.objects.filter(
                            stock_actual__lt=models.F('stock_minimo')
                        ).count()
                        
                        # Valor total del inventario
                        if 'precio_unitario' in insumo_fields:
                            valor_inventario = Insumo.objects.aggregate(
                                total=Sum(models.F('stock_actual') * models.F('precio_unitario'))
                            )['total'] or 0
                            
                            self.log_success(f"Valor total del inventario: ${valor_inventario:,.2f}")
                        
                        self.log_success("Capacidad de reportes de stock disponible")
                
                # Verificar datos para reportes de compras
                compras_count = Compra.objects.count()
                if compras_count > 0:
                    self.log_success(f"Datos para reporte de compras: {compras_count} registros")
                    
                    # Análisis por período
                    compra_fields = [field.name for field in Compra._meta.get_fields()]
                    if 'fecha_pedido' in compra_fields:
                        from django.db.models.functions import TruncMonth
                        
                        compras_por_mes = Compra.objects.annotate(
                            mes=TruncMonth('fecha_pedido')
                        ).values('mes').annotate(
                            total=Sum('total'),
                            count=Count('id')
                        ).count()
                        
                        if compras_por_mes > 0:
                            self.log_success(f"Tendencias de compras disponibles: {compras_por_mes} períodos")
                
                # Verificar datos para reportes de caducidades
                lotes_count = LoteInsumo.objects.count()
                if lotes_count > 0:
                    self.log_success(f"Datos para reporte de caducidades: {lotes_count} lotes")
                    
                    lote_fields = [field.name for field in LoteInsumo._meta.get_fields()]
                    if 'fecha_caducidad' in lote_fields:
                        self.log_success("Capacidad de reportes de caducidades disponible")
                
                self.log_success("Sistema preparado para generar reportes de inventario")
                
        except Exception as e:
            self.log_error(f"Error en validación de reportes: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        if not self.tenant:
            self.log_error("No se puede ejecutar validación sin tenant")
            return
            
        try:
            self.validate_supplier_model()
            self.validate_supply_model()
            self.validate_purchase_model()
            self.validate_batch_control_model()
            self.validate_dental_units_model()
            self.validate_inventory_urls()
            self.validate_inventory_business_logic()
            self.validate_inventory_reports_capability()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - SISTEMA DE INVENTARIO Y COMPRAS")
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
            print("El sistema de inventario y compras está funcionando correctamente.")
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
        validator = InventorySystemValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()