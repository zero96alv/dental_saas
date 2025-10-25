#!/usr/bin/env python
"""
Script para crear tenant 'dev' completamente configurado
Incluye todas las funcionalidades + datos para desarrollo y testing
"""
import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal

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
    ModuloSistema, Paciente, Cita, TratamientoCita,
    Proveedor, TipoTrabajoLaboratorio, TrabajoLaboratorio
)

def crear_tenant_dev():
    """Crear el tenant dev con dominio"""
    print("1. Creando tenant 'dev'...")

    # Verificar si ya existe
    if Clinica.objects.filter(schema_name='dev').exists():
        print("⚠️  El tenant 'dev' ya existe")
        tenant = Clinica.objects.get(schema_name='dev')
        return tenant

    # Crear nuevo tenant
    tenant = Clinica(
        schema_name='dev',
        nombre='Clínica Desarrollo'
    )
    tenant.save()
    print(f"✓ Tenant creado: {tenant.nombre}")

    # Crear dominio
    domain = Domain(
        domain='dev.localhost',
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
    ]

    for nombre_grupo, descripcion in grupos_basicos:
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        if created:
            print(f"✓ Grupo creado: {nombre_grupo}")

    # Crear superusuario
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@dev.com',
            password='admin123',
            first_name='Admin',
            last_name='Dev'
        )
        admin_user.groups.add(Group.objects.get(name='Administrador'))
        print("✓ Superusuario 'admin' creado (password: admin123)")

    # Crear dentista
    if not User.objects.filter(username='dentista').exists():
        dentista_user = User.objects.create_user(
            username='dentista',
            email='dentista@dev.com',
            password='dentista123',
            first_name='Dr. Juan',
            last_name='Pérez',
            is_staff=True
        )
        dentista_user.groups.add(Group.objects.get(name='Dentista'))
        print("✓ Usuario 'dentista' creado (password: dentista123)")

    # Crear recepcionista
    if not User.objects.filter(username='recepcion').exists():
        recep_user = User.objects.create_user(
            username='recepcion',
            email='recepcion@dev.com',
            password='recepcion123',
            first_name='María',
            last_name='González',
            is_staff=True
        )
        recep_user.groups.add(Group.objects.get(name='Recepcionista'))
        print("✓ Usuario 'recepcion' creado (password: recepcion123)")

def configurar_diagnosticos():
    """Crear diagnósticos dentales completos"""
    print("\n3. Configurando diagnósticos dentales...")

    diagnosticos_completos = [
        {'nombre': 'Sano', 'color_hex': '#28a745'},
        {'nombre': 'Cariado', 'color_hex': '#dc3545'},
        {'nombre': 'Obturado', 'color_hex': '#007bff'},
        {'nombre': 'Corona', 'color_hex': '#fd7e14'},
        {'nombre': 'Ausente', 'color_hex': '#000000'},
        {'nombre': 'Endodoncia', 'color_hex': '#6f42c1'},
        {'nombre': 'Implante', 'color_hex': '#20c997'},
        {'nombre': 'Puente', 'color_hex': '#6610f2'},
        {'nombre': 'Fracturado', 'color_hex': '#dc3545'},
    ]

    created_count = 0
    for diag_data in diagnosticos_completos:
        obj, created = Diagnostico.objects.get_or_create(
            nombre=diag_data['nombre'],
            defaults={'color_hex': diag_data['color_hex']}
        )
        if created:
            created_count += 1

    print(f"✓ {created_count} diagnósticos creados")

def configurar_especialidades():
    """Crear especialidades dentales"""
    print("\n4. Configurando especialidades dentales...")

    especialidades = [
        'Odontología General',
        'Ortodoncia',
        'Endodoncia',
        'Prostodoncia',
        'Cirugía Oral',
        'Estética Dental',
    ]

    created_count = 0
    for esp_nombre in especialidades:
        obj, created = Especialidad.objects.get_or_create(nombre=esp_nombre)
        if created:
            created_count += 1

    print(f"✓ {created_count} especialidades creadas")

