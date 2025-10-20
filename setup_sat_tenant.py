#!/usr/bin/env python
"""
Script para configurar las tablas SAT en un tenant específico
Uso: python setup_sat_tenant.py [nombre_tenant]
Ejemplo: python setup_sat_tenant.py dev
"""

import os
import django
import sys
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def ejecutar_sql_tenant(sql, descripcion="", tenant_schema="dev"):
    """Ejecuta SQL en un tenant específico de forma segura"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}")
            cursor.execute(sql)
        print(f"✅ {descripcion}")
        return True
    except Exception as e:
        print(f"❌ {descripcion}: {str(e)}")
        return False

def setup_sat_tenant(tenant_schema="dev"):
    """Configura las tablas SAT en un tenant específico"""
    
    print(f"🦷 CONFIGURANDO TABLAS SAT PARA TENANT: {tenant_schema.upper()}")
    print("=" * 60)
    
    # Establecer el esquema del tenant
    with connection.cursor() as cursor:
        cursor.execute(f"SET search_path TO {tenant_schema}")
    
    # Paso 1: Limpiar referencias SAT conflictivas
    print("\n📋 Paso 1: Limpiando referencias SAT existentes...")
    
    sqls_limpieza = [
        ("UPDATE core_pago SET forma_pago_sat_id = NULL WHERE forma_pago_sat_id IS NOT NULL", 
         "Limpiar referencias forma_pago_sat en core_pago"),
        ("UPDATE core_pago SET metodo_sat_id = NULL WHERE metodo_sat_id IS NOT NULL", 
         "Limpiar referencias metodo_sat en core_pago"),
        ("UPDATE core_datosfiscales SET uso_cfdi_id = NULL WHERE uso_cfdi_id IS NOT NULL", 
         "Limpiar referencias uso_cfdi en core_datosfiscales"),
        ("UPDATE core_datosfiscales SET regimen_fiscal_id = NULL WHERE regimen_fiscal_id IS NOT NULL", 
         "Limpiar referencias regimen_fiscal en core_datosfiscales"),
    ]
    
    for sql, descripcion in sqls_limpieza:
        ejecutar_sql_tenant(sql, descripcion, tenant_schema)
    
    # Paso 2: Crear/Verificar tablas SAT
    print("\n📋 Paso 2: Verificando/Creando tablas SAT...")
    
    # Crear tabla SatFormaPago
    sql_forma_pago = """
    CREATE TABLE IF NOT EXISTS core_satformapago (
        id BIGSERIAL PRIMARY KEY,
        codigo VARCHAR(3) UNIQUE NOT NULL,
        descripcion VARCHAR(255) NOT NULL,
        activo BOOLEAN DEFAULT TRUE
    );
    """
    ejecutar_sql_tenant(sql_forma_pago, "Tabla core_satformapago verificada/creada", tenant_schema)
    
    # Crear tabla SatMetodoPago
    sql_metodo_pago = """
    CREATE TABLE IF NOT EXISTS core_satmetodopago (
        id BIGSERIAL PRIMARY KEY,
        codigo VARCHAR(3) UNIQUE NOT NULL,
        descripcion VARCHAR(255) NOT NULL,
        activo BOOLEAN DEFAULT TRUE
    );
    """
    ejecutar_sql_tenant(sql_metodo_pago, "Tabla core_satmetodopago verificada/creada", tenant_schema)
    
    # Crear tabla SatRegimenFiscal
    sql_regimen = """
    CREATE TABLE IF NOT EXISTS core_satregimenfiscal (
        id BIGSERIAL PRIMARY KEY,
        codigo VARCHAR(3) UNIQUE NOT NULL,
        descripcion VARCHAR(255) NOT NULL,
        persona_fisica BOOLEAN DEFAULT TRUE,
        persona_moral BOOLEAN DEFAULT TRUE,
        activo BOOLEAN DEFAULT TRUE
    );
    """
    ejecutar_sql_tenant(sql_regimen, "Tabla core_satregimenfiscal verificada/creada", tenant_schema)
    
    # Crear tabla SatUsoCFDI
    sql_uso_cfdi = """
    CREATE TABLE IF NOT EXISTS core_satusocfdi (
        id BIGSERIAL PRIMARY KEY,
        codigo VARCHAR(3) UNIQUE NOT NULL,
        descripcion VARCHAR(255) NOT NULL,
        persona_fisica BOOLEAN DEFAULT TRUE,
        persona_moral BOOLEAN DEFAULT TRUE,
        activo BOOLEAN DEFAULT TRUE
    );
    """
    ejecutar_sql_tenant(sql_uso_cfdi, "Tabla core_satusocfdi verificada/creada", tenant_schema)
    
    # Paso 3: Poblar catálogos SAT
    print("\n📋 Paso 3: Poblando catálogos SAT básicos...")
    
    # Limpiar datos existentes y reinsertar
    ejecutar_sql_tenant("DELETE FROM core_satformapago", "Limpiar datos existentes en formas de pago", tenant_schema)
    ejecutar_sql_tenant("DELETE FROM core_satmetodopago", "Limpiar datos existentes en métodos de pago", tenant_schema)
    ejecutar_sql_tenant("DELETE FROM core_satregimenfiscal", "Limpiar datos existentes en regímenes fiscales", tenant_schema)
    ejecutar_sql_tenant("DELETE FROM core_satusocfdi", "Limpiar datos existentes en usos CFDI", tenant_schema)
    
    # Formas de pago
    formas_pago = [
        ("'01'", "'Efectivo'"),
        ("'03'", "'Transferencia electrónica de fondos'"),
        ("'04'", "'Tarjeta de crédito'"),
        ("'28'", "'Tarjeta de débito'"),
    ]
    
    for codigo, descripcion in formas_pago:
        sql = f"INSERT INTO core_satformapago (codigo, descripcion) VALUES ({codigo}, {descripcion});"
        ejecutar_sql_tenant(sql, f"Forma de pago {codigo} insertada", tenant_schema)
    
    # Métodos de pago
    metodos_pago = [
        ("'PUE'", "'Pago en una sola exhibición'"),
        ("'PPD'", "'Pago en parcialidades o diferido'"),
    ]
    
    for codigo, descripcion in metodos_pago:
        sql = f"INSERT INTO core_satmetodopago (codigo, descripcion) VALUES ({codigo}, {descripcion});"
        ejecutar_sql_tenant(sql, f"Método de pago {codigo} insertado", tenant_schema)
    
    # Regímenes fiscales básicos
    regimenes = [
        ("'612'", "'Personas Físicas con Actividades Empresariales y Profesionales'"),
        ("'601'", "'General de Ley Personas Morales'"),
        ("'605'", "'Sueldos y Salarios e Ingresos Asimilados a Salarios'"),
    ]
    
    for codigo, descripcion in regimenes:
        sql = f"INSERT INTO core_satregimenfiscal (codigo, descripcion) VALUES ({codigo}, {descripcion});"
        ejecutar_sql_tenant(sql, f"Régimen fiscal {codigo} insertado", tenant_schema)
    
    # Usos CFDI básicos
    usos_cfdi = [
        ("'G01'", "'Adquisición de mercancías'"),
        ("'G03'", "'Gastos en general'"),
        ("'D01'", "'Honorarios médicos, dentales y gastos hospitalarios'"),
    ]
    
    for codigo, descripcion in usos_cfdi:
        sql = f"INSERT INTO core_satusocfdi (codigo, descripcion) VALUES ({codigo}, {descripcion});"
        ejecutar_sql_tenant(sql, f"Uso CFDI {codigo} insertado", tenant_schema)
    
    # Paso 4: Agregar columnas SAT si no existen
    print("\n📋 Paso 4: Verificando columnas SAT en core_pago...")
    
    # Verificar y agregar columnas SAT a core_pago
    sqls_columnas = [
        ("ALTER TABLE core_pago ADD COLUMN IF NOT EXISTS forma_pago_sat_id BIGINT REFERENCES core_satformapago(id) ON DELETE SET NULL",
         "Columna forma_pago_sat_id agregada/verificada"),
        ("ALTER TABLE core_pago ADD COLUMN IF NOT EXISTS metodo_sat_id BIGINT REFERENCES core_satmetodopago(id) ON DELETE SET NULL",
         "Columna metodo_sat_id agregada/verificada"),
        ("ALTER TABLE core_datosfiscales ADD COLUMN IF NOT EXISTS regimen_fiscal_id BIGINT REFERENCES core_satregimenfiscal(id) ON DELETE SET NULL",
         "Columna regimen_fiscal_id agregada/verificada en datos fiscales"),
    ]
    
    for sql, descripcion in sqls_columnas:
        ejecutar_sql_tenant(sql, descripcion, tenant_schema)
    
    # Paso 5: Crear índices para mejor rendimiento
    print("\n📋 Paso 5: Creando índices...")
    
    indices = [
        ("CREATE INDEX IF NOT EXISTS idx_satformapago_codigo ON core_satformapago(codigo)", "Índice en forma_pago.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_satmetodopago_codigo ON core_satmetodopago(codigo)", "Índice en metodo_pago.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_satregimen_codigo ON core_satregimenfiscal(codigo)", "Índice en regimen_fiscal.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_satusocfdi_codigo ON core_satusocfdi(codigo)", "Índice en uso_cfdi.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_pago_forma_sat ON core_pago(forma_pago_sat_id)", "Índice en pago.forma_pago_sat_id"),
        ("CREATE INDEX IF NOT EXISTS idx_pago_metodo_sat ON core_pago(metodo_sat_id)", "Índice en pago.metodo_sat_id"),
    ]
    
    for sql, descripcion in indices:
        ejecutar_sql_tenant(sql, descripcion, tenant_schema)
    
    print(f"\n🎯 ¡Configuración SAT completada para tenant {tenant_schema.upper()}!")
    print("\n✨ Resumen:")
    print(f"   • Tablas SAT configuradas en esquema '{tenant_schema}'")
    print("   • Columnas SAT agregadas a core_pago")
    print("   • Catálogos básicos insertados (formas, métodos, regímenes, usos)")
    print("   • Índices de rendimiento creados")
    print("   • Referencias conflictivas limpiadas")

if __name__ == '__main__':
    tenant = sys.argv[1] if len(sys.argv) > 1 else 'dev'
    setup_sat_tenant(tenant)
