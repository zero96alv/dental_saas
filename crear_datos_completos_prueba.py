#!/usr/bin/env python
"""
Script para crear datos de prueba completos para el sistema dental SaaS
Incluye todos los datos necesarios para probar el flujo completo de citas
"""

import os
import sys
import django
from datetime import date, time, datetime, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.models import *

def crear_grupos():
    """Crear los grupos de usuarios necesarios"""
    grupos = ['Administrador', 'Dentista', 'Recepcionista', 'Paciente']
    for nombre in grupos:
        grupo, created = Group.objects.get_or_create(name=nombre)
        if created:
            print(f"✅ Grupo creado: {nombre}")
        else:
            print(f"ℹ️ Grupo ya existe: {nombre}")

def crear_catalogos_sat():
    """Crear catálogos SAT básicos"""
    # Formas de pago
    formas_pago = [
        ('01', 'Efectivo'),
        ('02', 'Cheque nominativo'),
        ('03', 'Transferencia electrónica de fondos'),
        ('04', 'Tarjeta de crédito'),
        ('28', 'Tarjeta de débito'),
    ]
    
    for codigo, desc in formas_pago:
        obj, created = SatFormaPago.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': desc, 'activo': True}
        )
        if created:
            print(f"✅ Forma de pago SAT: {codigo} - {desc}")

    # Métodos de pago
    metodos_pago = [
        ('PUE', 'Pago en una sola exhibición'),
        ('PPD', 'Pago en parcialidades o diferido'),
    ]
    
    for codigo, desc in metodos_pago:
        obj, created = SatMetodoPago.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': desc, 'activo': True}
        )
        if created:
            print(f"✅ Método de pago SAT: {codigo} - {desc}")

    # Regímenes fiscales
    regimenes = [
        ('601', 'General de Ley Personas Morales', False, True),
        ('603', 'Personas Morales con Fines no Lucrativos', False, True),
        ('605', 'Sueldos y Salarios e Ingresos Asimilados a Salarios', True, False),
        ('606', 'Arrendamiento', True, False),
        ('608', 'Demás ingresos', True, False),
        ('610', 'Residentes en el Extranjero sin Establecimiento Permanente en México', True, True),
        ('611', 'Ingresos por Dividendos (socios y accionistas)', True, False),
        ('612', 'Personas Físicas con Actividades Empresariales y Profesionales', True, False),
        ('614', 'Ingresos por intereses', True, False),
        ('615', 'Régimen de los ingresos por obtención de premios', True, False),
        ('616', 'Sin obligaciones fiscales', True, False),
        ('620', 'Sociedades Cooperativas de Producción que optan por diferir sus ingresos', False, True),
        ('621', 'Incorporación Fiscal', True, False),
        ('622', 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras', True, True),
        ('623', 'Opcional para Grupos de Sociedades', False, True),
        ('624', 'Coordinados', False, True),
        ('625', 'Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas', True, False),
        ('626', 'Régimen Simplificado de Confianza', True, True),
    ]
    
    for codigo, desc, fisica, moral in regimenes:
        obj, created = SatRegimenFiscal.objects.get_or_create(
            codigo=codigo,
            defaults={
                'descripcion': desc, 
                'persona_fisica': fisica, 
                'persona_moral': moral, 
                'activo': True
            }
        )
        if created:
            print(f"✅ Régimen fiscal SAT: {codigo} - {desc}")

    # Usos CFDI
    usos_cfdi = [
        ('G01', 'Adquisición de mercancías', True, True),
        ('G02', 'Devoluciones, descuentos o bonificaciones', True, True),
        ('G03', 'Gastos en general', True, True),
        ('I01', 'Construcciones', True, True),
        ('I02', 'Mobilario y equipo de oficina por inversiones', True, True),
        ('I03', 'Equipo de transporte', True, True),
        ('I04', 'Equipo de cómputo y accesorios', True, True),
        ('I05', 'Dados, troqueles, moldes, matrices y herramental', True, True),
        ('I06', 'Comunicaciones telefónicas', True, True),
        ('I07', 'Comunicaciones satelitales', True, True),
        ('I08', 'Otra maquinaria y equipo', True, True),
        ('D01', 'Honorarios médicos, dentales y gastos hospitalarios', True, False),
        ('D02', 'Gastos médicos por incapacidad o discapacidad', True, False),
        ('D03', 'Gastos funerales', True, False),
        ('D04', 'Donativos', True, False),
        ('D05', 'Intereses reales efectivamente pagados por créditos hipotecarios (casa habitación)', True, False),
        ('D06', 'Aportaciones voluntarias al SAR', True, False),
        ('D07', 'Primas por seguros de gastos médicos', True, False),
        ('D08', 'Gastos de transportación escolar obligatoria', True, False),
        ('D09', 'Depósitos en cuentas para el ahorro, primas que tengan como base planes de pensiones', True, False),
        ('D10', 'Pagos por servicios educativos (colegiaturas)', True, False),
        ('S01', 'Sin efectos fiscales', True, True),
        ('CP01', 'Pagos', True, True),
        ('CN01', 'Nómina', True, True),
    ]
    
    for codigo, desc, fisica, moral in usos_cfdi:
        obj, created = SatUsoCFDI.objects.get_or_create(
            codigo=codigo,
            defaults={
                'descripcion': desc, 
                'persona_fisica': fisica, 
                'persona_moral': moral, 
                'activo': True
            }
        )
        if created:
            print(f"✅ Uso CFDI SAT: {codigo} - {desc}")

def crear_especialidades():
    """Crear especialidades dentales"""
    especialidades_data = [
        'Odontología General',
        'Ortodoncia',
        'Endodoncia',
        'Periodoncia',
        'Cirugía Oral',
        'Prostodoncia',
        'Odontopediatría',
        'Implantología',
    ]
    
    for nombre in especialidades_data:
        obj, created = Especialidad.objects.get_or_create(nombre=nombre)
        if created:
            print(f"✅ Especialidad creada: {nombre}")

def crear_servicios():
    """Crear servicios dentales"""
    esp_general = Especialidad.objects.get(nombre='Odontología General')
    esp_ortodoncia = Especialidad.objects.get(nombre='Ortodoncia')
    esp_endodoncia = Especialidad.objects.get(nombre='Endodoncia')
    esp_cirugia = Especialidad.objects.get(nombre='Cirugía Oral')
    esp_periodoncia = Especialidad.objects.get(nombre='Periodoncia')
    
    servicios_data = [
        # Odontología General
        ('Consulta General', 'Examen odontológico general', Decimal('500.00'), esp_general, 30),
        ('Limpieza Dental', 'Profilaxis y limpieza dental', Decimal('800.00'), esp_general, 60),
        ('Resina Dental', 'Restauración con resina compuesta', Decimal('1200.00'), esp_general, 45),
        ('Amalgama', 'Restauración con amalgama', Decimal('800.00'), esp_general, 30),
        ('Extracción Simple', 'Extracción dental simple', Decimal('900.00'), esp_general, 30),
        ('Rayos X', 'Radiografía dental', Decimal('300.00'), esp_general, 10),
        
        # Ortodoncia
        ('Brackets Metálicos', 'Ortodoncia con brackets metálicos', Decimal('15000.00'), esp_ortodoncia, 120),
        ('Brackets Estéticos', 'Ortodoncia con brackets cerámicos', Decimal('20000.00'), esp_ortodoncia, 120),
        ('Retenedores', 'Retenedores de ortodoncia', Decimal('3000.00'), esp_ortodoncia, 60),
        
        # Endodoncia
        ('Endodoncia Molar', 'Tratamiento de conductos en molar', Decimal('3500.00'), esp_endodoncia, 90),
        ('Endodoncia Premolar', 'Tratamiento de conductos en premolar', Decimal('2800.00'), esp_endodoncia, 75),
        ('Endodoncia Anterior', 'Tratamiento de conductos en diente anterior', Decimal('2200.00'), esp_endodoncia, 60),
        
        # Cirugía Oral
        ('Extracción Quirúrgica', 'Extracción dental quirúrgica compleja', Decimal('2500.00'), esp_cirugia, 60),
        ('Cirugía de Cordales', 'Extracción de muelas del juicio', Decimal('4000.00'), esp_cirugia, 90),
        
        # Periodoncia
        ('Curetaje Dental', 'Raspado y alisado radicular', Decimal('1500.00'), esp_periodoncia, 60),
        ('Cirugía Periodontal', 'Cirugía de encías', Decimal('3000.00'), esp_periodoncia, 90),
    ]
    
    for nombre, desc, precio, esp, duracion in servicios_data:
        obj, created = Servicio.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': desc,
                'precio': precio,
                'especialidad': esp,
                'activo': True,
                'duracion_minutos': duracion
            }
        )
        if created:
            print(f"✅ Servicio creado: {nombre} - ${precio}")