def configurar_unidades_dentales():
    """Crear unidades dentales básicas"""
    print("\n5. Configurando unidades dentales...")

    unidades = [
        {'nombre': 'Unidad 1', 'descripcion': 'Consultorio Principal'},
        {'nombre': 'Unidad 2', 'descripcion': 'Consultorio Secundario'},
    ]

    created_count = 0
    for unidad_data in unidades:
        obj, created = UnidadDental.objects.get_or_create(
            nombre=unidad_data['nombre'],
            defaults={'descripcion': unidad_data['descripcion']}
        )
        if created:
            created_count += 1

    print(f"✓ {created_count} unidades dentales creadas")

def configurar_servicios_basicos():
    """Crear servicios dentales básicos"""
    print("\n6. Configurando servicios dentales...")

    esp_general = Especialidad.objects.get(nombre='Odontología General')
    esp_endo = Especialidad.objects.get(nombre='Endodoncia')
    esp_cirugia = Especialidad.objects.get(nombre='Cirugía Oral')
    esp_prosto = Especialidad.objects.get(nombre='Prostodoncia')

    servicios_basicos = [
        {'nombre': 'Consulta General', 'precio': 500.00, 'duracion': 30, 'especialidad': esp_general},
        {'nombre': 'Limpieza Dental', 'precio': 800.00, 'duracion': 45, 'especialidad': esp_general},
        {'nombre': 'Obturación Resina', 'precio': 1200.00, 'duracion': 60, 'especialidad': esp_general},
        {'nombre': 'Endodoncia', 'precio': 3500.00, 'duracion': 120, 'especialidad': esp_endo},
        {'nombre': 'Extracción Simple', 'precio': 800.00, 'duracion': 30, 'especialidad': esp_cirugia},
        {'nombre': 'Corona de Porcelana', 'precio': 8000.00, 'duracion': 90, 'especialidad': esp_prosto},
        {'nombre': 'Corona de Zirconia', 'precio': 12000.00, 'duracion': 90, 'especialidad': esp_prosto},
    ]

    created_count = 0
    for servicio_data in servicios_basicos:
        obj, created = Servicio.objects.get_or_create(
            nombre=servicio_data['nombre'],
            defaults={
                'precio': servicio_data['precio'],
                'duracion_minutos': servicio_data['duracion'],
                'especialidad': servicio_data['especialidad'],
                'activo': True
            }
        )
        if created:
            created_count += 1

    print(f"✓ {created_count} servicios creados")

def configurar_datos_sat():
    """Configurar datos del SAT (México)"""
    print("\n7. Configurando datos del SAT...")

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
        {'clave': 'PUE', 'descripcion': 'Pago en una sola exhibición'},
        {'clave': 'PPD', 'descripcion': 'Pago en parcialidades'},
    ]

    for metodo in metodos_pago:
        SatMetodoPago.objects.get_or_create(
            codigo=metodo['clave'],
            defaults={'descripcion': metodo['descripcion']}
        )

    regimenes = [
        {'clave': '612', 'descripcion': 'Personas Físicas con Actividades Empresariales'},
    ]

    for regimen in regimenes:
        SatRegimenFiscal.objects.get_or_create(
            codigo=regimen['clave'],
            defaults={'descripcion': regimen['descripcion']}
        )

    print("✓ Datos SAT configurados")

def configurar_perfiles_dentista():
    """Crear perfiles de dentistas"""
    print("\n8. Configurando perfiles de dentistas...")

    dentista_user = User.objects.get(username='dentista')
    esp_general = Especialidad.objects.get(nombre='Odontología General')

    perfil, created = PerfilDentista.objects.get_or_create(
        usuario=dentista_user,
        defaults={
            'nombre': dentista_user.first_name,
            'apellido': dentista_user.last_name,
            'email': dentista_user.email,
            'telefono': '5551234567',
            'activo': True
        }
    )

    if created:
        perfil.especialidades.add(esp_general)
        print(f"✓ Perfil dentista creado: {perfil}")

