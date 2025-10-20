#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
sys.path.append('.')
django.setup()

from django.apps import apps
from django.db import connection

def compare_models_tables():
    """Comparar modelos definidos en Django con tablas existentes."""
    
    # Obtener todos los modelos de la app core
    core_models = list(apps.get_app_config('core').get_models())
    
    print("=== MODELOS DEFINIDOS EN DJANGO (CORE) ===")
    model_tables = {}
    for model in core_models:
        table_name = model._meta.db_table
        model_name = model.__name__
        model_tables[table_name] = model_name
        print(f"- Modelo: {model_name} -> Tabla: {table_name}")
    
    print(f"\nTotal modelos core: {len(core_models)}")
    
    # Obtener tablas existentes en la BD
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'core_%'
            ORDER BY table_name
        """)
        
        existing_tables = [table[0] for table in cursor.fetchall()]
    
    print(f"\n=== TABLAS EXISTENTES EN LA BD (CORE) ===")
    for table in existing_tables:
        print(f"- {table}")
    
    print(f"\nTotal tablas core existentes: {len(existing_tables)}")
    
    # Comparar
    print(f"\n=== ANÁLISIS DE DISCREPANCIAS ===")
    
    # Tablas que deberían existir pero no existen
    missing_tables = set(model_tables.keys()) - set(existing_tables)
    if missing_tables:
        print("TABLAS FALTANTES (definidas en modelos pero no en BD):")
        for table in sorted(missing_tables):
            model_name = model_tables[table]
            print(f"  - {table} (modelo: {model_name})")
    else:
        print("✅ No hay tablas faltantes")
    
    # Tablas que existen pero no deberían (tablas huérfanas)
    extra_tables = set(existing_tables) - set(model_tables.keys())
    if extra_tables:
        print("\nTABLAS EXTRA (existen en BD pero no en modelos):")
        for table in sorted(extra_tables):
            print(f"  - {table}")
    else:
        print("✅ No hay tablas extra")
    
    print(f"\n=== RESUMEN ===")
    print(f"Modelos definidos: {len(model_tables)}")
    print(f"Tablas existentes: {len(existing_tables)}")
    print(f"Tablas faltantes: {len(missing_tables)}")
    print(f"Tablas extra: {len(extra_tables)}")

if __name__ == '__main__':
    compare_models_tables()
