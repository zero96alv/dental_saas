#!/usr/bin/env python3
"""
Script para crear datos de prueba completos para el reporte de facturación
Ejecutar desde el directorio raíz del proyecto con:
python manage.py shell < crear_datos_facturacion_prueba.py
"""

import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from core.models import *
from django.contrib.auth.models import User, Group

def crear_datos_facturacion():
    print("🔧 Creando datos de prueba para facturación...")
    
    # 1. Crear catálogos SAT si no existen
    print("📋 Creando catálogos SAT...")
    
    # Formas de pago SAT
    formas_pago = [
        ('01', 'Efectivo'),
        ('02', 'Cheque nominativo'),
        ('03', 'Transferencia electrónica de fondos'),
        ('04', 'Tarjeta de crédito'),
        ('28', 'Tarjeta de débito'),
        ('99', 'Por definir'),
    ]
    
    for codigo, descripcion in formas_pago:
        SatFormaPago.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': descripcion, 'activo': True}
        )
    
    # Métodos de pago SAT
    metodos_pago = [
        ('PUE', 'Pago en una sola exhibición'),
        ('PPD', 'Pago en parcialidades o diferido'),
    ]
    
    for codigo, descripcion in metodos_pago:
        SatMetodoPago.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': descripcion, 'activo': True}
        )
    
    # Regímenes fiscales SAT
    regimenes = [
        ('601', 'General de Ley Personas Morales', False, True),
        ('605', 'Sueldos y Salarios e Ingresos Asimilados a Salarios', True, False),
        ('606', 'Arrendamiento', True, True),
        ('612', 'Personas Físicas con Actividades Empresariales y Profesionales', True, False),
        ('621', 'Incorporación Fiscal', True, False),
        ('626', 'Régimen Simplificado de Confianza', True, False),
    ]
    
    for codigo, descripcion, pf, pm in regimenes:
        SatRegimenFiscal.objects.get_or_create(
            codigo=codigo,
            defaults={
                'descripcion': descripcion,
                'persona_fisica': pf,
                'persona_moral': pm,
                'activo': True
            }
        )
    
    # Usos CFDI
    usos_cfdi = [
        ('G01', 'Adquisición de mercancías', True, True),
        ('G02', 'Devoluciones, descuentos o bonificaciones', True, True),
        ('G03', 'Gastos en general', True, True),
        ('D10', 'Pagos por servicios de salud', True, False),
        ('P01', 'Por definir', True, True),
    ]
    
    for codigo, descripcion, pf, pm in usos_cfdi:
        SatUsoCFDI.objects.get_or_create(
            codigo=codigo,
            defaults={
                'descripcion': descripcion,
                'persona_fisica': pf,
                'persona_moral': pm,
                'activo': True
            }
        )
    
    # 2. Crear especialidades y servicios
    print("🦷 Creando especialidades y servicios...")
    
    especialidad_general, _ = Especialidad.objects.get_or_create(nombre='Odontología General')
    especialidad_ortodoncia, _ = Especialidad.objects.get_or_create(nombre='Ortodoncia')
    especialidad_endodoncia, _ = Especialidad.objects.get_or_create(nombre='Endodoncia')
    
    servicios_data = [
        ('Limpieza Dental', 'Limpieza y profilaxis dental', 800, especialidad_general),
        ('Consulta General', 'Consulta odontológica general', 500, especialidad_general),
        ('Ortodoncia Brackets Metálicos', 'Colocación de brackets metálicos', 15000, especialidad_ortodoncia),
        ('Endodoncia Molar', 'Tratamiento de conductos en molar', 3500, especialidad_endodoncia),
        ('Resina Dental', 'Restauración con resina compuesta', 1200, especialidad_general),
        ('Extracción Simple', 'Extracción dental simple', 900, especialidad_general),
    ]
    
    servicios = {}
    for nombre, desc, precio, esp in servicios_data:
        servicio, _ = Servicio.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': desc,
                'precio': Decimal(precio),
                'especialidad': esp,
                'activo': True,
                'duracion_minutos': 60
            }
        )
        servicios[nombre] = servicio
    
    # 3. Crear unidad dental
    print("🏥 Creando unidades dentales...")
    unidad, _ = UnidadDental.objects.get_or_create(
        nombre='Consultorio 1',
        defaults={'descripcion': 'Unidad dental principal'}
    )
    
    # 4. Crear dentista
    print("👨‍⚕️ Creando dentista...")
    user_dentista, created = User.objects.get_or_create(
        username='dr.martinez',
        defaults={
            'first_name': 'Carlos',
            'last_name': 'Martínez',
            'email': 'carlos.martinez@clinica.com',
            'is_active': True
        }
    )
    if created:
        user_dentista.set_password('password123')
        user_dentista.save()
    
    # Crear grupo dentista y asignar
    grupo_dentista, _ = Group.objects.get_or_create(name='Dentista')
    user_dentista.groups.add(grupo_dentista)
    
    perfil_dentista, _ = PerfilDentista.objects.get_or_create(
        usuario=user_dentista,
        defaults={
            'nombre': 'Carlos',
            'apellido': 'Martínez',
            'email': 'carlos.martinez@clinica.com',
            'activo': True
        }
    )
    perfil_dentista.especialidades.add(especialidad_general, especialidad_endodoncia)
    
    # 5. Crear pacientes con datos fiscales completos
    print("👥 Creando pacientes con datos fiscales...")
    
    pacientes_data = [
        {
            'nombre': 'María Elena',
            'apellido': 'González Pérez',
            'email': 'maria.gonzalez@email.com',
            'telefono': '55-1234-5678',
            'fecha_nacimiento': '1985-03-15',
            'datos_fiscales': {
                'rfc': 'GOPM850315AB1',
                'razon_social': 'María Elena González Pérez',
                'calle': 'Avenida Insurgentes Sur',
                'numero_exterior': '1234',
                'colonia': 'Del Valle',
                'municipio': 'Benito Juárez',
                'estado': 'Ciudad de México',
                'codigo_postal': '03100',
                'regimen_codigo': '612',
                'uso_cfdi_codigo': 'D10'
            }
        },
        {
            'nombre': 'Roberto',
            'apellido': 'Sánchez López',
            'email': 'roberto.sanchez@empresa.com',
            'telefono': '55-9876-5432',
            'fecha_nacimiento': '1978-08-22',
            'datos_fiscales': {
                'rfc': 'SALR780822CD2',
                'razon_social': 'Roberto Sánchez López',
                'calle': 'Calle Reforma',
                'numero_exterior': '567',
                'colonia': 'Centro',
                'municipio': 'Cuauhtémoc',
                'estado': 'Ciudad de México',
                'codigo_postal': '06000',
                'regimen_codigo': '605',
                'uso_cfdi_codigo': 'G03'
            }
        },
        {
            'nombre': 'Ana Patricia',
            'apellido': 'Rodríguez Morales',
            'email': 'ana.rodriguez@medico.com',
            'telefono': '55-5555-1111',
            'fecha_nacimiento': '1992-12-10',
            'datos_fiscales': {
                'rfc': 'ROMA921210EF3',
                'razon_social': 'Ana Patricia Rodríguez Morales',
                'calle': 'Paseo de la Reforma',
                'numero_exterior': '890',
                'numero_interior': 'Piso 5',
                'colonia': 'Juárez',
                'municipio': 'Cuauhtémoc',
                'estado': 'Ciudad de México',
                'codigo_postal': '06600',
                'regimen_codigo': '612',
                'uso_cfdi_codigo': 'D10'
            }
        },
        {
            'nombre': 'Constructora ABC',
            'apellido': 'S.A. de C.V.',
            'email': 'facturacion@constructoraabc.com',
            'telefono': '55-2222-3333',
            'fecha_nacimiento': '2000-01-01',  # Fecha simbólica para empresa
            'datos_fiscales': {
                'rfc': 'CAB000101ABC',
                'razon_social': 'Constructora ABC S.A. de C.V.',
                'calle': 'Boulevard Manuel Ávila Camacho',
                'numero_exterior': '1500',
                'colonia': 'Lomas de Chapultepec',
                'municipio': 'Miguel Hidalgo',
                'estado': 'Ciudad de México',
                'codigo_postal': '11000',
                'regimen_codigo': '601',
                'uso_cfdi_codigo': 'G01'
            }
        },
        {
            'nombre': 'Jorge Luis',
            'apellido': 'Hernández Vega',
            'email': 'jorge.hernandez@gmail.com',
            'telefono': '55-7777-8888',
            'fecha_nacimiento': '1965-04-30',
            'datos_fiscales': {
                'rfc': 'HEVJ650430GH4',
                'razon_social': 'Jorge Luis Hernández Vega',
                'calle': 'Avenida Universidad',
                'numero_exterior': '2100',
                'colonia': 'Copilco',
                'municipio': 'Coyoacán',
                'estado': 'Ciudad de México',
                'codigo_postal': '04360',
                'regimen_codigo': '626',
                'uso_cfdi_codigo': 'G03'
            }
        }
    ]
    
    pacientes = []
    for p_data in pacientes_data:
        # Crear paciente
        paciente, created = Paciente.objects.get_or_create(
            email=p_data['email'],
            defaults={
                'nombre': p_data['nombre'],
                'apellido': p_data['apellido'],
                'telefono': p_data['telefono'],
                'fecha_nacimiento': datetime.strptime(p_data['fecha_nacimiento'], '%Y-%m-%d').date(),
            }
        )
        
        if created:
            print(f"   ✅ Creado paciente: {paciente}")
        
        # Crear datos fiscales
        regimen = SatRegimenFiscal.objects.get(codigo=p_data['datos_fiscales']['regimen_codigo'])
        uso_cfdi = SatUsoCFDI.objects.get(codigo=p_data['datos_fiscales']['uso_cfdi_codigo'])
        
        datos_fiscales, created = DatosFiscales.objects.get_or_create(
            paciente=paciente,
            defaults={
                'rfc': p_data['datos_fiscales']['rfc'],
                'razon_social': p_data['datos_fiscales']['razon_social'],
                'calle': p_data['datos_fiscales']['calle'],
                'numero_exterior': p_data['datos_fiscales']['numero_exterior'],
                'numero_interior': p_data['datos_fiscales'].get('numero_interior', ''),
                'colonia': p_data['datos_fiscales']['colonia'],
                'municipio': p_data['datos_fiscales']['municipio'],
                'estado': p_data['datos_fiscales']['estado'],
                'codigo_postal': p_data['datos_fiscales']['codigo_postal'],
                'regimen_fiscal': regimen,
                'uso_cfdi': uso_cfdi,
            }
        )
        
        if created:
            print(f"   ✅ Creados datos fiscales para: {paciente}")
        
        pacientes.append(paciente)
    
    # 6. Crear citas con servicios realizados y pagos
    print("📅 Creando citas con servicios y pagos...")
    
    # Fechas variadas para los filtros
    fechas_citas = [
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=20),
        datetime.now() - timedelta(days=15),
        datetime.now() - timedelta(days=10),
        datetime.now() - timedelta(days=5),
        datetime.now() - timedelta(days=2),
        datetime.now(),
    ]
    
    citas_data = [
        {
            'paciente': pacientes[0],  # María Elena
            'servicios': ['Limpieza Dental', 'Consulta General'],
            'forma_pago': 'Tarjeta de crédito',
            'metodo_sat_codigo': 'PUE',
            'fecha': fechas_citas[0]
        },
        {
            'paciente': pacientes[1],  # Roberto
            'servicios': ['Endodoncia Molar'],
            'forma_pago': 'Transferencia',
            'metodo_sat_codigo': 'PUE',
            'fecha': fechas_citas[1]
        },
        {
            'paciente': pacientes[2],  # Ana Patricia
            'servicios': ['Resina Dental', 'Consulta General'],
            'forma_pago': 'Efectivo',
            'metodo_sat_codigo': 'PUE',
            'fecha': fechas_citas[2]
        },
        {
            'paciente': pacientes[3],  # Constructora ABC
            'servicios': ['Ortodoncia Brackets Metálicos'],
            'forma_pago': 'Transferencia',
            'metodo_sat_codigo': 'PPD',
            'fecha': fechas_citas[3]
        },
        {
            'paciente': pacientes[4],  # Jorge Luis
            'servicios': ['Extracción Simple', 'Consulta General'],
            'forma_pago': 'Tarjeta de débito',
            'metodo_sat_codigo': 'PUE',
            'fecha': fechas_citas[4]
        },
        {
            'paciente': pacientes[0],  # María Elena (segunda cita)
            'servicios': ['Resina Dental'],
            'forma_pago': 'Efectivo',
            'metodo_sat_codigo': 'PUE',
            'fecha': fechas_citas[5]
        },
        {
            'paciente': pacientes[1],  # Roberto (segunda cita)
            'servicios': ['Limpieza Dental'],
            'forma_pago': 'Tarjeta de crédito',
            'metodo_sat_codigo': 'PUE',
            'fecha': fechas_citas[6]
        }
    ]
    
    for i, cita_data in enumerate(citas_data):
        # Crear cita
        cita = Cita.objects.create(
            paciente=cita_data['paciente'],
            dentista=perfil_dentista,
            unidad_dental=unidad,
            fecha_hora=cita_data['fecha'],
            motivo='Tratamiento dental programado',
            estado='COM',  # Completada para que aparezca en facturación
            requiere_factura=True  # Marcar para facturación
        )
        
        # Agregar servicios realizados
        total_servicios = 0
        for nombre_servicio in cita_data['servicios']:
            servicio = servicios[nombre_servicio]
            cita.servicios_realizados.add(servicio)
            total_servicios += servicio.precio
        
        print(f"   ✅ Creada cita #{cita.id} para {cita.paciente} - Servicios: {', '.join(cita_data['servicios'])}")
        
        # Crear pago con mapeo SAT
        forma_pago_sat = None
        if cita_data['forma_pago'] == 'Efectivo':
            forma_pago_sat = SatFormaPago.objects.get(codigo='01')
        elif cita_data['forma_pago'] == 'Tarjeta de crédito':
            forma_pago_sat = SatFormaPago.objects.get(codigo='04')
        elif cita_data['forma_pago'] == 'Tarjeta de débito':
            forma_pago_sat = SatFormaPago.objects.get(codigo='28')
        elif cita_data['forma_pago'] == 'Transferencia':
            forma_pago_sat = SatFormaPago.objects.get(codigo='03')
        
        metodo_sat = SatMetodoPago.objects.get(codigo=cita_data['metodo_sat_codigo'])
        
        pago = Pago.objects.create(
            paciente=cita_data['paciente'],
            cita=cita,
            monto=total_servicios,
            metodo_pago=cita_data['forma_pago'],
            forma_pago_sat=forma_pago_sat,
            metodo_sat=metodo_sat,
            fecha_pago=cita_data['fecha'] + timedelta(minutes=30)  # 30 min después de la cita
        )
        
        print(f"   ✅ Creado pago de ${pago.monto} - {pago.metodo_pago} (SAT: {forma_pago_sat.codigo}/{metodo_sat.codigo})")
        
        # Actualizar saldo global del paciente
        cita_data['paciente'].actualizar_saldo_global()
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   • {len(pacientes)} pacientes con datos fiscales completos")
    print(f"   • {len(citas_data)} citas completadas listas para facturación")
    print(f"   • {Pago.objects.count()} pagos con mapeo SAT correcto")
    print(f"   • Catálogos SAT: {SatFormaPago.objects.count()} formas de pago, {SatMetodoPago.objects.count()} métodos")
    
    print("\n🔗 URLs para probar:")
    print("   📋 Reporte de Facturación: http://dev.localhost:8000/reportes/facturacion/")
    print("   📥 Exportar Excel: http://dev.localhost:8000/reportes/facturacion/export/")

if __name__ == "__main__":
    crear_datos_facturacion()
