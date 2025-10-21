#!/usr/bin/env python
"""
Script de configuración post-deploy para DigitalOcean App Platform
Ejecuta setup inicial de tenants y dominios
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

def setup_digitalocean():
    """
    Configuración inicial para DigitalOcean App Platform
    """
    print("🚀 Iniciando configuración para DigitalOcean App Platform...")
    
    # Importar modelos después de setup de Django
    from tenants.models import Clinica, Domain
    from django.contrib.auth.models import User, Group
    from django.db import connection
    
    try:
        # 1. Crear tenant público
        print("📋 Configurando tenant público...")
        public_tenant, created = Clinica.objects.get_or_create(
            schema_name='public',
            defaults={'nombre': 'Public Schema'}
        )
        if created:
            print("✅ Tenant público creado")
        else:
            print("ℹ️ Tenant público ya existe")
        
        # 2. Crear clínicas tenant
        clinicas_config = [
            {'schema_name': 'demo', 'nombre': 'Clínica Demo'},
            {'schema_name': 'sgdental', 'nombre': 'SG Dental'},
            {'schema_name': 'cgdental', 'nombre': 'CG Dental Care'}
        ]
        
        print("\n🏥 Configurando clínicas tenant...")
        for config in clinicas_config:
            tenant, created = Clinica.objects.get_or_create(
                schema_name=config['schema_name'],
                defaults={'nombre': config['nombre']}
            )
            
            if created:
                print(f"✅ Clínica {config['nombre']} creada")
            else:
                print(f"ℹ️ Clínica {config['nombre']} ya existe")
        
        # 3. Configurar usuarios admin para cada clínica
        print("\n👤 Configurando usuarios admin...")
        for config in clinicas_config:
            try:
                tenant = Clinica.objects.get(schema_name=config['schema_name'])
                connection.set_tenant(tenant)
                
                # Crear grupos estándar
                admin_group, _ = Group.objects.get_or_create(name="Administrador")
                dentist_group, _ = Group.objects.get_or_create(name="Dentista")
                recep_group, _ = Group.objects.get_or_create(name="Recepcionista")
                
                # Crear usuario admin
                if not User.objects.filter(username='admin').exists():
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email=f'admin@{config["schema_name"]}.dental-saas.com',
                        password='DemoAdmin2025!'
                    )
                    admin_user.groups.add(admin_group)
                    print(f"✅ Usuario admin creado para {config['nombre']}")
                else:
                    print(f"ℹ️ Usuario admin ya existe en {config['nombre']}")
                    
            except Exception as e:
                print(f"⚠️ Error configurando usuario en {config['schema_name']}: {e}")
        
        print("\n🎉 Configuración completada exitosamente!")
        print("\nCredenciales de acceso:")
        print("Usuario: admin")
        print("Contraseña: DemoAdmin2025!")
        print("\nURLs de las clínicas (usando dominio temporal de DigitalOcean):")
        print("- Demo: https://[tu-app].ondigitalocean.app/ (con parámetro ?tenant=demo)")
        print("- SG Dental: https://[tu-app].ondigitalocean.app/ (con parámetro ?tenant=sgdental)")
        print("- CG Dental: https://[tu-app].ondigitalocean.app/ (con parámetro ?tenant=cgdental)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        return False

if __name__ == "__main__":
    success = setup_digitalocean()
    sys.exit(0 if success else 1)