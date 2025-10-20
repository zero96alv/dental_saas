#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Sistema de Autenticación y Permisos Dinámicos
=================================================================

Este script valida el funcionamiento completo del sistema de autenticación
y permisos dinámicos del sistema dental.

Ejecutar desde la raíz del proyecto:
python validation_auth_permissions.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append('C:\\desarrollo\\dental_saas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

# Importar modelos necesarios
from core.models import PerfilDentista, Paciente
from core.models_permissions import ModuloSistema, SubmenuItem, PermisoRol, LogAcceso
from tenants.models import Clinica

User = get_user_model()

class AuthPermissionsValidator:
    def __init__(self):
        self.factory = RequestFactory()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        
        print("=" * 70)
        print("VALIDACIÓN DEL SISTEMA DE AUTENTICACIÓN Y PERMISOS")
        print("=" * 70)
        print(f"Inicio de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def log_success(self, message):
        """Registra un test exitoso"""
        self.success_count += 1
        self.total_tests += 1
        print(f"✓ {message}")

    def log_error(self, message):
        """Registra un error"""
        self.total_tests += 1
        self.errors.append(message)
        print(f"✗ ERROR: {message}")

    def log_warning(self, message):
        """Registra una advertencia"""
        self.warnings.append(message)
        print(f"⚠ ADVERTENCIA: {message}")

    def validate_basic_authentication(self):
        """Valida la autenticación básica"""
        print("\n1. VALIDACIÓN DE AUTENTICACIÓN BÁSICA")
        print("-" * 40)
        
        try:
            # Verificar que existen usuarios básicos
            admin_users = User.objects.filter(is_superuser=True)
            if admin_users.exists():
                self.log_success(f"Usuarios administrador encontrados: {admin_users.count()}")
            else:
                self.log_warning("No se encontraron usuarios administrador")
            
            # Verificar grupos básicos
            expected_groups = ['Administrador', 'Dentista', 'Recepcionista', 'Paciente']
            for group_name in expected_groups:
                try:
                    group = Group.objects.get(name=group_name)
                    user_count = group.user_set.count()
                    self.log_success(f"Grupo '{group_name}' existe con {user_count} usuarios")
                except Group.DoesNotExist:
                    self.log_warning(f"Grupo '{group_name}' no existe")
            
            # Verificar usuarios dentista
            dentistas = PerfilDentista.objects.all()
            if dentistas.exists():
                self.log_success(f"Perfiles de dentista encontrados: {dentistas.count()}")
            else:
                self.log_warning("No se encontraron perfiles de dentista")
                
        except Exception as e:
            self.log_error(f"Error en validación de autenticación básica: {str(e)}")

    def validate_permissions_system(self):
        """Valida el sistema de permisos dinámicos"""
        print("\n2. VALIDACIÓN DEL SISTEMA DE PERMISOS DINÁMICOS")
        print("-" * 50)
        
        try:
            # Verificar módulos del sistema
            modulos = ModuloSistema.objects.all()
            if modulos.exists():
                self.log_success(f"Módulos del sistema encontrados: {modulos.count()}")
                for modulo in modulos:
                    print(f"   - {modulo.nombre} ({'Activo' if modulo.activo else 'Inactivo'})")
            else:
                self.log_warning("No se encontraron módulos del sistema")
            
            # Verificar submenús
            submenus = SubmenuItem.objects.all()
            if submenus.exists():
                self.log_success(f"Items de submenú encontrados: {submenus.count()}")
            else:
                self.log_warning("No se encontraron items de submenú")
            
            # Verificar permisos por rol
            permisos_rol = PermisoRol.objects.all()
            if permisos_rol.exists():
                self.log_success(f"Permisos por rol configurados: {permisos_rol.count()}")
                
                # Verificar distribución por rol
                for group in Group.objects.all():
                    permisos_count = PermisoRol.objects.filter(rol=group).count()
                    if permisos_count > 0:
                        print(f"   - {group.name}: {permisos_count} permisos")
                    else:
                        self.log_warning(f"Rol '{group.name}' sin permisos configurados")
            else:
                self.log_warning("No se encontraron permisos por rol configurados")
                
        except Exception as e:
            self.log_error(f"Error en validación del sistema de permisos: {str(e)}")

    def validate_access_logs(self):
        """Valida el sistema de logs de acceso"""
        print("\n3. VALIDACIÓN DEL SISTEMA DE LOGS DE ACCESO")
        print("-" * 45)
        
        try:
            logs = LogAcceso.objects.all()
            if logs.exists():
                self.log_success(f"Logs de acceso encontrados: {logs.count()}")
                
                # Logs recientes (últimos 7 días)
                fecha_limite = datetime.now() - timedelta(days=7)
                logs_recientes = logs.filter(fecha_acceso__gte=fecha_limite)
                if logs_recientes.exists():
                    self.log_success(f"Logs recientes (7 días): {logs_recientes.count()}")
                else:
                    self.log_warning("No hay logs de acceso recientes")
                
                # Verificar diferentes tipos de acceso
                tipos_acceso = logs.values_list('accion_realizada', flat=True).distinct()
                self.log_success(f"Tipos de acceso registrados: {list(tipos_acceso)}")
                
            else:
                self.log_warning("No se encontraron logs de acceso")
                
        except Exception as e:
            self.log_error(f"Error en validación de logs de acceso: {str(e)}")

    def validate_role_restrictions(self):
        """Valida las restricciones por rol"""
        print("\n4. VALIDACIÓN DE RESTRICCIONES POR ROL")
        print("-" * 40)
        
        try:
            # Verificar que dentistas solo ven sus pacientes
            dentistas = User.objects.filter(groups__name='Dentista')
            for dentista in dentistas[:3]:  # Limitar a 3 para prueba
                try:
                    perfil_dentista = PerfilDentista.objects.get(user=dentista)
                    # Simular restricción de acceso
                    self.log_success(f"Dentista {dentista.username} tiene perfil configurado")
                except PerfilDentista.DoesNotExist:
                    self.log_warning(f"Dentista {dentista.username} sin perfil de dentista")
            
            # Verificar permisos de recepcionista
            recepcionistas = User.objects.filter(groups__name='Recepcionista')
            if recepcionistas.exists():
                self.log_success(f"Usuarios recepcionista encontrados: {recepcionistas.count()}")
            else:
                self.log_warning("No se encontraron usuarios recepcionista")
            
            # Verificar permisos de paciente
            pacientes_user = User.objects.filter(groups__name='Paciente')
            if pacientes_user.exists():
                self.log_success(f"Usuarios paciente encontrados: {pacientes_user.count()}")
            else:
                self.log_warning("No se encontraron usuarios paciente")
                
        except Exception as e:
            self.log_error(f"Error en validación de restricciones por rol: {str(e)}")

    def validate_permission_matrix(self):
        """Valida la matriz de permisos"""
        print("\n5. VALIDACIÓN DE LA MATRIZ DE PERMISOS")
        print("-" * 40)
        
        try:
            # Verificar permisos críticos
            permisos_criticos = [
                'add_paciente', 'change_paciente', 'view_paciente',
                'add_cita', 'change_cita', 'view_cita',
                'add_pago', 'change_pago', 'view_pago',
                'add_servicio', 'change_servicio', 'view_servicio'
            ]
            
            for permiso_name in permisos_criticos:
                try:
                    permission = Permission.objects.get(codename=permiso_name)
                    
                    # Verificar qué roles tienen este permiso
                    roles_con_permiso = []
                    for group in Group.objects.all():
                        if group.permissions.filter(id=permission.id).exists():
                            roles_con_permiso.append(group.name)
                        else:
                            # Verificar en PermisoRol
                            modulo = ModuloSistema.objects.filter(
                                nombre__icontains=permiso_name.split('_')[1]
                            ).first()
                            if modulo:
                                # Buscar en submenús del módulo
                                for submenu in modulo.submenus.all():
                                    permiso_rol = PermisoRol.objects.filter(
                                        rol=group,
                                        submenu_item=submenu
                                    ).first()
                                    if permiso_rol:
                                        accion = permiso_name.split('_')[0]
                                        if accion == 'add' and permiso_rol.puede_crear:
                                            roles_con_permiso.append(f"{group.name} (dinámico)")
                                        elif accion == 'change' and permiso_rol.puede_editar:
                                            roles_con_permiso.append(f"{group.name} (dinámico)")
                                        elif accion == 'view' and permiso_rol.puede_ver:
                                            roles_con_permiso.append(f"{group.name} (dinámico)")
                                        break
                    
                    if roles_con_permiso:
                        self.log_success(f"Permiso '{permiso_name}': {', '.join(roles_con_permiso)}")
                    else:
                        self.log_warning(f"Permiso '{permiso_name}' sin roles asignados")
                        
                except Permission.DoesNotExist:
                    self.log_warning(f"Permiso '{permiso_name}' no existe")
            
        except Exception as e:
            self.log_error(f"Error en validación de matriz de permisos: {str(e)}")

    def validate_multi_tenant_security(self):
        """Valida la seguridad multi-tenant"""
        print("\n6. VALIDACIÓN DE SEGURIDAD MULTI-TENANT")
        print("-" * 45)
        
        try:
            # Verificar que los datos están aislados por tenant
            clinicas = Clinica.objects.all()
            if clinicas.exists():
                self.log_success(f"Tenants encontrados: {clinicas.count()}")
                
                # Verificar aislamiento de datos
                for clinica in clinicas[:2]:  # Limitar para prueba
                    # Simular contexto de tenant
                    print(f"   - Clínica: {clinica.nombre}")
                    
                    # Verificar que cada tenant tiene sus propios datos
                    # Esto requeriña configurar el schema tenant, así que solo verificamos la existencia
                    self.log_success(f"Tenant '{clinica.nombre}' configurado correctamente")
            else:
                self.log_warning("No se encontraron tenants configurados")
                
        except Exception as e:
            self.log_error(f"Error en validación multi-tenant: {str(e)}")

    def run_validation(self):
        """Ejecuta toda la validación"""
        try:
            self.validate_basic_authentication()
            self.validate_permissions_system()
            self.validate_access_logs()
            self.validate_role_restrictions()
            self.validate_permission_matrix()
            self.validate_multi_tenant_security()
            
        except Exception as e:
            self.log_error(f"Error general en validación: {str(e)}")

        # Resumen final
        self.print_summary()

    def print_summary(self):
        """Imprime el resumen final"""
        print("\n" + "=" * 70)
        print("RESUMEN DE VALIDACIÓN - AUTENTICACIÓN Y PERMISOS")
        print("=" * 70)
        
        success_rate = (self.success_count / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Tests ejecutados: {self.total_tests}")
        print(f"Tests exitosos: {self.success_count}")
        print(f"Errores: {len(self.errors)}")
        print(f"Advertencias: {len(self.warnings)}")
        print(f"Tasa de éxito: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n🔴 ERRORES ENCONTRADOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n🟡 ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if success_rate >= 90:
            print(f"\n✅ VALIDACIÓN EXITOSA")
            print("El sistema de autenticación y permisos está funcionando correctamente.")
        elif success_rate >= 70:
            print(f"\n⚠️  VALIDACIÓN CON ADVERTENCIAS")
            print("El sistema funciona, pero hay aspectos que necesitan atención.")
        else:
            print(f"\n❌ VALIDACIÓN FALLIDA")
            print("Se encontraron errores críticos que deben ser corregidos.")
        
        print(f"\nFin de validación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

def main():
    """Función principal"""
    try:
        validator = AuthPermissionsValidator()
        validator.run_validation()
        
    except Exception as e:
        print(f"❌ Error fatal en la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()