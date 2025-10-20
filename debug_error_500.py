#!/usr/bin/env python
"""
Script para diagnosticar el error 500 en el sistema.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Clinica

def diagnosticar_error():
    """Diagnostica posibles causas del error 500."""
    
    print("🔍 Diagnosticando error 500...")
    
    # 1. Verificar tenant demo
    try:
        clinica_demo = Clinica.objects.get(schema_name='demo')
        print(f"✅ Tenant demo encontrado: {clinica_demo.nombre}")
    except Exception as e:
        print(f"❌ Error con tenant demo: {e}")
        return
    
    with tenant_context(clinica_demo):
        # 2. Verificar modelos de permisos
        try:
            from core.models_permissions import ModuloSistema, SubmenuItem, PermisoRol
            
            modulos = ModuloSistema.objects.count()
            submenus = SubmenuItem.objects.count()
            permisos = PermisoRol.objects.count()
            
            print(f"✅ Modelos de permisos OK: {modulos} módulos, {submenus} submenús, {permisos} permisos")
        except Exception as e:
            print(f"❌ Error con modelos de permisos: {e}")
            return
        
        # 3. Verificar context processor
        try:
            from core.permissions_utils import get_menu_for_user
            from django.contrib.auth.models import User
            
            # Probar con superusuario
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                menu = get_menu_for_user(admin_user)
                print(f"✅ Menú dinámico para admin OK: {len(menu)} módulos")
            else:
                print("⚠️ No hay superusuario para probar")
        except Exception as e:
            print(f"❌ Error con menú dinámico: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 4. Verificar template
        try:
            from django.template.loader import get_template
            template = get_template('core/partials/menu_dinamico.html')
            print("✅ Template de menú dinámico encontrado")
        except Exception as e:
            print(f"❌ Error con template: {e}")
            return
        
        # 5. Verificar vista dashboard
        try:
            from core.views import DashboardView
            print("✅ Vista Dashboard importada correctamente")
        except Exception as e:
            print(f"❌ Error con vista Dashboard: {e}")
            return
        
        # 6. Probar renderizado de menú con usuario real
        try:
            from django.contrib.auth.models import User
            usuarios_test = ['admin_test', 'dentista_test', 'recepcionista_test']
            
            for username in usuarios_test:
                try:
                    user = User.objects.get(username=username)
                    menu = get_menu_for_user(user)
                    print(f"✅ Menú para {username}: {len(menu)} módulos")
                except User.DoesNotExist:
                    print(f"⚠️ Usuario {username} no existe")
                except Exception as e:
                    print(f"❌ Error generando menú para {username}: {e}")
        except Exception as e:
            print(f"❌ Error general con usuarios: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    diagnosticar_error()
