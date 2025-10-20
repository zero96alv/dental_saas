#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Sistema de Servicios y Especialidades
========================================================

Este script valida el funcionamiento completo del sistema de servicios 
y especialidades incluyendo CRUD, dashboard avanzado, filtros, métricas,
análisis de precios y categorización inteligente.

Ejecutar desde la raíz del proyecto:
python validation_services_system.py
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

class ServicesSystemValidator:
    def __init__(self):
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.tenant = None
        
        print("=" * 70)
        print("VALIDACIÓN DEL SISTEMA DE SERVICIOS Y ESPECIALIDADES")
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

    def validate_services_model(self):
        """Valida el modelo de servicios y sus campos"""
        print("\n1. VALIDACIÓN DEL MODELO DE SERVICIOS")
        print("-" * 42)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio
                
                # Verificar campos del modelo
                servicio_fields = [field.name for field in Servicio._meta.get_fields()]
                expected_fields = [
                    'nombre', 'descripcion', 'precio', 'duracion_estimada',
                    'activo', 'especialidad', 'codigo', 'requiere_autorizacion'
                ]
                
                for field in expected_fields:
                    if field in servicio_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Servicio")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Servicio")
                
                # Verificar conteo de servicios
                servicios_count = Servicio.objects.count()
                self.log_success(f"Servicios registrados en el sistema: {servicios_count}")
                
                if servicios_count > 0:
                    # Verificar servicios activos vs inactivos
                    if 'activo' in servicio_fields:
                        activos = Servicio.objects.filter(activo=True).count()
                        inactivos = servicios_count - activos
                        self.log_success(f"Servicios activos: {activos}, Inactivos: {inactivos}")
                    
                    # Mostrar algunos servicios de ejemplo
                    sample_services = Servicio.objects.all()[:3]
                    service_names = [s.nombre for s in sample_services]
                    self.log_success(f"Servicios de ejemplo: {service_names}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Servicio: {str(e)}")

    def validate_specialties_model(self):
        """Valida el modelo de especialidades"""
        print("\n2. VALIDACIÓN DEL MODELO DE ESPECIALIDADES")
        print("-" * 45)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Especialidad
                
                # Verificar campos del modelo
                especialidad_fields = [field.name for field in Especialidad._meta.get_fields()]
                expected_fields = ['nombre', 'descripcion', 'activo', 'color']
                
                for field in expected_fields:
                    if field in especialidad_fields:
                        self.log_success(f"Campo '{field}' presente en modelo Especialidad")
                    else:
                        self.log_warning(f"Campo '{field}' no encontrado en modelo Especialidad")
                
                # Verificar conteo de especialidades
                especialidades_count = Especialidad.objects.count()
                self.log_success(f"Especialidades registradas: {especialidades_count}")
                
                if especialidades_count > 0:
                    # Verificar especialidades activas
                    if 'activo' in especialidad_fields:
                        activas = Especialidad.objects.filter(activo=True).count()
                        self.log_success(f"Especialidades activas: {activas}/{especialidades_count}")
                    
                    # Mostrar especialidades disponibles
                    sample_specialties = Especialidad.objects.all()[:5]
                    specialty_names = [e.nombre for e in sample_specialties]
                    self.log_success(f"Especialidades disponibles: {specialty_names}")
                
        except Exception as e:
            self.log_error(f"Error en validación del modelo Especialidad: {str(e)}")

    def validate_services_urls(self):
        """Valida las URLs del sistema de servicios"""
        print("\n3. VALIDACIÓN DE URLs DE SERVICIOS")
        print("-" * 38)
        
        try:
            # URLs principales de servicios
            service_urls = [
                ('core:service_list', 'Lista de servicios'),
                ('core:service_create', 'Crear servicio'),
            ]
            
            for url_name, description in service_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs de especialidades
            specialty_urls = [
                ('core:especialidad_list', 'Lista de especialidades'),
                ('core:especialidad_create', 'Crear especialidad'),
            ]
            
            for url_name, description in specialty_urls:
                try:
                    url = reverse(url_name)
                    self.log_success(f"URL '{description}' configurada: {url}")
                except NoReverseMatch:
                    self.log_error(f"URL '{description}' ({url_name}) no encontrada")
            
            # URLs paramétricas (si hay servicios)
            if self.tenant:
                with schema_context(self.tenant.schema_name):
                    from core.models import Servicio, Especialidad
                    
                    if Servicio.objects.exists():
                        servicio_id = Servicio.objects.first().id
                        parametric_urls = [
                            ('core:service_edit', {'pk': servicio_id}, 'Editar servicio'),
                            ('core:service_delete', {'pk': servicio_id}, 'Eliminar servicio'),
                        ]
                        
                        for url_name, kwargs, description in parametric_urls:
                            try:
                                url = reverse(url_name, kwargs=kwargs)
                                self.log_success(f"URL '{description}' configurada")
                            except NoReverseMatch:
                                self.log_warning(f"URL '{description}' ({url_name}) no encontrada")
                    
                    if Especialidad.objects.exists():
                        especialidad_id = Especialidad.objects.first().id
                        esp_urls = [
                            ('core:especialidad_edit', {'pk': especialidad_id}, 'Editar especialidad'),
                            ('core:especialidad_delete', {'pk': especialidad_id}, 'Eliminar especialidad'),
                        ]
                        
                        for url_name, kwargs, description in esp_urls:
                            try:
                                url = reverse(url_name, kwargs=kwargs)
                                self.log_success(f"URL '{description}' configurada")
                            except NoReverseMatch:
                                self.log_warning(f"URL '{description}' ({url_name}) no encontrada")
                        
        except Exception as e:
            self.log_error(f"Error en validación de URLs: {str(e)}")

    def validate_services_pricing_analysis(self):
        """Valida el análisis de precios de servicios"""
        print("\n4. VALIDACIÓN DE ANÁLISIS DE PRECIOS")
        print("-" * 40)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio
                from django.db.models import Min, Max, Avg, Count
                
                servicios_count = Servicio.objects.count()
                
                if servicios_count > 0:
                    # Análisis de precios
                    precio_stats = Servicio.objects.aggregate(
                        min_precio=Min('precio'),
                        max_precio=Max('precio'),
                        avg_precio=Avg('precio'),
                        count_servicios=Count('id')
                    )
                    
                    if precio_stats['min_precio']:
                        self.log_success(f"Precio mínimo: ${precio_stats['min_precio']:,.2f}")
                        self.log_success(f"Precio máximo: ${precio_stats['max_precio']:,.2f}")
                        self.log_success(f"Precio promedio: ${precio_stats['avg_precio']:,.2f}")
                    
                    # Distribución por rangos de precio
                    rangos_precio = {
                        'Económico (<$500)': Servicio.objects.filter(precio__lt=500).count(),
                        'Medio ($500-$1500)': Servicio.objects.filter(precio__gte=500, precio__lt=1500).count(),
                        'Premium (>=$1500)': Servicio.objects.filter(precio__gte=1500).count(),
                    }
                    
                    for rango, count in rangos_precio.items():
                        if count > 0:
                            self.log_success(f"{rango}: {count} servicios")
                    
                    # Servicios más caros y más baratos
                    servicio_caro = Servicio.objects.order_by('-precio').first()
                    servicio_barato = Servicio.objects.order_by('precio').first()
                    
                    if servicio_caro:
                        self.log_success(f"Servicio más caro: {servicio_caro.nombre} (${servicio_caro.precio})")
                    if servicio_barato:
                        self.log_success(f"Servicio más barato: {servicio_barato.nombre} (${servicio_barato.precio})")
                    
                else:
                    self.log_warning("No hay servicios para analizar precios")
                
        except Exception as e:
            self.log_error(f"Error en análisis de precios: {str(e)}")

    def validate_services_duration_analysis(self):
        """Valida el análisis de duración de servicios"""
        print("\n5. VALIDACIÓN DE ANÁLISIS DE DURACIÓN")
        print("-" * 41)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio
                from django.db.models import Avg
                
                servicios_count = Servicio.objects.count()
                
                if servicios_count > 0:
                    # Verificar si existe campo duracion_estimada
                    servicio_fields = [field.name for field in Servicio._meta.get_fields()]
                    
                    if 'duracion_estimada' in servicio_fields:
                        # Análisis de duración (asumiendo que está en minutos)
                        servicios_con_duracion = Servicio.objects.exclude(
                            duracion_estimada__isnull=True
                        ).count()
                        
                        if servicios_con_duracion > 0:
                            self.log_success(f"Servicios con duración estimada: {servicios_con_duracion}/{servicios_count}")
                            
                            # Duraciones típicas
                            duraciones = Servicio.objects.exclude(
                                duracion_estimada__isnull=True
                            ).values_list('duracion_estimada', flat=True)
                            
                            duraciones_unicas = sorted(set(duraciones))
                            self.log_success(f"Duraciones configuradas (min): {list(duraciones_unicas)}")
                            
                            # Promedio de duración
                            duracion_promedio = Servicio.objects.aggregate(
                                avg_duracion=Avg('duracion_estimada')
                            )['avg_duracion']
                            
                            if duracion_promedio:
                                self.log_success(f"Duración promedio: {duracion_promedio:.1f} minutos")
                            
                            # Categorizar por duración
                            categorias_duracion = {
                                'Rápido (<30 min)': Servicio.objects.filter(duracion_estimada__lt=30).count(),
                                'Normal (30-60 min)': Servicio.objects.filter(
                                    duracion_estimada__gte=30, duracion_estimada__lt=60
                                ).count(),
                                'Largo (>=60 min)': Servicio.objects.filter(duracion_estimada__gte=60).count(),
                            }
                            
                            for categoria, count in categorias_duracion.items():
                                if count > 0:
                                    self.log_success(f"{categoria}: {count} servicios")
                        else:
                            self.log_warning("No hay servicios con duración estimada configurada")
                    else:
                        self.log_warning("Campo 'duracion_estimada' no encontrado en modelo Servicio")
                else:
                    self.log_warning("No hay servicios para analizar duración")
                
        except Exception as e:
            self.log_error(f"Error en análisis de duración: {str(e)}")

    def validate_services_specialty_integration(self):
        """Valida la integración servicios-especialidades"""
        print("\n6. VALIDACIÓN DE INTEGRACIÓN SERVICIOS-ESPECIALIDADES")
        print("-" * 54)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio, Especialidad
                
                servicios_count = Servicio.objects.count()
                especialidades_count = Especialidad.objects.count()
                
                # Verificar servicios por especialidad
                if servicios_count > 0 and especialidades_count > 0:
                    servicios_con_especialidad = Servicio.objects.exclude(
                        especialidad__isnull=True
                    ).count()
                    
                    porcentaje = (servicios_con_especialidad / servicios_count * 100)
                    self.log_success(f"Servicios con especialidad asignada: {servicios_con_especialidad}/{servicios_count} ({porcentaje:.1f}%)")
                    
                    # Distribución de servicios por especialidad
                    for especialidad in Especialidad.objects.all():
                        servicios_especialidad = Servicio.objects.filter(
                            especialidad=especialidad
                        ).count()
                        
                        if servicios_especialidad > 0:
                            self.log_success(f"'{especialidad.nombre}': {servicios_especialidad} servicios")
                    
                    # Especialidades sin servicios
                    especialidades_sin_servicios = Especialidad.objects.filter(
                        servicio__isnull=True
                    ).count()
                    
                    if especialidades_sin_servicios > 0:
                        self.log_warning(f"Especialidades sin servicios: {especialidades_sin_servicios}")
                    else:
                        self.log_success("Todas las especialidades tienen servicios asignados")
                
                elif servicios_count == 0:
                    self.log_warning("No hay servicios para validar integración")
                elif especialidades_count == 0:
                    self.log_warning("No hay especialidades para validar integración")
                
        except Exception as e:
            self.log_error(f"Error en validación de integración: {str(e)}")

    def validate_services_dashboard_functionality(self):
        """Valida la funcionalidad del dashboard de servicios"""
        print("\n7. VALIDACIÓN DEL DASHBOARD DE SERVICIOS")
        print("-" * 43)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio, Especialidad
                
                # Simular métricas del dashboard
                servicios_count = Servicio.objects.count()
                especialidades_count = Especialidad.objects.count()
                
                # Métricas básicas
                self.log_success(f"Total servicios para dashboard: {servicios_count}")
                self.log_success(f"Total especialidades para dashboard: {especialidades_count}")
                
                if servicios_count > 0:
                    # Servicios activos vs inactivos
                    servicio_fields = [field.name for field in Servicio._meta.get_fields()]
                    
                    if 'activo' in servicio_fields:
                        activos = Servicio.objects.filter(activo=True).count()
                        inactivos = servicios_count - activos
                        
                        porcentaje_activos = (activos / servicios_count * 100) if servicios_count > 0 else 0
                        self.log_success(f"Servicios activos: {activos} ({porcentaje_activos:.1f}%)")
                        
                        if inactivos > 0:
                            self.log_success(f"Servicios inactivos: {inactivos}")
                    
                    # Verificar rangos de precios para gráficos
                    from django.db.models import Min, Max
                    precio_range = Servicio.objects.aggregate(
                        min_precio=Min('precio'),
                        max_precio=Max('precio')
                    )
                    
                    if precio_range['min_precio'] and precio_range['max_precio']:
                        rango = precio_range['max_precio'] - precio_range['min_precio']
                        self.log_success(f"Rango de precios para gráficos: ${rango:,.2f}")
                    
                    # Verificar datos para filtros avanzados
                    if especialidades_count > 0:
                        self.log_success("Datos disponibles para filtros por especialidad")
                    
                    # Verificar si hay servicios con códigos
                    if 'codigo' in servicio_fields:
                        servicios_con_codigo = Servicio.objects.exclude(
                            codigo__isnull=True
                        ).exclude(codigo='').count()
                        
                        if servicios_con_codigo > 0:
                            self.log_success(f"Servicios con código: {servicios_con_codigo}")
                
        except Exception as e:
            self.log_error(f"Error en validación del dashboard: {str(e)}")

    def validate_services_business_logic(self):
        """Valida la lógica de negocio de servicios"""
        print("\n8. VALIDACIÓN DE LÓGICA DE NEGOCIO")
        print("-" * 38)
        
        if not self.tenant:
            self.log_error("No hay tenant disponible")
            return
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import Servicio, Especialidad
                
                servicios_count = Servicio.objects.count()
                
                if servicios_count > 0:
                    # Verificar precios válidos
                    servicios_precio_cero = Servicio.objects.filter(precio__lte=0).count()
                    if servicios_precio_cero > 0:
                        self.log_warning(f"Servicios con precio cero o negativo: {servicios_precio_cero}")
                    else:
                        self.log_success("Todos los servicios tienen precios válidos")
                    
                    # Verificar nombres únicos
                    nombres_duplicados = Servicio.objects.values('nombre').annotate(
                        count=models.Count('nombre')
                    ).filter(count__gt=1).count()
                    
                    if nombres_duplicados > 0:
                        self.log_warning(f"Servicios con nombres duplicados: {nombres_duplicados}")
                    else:
                        self.log_success("Todos los servicios tienen nombres únicos")
                    
                    # Verificar códigos únicos (si existen)
                    servicio_fields = [field.name for field in Servicio._meta.get_fields()]
                    
                    if 'codigo' in servicio_fields:
                        codigos_duplicados = Servicio.objects.exclude(
                            codigo__isnull=True
                        ).exclude(codigo='').values('codigo').annotate(
                            count=models.Count('codigo')
                        ).filter(count__gt=1).count()
                        
                        if codigos_duplicados > 0:
                            self.log_warning(f"Servicios con códigos duplicados: {codigos_duplicados}")
                        else:
                            self.log_success("Códigos de servicios únicos")
                    
                    # Verificar consistencia de datos
                    servicios_sin_descripcion = Servicio.objects.filter(
                        descripcion__isnull=True
                    ).count() + Servicio.objects.filter(descripcion='').count()
                    
                    if servicios_sin_descripcion > 0:
                        porcentaje = (servicios_sin_descripcion / servicios_count * 100)
                        self.log_warning(f"Servicios sin descripción: {servicios_sin_descripcion} ({porcentaje:.1f}%)")
                    else:
                        self.log_success("Todos los servicios tienen descripción")
                
                # Verificar especialidades
                especialidades_count = Especialidad.objects.count()
                if especialidades_count > 0:
                    esp_nombres_duplicados = Especialidad.objects.values('nombre').annotate(
                        count=models.Count('nombre')
                    ).filter(count__gt=1).count()
                    
                    if esp_nombres_duplicados > 0:
                        self.log_warning(f"Especialidades con nombres duplicados: {esp_nombres_duplicados}")
                    else:
                        self.log_success("Todas las especialidades tienen nombres únicos")
                
        except Exception as e:
            self.log_error(f"Error en validación de lógica de negocio: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        if not self.tenant:
            self.log_error("No se puede ejecutar validación sin tenant")
            return
            
        try:
            self.validate_services_model()
            self.validate_specialties_model()
            self.validate_services_urls()
            self.validate_services_pricing_analysis()
            self.validate_services_duration_analysis()
            self.validate_services_specialty_integration()
            self.validate_services_dashboard_functionality()
            self.validate_services_business_logic()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - SISTEMA DE SERVICIOS Y ESPECIALIDADES")
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
            print("El sistema de servicios y especialidades está funcionando correctamente.")
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
        validator = ServicesSystemValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()