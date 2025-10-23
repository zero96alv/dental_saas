#!/usr/bin/env python3
"""
Script para generar datos de prueba COMPLETOS en el sistema dental
Demuestra TODAS las funcionalidades del sistema con datos realistas
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.db import connection, transaction
from django.utils import timezone
from tenants.models import Clinica
from core.models import (
    Paciente, PerfilDentista, Especialidad, Servicio, Cita,
    TratamientoCita, HistorialClinico, Diagnostico, EstadoDiente,
    HistorialEstadoDiente, Pago, UnidadDental, DatosFiscales,
    SatFormaPago, SatMetodoPago, SatUsoCFDI, SatRegimenFiscal,
    actualizar_estado_diente
)

# Cambiar al tenant demo
tenant = Clinica.objects.get(schema_name='demo')
connection.set_tenant(tenant)

print("=" * 80)
print("🦷 GENERANDO DATOS COMPLETOS DEL SISTEMA DENTAL")
print("=" * 80)

# ============================================================================
# DATOS BASE
# ============================================================================

# Diagnósticos base (asegurar que existan)
DIAGNOSTICOS_BASE = {
    'SANO': '#27ae60',
    'CARIES': '#e74c3c',
    'OBTURACION': '#f39c12',
    'CORONA': '#3498db',
    'ENDODONCIA': '#e91e63',
    'EXTRAIDO': '#95a5a6',
    'IMPLANTE': '#9b59b6',
}

print("\n📋 Asegurando diagnósticos base...")
diagnosticos = {}
for nombre, color in DIAGNOSTICOS_BASE.items():
    diag, created = Diagnostico.objects.get_or_create(
        nombre=nombre,
        defaults={'color_hex': color, 'icono_svg': ''}
    )
    diagnosticos[nombre] = diag
    if created:
        print(f"  ✓ Creado: {nombre}")
    else:
        print(f"  → Existente: {nombre}")

# Especialidades
print("\n🏥 Creando especialidades...")
especialidades = {}
especialidades_data = [
    'Odontología General',
    'Endodoncia',
    'Periodoncia',
    'Ortodoncia',
    'Cirugía Oral',
]

for nombre in especialidades_data:
    esp, created = Especialidad.objects.get_or_create(nombre=nombre)
    especialidades[nombre] = esp
    print(f"  {'✓' if created else '→'} {nombre}")

# Servicios
print("\n💰 Creando servicios...")
servicios = {}
servicios_data = [
    ('Limpieza dental', 'Odontología General', 300, 30),
    ('Radiografía panorámica', 'Odontología General', 400, 15),
    ('Obturación simple', 'Odontología General', 800, 45),
    ('Obturación compuesta', 'Odontología General', 1200, 60),
    ('Endodoncia unirradicular', 'Endodoncia', 2500, 90),
    ('Endodoncia multirradicular', 'Endodoncia', 3500, 120),
    ('Extracción simple', 'Cirugía Oral', 500, 30),
    ('Extracción quirúrgica', 'Cirugía Oral', 1500, 60),
    ('Corona de porcelana', 'Odontología General', 4000, 90),
    ('Implante dental', 'Cirugía Oral', 8000, 120),
    ('Blanqueamiento', 'Odontología General', 2000, 60),
    ('Limpieza profunda por cuadrante', 'Periodoncia', 600, 45),
]

for nombre, esp_nombre, precio, duracion in servicios_data:
    serv, created = Servicio.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': f'Servicio de {nombre.lower()}',
            'precio': Decimal(precio),
            'duracion_minutos': duracion,
            'especialidad': especialidades[esp_nombre],
            'activo': True
        }
    )
    servicios[nombre] = serv
    print(f"  {'✓' if created else '→'} {nombre} (${precio})")

# Unidades dentales
print("\n🪑 Creando unidades dentales...")
for i in range(1, 4):
    UnidadDental.objects.get_or_create(
        nombre=f'Unidad {i}',
        defaults={'descripcion': f'Unidad dental #{i}'}
    )
print(f"  ✓ 3 unidades dentales")

# ============================================================================
# PACIENTES CON HISTORIALES VARIADOS
# ============================================================================

print("\n👥 Creando pacientes con historiales completos...")

pacientes_data = [
    {
        'nombre': 'Carlos',
        'apellido': 'Rodríguez',
        'email': 'carlos.rodriguez@email.com',
        'telefono': '5551234567',
        'fecha_nacimiento': '1985-03-15',
        'escenario': 'paciente_antiguo',  # Mucho historial
    },
    {
        'nombre': 'María',
        'apellido': 'González',
        'email': 'maria.gonzalez@email.com',
        'telefono': '5559876543',
        'fecha_nacimiento': '1990-07-22',
        'escenario': 'tratamiento_activo',  # Tratamiento en curso
    },
    {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'email': 'juan.perez@email.com',
        'telefono': '5555551234',
        'fecha_nacimiento': '1978-11-30',
        'escenario': 'casos_complejos',  # Varios problemas
    },
    {
        'nombre': 'Ana',
        'apellido': 'Martínez',
        'email': 'ana.martinez@email.com',
        'telefono': '5554443322',
        'fecha_nacimiento': '1995-05-10',
        'escenario': 'paciente_nuevo',  # Primera vez
    },
    {
        'nombre': 'Luis',
        'apellido': 'Sánchez',
        'email': 'luis.sanchez@email.com',
        'telefono': '5552223344',
        'fecha_nacimiento': '1982-09-05',
        'escenario': 'saldo_pendiente',  # Con deuda
    },
]

pacientes = {}
for data in pacientes_data:
    escenario = data.pop('escenario')
    pac, created = Paciente.objects.get_or_create(
        email=data['email'],
        defaults=data
    )
    pacientes[escenario] = pac
    print(f"  {'✓' if created else '→'} {pac.nombre} {pac.apellido} ({escenario})")

# Dentistas (usar los existentes)
dentistas = list(PerfilDentista.objects.all())
if not dentistas:
    print("  ⚠️  No hay dentistas. Ejecuta create_demo_users.py primero")
    exit(1)

dentista_principal = dentistas[0]
print(f"  → Dentista principal: {dentista_principal.nombre}")

# Unidades
unidades = list(UnidadDental.objects.all())
unidad = unidades[0]

# ============================================================================
# ESCENARIO 1: Paciente Antiguo (Carlos) - Historial extenso
# ============================================================================

print("\n📅 ESCENARIO 1: Paciente con historial extenso (Carlos)")
paciente = pacientes['paciente_antiguo']

# Cita hace 6 meses: Primera consulta
fecha_1 = timezone.now() - timedelta(days=180)
cita1 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_1,
    estado='COM',
    motivo='Primera consulta - Revisión general'
)
cita1.servicios_planeados.add(servicios['Limpieza dental'], servicios['Radiografía panorámica'])

# Tratamiento: Limpieza + diagnóstico de caries
with transaction.atomic():
    trat1 = TratamientoCita.objects.create(
        cita=cita1,
        dientes_tratados='16,26,36,46',
        descripcion='Limpieza dental completa. Diagnóstico: caries en dientes 16 y 26.',
        requiere_seguimiento=True,
        fecha_seguimiento_sugerida=(fecha_1 + timedelta(days=30)).date(),
        registrado_por=dentista_principal
    )
    trat1.servicios.add(servicios['Limpieza dental'], servicios['Radiografía panorámica'])

    # Marcar caries detectadas
    for diente in [16, 26]:
        actualizar_estado_diente(
            paciente=paciente,
            numero_diente=diente,
            diagnostico_nuevo=diagnosticos['CARIES'],
            cita=cita1,
            tratamiento_descripcion=f'Caries detectada en diente {diente}'
        )

# Pago parcial
Pago.objects.create(
    paciente=paciente,
    cita=cita1,
    monto=Decimal('500'),
    metodo_pago='Efectivo',
    fecha_pago=fecha_1
)

print(f"  ✓ Cita 1: Limpieza y diagnóstico (hace 6 meses)")

# Cita hace 5 meses: Obturaciones
fecha_2 = timezone.now() - timedelta(days=150)
cita2 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_2,
    estado='COM',
    motivo='Obturaciones de caries diagnosticadas'
)
cita2.servicios_planeados.add(servicios['Obturación compuesta'], servicios['Obturación compuesta'])

with transaction.atomic():
    trat2 = TratamientoCita.objects.create(
        cita=cita2,
        dientes_tratados='16,26',
        descripcion='Obturaciones con resina compuesta A2 en dientes 16 y 26. Cavidad clase II mesial.',
        registrado_por=dentista_principal
    )
    trat2.servicios.add(servicios['Obturación compuesta'])

    # Actualizar a obturado
    for diente in [16, 26]:
        actualizar_estado_diente(
            paciente=paciente,
            numero_diente=diente,
            diagnostico_nuevo=diagnosticos['OBTURACION'],
            cita=cita2,
            tratamiento_descripcion=f'Obturación con resina compuesta en diente {diente}'
        )

# Pago completo
Pago.objects.create(
    paciente=paciente,
    cita=cita2,
    monto=Decimal('2400'),
    metodo_pago='Tarjeta de crédito',
    fecha_pago=fecha_2
)

print(f"  ✓ Cita 2: Obturaciones (hace 5 meses)")

# Cita hace 1 mes: Limpieza de control
fecha_3 = timezone.now() - timedelta(days=30)
cita3 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_3,
    estado='COM',
    motivo='Limpieza de control semestral'
)
cita3.servicios_planeados.add(servicios['Limpieza dental'])

with transaction.atomic():
    trat3 = TratamientoCita.objects.create(
        cita=cita3,
        dientes_tratados='',
        descripcion='Limpieza dental de control. Estado general excelente. Obturaciones en buen estado.',
        registrado_por=dentista_principal
    )
    trat3.servicios.add(servicios['Limpieza dental'])

Pago.objects.create(
    paciente=paciente,
    cita=cita3,
    monto=Decimal('300'),
    metodo_pago='Efectivo',
    fecha_pago=fecha_3
)

print(f"  ✓ Cita 3: Control (hace 1 mes)")

# Actualizar saldo
paciente.actualizar_saldo_global()

# ============================================================================
# ESCENARIO 2: Tratamiento Activo (María) - Endodoncia en progreso
# ============================================================================

print("\n📅 ESCENARIO 2: Tratamiento activo (María)")
paciente = pacientes['tratamiento_activo']

# Cita hace 2 meses: Diagnóstico
fecha_1 = timezone.now() - timedelta(days=60)
cita1 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_1,
    estado='COM',
    motivo='Dolor intenso en molar inferior derecho'
)
cita1.servicios_planeados.add(servicios['Radiografía panorámica'])

with transaction.atomic():
    trat1 = TratamientoCita.objects.create(
        cita=cita1,
        dientes_tratados='46',
        descripcion='Diagnóstico: pulpitis irreversible en diente 46. Requiere endodoncia urgente.',
        requiere_seguimiento=True,
        fecha_seguimiento_sugerida=(fecha_1 + timedelta(days=7)).date(),
        registrado_por=dentista_principal
    )
    trat1.servicios.add(servicios['Radiografía panorámica'])

Pago.objects.create(
    paciente=paciente,
    cita=cita1,
    monto=Decimal('400'),
    metodo_pago='Efectivo',
    fecha_pago=fecha_1
)

print(f"  ✓ Cita 1: Diagnóstico - requiere endodoncia")

# Cita hace 1 mes: Primera sesión de endodoncia
fecha_2 = timezone.now() - timedelta(days=30)
cita2 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_2,
    estado='COM',
    motivo='Primera sesión de endodoncia'
)
cita2.servicios_planeados.add(servicios['Endodoncia multirradicular'])

with transaction.atomic():
    trat2 = TratamientoCita.objects.create(
        cita=cita2,
        dientes_tratados='46',
        descripcion='Primera sesión de endodoncia. Apertura cameral, remoción pulpar, conductometría. Medicación intraconducto.',
        requiere_seguimiento=True,
        fecha_seguimiento_sugerida=(fecha_2 + timedelta(days=15)).date(),
        registrado_por=dentista_principal
    )
    trat2.servicios.add(servicios['Endodoncia multirradicular'])

    actualizar_estado_diente(
        paciente=paciente,
        numero_diente=46,
        diagnostico_nuevo=diagnosticos['ENDODONCIA'],
        cita=cita2,
        tratamiento_descripcion='Endodoncia en progreso - primera sesión'
    )

# Pago parcial
Pago.objects.create(
    paciente=paciente,
    cita=cita2,
    monto=Decimal('2000'),
    metodo_pago='Transferencia',
    fecha_pago=fecha_2
)

print(f"  ✓ Cita 2: Primera sesión endodoncia (pago parcial)")

# Cita PROGRAMADA para mañana: Finalizar endodoncia
fecha_3 = timezone.now() + timedelta(days=1)
cita3 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_3,
    estado='CON',  # Confirmada
    motivo='Segunda sesión - Finalizar endodoncia'
)
cita3.servicios_planeados.add(servicios['Endodoncia multirradicular'], servicios['Corona de porcelana'])

print(f"  ✓ Cita 3: Programada para MAÑANA (finalizar endodoncia)")

# Actualizar saldo (debe tener pendiente)
paciente.actualizar_saldo_global()

# ============================================================================
# ESCENARIO 3: Casos Complejos (Juan) - Múltiples problemas
# ============================================================================

print("\n📅 ESCENARIO 3: Casos complejos (Juan)")
paciente = pacientes['casos_complejos']

# Cita hace 3 meses: Evaluación completa
fecha_1 = timezone.now() - timedelta(days=90)
cita1 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_1,
    estado='COM',
    motivo='Evaluación integral - múltiples problemas dentales'
)
cita1.servicios_planeados.add(servicios['Radiografía panorámica'], servicios['Limpieza dental'])

with transaction.atomic():
    trat1 = TratamientoCita.objects.create(
        cita=cita1,
        dientes_tratados='18,28,38,48,16,26,36',
        descripcion='Evaluación completa: Cordales impactados (18,28,38,48), caries profundas (16,26,36), enfermedad periodontal generalizada.',
        requiere_seguimiento=True,
        registrado_por=dentista_principal
    )
    trat1.servicios.add(servicios['Radiografía panorámica'], servicios['Limpieza dental'])

    # Marcar cordales para extracción
    for diente in [18, 28, 38, 48]:
        actualizar_estado_diente(
            paciente=paciente,
            numero_diente=diente,
            diagnostico_nuevo=diagnosticos['CARIES'],
            cita=cita1,
            tratamiento_descripcion=f'Cordal impactado - requiere extracción quirúrgica'
        )

    # Marcar caries
    for diente in [16, 26, 36]:
        actualizar_estado_diente(
            paciente=paciente,
            numero_diente=diente,
            diagnostico_nuevo=diagnosticos['CARIES'],
            cita=cita1,
            tratamiento_descripcion=f'Caries profunda - requiere tratamiento'
        )

Pago.objects.create(
    paciente=paciente,
    cita=cita1,
    monto=Decimal('700'),
    metodo_pago='Efectivo',
    fecha_pago=fecha_1
)

print(f"  ✓ Cita 1: Evaluación - múltiples problemas detectados")

# Cita hace 2 meses: Extracción cordales superiores
fecha_2 = timezone.now() - timedelta(days=60)
cita2 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_2,
    estado='COM',
    motivo='Extracción quirúrgica cordales superiores'
)
cita2.servicios_planeados.add(servicios['Extracción quirúrgica'], servicios['Extracción quirúrgica'])

with transaction.atomic():
    trat2 = TratamientoCita.objects.create(
        cita=cita2,
        dientes_tratados='18,28',
        descripcion='Extracción quirúrgica de cordales superiores. Procedimiento sin complicaciones. Sutura con seda 3-0.',
        requiere_seguimiento=True,
        fecha_seguimiento_sugerida=(fecha_2 + timedelta(days=7)).date(),
        registrado_por=dentista_principal
    )
    trat2.servicios.add(servicios['Extracción quirúrgica'])

    for diente in [18, 28]:
        actualizar_estado_diente(
            paciente=paciente,
            numero_diente=diente,
            diagnostico_nuevo=diagnosticos['EXTRAIDO'],
            cita=cita2,
            tratamiento_descripcion=f'Extracción quirúrgica realizada'
        )

Pago.objects.create(
    paciente=paciente,
    cita=cita2,
    monto=Decimal('3000'),
    metodo_pago='Tarjeta de crédito',
    fecha_pago=fecha_2
)

print(f"  ✓ Cita 2: Extracciones cordales superiores")

# Cita ATENDIDA hoy: Obturaciones (para demostrar vista de gestión)
fecha_3 = timezone.now()
cita3 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_3,
    estado='ATN',  # ATENDIDA - perfecta para demostrar
    motivo='Obturaciones de caries en molares'
)
cita3.servicios_planeados.add(
    servicios['Obturación compuesta'],
    servicios['Obturación compuesta'],
    servicios['Obturación compuesta']
)

print(f"  ✓ Cita 3: EN ATENCIÓN AHORA (perfecta para demo)")

# Actualizar saldo
paciente.actualizar_saldo_global()

# ============================================================================
# ESCENARIO 4: Paciente Nuevo (Ana) - Primera vez
# ============================================================================

print("\n📅 ESCENARIO 4: Paciente nuevo (Ana)")
paciente = pacientes['paciente_nuevo']

# Cita PROGRAMADA mañana: Primera consulta
fecha_1 = timezone.now() + timedelta(days=1)
cita1 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_1,
    estado='PRO',
    motivo='Primera consulta - Revisión general'
)
cita1.servicios_planeados.add(servicios['Limpieza dental'], servicios['Radiografía panorámica'])

print(f"  ✓ Cita 1: Programada para mañana (primera vez)")

# ============================================================================
# ESCENARIO 5: Saldo Pendiente (Luis) - Con deuda
# ============================================================================

print("\n📅 ESCENARIO 5: Paciente con saldo pendiente (Luis)")
paciente = pacientes['saldo_pendiente']

# Cita hace 1 mes: Implante
fecha_1 = timezone.now() - timedelta(days=30)
cita1 = Cita.objects.create(
    paciente=paciente,
    dentista=dentista_principal,
    unidad_dental=unidad,
    fecha_hora=fecha_1,
    estado='COM',
    motivo='Colocación de implante dental'
)
cita1.servicios_planeados.add(servicios['Implante dental'], servicios['Radiografía panorámica'])

with transaction.atomic():
    trat1 = TratamientoCita.objects.create(
        cita=cita1,
        dientes_tratados='36',
        descripcion='Colocación de implante dental en posición 36. Implante osteointegrado de 4.5mm x 12mm. Cicatrización estimada 3-4 meses.',
        requiere_seguimiento=True,
        fecha_seguimiento_sugerida=(fecha_1 + timedelta(days=90)).date(),
        registrado_por=dentista_principal
    )
    trat1.servicios.add(servicios['Implante dental'], servicios['Radiografía panorámica'])

    actualizar_estado_diente(
        paciente=paciente,
        numero_diente=36,
        diagnostico_nuevo=diagnosticos['IMPLANTE'],
        cita=cita1,
        tratamiento_descripcion='Implante dental colocado'
    )

# Pago inicial (solo 50%)
Pago.objects.create(
    paciente=paciente,
    cita=cita1,
    monto=Decimal('4200'),
    metodo_pago='Tarjeta de débito',
    fecha_pago=fecha_1
)

print(f"  ✓ Cita 1: Implante (pago parcial - queda saldo)")

# Actualizar saldo (debe mostrar deuda)
paciente.actualizar_saldo_global()

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "=" * 80)
print("📊 RESUMEN DE DATOS GENERADOS")
print("=" * 80)

total_pacientes = Paciente.objects.count()
total_citas = Cita.objects.count()
total_tratamientos = TratamientoCita.objects.count()
total_historial = HistorialEstadoDiente.objects.count()
total_pagos = Pago.objects.count()

print(f"\n✅ Pacientes: {total_pacientes}")
print(f"✅ Citas: {total_citas}")
print(f"   - Completadas: {Cita.objects.filter(estado='COM').count()}")
print(f"   - Atendidas: {Cita.objects.filter(estado='ATN').count()}")
print(f"   - Confirmadas: {Cita.objects.filter(estado='CON').count()}")
print(f"   - Programadas: {Cita.objects.filter(estado='PRO').count()}")
print(f"✅ Tratamientos registrados: {total_tratamientos}")
print(f"✅ Cambios dentales en historial: {total_historial}")
print(f"✅ Pagos: {total_pagos}")
print(f"✅ Servicios disponibles: {Servicio.objects.count()}")
print(f"✅ Diagnósticos: {Diagnostico.objects.count()}")

print("\n💰 SALDOS DE PACIENTES:")
for nombre, paciente in pacientes.items():
    paciente.refresh_from_db()
    saldo = float(paciente.saldo_global)
    simbolo = "💸" if saldo > 0 else "✅"
    print(f"   {simbolo} {paciente.nombre} {paciente.apellido}: ${saldo:.2f}")

print("\n🎯 CASOS DE USO DEMOSTRADOS:")
print("   ✓ Paciente con historial extenso (Carlos)")
print("   ✓ Tratamiento activo en múltiples sesiones (María)")
print("   ✓ Casos complejos con múltiples problemas (Juan)")
print("   ✓ Paciente nuevo sin historial (Ana)")
print("   ✓ Paciente con saldo pendiente (Luis)")
print("   ✓ Cita EN ATENCIÓN para demo de gestión (Juan - Cita #3)")

print("\n🔗 URLs DE INTERÉS:")
print("   📅 Agenda: /demo/agenda/")
print("   📋 Lista de citas: /demo/citas/")
print("   👥 Lista de pacientes: /demo/pacientes/")
cita_demo = Cita.objects.filter(estado='ATN').first()
if cita_demo:
    print(f"   🦷 Gestionar cita EN ATENCIÓN: /demo/citas/{cita_demo.id}/gestionar/")

print("\n" + "=" * 80)
print("✅ DATOS GENERADOS EXITOSAMENTE")
print("=" * 80)
