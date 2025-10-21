#!/usr/bin/env python3
"""
Script para agregar TenantSuccessUrlMixin a todas las vistas CreateView, UpdateView, DeleteView
"""
import re

def fix_views_file():
    """Actualiza todas las vistas CBV para incluir TenantSuccessUrlMixin"""
    filepath = 'core/views.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Patrón para encontrar clases que heredan de CreateView, UpdateView o DeleteView
    # y que ya tengan TenantLoginRequiredMixin pero NO tengan TenantSuccessUrlMixin
    pattern = r'class\s+(\w+)\(([^)]*(?:CreateView|UpdateView|DeleteView)[^)]*)\):'
    
    def replace_class(match):
        class_name = match.group(1)
        inheritance = match.group(2)
        
        # Si ya tiene TenantSuccessUrlMixin, no hacer nada
        if 'TenantSuccessUrlMixin' in inheritance:
            return match.group(0)
        
        # Si tiene CreateView, UpdateView o DeleteView, agregar TenantSuccessUrlMixin
        if any(view in inheritance for view in ['CreateView', 'UpdateView', 'DeleteView']):
            # Si tiene TenantLoginRequiredMixin, agregar TenantSuccessUrlMixin antes
            if 'TenantLoginRequiredMixin' in inheritance:
                new_inheritance = inheritance.replace('TenantLoginRequiredMixin', 'TenantSuccessUrlMixin, TenantLoginRequiredMixin')
            elif 'LoginRequiredMixin' in inheritance:
                # Si solo tiene LoginRequiredMixin, reemplazarlo
                new_inheritance = inheritance.replace('LoginRequiredMixin', 'TenantSuccessUrlMixin, TenantLoginRequiredMixin')
            else:
                # Si no tiene ninguno, agregarlo al principio
                new_inheritance = f'TenantSuccessUrlMixin, {inheritance}'
            
            print(f"✓ {class_name}: {inheritance.strip()} -> {new_inheritance.strip()}")
            return f'class {class_name}({new_inheritance}):'
        
        return match.group(0)
    
    content = re.sub(pattern, replace_class, content)
    
    # Si hubo cambios, guardar
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

if __name__ == '__main__':
    if fix_views_file():
        print("\n✅ Archivo core/views.py actualizado")
    else:
        print("\n✅ No se necesitaron cambios")
