#!/usr/bin/env python
"""
Script para configurar tenants iniciales en producción
Ejecutar después del deploy en Render
"""
import os
import sys
import django

# Configurar Django para producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings_production')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User, Group
from django.db import transaction, connection
from tenants.models import Clinica, Domain
from core.models import (
    Diagnostico, CategoriaHistorial, 
    Especialidad, UnidadDental, Servicio,
    SatFormaPago, SatMetodoPago, SatRegimenFiscal,
    ModuloSistema
)

def crear_tenant_demo():
    """Crear tenant de demostración"""
    print("1. Creando tenant 'demo'...")
    
    # Crear tenant demo si no existe
    if not Clinica.objects.filter(schema_name='demo').exists():
        tenant = Clinica(
            schema_name='demo',
            nombre='Demo Dental - Clínica de Pruebas'
        )
        tenant.save()
        
        # Crear dominio
        domain = Domain(
            domain='demo.dental-saas.onrender.com',
            tenant=tenant,
            is_primary=True
        )
        domain.save()
        print(f"✓ Tenant demo creado: {tenant.nombre}")
        return tenant
    else:
        tenant = Clinica.objects.get(schema_name='demo')
        print(f"- Tenant demo ya existe: {tenant.nombre}")
        return tenant

def configurar_datos_basicos(tenant_schema):
    """Configurar datos básicos para un tenant"""
    print(f"\n2. Configurando datos básicos para {tenant_schema}...")
    
    try:
        # Obtener tenant y cambiar al esquema
        tenant = Clinica.objects.get(schema_name=tenant_schema)
        connection.set_tenant(tenant)
        
        with transaction.atomic():
            # Crear grupos básicos
            grupos_basicos = ['Administrador', 'Dentista', 'Recepcionista', 'Asistente']
            for nombre_grupo in grupos_basicos:
                Group.objects.get_or_create(name=nombre_grupo)
            
            # Crear usuario admin para el tenant
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@demo.dental-saas.com',
                    password='DemoAdmin2025!',
                    first_name='Administrador',
                    last_name='Demo'
                )
                admin_user.groups.add(Group.objects.get(name='Administrador'))
                print("✓ Usuario admin creado para demo")
            
            # Diagnósticos básicos
            diagnosticos_basicos = [
                {'nombre': 'Sano', 'color_hex': '#28a745'},
                {'nombre': 'Cariado', 'color_hex': '#dc3545'},
                {'nombre': 'Obturado', 'color_hex': '#007bff'},
                {'nombre': 'Corona', 'color_hex': '#fd7e14'},
                {'nombre': 'Ausente', 'color_hex': '#000000'},
                {'nombre': 'Endodoncia', 'color_hex': '#6f42c1'},
            ]
            
            for diag_data in diagnosticos_basicos:
                Diagnostico.objects.get_or_create(
                    nombre=diag_data['nombre'],
                    defaults={'color_hex': diag_data['color_hex']}
                )
            
            # Categorías de historial
            categorias = [
                {
                    'nombre': 'General', 
                    'descripcion': 'Registros generales del historial clínico',
                    'icono': 'bi bi-clipboard-heart',
                    'color': '#0d6efd',
                    'orden': 1
                },
                {
                    'nombre': 'Tratamientos', 
                    'descripcion': 'Tratamientos realizados',
                    'icono': 'bi bi-tools',
                    'color': '#fd7e14',
                    'orden': 2
                },
            ]
            
            for cat_data in categorias:
                CategoriaHistorial.objects.get_or_create(
                    nombre=cat_data['nombre'],
                    defaults={
                        'descripcion': cat_data['descripcion'],
                        'icono': cat_data['icono'],
                        'color': cat_data['color'],
                        'orden': cat_data['orden']
                    }
                )
            
            # Especialidades básicas
            especialidades = ['Odontología General', 'Endodoncia', 'Ortodoncia']
            for esp_nombre in especialidades:
                Especialidad.objects.get_or_create(nombre=esp_nombre)
            
            # Unidades dentales básicas
            unidades = [
                {'nombre': 'Unidad 1', 'descripcion': 'Consultorio Principal'},
                {'nombre': 'Unidad 2', 'descripcion': 'Consultorio Secundario'},
            ]
            
            for unidad_data in unidades:
                UnidadDental.objects.get_or_create(
                    nombre=unidad_data['nombre'],
                    defaults={'descripcion': unidad_data['descripcion']}
                )
            
            # Servicios básicos
            esp_general = Especialidad.objects.get(nombre='Odontología General')
            servicios_basicos = [
                {'nombre': 'Consulta General', 'precio': 500.00, 'duracion': 30},
                {'nombre': 'Limpieza Dental', 'precio': 800.00, 'duracion': 45},
                {'nombre': 'Obturación Resina', 'precio': 1200.00, 'duracion': 60},
            ]
            
            for servicio_data in servicios_basicos:
                Servicio.objects.get_or_create(
                    nombre=servicio_data['nombre'],
                    defaults={
                        'precio': servicio_data['precio'],
                        'duracion_minutos': servicio_data['duracion'],
                        'descripcion': f"Servicio básico",
                        'especialidad': esp_general,
                        'activo': True
                    }
                )
            
            # Datos SAT básicos
            formas_pago = [
                {'clave': '01', 'descripcion': 'Efectivo'},
                {'clave': '03', 'descripcion': 'Transferencia electrónica'},
                {'clave': '04', 'descripcion': 'Tarjeta de crédito'},
            ]
            
            for forma in formas_pago:
                SatFormaPago.objects.get_or_create(
                    codigo=forma['clave'],
                    defaults={'descripcion': forma['descripcion']}
                )
            
            metodos_pago = [
                {'clave': 'PUE', 'descripcion': 'Pago en una exhibición'},
            ]
            
            for metodo in metodos_pago:
                SatMetodoPago.objects.get_or_create(
                    codigo=metodo['clave'],
                    defaults={'descripcion': metodo['descripcion']}
                )
            
            print(f"✓ Datos básicos configurados para {tenant_schema}")
            
    except Exception as e:
        print(f"❌ Error configurando {tenant_schema}: {e}")
        raise

def main():
    """Función principal"""
    print("=== CONFIGURACIÓN DE TENANTS EN PRODUCCIÓN ===\n")
    
    try:
        # Crear y configurar tenant demo
        tenant_demo = crear_tenant_demo()
        configurar_datos_basicos('demo')
        
        print("\n" + "="*50)
        print("✅ TENANTS CONFIGURADOS EXITOSAMENTE")
        print("="*50)
        print("🌐 URLs disponibles:")
        print("  - Principal: https://dental-saas.onrender.com/")
        print("  - Demo: https://demo.dental-saas.onrender.com/")
        print("\n🔐 Credenciales:")
        print("  - Admin principal: admin / DentalSaaS2025!")
        print("  - Admin demo: admin / DemoAdmin2025!")
        print("\n🚀 Sistema listo para usar!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()