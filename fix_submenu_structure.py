#!/usr/bin/env python
"""
Script para reclasificar la estructura de submenús con URLs apropiadas para el menú.
SOLUCIÓN DEFINITIVA: En lugar de parches temporales, rediseñamos la estructura.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Clinica

def reclasificar_estructura_submenus():
    """Reclasifica y mejora la estructura de submenús para el menú dinámico."""
    
    print("🔧 Reclasificando estructura de submenús...")
    
    # Obtener el tenant demo
    try:
        clinica_demo = Clinica.objects.get(schema_name='demo')
        print(f"✅ Tenant demo encontrado: {clinica_demo.nombre}")
    except Exception as e:
        print(f"❌ Error con tenant demo: {e}")
        return
    
    with tenant_context(clinica_demo):
        from core.models_permissions import ModuloSistema, SubmenuItem
        
        print("🔄 Aplicando correcciones específicas...")
        
        # 1. Corregir "Historial Clínico" -> debe ir a lista de pacientes
        try:
            historial_submenu = SubmenuItem.objects.get(url_name='core:paciente_history')
            historial_submenu.nombre = "Gestión de Pacientes"
            historial_submenu.url_name = "core:paciente_list"
            historial_submenu.descripcion = "Gestión completa de pacientes e historiales clínicos"
            historial_submenu.save()
            print(f"✅ Corregido: {historial_submenu.modulo.nombre} - {historial_submenu.nombre}")
        except SubmenuItem.DoesNotExist:
            print("⚠️  Submenu 'core:paciente_history' no encontrado")
        
        # 2. Corregir "Horarios Laborales" -> debe ir a lista de dentistas
        try:
            horario_submenu = SubmenuItem.objects.get(url_name='core:gestionar_horario')
            horario_submenu.nombre = "Gestión de Horarios"
            horario_submenu.url_name = "core:dentista_list"
            horario_submenu.descripcion = "Gestión de horarios laborales del personal"
            horario_submenu.save()
            print(f"✅ Corregido: {horario_submenu.modulo.nombre} - {horario_submenu.nombre}")
        except SubmenuItem.DoesNotExist:
            print("⚠️  Submenu 'core:gestionar_horario' no encontrado")
        
        # 3. Verificar que todas las URLs ahora funcionan
        print("\n🔍 Verificando URLs corregidas...")
        from django.urls import reverse, NoReverseMatch
        
        submenus_problematicos = 0
        submenus_total = 0
        
        for submenu in SubmenuItem.objects.filter(activo=True):
            submenus_total += 1
            try:
                url = reverse(submenu.url_name)
                print(f"✅ {submenu.modulo.nombre} - {submenu.nombre}: {submenu.url_name} -> {url}")
            except NoReverseMatch as e:
                submenus_problematicos += 1
                print(f"❌ {submenu.modulo.nombre} - {submenu.nombre}: {submenu.url_name} -> ERROR")
        
        # 4. Resumen
        print(f"\n📊 RESULTADO DE LA RECLASIFICACIÓN:")
        print(f"   • Total submenús: {submenus_total}")
        print(f"   • Submenús problemáticos: {submenus_problematicos}")
        print(f"   • Submenús funcionales: {submenus_total - submenus_problematicos}")
        
        if submenus_problematicos == 0:
            print("\n🎉 ¡ÉXITO! Todos los submenús ahora tienen URLs funcionales")
            print("✅ El menú dinámico debería funcionar perfectamente")
            return True
        else:
            print(f"\n⚠️  Aún hay {submenus_problematicos} submenús con problemas")
            return False

if __name__ == '__main__':
    print("🚀 Iniciando reclasificación de estructura de submenús...")
    success = reclasificar_estructura_submenus()
    
    if success:
        print("\n✅ ¡Reclasificación completada exitosamente!")
        print("💡 El sistema de menú dinámico ahora debería funcionar sin errores.")
    else:
        print("\n❌ Algunos problemas persisten.")
        sys.exit(1)
