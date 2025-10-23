#!/usr/bin/env python
"""
Script para migrar datos base (catálogos) entre tenants.

Migra SOLO datos de configuración base necesarios para operación:
- Especialidades
- Servicios
- Categorías de Historial Clínico
- Preguntas de Historial Clínico
- Consentimientos Informados (plantillas)

NO migra datos operacionales (pacientes, citas, pagos, etc.)

Uso:
    python migrate_base_data.py --from demo --to sgdental [--dry-run]
"""

import os
import sys
import django
import argparse
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.db import connection, transaction
from tenants.models import Clinica
from core import models


class TenantDataMigrator:
    """Migrador de datos base entre tenants"""

    def __init__(self, source_tenant_name, target_tenant_name, dry_run=False):
        self.source_tenant_name = source_tenant_name
        self.target_tenant_name = target_tenant_name
        self.dry_run = dry_run
        self.stats = {
            'especialidades': 0,
            'servicios': 0,
            'categorias': 0,
            'preguntas': 0,
            'consentimientos': 0,
        }

    def log(self, message, level='INFO'):
        """Log con formato"""
        prefix = {
            'INFO': '✓',
            'WARNING': '⚠',
            'ERROR': '✗',
            'SUCCESS': '✅',
        }.get(level, 'ℹ')
        print(f"{prefix} {message}")

    def connect_to_tenant(self, tenant_name):
        """Conecta a un tenant específico"""
        try:
            tenant = Clinica.objects.get(schema_name=tenant_name)
            connection.set_tenant(tenant)
            return tenant
        except Clinica.DoesNotExist:
            raise ValueError(f"Tenant '{tenant_name}' no existe")

    def migrate_especialidades(self, source_data):
        """Migra especialidades"""
        self.log(f"\n📋 Migrando Especialidades ({len(source_data)} registros)...")

        for esp_data in source_data:
            # Verificar si ya existe (por nombre)
            existing = models.Especialidad.objects.filter(nombre=esp_data['nombre']).first()

            if existing:
                self.log(f"   ⏭️  Ya existe: {esp_data['nombre']}", 'WARNING')
            else:
                if not self.dry_run:
                    models.Especialidad.objects.create(**esp_data)
                self.log(f"   ➕ Creada: {esp_data['nombre']}")
                self.stats['especialidades'] += 1

    def migrate_servicios(self, source_data, especialidad_map):
        """Migra servicios"""
        self.log(f"\n💰 Migrando Servicios ({len(source_data)} registros)...")

        for serv_data in source_data:
            # Verificar si ya existe (por nombre)
            existing = models.Servicio.objects.filter(nombre=serv_data['nombre']).first()

            if existing:
                self.log(f"   ⏭️  Ya existe: {serv_data['nombre']}", 'WARNING')
            else:
                # Mapear especialidad si existe
                if serv_data.get('especialidad_id'):
                    source_esp_id = serv_data['especialidad_id']
                    serv_data['especialidad_id'] = especialidad_map.get(source_esp_id)

                if not self.dry_run:
                    models.Servicio.objects.create(**serv_data)
                self.log(f"   ➕ Creado: {serv_data['nombre']} - ${serv_data['precio']}")
                self.stats['servicios'] += 1

    def migrate_categorias_historial(self, source_data):
        """Migra categorías de historial clínico"""
        self.log(f"\n📂 Migrando Categorías de Historial ({len(source_data)} registros)...")

        categoria_map = {}

        for cat_data in source_data:
            source_id = cat_data.pop('id')

            # Verificar si ya existe (por nombre)
            existing = models.CategoriaHistorial.objects.filter(nombre=cat_data['nombre']).first()

            if existing:
                self.log(f"   ⏭️  Ya existe: {cat_data['nombre']}", 'WARNING')
                categoria_map[source_id] = existing.id
            else:
                if not self.dry_run:
                    nueva = models.CategoriaHistorial.objects.create(**cat_data)
                    categoria_map[source_id] = nueva.id
                else:
                    # En dry-run, simular el ID con el source_id
                    categoria_map[source_id] = source_id

                self.log(f"   ➕ Creada: {cat_data['nombre']} (orden: {cat_data['orden']})")
                self.stats['categorias'] += 1

        return categoria_map

    def migrate_preguntas_historial(self, source_data, categoria_map):
        """Migra preguntas de historial clínico"""
        self.log(f"\n❓ Migrando Preguntas de Historial ({len(source_data)} registros)...")

        for preg_data in source_data:
            # Mapear categoría
            source_cat_id = preg_data['categoria_id']
            target_cat_id = categoria_map.get(source_cat_id)

            if not target_cat_id:
                self.log(f"   ⏭️  Categoría no encontrada para: {preg_data['texto'][:50]}...", 'WARNING')
                continue

            preg_data['categoria_id'] = target_cat_id

            # Verificar si ya existe (por texto y categoría)
            if not self.dry_run:
                existing = models.PreguntaHistorial.objects.filter(
                    texto=preg_data['texto'],
                    categoria_id=preg_data['categoria_id']
                ).first()

                if existing:
                    self.log(f"   ⏭️  Ya existe: {preg_data['texto'][:50]}...", 'WARNING')
                    continue

                models.PreguntaHistorial.objects.create(**preg_data)

            self.log(f"   ➕ Creada: {preg_data['texto'][:60]}...")
            self.stats['preguntas'] += 1

    def migrate_consentimientos(self, source_data):
        """Migra consentimientos informados (plantillas)"""
        self.log(f"\n📄 Migrando Consentimientos Informados ({len(source_data)} registros)...")

        for cons_data in source_data:
            # Verificar si ya existe (por título)
            existing = models.ConsentimientoInformado.objects.filter(titulo=cons_data['titulo']).first()

            if existing:
                self.log(f"   ⏭️  Ya existe: {cons_data['titulo']}", 'WARNING')
            else:
                if not self.dry_run:
                    models.ConsentimientoInformado.objects.create(**cons_data)
                self.log(f"   ➕ Creado: {cons_data['titulo']}")
                self.stats['consentimientos'] += 1

    def extract_data_from_source(self):
        """Extrae datos del tenant origen"""
        self.log(f"\n🔍 Extrayendo datos de tenant '{self.source_tenant_name}'...")

        source_tenant = self.connect_to_tenant(self.source_tenant_name)
        self.log(f"   Conectado a: {source_tenant.nombre}")

        data = {
            'especialidades': [],
            'servicios': [],
            'categorias': [],
            'preguntas': [],
            'consentimientos': [],
        }

        # Especialidades
        for esp in models.Especialidad.objects.all():
            data['especialidades'].append({
                'id': esp.id,
                'nombre': esp.nombre,
            })

        # Servicios
        for serv in models.Servicio.objects.all():
            data['servicios'].append({
                'nombre': serv.nombre,
                'descripcion': serv.descripcion,
                'precio': serv.precio,
                'duracion_minutos': serv.duracion_minutos,
                'especialidad_id': serv.especialidad_id if serv.especialidad else None,
                'activo': serv.activo,
            })

        # Categorías de historial
        for cat in models.CategoriaHistorial.objects.all():
            data['categorias'].append({
                'id': cat.id,
                'nombre': cat.nombre,
                'descripcion': cat.descripcion,
                'icono': cat.icono,
                'color': cat.color,
                'orden': cat.orden,
                'activa': cat.activa,
            })

        # Preguntas de historial
        for preg in models.PreguntaHistorial.objects.all():
            data['preguntas'].append({
                'categoria_id': preg.categoria_id,
                'texto': preg.texto,
                'subtitulo': preg.subtitulo,
                'tipo': preg.tipo,
                'opciones': preg.opciones,
                'orden': preg.orden,
                'obligatoria': preg.obligatoria,
                'importancia': preg.importancia,
                'activa': preg.activa,
                'requiere_seguimiento': preg.requiere_seguimiento,
                'alerta_cofepris': preg.alerta_cofepris,
            })

        # Consentimientos informados
        for cons in models.ConsentimientoInformado.objects.all():
            data['consentimientos'].append({
                'titulo': cons.titulo,
                'contenido_html': cons.contenido_html,
                'version': cons.version,
                'activo': cons.activo,
                'requiere_firma': cons.requiere_firma,
            })

        self.log(f"\n📊 Datos extraídos:")
        self.log(f"   - Especialidades: {len(data['especialidades'])}")
        self.log(f"   - Servicios: {len(data['servicios'])}")
        self.log(f"   - Categorías: {len(data['categorias'])}")
        self.log(f"   - Preguntas: {len(data['preguntas'])}")
        self.log(f"   - Consentimientos: {len(data['consentimientos'])}")

        return data

    def migrate(self):
        """Ejecuta la migración completa"""
        try:
            self.log("=" * 70)
            self.log(f"MIGRACIÓN DE DATOS BASE", 'INFO')
            self.log(f"Origen: {self.source_tenant_name}")
            self.log(f"Destino: {self.target_tenant_name}")
            self.log(f"Modo: {'DRY RUN (sin cambios)' if self.dry_run else 'PRODUCCIÓN'}")
            self.log("=" * 70)

            # Extraer datos del origen
            source_data = self.extract_data_from_source()

            # Conectar al destino
            self.log(f"\n🎯 Conectando a tenant destino '{self.target_tenant_name}'...")
            target_tenant = self.connect_to_tenant(self.target_tenant_name)
            self.log(f"   Conectado a: {target_tenant.nombre}")

            # Ejecutar migraciones en orden (respetando dependencias)
            if not self.dry_run:
                with transaction.atomic():
                    # 1. Especialidades (sin dependencias)
                    self.migrate_especialidades(source_data['especialidades'])

                    # Crear mapa de especialidades
                    especialidad_map = {}
                    for esp_data in source_data['especialidades']:
                        target_esp = models.Especialidad.objects.filter(nombre=esp_data['nombre']).first()
                        if target_esp:
                            especialidad_map[esp_data['id']] = target_esp.id

                    # 2. Servicios (dependen de especialidades)
                    self.migrate_servicios(source_data['servicios'], especialidad_map)

                    # 3. Categorías de historial (sin dependencias)
                    categoria_map = self.migrate_categorias_historial(source_data['categorias'])

                    # 4. Preguntas de historial (dependen de categorías)
                    self.migrate_preguntas_historial(source_data['preguntas'], categoria_map)

                    # 5. Consentimientos (sin dependencias)
                    self.migrate_consentimientos(source_data['consentimientos'])
            else:
                # Modo dry-run: simular sin transacción
                self.migrate_especialidades(source_data['especialidades'])
                self.migrate_servicios(source_data['servicios'], {})
                self.migrate_categorias_historial(source_data['categorias'])
                self.migrate_preguntas_historial(source_data['preguntas'], {})
                self.migrate_consentimientos(source_data['consentimientos'])

            # Resumen final
            self.log("\n" + "=" * 70)
            self.log("RESUMEN DE MIGRACIÓN", 'SUCCESS')
            self.log("=" * 70)
            self.log(f"✅ Especialidades migradas: {self.stats['especialidades']}")
            self.log(f"✅ Servicios migrados: {self.stats['servicios']}")
            self.log(f"✅ Categorías migradas: {self.stats['categorias']}")
            self.log(f"✅ Preguntas migradas: {self.stats['preguntas']}")
            self.log(f"✅ Consentimientos migrados: {self.stats['consentimientos']}")

            total_migrados = sum(self.stats.values())
            self.log(f"\n🎉 Total de registros migrados: {total_migrados}")

            if self.dry_run:
                self.log("\n⚠️  Modo DRY RUN: No se realizaron cambios reales", 'WARNING')
            else:
                self.log("\n✅ Migración completada exitosamente", 'SUCCESS')

        except Exception as e:
            self.log(f"\n❌ ERROR durante la migración: {str(e)}", 'ERROR')
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Migrar datos base (catálogos) entre tenants'
    )
    parser.add_argument(
        '--from',
        dest='source',
        required=True,
        help='Tenant origen (ej: demo)'
    )
    parser.add_argument(
        '--to',
        dest='target',
        required=True,
        help='Tenant destino (ej: sgdental)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Modo de prueba (no realiza cambios)'
    )

    args = parser.parse_args()

    # Confirmar antes de ejecutar
    if not args.dry_run:
        print(f"\n⚠️  ADVERTENCIA: Se migrarán datos de '{args.source}' a '{args.target}'")
        confirm = input("¿Desea continuar? (yes/no): ")
        if confirm.lower() not in ['yes', 'y', 'si', 's']:
            print("❌ Operación cancelada")
            sys.exit(0)

    # Ejecutar migración
    migrator = TenantDataMigrator(args.source, args.target, args.dry_run)
    migrator.migrate()


if __name__ == '__main__':
    main()
