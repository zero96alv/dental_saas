#!/usr/bin/env python
"""
Script para crear datos básicos necesarios para probar el sistema clínico
Para tenant demo
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Configurar tenant demo
from django.db import connection
connection.set_schema('demo')

from core.models import Diagnostico, CategoriaHistorial
from django.db import transaction

def crear_diagnosticos_basicos():
    """Crear diagnósticos básicos si no existen"""
    diagnosticos_basicos = [
        {'nombre': 'Sano', 'color_hex': '#28a745'},
        {'nombre': 'Cariado', 'color_hex': '#dc3545'},
        {'nombre': 'Obturado', 'color_hex': '#007bff'},
        {'nombre': 'Endodoncia', 'color_hex': '#6f42c1'},
        {'nombre': 'Corona', 'color_hex': '#fd7e14'},
        {'nombre': 'Extracción Indicada', 'color_hex': '#6c757d'},
        {'nombre': 'Ausente', 'color_hex': '#000000'},
    ]
    
    created_count = 0
    for diag_data in diagnosticos_basicos:
        obj, created = Diagnostico.objects.get_or_create(
            nombre=diag_data['nombre'],
            defaults={'color_hex': diag_data['color_hex']}
        )
        if created:
            created_count += 1
            print(f"✓ Creado diagnóstico: {obj.nombre}")
        else:
            print(f"- Ya existe diagnóstico: {obj.nombre}")
    
    return created_count

def crear_categorias_historial():
    """Crear categorías de historial si no existen"""
    categorias_basicas = [
        {
            'nombre': 'General', 
            'descripcion': 'Registros generales del historial clínico',
            'icono': 'bi bi-clipboard-heart',
            'color': '#0d6efd',
            'orden': 1
        },
        {
            'nombre': 'Diagnósticos', 
            'descripcion': 'Diagnósticos y evaluaciones dentales',
            'icono': 'bi bi-search',
            'color': '#198754',
            'orden': 2
        },
        {
            'nombre': 'Tratamientos', 
            'descripcion': 'Tratamientos realizados y procedimientos',
            'icono': 'bi bi-tools',
            'color': '#fd7e14',
            'orden': 3
        },
    ]
    
    created_count = 0
    for cat_data in categorias_basicas:
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
            print(f"✓ Creada categoría: {obj.nombre}")
        else:
            print(f"- Ya existe categoría: {obj.nombre}")
    
    return created_count

def main():
    print("=== Configurando datos básicos para pruebas ===\n")
    
    try:
        with transaction.atomic():
            # Crear categorías de historial
            print("1. Creando categorías de historial...")
            cat_count = crear_categorias_historial()
            
            # Crear diagnósticos básicos  
            print("\n2. Creando diagnósticos básicos...")
            diag_count = crear_diagnosticos_basicos()
            
            print(f"\n=== Resumen ===")
            print(f"- Categorías creadas: {cat_count}")
            print(f"- Diagnósticos creados: {diag_count}")
            print("\n✅ ¡Datos básicos configurados correctamente!")
            print("\nAhora puedes probar el sistema clínico.")
            
    except Exception as e:
        print(f"❌ Error al crear datos: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()