def configurar_laboratorios():
    """Crear laboratorios/proveedores para trabajos dentales"""
    print("\n9. Configurando laboratorios dentales...")

    laboratorios = [
        {
            'nombre': 'Laboratorio Dental ProDent',
            'rfc': 'LDP950101XYZ',
            'nombre_contacto': 'Carlos Técnico',
            'telefono': '5559876543',
            'email': 'contacto@prodent.com.mx',
            'direccion_fiscal': 'Av. Dental 123, Col. Centro, CDMX'
        },
        {
            'nombre': 'Lab Express Dental',
            'rfc': 'LED880515ABC',
            'nombre_contacto': 'Ana Laboratorista',
            'telefono': '5558765432',
            'email': 'labexpress@dental.com',
            'direccion_fiscal': 'Calle Lab 456, Col. Dental, CDMX'
        }
    ]

    created_count = 0
    for lab_data in laboratorios:
        obj, created = Proveedor.objects.get_or_create(
            nombre=lab_data['nombre'],
            defaults=lab_data
        )
        if created:
            created_count += 1

    print(f"✓ {created_count} laboratorios creados")

def configurar_tipos_trabajo_laboratorio():
    """Crear catálogo de tipos de trabajo de laboratorio"""
    print("\n10. Configurando tipos de trabajo de laboratorio...")

    tipos_trabajo = [
        {'nombre': 'Corona de Porcelana', 'descripcion': 'Corona individual de porcelana', 'costo': 2000.00},
        {'nombre': 'Corona de Zirconia', 'descripcion': 'Corona de zirconia monolítica', 'costo': 3500.00},
        {'nombre': 'Puente Fijo', 'descripcion': 'Puente dental fijo', 'costo': 6000.00},
        {'nombre': 'Prótesis Parcial Removible', 'descripcion': 'Prótesis removible parcial', 'costo': 5000.00},
        {'nombre': 'Prótesis Total', 'descripcion': 'Dentadura completa', 'costo': 6000.00},
        {'nombre': 'Incrustación', 'descripcion': 'Inlay/Onlay de porcelana', 'costo': 1800.00},
        {'nombre': 'Carilla Dental', 'descripcion': 'Lámina estética de porcelana', 'costo': 3000.00},
        {'nombre': 'Guarda Oclusal', 'descripcion': 'Férula de descarga', 'costo': 1200.00},
        {'nombre': 'Provisional', 'descripcion': 'Corona temporal', 'costo': 500.00},
    ]

    created_count = 0
    for tipo_data in tipos_trabajo:
        obj, created = TipoTrabajoLaboratorio.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults={
                'descripcion': tipo_data['descripcion'],
                'costo_referencia': Decimal(str(tipo_data['costo'])),
                'activo': True
            }
        )
        if created:
            created_count += 1

    print(f"✓ {created_count} tipos de trabajo creados")

