#!/usr/bin/env python
"""
Script para migrar campo uso_cfdi de texto a ForeignKey
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Clinica
from django.db import connection, transaction

def main():
    try:
        tenant_dev = Clinica.objects.get(schema_name='dev')
        print(f"🏥 Corrigiendo campo uso_cfdi en {tenant_dev.schema_name}")
        
        with tenant_context(tenant_dev):
            cursor = connection.cursor()
            
            with transaction.atomic():
                # Paso 1: Agregar nuevo campo uso_cfdi_id
                print("📝 Paso 1: Agregando campo uso_cfdi_id...")
                cursor.execute("""
                    ALTER TABLE core_datosfiscales 
                    ADD COLUMN IF NOT EXISTS uso_cfdi_id BIGINT NULL 
                    REFERENCES core_satusocfdi(id) ON DELETE SET NULL;
                """)
                
                # Paso 2: Migrar datos existentes
                print("📝 Paso 2: Migrando datos existentes...")
                
                # Obtener registros con datos en uso_cfdi
                cursor.execute("SELECT id, uso_cfdi FROM core_datosfiscales WHERE uso_cfdi IS NOT NULL AND uso_cfdi != '';")
                registros = cursor.fetchall()
                
                print(f"   Encontrados {len(registros)} registros para migrar")
                
                for record_id, uso_cfdi_texto in registros:
                    # Buscar el ID correspondiente en core_satusocfdi
                    cursor.execute("SELECT id FROM core_satusocfdi WHERE codigo = %s LIMIT 1;", [uso_cfdi_texto.strip()])
                    sat_record = cursor.fetchone()
                    
                    if sat_record:
                        sat_id = sat_record[0]
                        cursor.execute("UPDATE core_datosfiscales SET uso_cfdi_id = %s WHERE id = %s;", [sat_id, record_id])
                        print(f"   ✅ Migrado registro {record_id}: '{uso_cfdi_texto}' -> ID {sat_id}")
                    else:
                        print(f"   ⚠️  No se encontró código SAT '{uso_cfdi_texto}' para registro {record_id}")
                
                # Paso 3: Eliminar campo antiguo
                print("📝 Paso 3: Eliminando campo antiguo uso_cfdi...")
                cursor.execute("ALTER TABLE core_datosfiscales DROP COLUMN IF EXISTS uso_cfdi;")
                
                print("✅ Migración completada exitosamente")
                
                # Verificar resultado
                print("\n📊 Verificando resultado:")
                cursor.execute("""
                    SELECT df.id, df.rfc, df.razon_social, sc.codigo, sc.descripcion 
                    FROM core_datosfiscales df
                    LEFT JOIN core_satusocfdi sc ON df.uso_cfdi_id = sc.id
                    LIMIT 3;
                """)
                
                resultados = cursor.fetchall()
                print("ID | RFC         | Razón Social         | Código | Descripción")
                print("-" * 70)
                for res in resultados:
                    codigo = res[3] or 'NULL'
                    desc = (res[4] or 'NULL')[:20]
                    print(f"{res[0]:2} | {res[1]:11} | {res[2][:20]:20} | {codigo:6} | {desc}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
