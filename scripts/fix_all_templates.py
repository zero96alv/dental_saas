#!/usr/bin/env python3
"""
Script para actualizar todos los templates HTML para usar tenant_url en lugar de url.
Esto asegura que todos los enlaces mantengan el prefijo del tenant.
"""
import os
import re

def fix_template(filepath):
    """Actualiza un template para usar tenant_url"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Verificar si ya tiene tenant_urls cargado
    has_tenant_urls = '{% load tenant_urls %}' in content
    has_extends = '{% extends' in content
    has_url_tags = '{% url' in content and '{% tenant_url' not in content
    
    if not has_url_tags:
        return False  # No necesita cambios
    
    # Agregar {% load tenant_urls %} si no existe
    if not has_tenant_urls:
        if has_extends:
            # Insertar después de {% extends %}
            content = re.sub(
                r'({% extends [^%]+%})',
                r'\1\n{% load tenant_urls %}',
                content,
                count=1
            )
        else:
            # Insertar al principio
            content = '{% load tenant_urls %}\n' + content
    
    # Reemplazar {% url con {% tenant_url
    content = content.replace('{% url ', '{% tenant_url ')
    
    # Si hubo cambios, guardar
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Procesa todos los templates en core/templates"""
    templates_dir = 'core/templates'
    count = 0
    
    for root, dirs, files in os.walk(templates_dir):
        for filename in files:
            if filename.endswith('.html'):
                filepath = os.path.join(root, filename)
                if fix_template(filepath):
                    count += 1
                    print(f"✓ {filepath}")
    
    print(f"\n✅ {count} templates actualizados")

if __name__ == '__main__':
    main()