def crear_datos_prueba():
    """Crear datos de prueba: pacientes, citas y trabajos de laboratorio"""
    print("\n11. Creando datos de prueba...")

    # Crear paciente de prueba
    paciente, created = Paciente.objects.get_or_create(
        email='paciente.test@dev.com',
        defaults={
            'nombre': 'Juan',
            'apellido': 'Test',
            'telefono': '5551234567',
            'fecha_nacimiento': date(1985, 5, 15),
            'calle': 'Test 123',
            'colonia': 'Centro',
            'municipio': 'CDMX',
            'estado': 'CDMX',
            'codigo_postal': '01000'
        }
    )

    if created:
        print(f"✓ Paciente creado: {paciente}")

    # Crear cita de prueba
    dentista = PerfilDentista.objects.first()
    unidad = UnidadDental.objects.first()
    servicio_corona = Servicio.objects.get(nombre='Corona de Zirconia')

    cita, created = Cita.objects.get_or_create(
        paciente=paciente,
        dentista=dentista,
        defaults={
            'unidad_dental': unidad,
            'fecha_hora': datetime.now() - timedelta(days=7),
            'estado': 'COM',
            'motivo': 'Colocación de corona',
        }
    )

    if created:
        cita.servicios_planeados.add(servicio_corona)
        print(f"✓ Cita creada: {cita}")

    # Crear trabajo de laboratorio
    tipo_trabajo = TipoTrabajoLaboratorio.objects.get(nombre='Corona de Zirconia')
    laboratorio = Proveedor.objects.first()

    trabajo, created = TrabajoLaboratorio.objects.get_or_create(
        paciente=paciente,
        cita_origen=cita,
        tipo_trabajo=tipo_trabajo,
        defaults={
            'laboratorio': laboratorio,
            'dientes': '11',
            'material': 'Zirconia',
            'color': 'A2',
            'observaciones': 'Corona anterior estética',
            'fecha_entrega_estimada': date.today() + timedelta(days=7),
            'estado': 'EN_PROCESO',
            'costo_laboratorio': Decimal('3500.00'),
            'precio_paciente': Decimal('12000.00'),
            'dentista_solicitante': dentista,
        }
    )

    if created:
        print(f"✓ Trabajo de laboratorio creado: {trabajo}")

    print("✓ Datos de prueba creados")

def main():
    """Función principal"""
    print("=== CREACIÓN DE TENANT DEV ===")
    print("Este script creará un tenant completo para desarrollo\n")

    try:
        # 1. Crear tenant y dominio
        tenant = crear_tenant_dev()

        # Cambiar al esquema del nuevo tenant
        connection.set_tenant(tenant)

        with transaction.atomic():
            # 2. Configurar usuarios básicos
            configurar_usuarios_basicos()

            # 3. Configurar datos clínicos
            configurar_diagnosticos()
            configurar_especialidades()
            configurar_unidades_dentales()
            configurar_servicios_basicos()

            # 4. Configurar datos fiscales/administrativos
            configurar_datos_sat()

            # 5. Configurar perfiles de dentista
            configurar_perfiles_dentista()

            # 6. Configurar laboratorios
            configurar_laboratorios()
            configurar_tipos_trabajo_laboratorio()

            # 7. Crear datos de prueba
            crear_datos_prueba()

        # 8. Inicializar sistema de permisos
        print("\n12. Inicializando sistema de permisos...")
        from django.core.management import call_command
        call_command('init_permisos')
        print("✓ Sistema de permisos inicializado")

        print("\n" + "="*60)
        print("✅ TENANT DEV CREADO EXITOSAMENTE")
        print("="*60)
        print(f"🌐 URL: http://localhost:8000/dev/")
        print(f"👤 Admin: admin / admin123")
        print(f"👨‍⚕️  Dentista: dentista / dentista123")
        print(f"👩 Recepción: recepcion / recepcion123")
        print(f"\n📊 Estadísticas:")
        print(f"  • {Diagnostico.objects.count()} diagnósticos")
        print(f"  • {Especialidad.objects.count()} especialidades")
        print(f"  • {UnidadDental.objects.count()} unidades dentales")
        print(f"  • {Servicio.objects.count()} servicios")
        print(f"  • {Proveedor.objects.count()} laboratorios")
        print(f"  • {TipoTrabajoLaboratorio.objects.count()} tipos de trabajo")
        print(f"  • {Paciente.objects.count()} pacientes")
        print(f"  • {TrabajoLaboratorio.objects.count()} trabajos de laboratorio")
        print("\n🚀 ¡Listo para desarrollo!")

    except Exception as e:
        print(f"\n❌ Error al crear tenant: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
