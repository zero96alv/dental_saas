#!/usr/bin/env python
"""
Script para listar todas las tablas en la base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.db import connection

def main():
    cursor = connection.cursor()
    
    # Listar todas las tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print("📊 Tablas en la base de datos:")
    print("-" * 40)
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"{table_name:35} ({count} filas)")

if __name__ == '__main__':
    main()
