#!/usr/bin/env python
"""
Script para poblar datos de demostración del historial clínico mejorado
Este script crea categorías y preguntas de ejemplo para demostrar las nuevas funcionalidades
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core import models

def crear_categorias_historial():
    """Crear categorías para el historial clínico"""
    print("Creando categorías de historial clínico...")
    
    categorias = [
        {
            'nombre': 'Datos Generales',
            'descripcion': 'Información básica del paciente',
            'icono': 'fas fa-user',
            'color': '#3b82f6',
            'orden': 1
        },
        {
            'nombre': 'Dolor y Molestias',
            'descripcion': 'Evaluación del dolor y molestias actuales',
            'icono': 'fas fa-thermometer-half',
            'color': '#8b5cf6',
            'orden': 2
        },
        {
            'nombre': 'Antecedentes Patológicos Personales',
            'descripcion': 'Historial médico personal del paciente',
            'icono': 'fas fa-file-medical-alt',
            'color': '#f59e0b',
            'orden': 3
        },
        {
            'nombre': 'Alergias y Medicamentos',
            'descripcion': 'Alergias conocidas y medicamentos actuales',
            'icono': 'fas fa-pills',
            'color': '#f97316',
            'orden': 4
        }
    ]
    
    for cat_data in categorias:
        categoria, created = models.CategoriaHistorial.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults=cat_data
        )
        if created:
            print(f"  ✓ Creada categoría: {categoria.nombre}")
        else:
            print(f"  - Ya existe: {categoria.nombre}")

def crear_preguntas_historial():
    """Crear preguntas de ejemplo para cada categoría"""
    print("\nCreando preguntas de historial clínico...")
    
    # Obtener categorías
    try:
        datos_generales = models.CategoriaHistorial.objects.get(nombre='Datos Generales')
        antecedentes_personales = models.CategoriaHistorial.objects.get(nombre='Antecedentes Patológicos Personales')
        dolor = models.CategoriaHistorial.objects.get(nombre='Dolor y Molestias')
        alergias = models.CategoriaHistorial.objects.get(nombre='Alergias y Medicamentos')
    except models.CategoriaHistorial.DoesNotExist as e:
        print(f"Error: No se encontró una categoría requerida: {e}")
        return
    
    preguntas = [
        # Datos Generales
        {
            'categoria': datos_generales,
            'texto': '¿Cuál es el motivo principal de su consulta dental?',
            'subtitulo': 'Describa brevemente qué le trae al dentista hoy',
            'tipo': 'TEXTAREA',
            'orden': 1,
            'obligatoria': True,
            'importancia': 'ALTA'
        },
        {
            'categoria': datos_generales,
            'texto': '¿Ha visitado al dentista en los últimos 6 meses?',
            'tipo': 'SI_NO',
            'orden': 2,
            'obligatoria': True,
            'importancia': 'MEDIA'
        },
        
        # Antecedentes Patológicos Personales
        {
            'categoria': antecedentes_personales,
            'texto': '¿Padece diabetes?',
            'subtitulo': 'Incluya diabetes tipo 1, tipo 2 o gestacional',
            'tipo': 'SI_NO',
            'orden': 1,
            'obligatoria': True,
            'importancia': 'ALTA',
            'requiere_seguimiento': True
        },
        {
            'categoria': antecedentes_personales,
            'texto': '¿Tiene problemas cardiacos?',
            'subtitulo': 'Arritmias, infartos previos, marcapasos, etc.',
            'tipo': 'SI_NO',
            'orden': 2,
            'obligatoria': True,
            'importancia': 'CRITICA',
            'requiere_seguimiento': True
        },
        
        # Dolor y Molestias
        {
            'categoria': dolor,
            'texto': '¿Experimenta dolor dental actualmente?',
            'tipo': 'SI_NO',
            'orden': 1,
            'obligatoria': True,
            'importancia': 'ALTA'
        },
        {
            'categoria': dolor,
            'texto': '¿El dolor aumenta con alimentos fríos o calientes?',
            'tipo': 'SI_NO',
            'orden': 2,
            'obligatoria': False,
            'importancia': 'MEDIA'
        },
        
        # Alergias y Medicamentos
        {
            'categoria': alergias,
            'texto': '¿Es alérgico a algún medicamento?',
            'subtitulo': 'Especifique cuáles y qué reacción produce',
            'tipo': 'SI_NO',
            'orden': 1,
            'obligatoria': True,
            'importancia': 'CRITICA',
            'alerta_cofepris': True
        },
        {
            'categoria': alergias,
            'texto': '¿Toma algún medicamento actualmente?',
            'subtitulo': 'Incluya medicamentos con y sin receta, suplementos',
            'tipo': 'SI_NO',
            'orden': 2,
            'obligatoria': True,
            'importancia': 'ALTA'
        }
    ]
    
    for pregunta_data in preguntas:
        pregunta, created = models.PreguntaHistorial.objects.get_or_create(
            categoria=pregunta_data['categoria'],
            texto=pregunta_data['texto'],
            defaults=pregunta_data
        )
        if created:
            print(f"  ✓ Creada pregunta: {pregunta.texto[:50]}...")
        else:
            print(f"  - Ya existe: {pregunta.texto[:50]}...")

def main():
    """Función principal"""
    print("=" * 60)
    print("POBLANDO DATOS DEMO - HISTORIAL CLÍNICO MEJORADO")
    print("=" * 60)
    
    try:
        crear_categorias_historial()
        crear_preguntas_historial()
        
        print("\n" + "=" * 60)
        print("✅ DATOS DE DEMOSTRACIÓN CREADOS EXITOSAMENTE")
        print("=" * 60)
        print("\nPuede ahora probar el historial clínico mejorado:")
        print("1. Vaya a cualquier paciente")
        print("2. Haga clic en 'Historial Clínico Mejorado'")
        print("3. Complete el formulario con las escalas de dolor")
        print("4. Explore las nuevas funcionalidades")
        print("\n¡Disfrute del nuevo sistema!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nVerifique que:")
        print("- Django esté configurado correctamente")
        print("- La base de datos esté accesible")
        print("- Los modelos estén migrados")
        sys.exit(1)

if __name__ == '__main__':
    main()