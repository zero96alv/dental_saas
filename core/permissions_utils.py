# core/permissions_utils.py
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import SubmenuItem, PermisoRol, LogAcceso

class PermisoDinamicoMixin(AccessMixin):
    """
    Mixin que verifica permisos dinámicos basados en el modelo PermisoRol.
    Debe definirse el atributo `url_name` en la vista para identificar el submenu.
    """
    url_name = None  # Debe ser definido en cada vista (ej: 'core:paciente_list')
    permiso_requerido = 'ver'  # por defecto: 'ver', 'crear', 'editar', 'eliminar'
    
    def dispatch(self, request, *args, **kwargs):
        if not self.url_name:
            raise ValueError("Debe definir 'url_name' en la vista para usar PermisoDinamicoMixin")
        
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar permisos
        if not self.tiene_permiso(request.user, self.url_name, self.permiso_requerido):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'No tienes permisos para realizar esta acción.'}, status=403)
            messages.error(request, 'No tienes permisos para acceder a esta función.')
            return HttpResponseForbidden("No tienes permisos para acceder a esta función.")
        
        # Registrar acceso para auditoría
        self.registrar_acceso(request.user, self.url_name)
        
        return super().dispatch(request, *args, **kwargs)
    
    def tiene_permiso(self, user, url_name, permiso_requerido):
        """
        Verifica si el usuario tiene el permiso requerido para la URL especificada.
        """
        # Superusuarios siempre tienen acceso
        if user.is_superuser:
            return True
        
        try:
            submenu_item = SubmenuItem.objects.get(url_name=url_name, activo=True)
        except SubmenuItem.DoesNotExist:
            # Si no existe configuración, permitir acceso por defecto
            return True
        
        # Verificar permisos por cada grupo del usuario
        for grupo in user.groups.all():
            try:
                permiso_rol = PermisoRol.objects.get(
                    rol=grupo,
                    submenu_item=submenu_item
                )
                
                # Verificar el permiso específico
                if permiso_requerido == 'ver' and permiso_rol.puede_ver:
                    return True
                elif permiso_requerido == 'crear' and permiso_rol.puede_crear:
                    return True
                elif permiso_requerido == 'editar' and permiso_rol.puede_editar:
                    return True
                elif permiso_requerido == 'eliminar' and permiso_rol.puede_eliminar:
                    return True
                elif permiso_requerido == 'exportar' and permiso_rol.puede_exportar:
                    return True
                    
            except PermisoRol.DoesNotExist:
                # Si no existe configuración específica, denegar acceso
                continue
        
        return False
    
    def registrar_acceso(self, user, url_name):
        """
        Registra el acceso del usuario para auditoría.
        """
        try:
            submenu_item = SubmenuItem.objects.get(url_name=url_name, activo=True)
            LogAcceso.objects.create(
                usuario=user,
                submenu_item=submenu_item,
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        except SubmenuItem.DoesNotExist:
            pass  # No registrar si no existe el submenu_item
    
    def get_client_ip(self):
        """
        Obtiene la IP del cliente.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

def verificar_permiso_ajax(user, url_name, permiso_requerido='ver'):
    """
    Función utilitaria para verificar permisos en vistas basadas en funciones.
    """
    if user.is_superuser:
        return True
    
    try:
        submenu_item = SubmenuItem.objects.get(url_name=url_name, activo=True)
    except SubmenuItem.DoesNotExist:
        return True  # Permitir por defecto si no hay configuración
    
    for grupo in user.groups.all():
        try:
            permiso_rol = PermisoRol.objects.get(rol=grupo, submenu_item=submenu_item)
            if permiso_requerido == 'ver' and permiso_rol.puede_ver:
                return True
            elif permiso_requerido == 'crear' and permiso_rol.puede_crear:
                return True
            elif permiso_requerido == 'editar' and permiso_rol.puede_editar:
                return True
            elif permiso_requerido == 'eliminar' and permiso_rol.puede_eliminar:
                return True
        except PermisoRol.DoesNotExist:
            continue
    
    return False

def get_menu_for_user(user):
    """
    Genera el menú dinámico basado en los permisos del usuario.
    """
    if not user.is_authenticated:
        return []
    
    menu = []
    
    # Si es superusuario, mostrar todo
    if user.is_superuser:
        from .models import ModuloSistema
        modulos = ModuloSistema.objects.filter(activo=True).prefetch_related('submenus')
        for modulo in modulos:
            submenus_activos = modulo.submenus.filter(activo=True)
            if submenus_activos.exists():
                menu.append({
                    'modulo': modulo,
                    'submenus': list(submenus_activos)
                })
    else:
        # Obtener módulos basados en permisos
        grupos_usuario = user.groups.all()
        permisos_usuario = PermisoRol.objects.filter(
            rol__in=grupos_usuario,
            puede_ver=True,
            submenu_item__activo=True,
            submenu_item__modulo__activo=True
        ).select_related('submenu_item__modulo').order_by(
            'submenu_item__modulo__orden',
            'submenu_item__orden'
        )
        
        # Organizar por módulos
        modulos_dict = {}
        for permiso in permisos_usuario:
            modulo = permiso.submenu_item.modulo
            if modulo not in modulos_dict:
                modulos_dict[modulo] = []
            modulos_dict[modulo].append(permiso.submenu_item)
        
        # Convertir a formato de menú
        for modulo, submenus in modulos_dict.items():
            menu.append({
                'modulo': modulo,
                'submenus': submenus
            })
    
    return menu

def inicializar_permisos_por_defecto():
    """
    Función utilitaria para inicializar permisos por defecto.
    Debe ser llamada después de las migraciones.
    """
    from django.contrib.auth.models import Group
    from .models import ModuloSistema, SubmenuItem, PermisoRol
    
    # Crear grupos básicos si no existen
    admin_group, _ = Group.objects.get_or_create(name='Administrador')
    dentista_group, _ = Group.objects.get_or_create(name='Dentista')
    recepcionista_group, _ = Group.objects.get_or_create(name='Recepcionista')
    
    # Crear módulos básicos
    modulos_basicos = [
        {
            'nombre': 'Dashboard',
            'icono': 'fas fa-tachometer-alt',
            'orden': 1,
            'submenus': [
                {'nombre': 'Panel Principal', 'url_name': 'core:dashboard', 'orden': 1},
            ]
        },
        {
            'nombre': 'Pacientes',
            'icono': 'fas fa-user-injured',
            'orden': 2,
            'submenus': [
                {'nombre': 'Lista de Pacientes', 'url_name': 'core:paciente_list', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Nuevo Paciente', 'url_name': 'core:paciente_create', 'orden': 2, 'requiere_crear': True},
                {'nombre': 'Saldos Pendientes', 'url_name': 'core:saldos_pendientes', 'orden': 3},
            ]
        },
        {
            'nombre': 'Agenda',
            'icono': 'fas fa-calendar-alt',
            'orden': 3,
            'submenus': [
                {'nombre': 'Agenda', 'url_name': 'core:agenda', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True},
                {'nombre': 'Lista de Citas', 'url_name': 'core:cita_list', 'orden': 2, 'requiere_editar': True},
                {'nombre': 'Citas Pendientes de Pago', 'url_name': 'core:citas_pendientes_pago', 'orden': 3},
            ]
        },
        {
            'nombre': 'Servicios',
            'icono': 'fas fa-tooth',
            'orden': 4,
            'submenus': [
                {'nombre': 'Lista de Servicios', 'url_name': 'core:service_list', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Especialidades', 'url_name': 'core:especialidad_list', 'orden': 2, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Diagnósticos', 'url_name': 'core:diagnostico_list', 'orden': 3, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
            ]
        },
        {
            'nombre': 'Personal',
            'icono': 'fas fa-users',
            'orden': 5,
            'submenus': [
                {'nombre': 'Lista de Personal', 'url_name': 'core:usuario_list', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True},
                {'nombre': 'Dentistas', 'url_name': 'core:dentista_list', 'orden': 2},
            ]
        },
        {
            'nombre': 'Finanzas',
            'icono': 'fas fa-dollar-sign',
            'orden': 6,
            'submenus': [
                {'nombre': 'Pagos', 'url_name': 'core:pago_list', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Reportes de Ingresos', 'url_name': 'core:reporte_ingresos', 'orden': 2},
                {'nombre': 'Reporte de Saldos', 'url_name': 'core:reporte_saldos', 'orden': 3},
            ]
        },
        {
            'nombre': 'Inventario',
            'icono': 'fas fa-boxes',
            'orden': 7,
            'submenus': [
                {'nombre': 'Insumos', 'url_name': 'core:insumo_list', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Proveedores', 'url_name': 'core:proveedor_list', 'orden': 2, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Compras', 'url_name': 'core:compra_list', 'orden': 3, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
            ]
        },
        {
            'nombre': 'COFEPRIS',
            'icono': 'fas fa-shield-alt',
            'orden': 8,
            'submenus': [
                {'nombre': 'Panel COFEPRIS', 'url_name': 'core:dashboard_cofepris', 'orden': 1},
                {'nombre': 'Aviso de Funcionamiento', 'url_name': 'core:aviso_list', 'orden': 2, 'requiere_crear': True, 'requiere_editar': True},
                {'nombre': 'Equipos', 'url_name': 'core:equipo_list', 'orden': 3, 'requiere_crear': True, 'requiere_editar': True},
                {'nombre': 'Residuos', 'url_name': 'core:residuos_list', 'orden': 4, 'requiere_crear': True, 'requiere_editar': True},
            ]
        },
        {
            'nombre': 'Configuración',
            'icono': 'fas fa-cog',
            'orden': 9,
            'submenus': [
                {'nombre': 'Unidades Dentales', 'url_name': 'core:unidad_dental_list', 'orden': 1, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
                {'nombre': 'Preguntas de Historial', 'url_name': 'core:pregunta_list', 'orden': 2, 'requiere_crear': True, 'requiere_editar': True, 'requiere_eliminar': True},
            ]
        }
    ]
    
    for modulo_data in modulos_basicos:
        modulo, created = ModuloSistema.objects.get_or_create(
            nombre=modulo_data['nombre'],
            defaults={
                'icono': modulo_data['icono'],
                'orden': modulo_data['orden'],
                'activo': True
            }
        )
        
        for submenu_data in modulo_data['submenus']:
            submenu, created = SubmenuItem.objects.get_or_create(
                modulo=modulo,
                nombre=submenu_data['nombre'],
                url_name=submenu_data['url_name'],
                defaults={
                    'orden': submenu_data['orden'],
                    'requiere_crear': submenu_data.get('requiere_crear', False),
                    'requiere_editar': submenu_data.get('requiere_editar', False),
                    'requiere_eliminar': submenu_data.get('requiere_eliminar', False),
                    'activo': True
                }
            )
    
    # Asignar permisos por defecto
    asignar_permisos_por_defecto(admin_group, dentista_group, recepcionista_group)

def asignar_permisos_por_defecto(admin_group, dentista_group, recepcionista_group):
    """
    Asigna permisos por defecto a los grupos.
    """
    from .models import SubmenuItem, PermisoRol
    
    # Administrador: Acceso completo a todo
    for submenu in SubmenuItem.objects.filter(activo=True):
        PermisoRol.objects.get_or_create(
            rol=admin_group,
            submenu_item=submenu,
            defaults={'nivel_acceso': 'completo'}
        )
    
    # Dentista: Acceso a pacientes, agenda, servicios (limitado en personal/finanzas)
    permisos_dentista = {
        # Dashboard
        'core:dashboard': 'VER',
        
        # Pacientes
        'core:paciente_list': 'COMPLETO',
        'core:paciente_create': 'CREAR',
        'core:saldos_pendientes': 'VER',
        
        # Agenda  
        'core:agenda': 'COMPLETO',
        'core:cita_list': 'EDITAR',
        'core:citas_pendientes_pago': 'VER',
        
        # Servicios
        'core:service_list': 'VER',
        'core:especialidad_list': 'VER',
        'core:diagnostico_list': 'VER',
        
        # Personal (solo ver)
        'core:usuario_list': 'VER',
        'core:dentista_list': 'VER',
        
        # Finanzas (solo ver algunos reportes)
        'core:pago_list': 'VER',
        
        # Inventario (solo ver)
        'core:insumo_list': 'VER',
        'core:proveedor_list': 'VER',
        'core:compra_list': 'VER',
        
        # Configuración (solo ver)
        'core:unidad_dental_list': 'VER',
        'core:pregunta_list': 'VER',
    }
    
    def _map_nivel(n):
        return {
            'VER': 'lectura',
            'CREAR': 'escritura',
            'EDITAR': 'escritura',
            'COMPLETO': 'completo',
        }.get(n, 'lectura')

    for url_name, nivel in permisos_dentista.items():
        submenus = SubmenuItem.objects.filter(url_name=url_name, activo=True)
        if not submenus.exists():
            continue
        for submenu in submenus:
            PermisoRol.objects.get_or_create(
                rol=dentista_group,
                submenu_item=submenu,
                defaults={'nivel_acceso': _map_nivel(nivel)}
            )
    
    # Recepcionista: Acceso a pacientes, agenda, algunos reportes
    permisos_recepcionista = {
        # Dashboard
        'core:dashboard': 'VER',
        
        # Pacientes
        'core:paciente_list': 'COMPLETO',
        'core:paciente_create': 'CREAR',
        'core:saldos_pendientes': 'VER',
        
        # Agenda
        'core:agenda': 'COMPLETO',
        'core:cita_list': 'EDITAR',
        'core:citas_pendientes_pago': 'COMPLETO',
        
        # Servicios (solo ver)
        'core:service_list': 'VER',
        'core:especialidad_list': 'VER',
        'core:diagnostico_list': 'VER',
        
        # Personal (solo ver)
        'core:usuario_list': 'VER',
        'core:dentista_list': 'VER',
        
        # Finanzas
        'core:pago_list': 'COMPLETO',
        'core:reporte_ingresos': 'VER',
        'core:reporte_saldos': 'VER',
        
        # Inventario (denegado)
        # Configuración (denegado)
    }
    
    for url_name, nivel in permisos_recepcionista.items():
        submenus = SubmenuItem.objects.filter(url_name=url_name, activo=True)
        if not submenus.exists():
            continue
        for submenu in submenus:
            PermisoRol.objects.get_or_create(
                rol=recepcionista_group,
                submenu_item=submenu,
                defaults={'nivel_acceso': _map_nivel(nivel)}
            )
