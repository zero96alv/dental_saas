#!/usr/bin/env python
"""
Script para listar todas las tablas en el schema del tenant dev
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Clinica
from django.db import connection

def main():
    # Obtener el tenant dev
    try:
        tenant_dev = Clinica.objects.get(schema_name='dev')
        print(f"🏥 Conectando al tenant: {tenant_dev.nombre} (schema: {tenant_dev.schema_name})")
        
        with tenant_context(tenant_dev):
            cursor = connection.cursor()
            
            # Listar todas las tablas en el schema dev
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{tenant_dev.schema_name}' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            print(f"\n📊 Tablas en el schema '{tenant_dev.schema_name}':")
            print("-" * 50)
            
            if not tables:
                print("❌ No se encontraron tablas en este schema")
                return
            
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    print(f"{table_name:35} ({count} filas)")
                except Exception as e:
                    print(f"{table_name:35} (Error: {str(e)[:20]}...)")
                    
    except Clinica.DoesNotExist:
        print("❌ No se encontró el tenant 'dev'")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
