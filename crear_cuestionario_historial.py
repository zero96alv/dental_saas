#!/usr/bin/env python
"""
Script para crear el cuestionario completo de historial clínico
Incluye preguntas estándar médicas, dentales, y cumplimiento COFEPRIS

Uso:
    python crear_cuestionario_historial.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.db import connection
from tenants.models import Clinica
from core.models import CategoriaHistorial, PreguntaHistorial

def crear_cuestionario_historial():
    """Crea categorías y preguntas del historial clínico"""

    # Conectar al tenant demo
    print("=" * 80)
    print("CREACIÓN DE CUESTIONARIO DE HISTORIAL CLÍNICO")
    print("=" * 80)

    try:
        tenant = Clinica.objects.get(schema_name='demo')
        connection.set_tenant(tenant)
        print(f"✅ Conectado al tenant: {tenant.nombre} ({tenant.schema_name})")
    except Clinica.DoesNotExist:
        print("❌ Error: Tenant 'demo' no encontrado")
        return

    # Limpiar datos previos si existen
    print("\n🗑️  Limpiando datos previos...")
    PreguntaHistorial.objects.all().delete()
    CategoriaHistorial.objects.all().delete()
    print("   ✅ Datos previos eliminados")

    # ========================================
    # CATEGORÍAS
    # ========================================
    print("\n📂 Creando categorías...")

    categorias = {
        'datos_personales': CategoriaHistorial.objects.create(
            nombre='Datos Personales y Emergencia',
            descripcion='Información básica y contacto de emergencia',
            icono='bi bi-person-badge',
            color='#0d6efd',
            orden=1
        ),
        'antecedentes_medicos': CategoriaHistorial.objects.create(
            nombre='Antecedentes Médicos Generales',
            descripcion='Enfermedades, cirugías y tratamientos previos',
            icono='bi bi-heart-pulse',
            color='#dc3545',
            orden=2
        ),
        'medicamentos': CategoriaHistorial.objects.create(
            nombre='Medicamentos y Alergias',
            descripcion='Medicamentos actuales y alergias conocidas',
            icono='bi bi-capsule',
            color='#fd7e14',
            orden=3
        ),
        'antecedentes_dentales': CategoriaHistorial.objects.create(
            nombre='Antecedentes Dentales',
            descripcion='Historial de tratamientos y condiciones dentales',
            icono='bi bi-teeth',
            color='#198754',
            orden=4
        ),
        'habitos': CategoriaHistorial.objects.create(
            nombre='Hábitos y Estilo de Vida',
            descripcion='Tabaquismo, alcohol y otros hábitos relevantes',
            icono='bi bi-activity',
            color='#6c757d',
            orden=5
        ),
        'mujer': CategoriaHistorial.objects.create(
            nombre='Salud de la Mujer',
            descripcion='Preguntas específicas para pacientes femeninas',
            icono='bi bi-gender-female',
            color='#d63384',
            orden=6
        ),
        'cofepris': CategoriaHistorial.objects.create(
            nombre='Consentimientos y COFEPRIS',
            descripcion='Autorizaciones y cumplimiento normativo mexicano',
            icono='bi bi-shield-check',
            color='#0dcaf0',
            orden=7
        ),
    }

    print(f"   ✅ {len(categorias)} categorías creadas")

    # ========================================
    # PREGUNTAS
    # ========================================
    print("\n📝 Creando preguntas...")

    orden = 1
    total_preguntas = 0

    # --- DATOS PERSONALES ---
    cat = categorias['datos_personales']
    preguntas_datos = [
        {
            'texto': '¿Cuál es su grupo sanguíneo?',
            'tipo': 'MULTIPLE',
            'opciones': 'O+, O-, A+, A-, B+, B-, AB+, AB-, No lo sé',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Nombre completo de contacto de emergencia',
            'tipo': 'TEXT',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Teléfono de contacto de emergencia',
            'tipo': 'TELEFONO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Relación con el contacto de emergencia',
            'tipo': 'MULTIPLE',
            'opciones': 'Padre/Madre, Hijo/a, Esposo/a, Hermano/a, Otro familiar, Amigo/a',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
    ]

    for p in preguntas_datos:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # --- ANTECEDENTES MÉDICOS ---
    cat = categorias['antecedentes_medicos']
    preguntas_medicos = [
        {
            'texto': '¿Padece o ha padecido diabetes?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': '¿Padece o ha padecido hipertensión (presión alta)?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': '¿Padece o ha padecido enfermedades cardíacas?',
            'subtitulo': 'Incluyendo infarto, arritmias, insuficiencia cardíaca, etc.',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': '¿Ha tenido problemas de coagulación o hemorragias prolongadas?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': '¿Padece alguna enfermedad respiratoria?',
            'subtitulo': 'Asma, EPOC, bronquitis crónica, etc.',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Padece o ha padecido hepatitis o enfermedades del hígado?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
            'alerta_cofepris': True,
        },
        {
            'texto': '¿Padece o ha padecido VIH/SIDA?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'alerta_cofepris': True,
        },
        {
            'texto': '¿Padece o ha padecido tuberculosis?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'alerta_cofepris': True,
        },
        {
            'texto': '¿Padece artritis reumatoide u otra enfermedad autoinmune?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Padece o ha padecido cáncer?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': 'Si respondió Sí a alguna enfermedad, especifique detalles',
            'subtitulo': 'Diagnóstico completo, fecha, tratamiento actual, médico tratante',
            'tipo': 'TEXTAREA',
            'importancia': 'ALTA',
            'obligatoria': False,
        },
        {
            'texto': '¿Ha sido hospitalizado o intervenido quirúrgicamente?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Si ha sido hospitalizado/operado, especifique',
            'subtitulo': 'Tipo de cirugía, fecha aproximada, motivo',
            'tipo': 'TEXTAREA',
            'importancia': 'MEDIA',
            'obligatoria': False,
        },
    ]

    for p in preguntas_medicos:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # --- MEDICAMENTOS Y ALERGIAS ---
    cat = categorias['medicamentos']
    preguntas_medicamentos = [
        {
            'texto': '¿Es alérgico a algún medicamento?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
        },
        {
            'texto': 'Si es alérgico a medicamentos, especifique cuál(es) y qué reacción tuvo',
            'subtitulo': 'Muy importante: Penicilina, anestésicos, ibuprofeno, etc.',
            'tipo': 'TEXTAREA',
            'importancia': 'CRITICA',
            'obligatoria': False,
        },
        {
            'texto': '¿Ha tenido reacciones adversas a anestesia local o general?',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': 'Si ha tenido reacciones a anestesia, describa la reacción',
            'tipo': 'TEXTAREA',
            'importancia': 'CRITICA',
            'obligatoria': False,
        },
        {
            'texto': '¿Toma algún medicamento actualmente?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Liste todos los medicamentos que toma actualmente',
            'subtitulo': 'Incluir nombre, dosis y frecuencia (ej: Aspirina 100mg, 1 vez al día)',
            'tipo': 'TEXTAREA',
            'importancia': 'ALTA',
            'obligatoria': False,
        },
        {
            'texto': '¿Toma anticoagulantes?',
            'subtitulo': 'Warfarina, Aspirina, Clopidogrel, etc.',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': '¿Es alérgico al látex?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Tiene alergias a alimentos, metales u otras sustancias?',
            'subtitulo': 'Mariscos, níquel, yodo, etc.',
            'tipo': 'TEXTAREA',
            'importancia': 'ALTA',
            'obligatoria': False,
        },
    ]

    for p in preguntas_medicamentos:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # --- ANTECEDENTES DENTALES ---
    cat = categorias['antecedentes_dentales']
    preguntas_dentales = [
        {
            'texto': '¿Cuándo fue su última visita al dentista?',
            'tipo': 'MULTIPLE',
            'opciones': 'Hace menos de 6 meses, Hace 6-12 meses, Hace 1-2 años, Hace más de 2 años, Primera vez, No recuerdo',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Cuál es el motivo principal de su visita hoy?',
            'tipo': 'TEXTAREA',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Sangran sus encías al cepillarse o usar hilo dental?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Tiene sensibilidad dental al frío, calor o dulce?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Ha tenido dolor dental recientemente?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Ha notado movilidad en algún diente?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Ha tenido tratamientos de conductos (endodoncia)?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Ha usado o usa actualmente ortodoncia (brackets/aparatos)?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Le han extraído dientes permanentes?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Ha tenido cirugías bucales?',
            'subtitulo': 'Muelas del juicio, implantes, injertos, etc.',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Con qué frecuencia se cepilla los dientes?',
            'tipo': 'MULTIPLE',
            'opciones': '3 o más veces al día, 2 veces al día, 1 vez al día, Ocasionalmente',
            'importancia': 'BAJA',
            'obligatoria': True,
        },
        {
            'texto': '¿Usa hilo dental?',
            'tipo': 'MULTIPLE',
            'opciones': 'Diariamente, Varias veces por semana, Ocasionalmente, Nunca',
            'importancia': 'BAJA',
            'obligatoria': True,
        },
    ]

    for p in preguntas_dentales:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # --- HÁBITOS ---
    cat = categorias['habitos']
    preguntas_habitos = [
        {
            'texto': '¿Fuma o ha fumado?',
            'tipo': 'MULTIPLE',
            'opciones': 'Nunca he fumado, Fumador actual, Ex fumador',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Si fuma o fumó, ¿cuántos cigarrillos al día aproximadamente?',
            'tipo': 'NUMERO',
            'importancia': 'MEDIA',
            'obligatoria': False,
        },
        {
            'texto': '¿Consume bebidas alcohólicas?',
            'tipo': 'MULTIPLE',
            'opciones': 'No consumo, Ocasionalmente (fiestas/eventos), 1-2 veces por semana, 3 o más veces por semana, Diariamente',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Rechina o aprieta los dientes (bruxismo)?',
            'subtitulo': 'Especialmente durante la noche',
            'tipo': 'MULTIPLE',
            'opciones': 'Sí, frecuentemente, A veces, No que yo sepa, Me han dicho que sí',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': '¿Se muerde las uñas, labios o mejillas?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Mastica hielo, lápices u objetos duros?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
        {
            'texto': '¿Ha experimentado estrés o ansiedad recientemente?',
            'tipo': 'MULTIPLE',
            'opciones': 'No, Leve, Moderado, Severo',
            'importancia': 'MEDIA',
            'obligatoria': True,
        },
    ]

    for p in preguntas_habitos:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # --- SALUD DE LA MUJER ---
    cat = categorias['mujer']
    preguntas_mujer = [
        {
            'texto': '¿Está embarazada actualmente?',
            'tipo': 'MULTIPLE',
            'opciones': 'No, Sí, No estoy segura, No aplica (hombre)',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'requiere_seguimiento': True,
        },
        {
            'texto': 'Si está embarazada, ¿de cuántos meses?',
            'tipo': 'NUMERO',
            'importancia': 'CRITICA',
            'obligatoria': False,
        },
        {
            'texto': '¿Está en período de lactancia?',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': False,
        },
        {
            'texto': '¿Toma anticonceptivos orales?',
            'tipo': 'SI_NO',
            'importancia': 'MEDIA',
            'obligatoria': False,
        },
    ]

    for p in preguntas_mujer:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # --- COFEPRIS Y CONSENTIMIENTOS ---
    cat = categorias['cofepris']
    preguntas_cofepris = [
        {
            'texto': 'He leído y acepto el Aviso de Privacidad',
            'subtitulo': 'De acuerdo con la Ley Federal de Protección de Datos Personales en Posesión de los Particulares',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'alerta_cofepris': True,
        },
        {
            'texto': 'Autorizo el tratamiento de mis datos personales y datos sensibles de salud',
            'subtitulo': 'Conforme a la normativa COFEPRIS y LFPDPPP',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
            'alerta_cofepris': True,
        },
        {
            'texto': 'Autorizo al dentista a realizar los tratamientos necesarios',
            'subtitulo': 'Basado en su criterio profesional y habiendo sido informado',
            'tipo': 'SI_NO',
            'importancia': 'CRITICA',
            'obligatoria': True,
        },
        {
            'texto': 'Entiendo que debo informar cualquier cambio en mi estado de salud',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
        {
            'texto': 'Declaro que toda la información proporcionada es verdadera y completa',
            'tipo': 'SI_NO',
            'importancia': 'ALTA',
            'obligatoria': True,
        },
    ]

    for p in preguntas_cofepris:
        PreguntaHistorial.objects.create(categoria=cat, orden=orden, **p)
        orden += 1
        total_preguntas += 1

    # ========================================
    # RESUMEN
    # ========================================
    print(f"\n✅ {total_preguntas} preguntas creadas")
    print("\n" + "=" * 80)
    print("RESUMEN DEL CUESTIONARIO")
    print("=" * 80)

    for cat_key, cat_obj in categorias.items():
        num_preguntas = PreguntaHistorial.objects.filter(categoria=cat_obj).count()
        print(f"\n📁 {cat_obj.nombre}")
        print(f"   • {num_preguntas} preguntas")
        print(f"   • Orden: {cat_obj.orden}")
        print(f"   • Ícono: {cat_obj.icono}")
        print(f"   • Color: {cat_obj.color}")

    # Estadísticas
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS")
    print("=" * 80)
    total = PreguntaHistorial.objects.count()
    obligatorias = PreguntaHistorial.objects.filter(obligatoria=True).count()
    criticas = PreguntaHistorial.objects.filter(importancia='CRITICA').count()
    altas = PreguntaHistorial.objects.filter(importancia='ALTA').count()
    cofepris = PreguntaHistorial.objects.filter(alerta_cofepris=True).count()
    seguimiento = PreguntaHistorial.objects.filter(requiere_seguimiento=True).count()

    print(f"\n📊 Total de preguntas: {total}")
    print(f"   • Obligatorias: {obligatorias}")
    print(f"   • Críticas: {criticas}")
    print(f"   • Alta importancia: {altas}")
    print(f"   • Alertas COFEPRIS: {cofepris}")
    print(f"   • Requieren seguimiento: {seguimiento}")

    # Por tipo
    print(f"\n📝 Por tipo de pregunta:")
    tipos = PreguntaHistorial.objects.values_list('tipo', flat=True).distinct()
    for tipo in tipos:
        count = PreguntaHistorial.objects.filter(tipo=tipo).count()
        tipo_label = dict(PreguntaHistorial.TIPO_PREGUNTA).get(tipo, tipo)
        print(f"   • {tipo_label}: {count}")

    print("\n" + "=" * 80)
    print("✅ CUESTIONARIO CREADO EXITOSAMENTE")
    print("=" * 80)
    print(f"\nURL para completar: http://142.93.87.37/demo/pacientes/<ID>/historial/completar/")
    print(f"O desde el detalle de cualquier paciente: Botón 'Completar Historial Clínico'")
    print("\n")

if __name__ == '__main__':
    crear_cuestionario_historial()
