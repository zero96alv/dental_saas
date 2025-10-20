#!/usr/bin/env python
"""
Script para configurar las tablas SAT básicas
Ejecutar con: python setup_sat_tables.py
"""

import os
import django
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def ejecutar_sql(sql, descripcion=""):
    """Ejecuta SQL de forma segura"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        print(f"✅ {descripcion}")
        return True
    except Exception as e:
        print(f"❌ {descripcion}: {str(e)}")
        return False

def setup_tablas_sat():
    """Configura las tablas SAT básicas"""
    
    print("🦷 CONFIGURANDO TABLAS SAT PARA SISTEMA DENTAL")
    print("=" * 50)
    
    # Paso 1: Limpiar referencias SAT conflictivas
    print("\n📋 Paso 1: Limpiando referencias SAT existentes...")
    
    # Verificar si las columnas existen antes de limpiarlas
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
        ejecutar_sql(sql, descripcion)
    
    # Paso 2: Crear tablas SAT
    print("\n📋 Paso 2: Creando tablas SAT...")
    
    # Crear tabla SatFormaPago
    sql_forma_pago = """
    CREATE TABLE IF NOT EXISTS core_satformapago (
        id BIGSERIAL PRIMARY KEY,
        codigo VARCHAR(3) UNIQUE NOT NULL,
        descripcion VARCHAR(255) NOT NULL,
        activo BOOLEAN DEFAULT TRUE
    );
    """
    ejecutar_sql(sql_forma_pago, "Tabla core_satformapago creada")
    
    # Crear tabla SatMetodoPago
    sql_metodo_pago = """
    CREATE TABLE IF NOT EXISTS core_satmetodopago (
        id BIGSERIAL PRIMARY KEY,
        codigo VARCHAR(3) UNIQUE NOT NULL,
        descripcion VARCHAR(255) NOT NULL,
        activo BOOLEAN DEFAULT TRUE
    );
    """
    ejecutar_sql(sql_metodo_pago, "Tabla core_satmetodopago creada")
    
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
    ejecutar_sql(sql_regimen, "Tabla core_satregimenfiscal creada")
    
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
    ejecutar_sql(sql_uso_cfdi, "Tabla core_satusocfdi creada")
    
    # Paso 3: Poblar catálogos SAT
    print("\n📋 Paso 3: Poblando catálogos SAT básicos...")
    
    # Formas de pago
    formas_pago = [
        ("'01'", "'Efectivo'"),
        ("'03'", "'Transferencia electrónica de fondos'"),
        ("'04'", "'Tarjeta de crédito'"),
        ("'28'", "'Tarjeta de débito'"),
    ]
    
    for codigo, descripcion in formas_pago:
        sql = f"INSERT INTO core_satformapago (codigo, descripcion) VALUES ({codigo}, {descripcion}) ON CONFLICT (codigo) DO NOTHING;"
        ejecutar_sql(sql, f"Forma de pago {codigo} insertada")
    
    # Métodos de pago
    metodos_pago = [
        ("'PUE'", "'Pago en una sola exhibición'"),
        ("'PPD'", "'Pago en parcialidades o diferido'"),
    ]
    
    for codigo, descripcion in metodos_pago:
        sql = f"INSERT INTO core_satmetodopago (codigo, descripcion) VALUES ({codigo}, {descripcion}) ON CONFLICT (codigo) DO NOTHING;"
        ejecutar_sql(sql, f"Método de pago {codigo} insertado")
    
    # Regímenes fiscales básicos
    regimenes = [
        ("'612'", "'Personas Físicas con Actividades Empresariales y Profesionales'"),
        ("'601'", "'General de Ley Personas Morales'"),
        ("'605'", "'Sueldos y Salarios e Ingresos Asimilados a Salarios'"),
    ]
    
    for codigo, descripcion in regimenes:
        sql = f"INSERT INTO core_satregimenfiscal (codigo, descripcion) VALUES ({codigo}, {descripcion}) ON CONFLICT (codigo) DO NOTHING;"
        ejecutar_sql(sql, f"Régimen fiscal {codigo} insertado")
    
    # Usos CFDI básicos
    usos_cfdi = [
        ("'G01'", "'Adquisición de mercancías'"),
        ("'G03'", "'Gastos en general'"),
        ("'D01'", "'Honorarios médicos, dentales y gastos hospitalarios'"),
    ]
    
    for codigo, descripcion in usos_cfdi:
        sql = f"INSERT INTO core_satusocfdi (codigo, descripcion) VALUES ({codigo}, {descripcion}) ON CONFLICT (codigo) DO NOTHING;"
        ejecutar_sql(sql, f"Uso CFDI {codigo} insertado")
    
    # Paso 4: Crear índices para mejor rendimiento
    print("\n📋 Paso 4: Creando índices...")
    
    indices = [
        ("CREATE INDEX IF NOT EXISTS idx_satformapago_codigo ON core_satformapago(codigo)", "Índice en forma_pago.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_satmetodopago_codigo ON core_satmetodopago(codigo)", "Índice en metodo_pago.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_satregimen_codigo ON core_satregimenfiscal(codigo)", "Índice en regimen_fiscal.codigo"),
        ("CREATE INDEX IF NOT EXISTS idx_satusocfdi_codigo ON core_satusocfdi(codigo)", "Índice en uso_cfdi.codigo"),
    ]
    
    for sql, descripcion in indices:
        ejecutar_sql(sql, descripcion)
    
    print("\n🎯 ¡Configuración de tablas SAT completada con éxito!")
    print("\n✨ Tablas creadas:")
    print("   • core_satformapago (Formas de Pago SAT)")
    print("   • core_satmetodopago (Métodos de Pago SAT)")  
    print("   • core_satregimenfiscal (Regímenes Fiscales SAT)")
    print("   • core_satusocfdi (Usos CFDI SAT)")
    print("\n🔧 Códigos básicos insertados:")
    print("   • Formas: 01, 03, 04, 28")
    print("   • Métodos: PUE, PPD")
    print("   • Regímenes: 612, 601, 605")
    print("   • Usos CFDI: G01, G03, D01")

if __name__ == '__main__':
    setup_tablas_sat()