def crear_unidades_dentales():
    """Crear unidades dentales"""
    unidades_data = [
        ('Consultorio 1', 'Unidad dental principal'),
        ('Consultorio 2', 'Unidad dental secundaria'),
        ('Sala de Cirugía', 'Unidad especializada para cirugías'),
    ]
    
    for nombre, desc in unidades_data:
        obj, created = UnidadDental.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': desc}
        )
        if created:
            print(f"✅ Unidad dental creada: {nombre}")

def crear_usuarios_y_dentistas():
    """Crear usuarios y perfiles de dentistas"""
    # Crear usuario administrador si no existe
    admin_user, created = User.objects.get_or_create(
        username='admin.dev',
        defaults={
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'email': 'admin@clinica.dev',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        admin_group = Group.objects.get(name='Administrador')
        admin_user.groups.add(admin_group)
        print("✅ Usuario administrador creado")

    # Crear dentistas
    dentistas_data = [
        ('dr.martinez', 'Carlos', 'Martínez', 'carlos.martinez@clinica.dev', ['Odontología General', 'Endodoncia']),
        ('dra.rodriguez', 'Ana', 'Rodríguez', 'ana.rodriguez@clinica.dev', ['Ortodoncia']),
        ('dr.lopez', 'Miguel', 'López', 'miguel.lopez@clinica.dev', ['Cirugía Oral', 'Periodoncia']),
    ]
    
    grupo_dentista = Group.objects.get(name='Dentista')
    
    for username, nombre, apellido, email, especialidades in dentistas_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': nombre,
                'last_name': apellido,
                'email': email,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            user.groups.add(grupo_dentista)
            print(f"✅ Usuario dentista creado: {username}")

        # Crear o actualizar perfil de dentista
        perfil, perfil_created = PerfilDentista.objects.get_or_create(
            usuario=user,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'email': email,
                'activo': True
            }
        )
        
        # Asignar especialidades
        for esp_nombre in especialidades:
            try:
                especialidad = Especialidad.objects.get(nombre=esp_nombre)
                perfil.especialidades.add(especialidad)
            except Especialidad.DoesNotExist:
                print(f"❌ Especialidad no encontrada: {esp_nombre}")
        
        if perfil_created:
            print(f"✅ Perfil de dentista creado: Dr. {nombre} {apellido}")

def crear_horarios_laborales():
    """Crear horarios laborales para los dentistas"""
    dentistas = PerfilDentista.objects.all()
    
    # Horario estándar: Lunes a Viernes 9:00-18:00, Sábados 9:00-14:00
    horarios_estandar = [
        (0, time(9, 0), time(18, 0)),  # Lunes
        (1, time(9, 0), time(18, 0)),  # Martes
        (2, time(9, 0), time(18, 0)),  # Miércoles
        (3, time(9, 0), time(18, 0)),  # Jueves
        (4, time(9, 0), time(18, 0)),  # Viernes
        (5, time(9, 0), time(14, 0)),  # Sábado
    ]
    
    for dentista in dentistas:
        for dia, hora_inicio, hora_fin in horarios_estandar:
            horario, created = HorarioLaboral.objects.get_or_create(
                dentista=dentista,
                dia_semana=dia,
                defaults={
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'activo': True
                }
            )
            if created:
                print(f"✅ Horario creado para {dentista}: {horario.get_dia_semana_display()} {hora_inicio}-{hora_fin}")

def crear_pacientes():
    """Crear pacientes de prueba"""
    pacientes_data = [
        ('Juan', 'Pérez', 'juan.perez@email.com', '555-123-4567', '1985-03-15'),
        ('María', 'González', 'maria.gonzalez@email.com', '555-234-5678', '1990-07-22'),
        ('Pedro', 'Ramírez', 'pedro.ramirez@email.com', '555-345-6789', '1978-11-08'),
        ('Ana', 'Torres', 'ana.torres@email.com', '555-456-7890', '1995-02-14'),
        ('Luis', 'Morales', 'luis.morales@email.com', '555-567-8901', '1982-09-30'),
    ]
    
    for nombre, apellido, email, telefono, fecha_nac in pacientes_data:
        paciente, created = Paciente.objects.get_or_create(
            email=email,
            defaults={
                'nombre': nombre,
                'apellido': apellido,
                'telefono': telefono,
                'fecha_nacimiento': datetime.strptime(fecha_nac, '%Y-%m-%d').date(),
                'calle': 'Calle Principal',
                'numero_exterior': '123',
                'codigo_postal': '12345',
                'colonia': 'Centro',
                'municipio': 'Ciudad',
                'estado': 'Estado'
            }
        )
        
        if created:
            print(f"✅ Paciente creado: {nombre} {apellido}")
            
            # Crear datos fiscales para algunos pacientes
            if nombre in ['Juan', 'María']:
                datos_fiscales, df_created = DatosFiscales.objects.get_or_create(
                    paciente=paciente,
                    defaults={
                        'rfc': f'{nombre.upper()[:4]}{apellido.upper()[:2]}850315ABC' if nombre == 'Juan' else 'MARG900722XYZ',
                        'razon_social': f'{nombre} {apellido}',
                        'calle': 'Av. Reforma',
                        'numero_exterior': '456',
                        'codigo_postal': '54321',
                        'colonia': 'Del Valle',
                        'municipio': 'Ciudad',
                        'estado': 'Estado',
                        'regimen_fiscal': SatRegimenFiscal.objects.filter(persona_fisica=True).first(),
                        'uso_cfdi': SatUsoCFDI.objects.filter(codigo='D01').first(),
                    }
                )
                if df_created:
                    print(f"✅ Datos fiscales creados para: {nombre} {apellido}")

def crear_diagnosticos():
    """Crear diagnósticos básicos para el odontograma"""
    diagnosticos_data = [
        ('SANO', '#FFFFFF', ''),
        ('CARIES', '#8B4513', ''),
        ('RESTAURADO', '#4169E1', ''),
        ('AUSENTE', '#000000', ''),
        ('PROTESIS', '#FFD700', ''),
        ('ENDODONCIA', '#FF0000', ''),
        ('CORONA', '#C0C0C0', ''),
    ]
    
    for nombre, color, icono in diagnosticos_data:
        obj, created = Diagnostico.objects.get_or_create(
            nombre=nombre,
            defaults={
                'color_hex': color,
                'icono_svg': icono
            }
        )
        if created:
            print(f"✅ Diagnóstico creado: {nombre}")

def main():
    """Función principal para crear todos los datos de prueba"""
    print("🚀 Iniciando creación de datos de prueba completos...")
    print()
    
    try:
        # Crear en orden de dependencias
        print("📋 Creando grupos de usuarios...")
        crear_grupos()
        print()
        
        print("📋 Creando catálogos SAT...")
        crear_catalogos_sat()
        print()
        
        print("📋 Creando especialidades...")
        crear_especialidades()
        print()
        
        print("📋 Creando servicios...")
        crear_servicios()
        print()
        
        print("📋 Creando unidades dentales...")
        crear_unidades_dentales()
        print()
        
        print("📋 Creando usuarios y dentistas...")
        crear_usuarios_y_dentistas()
        print()
        
        print("📋 Creando horarios laborales...")
        crear_horarios_laborales()
        print()
        
        print("📋 Creando pacientes...")
        crear_pacientes()
        print()
        
        print("📋 Creando diagnósticos...")
        crear_diagnosticos()
        print()
        
        print("🎉 ¡Datos de prueba creados exitosamente!")
        print()
        print("📊 Resumen de datos creados:")
        print(f"   - Especialidades: {Especialidad.objects.count()}")
        print(f"   - Servicios: {Servicio.objects.count()}")
        print(f"   - Dentistas: {PerfilDentista.objects.count()}")
        print(f"   - Pacientes: {Paciente.objects.count()}")
        print(f"   - Unidades Dentales: {UnidadDental.objects.count()}")
        print(f"   - Horarios Laborales: {HorarioLaboral.objects.count()}")
        print(f"   - Diagnósticos: {Diagnostico.objects.count()}")
        print()
        print("👤 Credenciales de acceso:")
        print("   Admin: admin.dev / admin123")
        print("   Dentistas: dr.martinez, dra.rodriguez, dr.lopez / password123")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
