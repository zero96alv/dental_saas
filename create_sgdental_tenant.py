#!/usr/bin/env python
"""
Script para crear tenant 'sgdental' completamente configurado
Incluye todas las funcionalidades implementadas y datos básicos necesarios
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User, Group
from django.db import transaction, connection
from tenants.models import Clinica, Domain
from core.models import (
    Diagnostico, CategoriaHistorial, PreguntaHistorial, 
    PerfilDentista, Especialidad, UnidadDental, Servicio,
    SatFormaPago, SatMetodoPago, SatRegimenFiscal,
    ModuloSistema
)

def crear_tenant_sgdental():
    """Crear el tenant sgdental con dominio"""
    print("1. Creando tenant 'sgdental'...")
    
    # Verificar si ya existe
    if Clinica.objects.filter(schema_name='sgdental').exists():
        print("❌ El tenant 'sgdental' ya existe")
        print("Usa http://sgdental.localhost:8000/ para acceder")
        return None
    
    # Crear nuevo tenant
    tenant = Clinica(
        schema_name='sgdental',
        nombre='SG Dental - Consultorio Integral',
        creado_en=datetime.now()
    )
    tenant.save()
    print(f"✓ Tenant creado: {tenant.nombre}")
    
    # Crear dominio
    domain = Domain(
        domain='sgdental.localhost',
        tenant=tenant,
        is_primary=True
    )
    domain.save()
    print(f"✓ Dominio creado: {domain.domain}")
    
    return tenant

def configurar_usuarios_basicos():
    """Crear usuarios administrador y superusuario en el tenant"""
    print("\n2. Configurando usuarios básicos...")
    
    # Crear grupos básicos
    grupos_basicos = [
        ('Administrador', 'Acceso completo al sistema'),
        ('Dentista', 'Dentistas y especialistas'),
        ('Recepcionista', 'Personal de recepción'),
        ('Asistente', 'Asistentes dentales'),
    ]
    
    for nombre_grupo, descripcion in grupos_basicos:
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        if created:
            print(f"✓ Grupo creado: {nombre_grupo}")
    
    # Crear superusuario
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@sgdental.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        admin_user.groups.add(Group.objects.get(name='Administrador'))
        print("✓ Superusuario 'admin' creado (password: admin123)")
    
    # Crear usuario administrador del consultorio
    if not User.objects.filter(username='sgdental_admin').exists():
        clinica_admin = User.objects.create_user(
            username='sgdental_admin',
            email='administrador@sgdental.com',
            password='sgdental2025',
            first_name='Administrador',
            last_name='SG Dental',
            is_staff=True
        )
        clinica_admin.groups.add(Group.objects.get(name='Administrador'))
        print("✓ Administrador 'sgdental_admin' creado (password: sgdental2025)")

def configurar_diagnosticos():
    """Crear diagnósticos dentales completos"""
    print("\n3. Configurando diagnósticos dentales...")
    
    diagnosticos_completos = [
        # Estados básicos
        {'nombre': 'Sano', 'color_hex': '#28a745'},
        {'nombre': 'Cariado', 'color_hex': '#dc3545'},
        {'nombre': 'Obturado', 'color_hex': '#007bff'},
        {'nombre': 'Corona', 'color_hex': '#fd7e14'},
        {'nombre': 'Ausente', 'color_hex': '#000000'},
        
        # Tratamientos especializados
        {'nombre': 'Endodoncia', 'color_hex': '#6f42c1'},
        {'nombre': 'Implante', 'color_hex': '#20c997'},
        {'nombre': 'Puente', 'color_hex': '#6610f2'},
        {'nombre': 'Prótesis Parcial', 'color_hex': '#e83e8c'},
        {'nombre': 'Prótesis Total', 'color_hex': '#fd7e14'},
        
        # Estados patológicos
        {'nombre': 'Fracturado', 'color_hex': '#dc3545'},
        {'nombre': 'Movilidad', 'color_hex': '#ffc107'},
        {'nombre': 'Extracción Indicada', 'color_hex': '#6c757d'},
        {'nombre': 'Sellador', 'color_hex': '#17a2b8'},
        
        # Ortodoncia
        {'nombre': 'Bracket', 'color_hex': '#007bff'},
        {'nombre': 'Banda Ortodóncica', 'color_hex': '#6610f2'},
    ]
    
    created_count = 0
    for diag_data in diagnosticos_completos:
        obj, created = Diagnostico.objects.get_or_create(
            nombre=diag_data['nombre'],
            defaults={'color_hex': diag_data['color_hex']}
        )
        if created:
            created_count += 1
            print(f"✓ Diagnóstico: {obj.nombre}")
    
    print(f"✓ {created_count} diagnósticos creados")

def configurar_categorias_historial():
    """Crear categorías de historial clínico"""
    print("\n4. Configurando categorías de historial clínico...")
    
    categorias_completas = [
        {
            'nombre': 'Anamnesis', 
            'descripcion': 'Historia clínica y antecedentes del paciente',
            'icono': 'bi bi-person-lines-fill',
            'color': '#6f42c1',
            'orden': 1
        },
        {
            'nombre': 'Exploración', 
            'descripcion': 'Examen físico y exploración clínica',
            'icono': 'bi bi-search',
            'color': '#198754',
            'orden': 2
        },
        {
            'nombre': 'Diagnósticos', 
            'descripcion': 'Diagnósticos y evaluaciones dentales',
            'icono': 'bi bi-clipboard-check',
            'color': '#dc3545',
            'orden': 3
        },
        {
            'nombre': 'Plan de Tratamiento', 
            'descripcion': 'Planificación y propuesta de tratamiento',
            'icono': 'bi bi-list-check',
            'color': '#0dcaf0',
            'orden': 4
        },
        {
            'nombre': 'Tratamientos', 
            'descripcion': 'Tratamientos realizados y procedimientos',
            'icono': 'bi bi-tools',
            'color': '#fd7e14',
            'orden': 5
        },
        {
            'nombre': 'Seguimiento', 
            'descripcion': 'Control post-tratamiento y seguimiento',
            'icono': 'bi bi-arrow-repeat',
            'color': '#20c997',
            'orden': 6
        },
        {
            'nombre': 'Emergencias', 
            'descripcion': 'Atención de urgencias y emergencias',
            'icono': 'bi bi-exclamation-triangle',
            'color': '#dc3545',
            'orden': 7
        },
    ]
    
    created_count = 0
    for cat_data in categorias_completas:
        obj, created = CategoriaHistorial.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={
                'descripcion': cat_data['descripcion'],
                'icono': cat_data['icono'],
                'color': cat_data['color'],
                'orden': cat_data['orden']
            }
        )
        if created:
            created_count += 1
            print(f"✓ Categoría: {obj.nombre}")
    
    print(f"✓ {created_count} categorías creadas")

def configurar_especialidades():
    """Crear especialidades dentales"""
    print("\n5. Configurando especialidades dentales...")
    
    especialidades = [
        'Odontología General',
        'Ortodoncia',
        'Endodoncia',
        'Periodoncia',
        'Cirugía Oral y Maxilofacial',
        'Odontopediatría',
        'Prostodoncia',
        'Implantología',
        'Estética Dental',
        'Patología Oral',
    ]
    
    created_count = 0
    for esp_nombre in especialidades:
        obj, created = Especialidad.objects.get_or_create(nombre=esp_nombre)
        if created:
            created_count += 1
            print(f"✓ Especialidad: {esp_nombre}")
    
    print(f"✓ {created_count} especialidades creadas")

def configurar_unidades_dentales():
    """Crear unidades dentales básicas"""
    print("\n6. Configurando unidades dentales...")
    
    unidades = [
        {
            'nombre': 'Unidad 1',
            'descripcion': 'Consultorio Principal'
        },
        {
            'nombre': 'Unidad 2', 
            'descripcion': 'Consultorio Secundario'
        },
        {
            'nombre': 'Unidad Cirugía',
            'descripcion': 'Sala de Cirugía'
        }
    ]
    
    created_count = 0
    for unidad_data in unidades:
        obj, created = UnidadDental.objects.get_or_create(
            nombre=unidad_data['nombre'],
            defaults={
                'descripcion': unidad_data['descripcion']
            }
        )
        if created:
            created_count += 1
            print(f"✓ Unidad dental: {obj.nombre}")
    
    print(f"✓ {created_count} unidades dentales creadas")

def configurar_servicios_basicos():
    """Crear servicios dentales básicos"""
    print("\n7. Configurando servicios dentales...")
    
    servicios_basicos = [
        # Preventivos
        {'nombre': 'Consulta General', 'precio': 500.00, 'duracion': 30, 'categoria': 'Preventivo'},
        {'nombre': 'Limpieza Dental', 'precio': 800.00, 'duracion': 45, 'categoria': 'Preventivo'},
        {'nombre': 'Aplicación de Flúor', 'precio': 300.00, 'duracion': 15, 'categoria': 'Preventivo'},
        
        # Restaurativos
        {'nombre': 'Obturación Resina', 'precio': 1200.00, 'duracion': 60, 'categoria': 'Restaurativo'},
        {'nombre': 'Obturación Amalgama', 'precio': 800.00, 'duracion': 45, 'categoria': 'Restaurativo'},
        {'nombre': 'Corona de Porcelana', 'precio': 8000.00, 'duracion': 90, 'categoria': 'Restaurativo'},
        
        # Endodoncia
        {'nombre': 'Endodoncia Unirradicular', 'precio': 3500.00, 'duracion': 120, 'categoria': 'Endodoncia'},
        {'nombre': 'Endodoncia Multirradicular', 'precio': 5500.00, 'duracion': 150, 'categoria': 'Endodoncia'},
        
        # Cirugía
        {'nombre': 'Extracción Simple', 'precio': 800.00, 'duracion': 30, 'categoria': 'Cirugía'},
        {'nombre': 'Extracción Compleja', 'precio': 2000.00, 'duracion': 60, 'categoria': 'Cirugía'},
        {'nombre': 'Implante Dental', 'precio': 15000.00, 'duracion': 120, 'categoria': 'Implantología'},
        
        # Ortodoncia
        {'nombre': 'Consulta Ortodóncica', 'precio': 800.00, 'duracion': 60, 'categoria': 'Ortodoncia'},
        {'nombre': 'Colocación de Brackets', 'precio': 25000.00, 'duracion': 180, 'categoria': 'Ortodoncia'},
        {'nombre': 'Ajuste Mensual', 'precio': 1200.00, 'duracion': 45, 'categoria': 'Ortodoncia'},
        
        # Estética
        {'nombre': 'Blanqueamiento Dental', 'precio': 3500.00, 'duracion': 90, 'categoria': 'Estética'},
        {'nombre': 'Carillas de Porcelana', 'precio': 8500.00, 'duracion': 120, 'categoria': 'Estética'},
    ]
    
    created_count = 0
    for servicio_data in servicios_basicos:
        obj, created = Servicio.objects.get_or_create(
            nombre=servicio_data['nombre'],
            defaults={
                'precio': servicio_data['precio'],
                'duracion_minutos': servicio_data['duracion'],
                'descripcion': f"Servicio de {servicio_data['categoria'].lower()}",
                'activo': True
            }
        )
        if created:
            created_count += 1
            print(f"✓ Servicio: {obj.nombre} - ${obj.precio}")
    
    print(f"✓ {created_count} servicios creados")

def configurar_datos_sat():
    """Configurar datos del SAT (México)"""
    print("\n8. Configurando datos del SAT...")
    
    # Formas de pago más comunes
    formas_pago = [
        {'clave': '01', 'descripcion': 'Efectivo'},
        {'clave': '02', 'descripcion': 'Cheque nominativo'},
        {'clave': '03', 'descripcion': 'Transferencia electrónica de fondos'},
        {'clave': '04', 'descripcion': 'Tarjeta de crédito'},
        {'clave': '28', 'descripcion': 'Tarjeta de débito'},
        {'clave': '99', 'descripcion': 'Por definir'},
    ]
    
    for forma in formas_pago:
        SatFormaPago.objects.get_or_create(
            codigo=forma['clave'],
            defaults={'descripcion': forma['descripcion']}
        )
    
    # Métodos de pago
    metodos_pago = [
        {'clave': 'PUE', 'descripcion': 'Pago en una sola exhibición'},
        {'clave': 'PPD', 'descripcion': 'Pago en parcialidades o diferido'},
    ]
    
    for metodo in metodos_pago:
        SatMetodoPago.objects.get_or_create(
            codigo=metodo['clave'],
            defaults={'descripcion': metodo['descripcion']}
        )
    
    # Regímenes fiscales comunes para dentistas
    regimenes = [
        {'clave': '612', 'descripcion': 'Personas Físicas con Actividades Empresariales y Profesionales'},
        {'clave': '601', 'descripcion': 'General de Ley Personas Morales'},
        {'clave': '605', 'descripcion': 'Sueldos y Salarios e Ingresos Asimilados a Salarios'},
    ]
    
    for regimen in regimenes:
        SatRegimenFiscal.objects.get_or_create(
            codigo=regimen['clave'],
            defaults={'descripcion': regimen['descripcion']}
        )
    
    print("✓ Datos SAT configurados")

def configurar_modulos_sistema():
    """Configurar módulos del sistema"""
    print("\n9. Configurando módulos del sistema...")
    
    modulos = [
        {'nombre': 'Gestión de Pacientes', 'activo': True, 'orden': 1},
        {'nombre': 'Agenda y Citas', 'activo': True, 'orden': 2},
        {'nombre': 'Historial Clínico', 'activo': True, 'orden': 3},
        {'nombre': 'Odontograma', 'activo': True, 'orden': 4},
        {'nombre': 'Tratamientos', 'activo': True, 'orden': 5},
        {'nombre': 'Facturación', 'activo': True, 'orden': 6},
        {'nombre': 'Inventarios', 'activo': True, 'orden': 7},
        {'nombre': 'Reportes', 'activo': True, 'orden': 8},
    ]
    
    created_count = 0
    for modulo_data in modulos:
        obj, created = ModuloSistema.objects.get_or_create(
            nombre=modulo_data['nombre'],
            defaults={
                'activo': modulo_data['activo'],
                'orden': modulo_data['orden']
            }
        )
        if created:
            created_count += 1
    
    print(f"✓ {created_count} módulos configurados")

def main():
    """Función principal"""
    print("=== CREACIÓN DE TENANT SGDENTAL ===")
    print("Este script creará un tenant completo para producción\n")
    
    try:
        # 1. Crear tenant y dominio
        tenant = crear_tenant_sgdental()
        if not tenant:
            return
        
        # Cambiar al esquema del nuevo tenant
        connection.set_tenant(tenant)
        
        with transaction.atomic():
            # 2. Configurar usuarios básicos
            configurar_usuarios_basicos()
            
            # 3. Configurar datos clínicos
            configurar_diagnosticos()
            configurar_categorias_historial()
            configurar_especialidades()
            configurar_unidades_dentales()
            configurar_servicios_basicos()
            
            # 4. Configurar datos fiscales/administrativos
            configurar_datos_sat()
            configurar_modulos_sistema()
        
        print("\n" + "="*50)
        print("✅ TENANT SGDENTAL CREADO EXITOSAMENTE")
        print("="*50)
        print(f"🌐 Dominio: http://sgdental.localhost:8000/")
        print(f"👤 Superusuario: admin / admin123")
        print(f"🏥 Administrador: sgdental_admin / sgdental2025")
        print(f"📊 {Diagnostico.objects.count()} diagnósticos configurados")
        print(f"📋 {CategoriaHistorial.objects.count()} categorías de historial")
        print(f"🏥 {UnidadDental.objects.count()} unidades dentales")
        print(f"⚕️ {Servicio.objects.count()} servicios dentales")
        print("\n🚀 ¡Listo para comenzar a operar!")
        
    except Exception as e:
        print(f"\n❌ Error al crear tenant: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()