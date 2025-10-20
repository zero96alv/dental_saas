#!/usr/bin/env python
"""
Script simplificado para crear datos básicos de prueba
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

def crear_catalogos_sat_basicos():
    """Crear catálogos SAT básicos con códigos cortos"""
    # Solo los más básicos
    formas_pago = [
        ('01', 'Efectivo'),
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
    ]
    
    for codigo, desc in metodos_pago:
        obj, created = SatMetodoPago.objects.get_or_create(
            codigo=codigo,
            defaults={'descripcion': desc, 'activo': True}
        )
        if created:
            print(f"✅ Método de pago SAT: {codigo} - {desc}")

    # Regímenes fiscales básicos
    regimenes = [
        ('612', 'Personas Físicas con Actividades Empresariales y Profesionales', True, False),
        ('616', 'Sin obligaciones fiscales', True, False),
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

    # Usos CFDI básicos
    usos_cfdi = [
        ('D01', 'Honorarios médicos, dentales y gastos hospitalarios', True, False),
        ('G03', 'Gastos en general', True, True),
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
    """Crear especialidades dentales básicas"""
    especialidades_data = [
        'Odontología General',
        'Ortodoncia',
        'Endodoncia',
    ]
    
    for nombre in especialidades_data:
        obj, created = Especialidad.objects.get_or_create(nombre=nombre)
        if created:
            print(f"✅ Especialidad creada: {nombre}")

def crear_servicios():
    """Crear servicios dentales básicos"""
    esp_general = Especialidad.objects.get(nombre='Odontología General')
    esp_ortodoncia = Especialidad.objects.get(nombre='Ortodoncia')
    esp_endodoncia = Especialidad.objects.get(nombre='Endodoncia')
    
    servicios_data = [
        ('Consulta General', 'Examen odontológico general', Decimal('500.00'), esp_general, 30),
        ('Limpieza Dental', 'Profilaxis y limpieza dental', Decimal('800.00'), esp_general, 60),
        ('Resina Dental', 'Restauración con resina compuesta', Decimal('1200.00'), esp_general, 45),
        ('Brackets Metálicos', 'Ortodoncia con brackets metálicos', Decimal('15000.00'), esp_ortodoncia, 120),
        ('Endodoncia Molar', 'Tratamiento de conductos en molar', Decimal('3500.00'), esp_endodoncia, 90),
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

    # Crear dentistas básicos
    dentistas_data = [
        ('dr.martinez', 'Carlos', 'Martínez', 'carlos.martinez@clinica.dev', ['Odontología General', 'Endodoncia']),
        ('dra.rodriguez', 'Ana', 'Rodríguez', 'ana.rodriguez@clinica.dev', ['Ortodoncia']),
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

        # Crear perfil de dentista
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
    
    # Horario básico: Lunes a Viernes 9:00-18:00
    horarios_basicos = [
        (0, time(9, 0), time(18, 0)),  # Lunes
        (1, time(9, 0), time(18, 0)),  # Martes
        (2, time(9, 0), time(18, 0)),  # Miércoles
        (3, time(9, 0), time(18, 0)),  # Jueves
        (4, time(9, 0), time(18, 0)),  # Viernes
    ]
    
    for dentista in dentistas:
        for dia, hora_inicio, hora_fin in horarios_basicos:
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
            
            # Crear datos fiscales para Juan
            if nombre == 'Juan':
                datos_fiscales, df_created = DatosFiscales.objects.get_or_create(
                    paciente=paciente,
                    defaults={
                        'rfc': 'JUPÉ850315ABC',
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
    """Crear diagnósticos básicos"""
    diagnosticos_data = [
        ('SANO', '#FFFFFF', ''),
        ('CARIES', '#8B4513', ''),
        ('RESTAURADO', '#4169E1', ''),
        ('AUSENTE', '#000000', ''),
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
    """Función principal"""
    print("🚀 Creando datos básicos de prueba...")
    print()
    
    try:
        crear_grupos()
        print()
        
        crear_catalogos_sat_basicos()
        print()
        
        crear_especialidades()
        print()
        
        crear_servicios()
        print()
        
        crear_unidades_dentales()
        print()
        
        crear_usuarios_y_dentistas()
        print()
        
        crear_horarios_laborales()
        print()
        
        crear_pacientes()
        print()
        
        crear_diagnosticos()
        print()
        
        print("🎉 ¡Datos básicos creados exitosamente!")
        print()
        print("📊 Resumen:")
        print(f"   - Especialidades: {Especialidad.objects.count()}")
        print(f"   - Servicios: {Servicio.objects.count()}")  
        print(f"   - Dentistas: {PerfilDentista.objects.count()}")
        print(f"   - Pacientes: {Paciente.objects.count()}")
        print(f"   - Unidades Dentales: {UnidadDental.objects.count()}")
        print(f"   - Horarios Laborales: {HorarioLaboral.objects.count()}")
        print()
        print("👤 Credenciales:")
        print("   Admin: admin.dev / admin123")
        print("   Dentistas: dr.martinez, dra.rodriguez / password123")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
