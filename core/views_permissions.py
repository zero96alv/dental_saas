# core/views_permissions.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.messages.views import SuccessMessageMixin

from .models_permissions import ModuloSistema, SubmenuItem, PermisoRol, LogAcceso
from .permissions_utils import PermisoDinamicoMixin


class PermisosAdminView(LoginRequiredMixin, TemplateView):
    """
    Vista principal para administrar permisos dinámicos.
    """
    template_name = 'core/permisos/admin_permisos_simple.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo administradores pueden acceder
        if not (self.request.user.is_superuser or 
                self.request.user.groups.filter(name='Administrador').exists()):
            messages.error(self.request, 'No tienes permisos para acceder a esta función.')
            return context
        
        context['grupos'] = Group.objects.all()
        context['modulos'] = ModuloSistema.objects.filter(activo=True).prefetch_related(
            'submenus'
        ).order_by('orden')
        
        return context


class ModuloSistemaListView(LoginRequiredMixin, ListView):
    model = ModuloSistema
    template_name = 'core/permisos/modulo_list.html'
    context_object_name = 'modulos'
    paginate_by = 20

    def get_queryset(self):
        return ModuloSistema.objects.prefetch_related('submenus').order_by('orden', 'nombre')


class ModuloSistemaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ModuloSistema
    template_name = 'core/permisos/modulo_form.html'
    fields = ['nombre', 'descripcion', 'icono', 'orden', 'activo', 'url_pattern']
    success_url = reverse_lazy('core:modulo_list')
    success_message = "Módulo '%(nombre)s' creado con éxito."


class ModuloSistemaUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ModuloSistema
    template_name = 'core/permisos/modulo_form.html'
    fields = ['nombre', 'descripcion', 'icono', 'orden', 'activo', 'url_pattern']
    success_url = reverse_lazy('core:modulo_list')
    success_message = "Módulo '%(nombre)s' actualizado con éxito."


class ModuloSistemaDeleteView(LoginRequiredMixin, DeleteView):
    model = ModuloSistema
    template_name = 'core/permisos/modulo_confirm_delete.html'
    success_url = reverse_lazy('core:modulo_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Módulo '{self.object.nombre}' eliminado con éxito.")
        return super().form_valid(form)


class SubmenuItemListView(LoginRequiredMixin, ListView):
    model = SubmenuItem
    template_name = 'core/permisos/submenu_list.html'
    context_object_name = 'submenus'
    paginate_by = 30

    def get_queryset(self):
        modulo_id = self.request.GET.get('modulo')
        queryset = SubmenuItem.objects.select_related('modulo').order_by(
            'modulo__orden', 'orden', 'nombre'
        )
        if modulo_id:
            queryset = queryset.filter(modulo_id=modulo_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulos'] = ModuloSistema.objects.filter(activo=True).order_by('orden')
        context['modulo_seleccionado'] = self.request.GET.get('modulo', '')
        return context


class SubmenuItemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = SubmenuItem
    template_name = 'core/permisos/submenu_form.html'
    fields = [
        'modulo', 'nombre', 'descripcion', 'url_name', 'icono', 'orden', 'activo',
        'requiere_crear', 'requiere_editar', 'requiere_eliminar', 'requiere_ver'
    ]
    success_url = reverse_lazy('core:submenu_list')
    success_message = "Elemento de submenú '%(nombre)s' creado con éxito."


class SubmenuItemUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SubmenuItem
    template_name = 'core/permisos/submenu_form.html'
    fields = [
        'modulo', 'nombre', 'descripcion', 'url_name', 'icono', 'orden', 'activo',
        'requiere_crear', 'requiere_editar', 'requiere_eliminar', 'requiere_ver'
    ]
    success_url = reverse_lazy('core:submenu_list')
    success_message = "Elemento de submenú '%(nombre)s' actualizado con éxito."


class SubmenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = SubmenuItem
    template_name = 'core/permisos/submenu_confirm_delete.html'
    success_url = reverse_lazy('core:submenu_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Elemento de submenú '{self.object.nombre}' eliminado con éxito.")
        return super().form_valid(form)


class PermisosRolMatrizView(LoginRequiredMixin, TemplateView):
    """
    Vista de matriz para gestionar permisos de roles de forma visual.
    """
    template_name = 'core/permisos/permisos_matriz.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Solo administradores
        if not (self.request.user.is_superuser or 
                self.request.user.groups.filter(name='Administrador').exists()):
            messages.error(self.request, 'No tienes permisos para acceder a esta función.')
            return context
        
        # Obtener roles y módulos
        context['roles'] = Group.objects.all().order_by('name')
        context['modulos'] = ModuloSistema.objects.filter(activo=True).prefetch_related(
            'submenus__permisos__rol'
        ).order_by('orden')
        
        # Crear matriz de permisos
        permisos_matriz = {}
        for rol in context['roles']:
            permisos_matriz[rol.id] = {}
            permisos_rol = PermisoRol.objects.filter(rol=rol).select_related('submenu_item')
            for permiso in permisos_rol:
                permisos_matriz[rol.id][permiso.submenu_item.id] = permiso
        
        context['permisos_matriz'] = permisos_matriz
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Actualizar permisos masivamente desde la matriz.
        """
        if not (request.user.is_superuser or 
                request.user.groups.filter(name='Administrador').exists()):
            return JsonResponse({'error': 'No tienes permisos'}, status=403)
        
        try:
            with transaction.atomic():
                for key, value in request.POST.items():
                    if key.startswith('permiso_'):
                        # Formato: permiso_{rol_id}_{submenu_id}
                        parts = key.split('_')
                        if len(parts) == 3:
                            rol_id = parts[1]
                            submenu_id = parts[2]
                            
                            rol = get_object_or_404(Group, pk=rol_id)
                            submenu = get_object_or_404(SubmenuItem, pk=submenu_id)
                            
                            permiso, created = PermisoRol.objects.get_or_create(
                                rol=rol,
                                submenu_item=submenu,
                                defaults={'nivel_acceso': value}
                            )
                            
                            if not created:
                                permiso.nivel_acceso = value
                                permiso.save()
                
                messages.success(request, 'Permisos actualizados correctamente.')
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class LogAccesoListView(LoginRequiredMixin, ListView):
    """
    Vista para mostrar logs de acceso.
    """
    model = LogAcceso
    template_name = 'core/permisos/log_acceso_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = LogAcceso.objects.select_related(
            'usuario', 'submenu_item__modulo'
        ).order_by('-fecha_acceso')
        
        # Filtros
        usuario = self.request.GET.get('usuario')
        if usuario:
            queryset = queryset.filter(usuario__username__icontains=usuario)
            
        modulo = self.request.GET.get('modulo')
        if modulo:
            queryset = queryset.filter(submenu_item__modulo_id=modulo)
            
        fecha_desde = self.request.GET.get('fecha_desde')
        if fecha_desde:
            from datetime import datetime
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_acceso__date__gte=fecha_desde)
            
        fecha_hasta = self.request.GET.get('fecha_hasta')
        if fecha_hasta:
            from datetime import datetime
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_acceso__date__lte=fecha_hasta)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulos'] = ModuloSistema.objects.filter(activo=True).order_by('nombre')
        
        # Mantener filtros en el contexto
        context['filtros'] = {
            'usuario': self.request.GET.get('usuario', ''),
            'modulo': self.request.GET.get('modulo', ''),
            'fecha_desde': self.request.GET.get('fecha_desde', ''),
            'fecha_hasta': self.request.GET.get('fecha_hasta', ''),
        }
        return context


def inicializar_sistema_permisos(request):
    """
    Vista AJAX para inicializar el sistema de permisos usando SQL directo.
    """
    if not (request.user.is_superuser or 
            request.user.groups.filter(name='Administrador').exists()):
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Crear grupos básicos
            for group_name in ['Administrador', 'Dentista', 'Recepcionista']:
                cursor.execute("""
                    INSERT INTO auth_group (name) 
                    VALUES (%s) 
                    ON CONFLICT (name) DO NOTHING
                """, [group_name])
            
            # Crear módulos básicos
            modulos = [
                ("Pacientes", "Gestión de pacientes", "fas fa-users", 1, "/pacientes/"),
                ("Agenda", "Agenda y citas", "fas fa-calendar", 2, "/agenda/"),
                ("Servicios", "Catálogo de servicios", "fas fa-teeth", 3, "/services/"),
                ("Personal", "Gestión de usuarios", "fas fa-user-md", 4, "/usuarios/"),
                ("Inventario", "Control de insumos", "fas fa-boxes", 5, "/insumos/"),
                ("Finanzas", "Pagos y reportes", "fas fa-dollar-sign", 6, "/pagos/"),
                ("Administración", "Configuración del sistema", "fas fa-cog", 7, "/admin/permisos/"),
            ]
            
            for nombre, desc, icono, orden, url in modulos:
                cursor.execute("""
                    INSERT INTO core_modulosistema (nombre, descripcion, icono, orden, activo, url_pattern)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nombre) DO NOTHING
                """, [nombre, desc, icono, orden, True, url])
            
            # Crear submenús completos para el sistema granular
            submenus = [
                # Módulo Pacientes (orden=1)
                ("Lista de Pacientes", "core:paciente_list", "fas fa-list", 1, 1),
                ("Nuevo Paciente", "core:paciente_create", "fas fa-plus", 2, 1),
                ("Historial Clínico", "core:paciente_history", "fas fa-file-medical", 3, 1),
                ("Saldos Pendientes", "core:saldos_pendientes", "fas fa-exclamation-triangle", 4, 1),
                
                # Módulo Agenda (orden=2)
                ("Ver Agenda", "core:agenda", "fas fa-calendar-alt", 1, 2),
                ("Lista de Citas", "core:cita_list", "fas fa-list-ul", 2, 2),
                ("Nueva Cita", "core:cita_create", "fas fa-plus-circle", 3, 2),
                ("Citas Pendientes de Pago", "core:citas_pendientes_pago", "fas fa-clock", 4, 2),
                
                # Módulo Servicios (orden=3)
                ("Catálogo de Servicios", "core:service_list", "fas fa-list", 1, 3),
                ("Nuevo Servicio", "core:service_create", "fas fa-plus", 2, 3),
                ("Especialidades", "core:especialidad_list", "fas fa-stethoscope", 3, 3),
                ("Diagnósticos", "core:diagnostico_list", "fas fa-diagnoses", 4, 3),
                
                # Módulo Personal (orden=4)
                ("Gestión de Usuarios", "core:usuario_list", "fas fa-users", 1, 4),
                ("Nuevo Usuario", "core:usuario_create", "fas fa-user-plus", 2, 4),
                ("Dentistas", "core:dentista_list", "fas fa-user-md", 3, 4),
                ("Horarios Laborales", "core:gestionar_horario", "fas fa-calendar-check", 4, 4),
                
                # Módulo Inventario (orden=5)
                ("Lista de Insumos", "core:insumo_list", "fas fa-boxes", 1, 5),
                ("Nuevo Insumo", "core:insumo_create", "fas fa-plus", 2, 5),
                ("Compras", "core:compra_list", "fas fa-shopping-cart", 3, 5),
                ("Proveedores", "core:proveedor_list", "fas fa-truck", 4, 5),
                ("Unidades Dentales", "core:unidad_dental_list", "fas fa-clinic-medical", 5, 5),
                
                # Módulo Finanzas (orden=6)
                ("Lista de Pagos", "core:pago_list", "fas fa-money-bill-wave", 1, 6),
                ("Registrar Pago", "core:pago_create", "fas fa-plus", 2, 6),
                ("Reporte de Ingresos", "core:reporte_ingresos", "fas fa-chart-line", 3, 6),
                ("Reporte de Saldos", "core:reporte_saldos", "fas fa-balance-scale", 4, 6),
                ("Reporte de Facturación", "core:reporte_facturacion", "fas fa-file-invoice", 5, 6),
                
                # Módulo Administración (orden=7)
                ("Gestión de Permisos", "core:admin_permisos", "fas fa-shield-alt", 1, 7),
                ("Matriz de Permisos", "core:permisos_matriz", "fas fa-table", 2, 7),
                ("Logs de Acceso", "core:log_acceso_list", "fas fa-history", 3, 7),
                ("COFEPRIS", "core:dashboard_cofepris", "fas fa-certificate", 4, 7),
            ]
            
            for submenu_nombre, url_name, icono, orden, modulo_orden in submenus:
                cursor.execute("""
                    INSERT INTO core_submenuitem (nombre, descripcion, url_name, icono, orden, activo, modulo_id, requiere_ver, requiere_crear, requiere_editar, requiere_eliminar)
                    SELECT %s, '', %s, %s, %s, %s, m.id, %s, %s, %s, %s
                    FROM core_modulosistema m 
                    WHERE m.orden = %s
                    ON CONFLICT (modulo_id, nombre) DO NOTHING
                """, [submenu_nombre, url_name, icono, orden, True, True, False, False, False, modulo_orden])
        
        return JsonResponse({
            'success': True,
            'message': 'Sistema de permisos inicializado correctamente con SQL directo.'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def clonar_permisos_rol(request):
    """
    Vista AJAX para clonar permisos de un rol a otro.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if not (request.user.is_superuser or 
            request.user.groups.filter(name='Administrador').exists()):
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    try:
        import json
        data = json.loads(request.body)
        rol_origen_id = data.get('rol_origen_id')
        rol_destino_id = data.get('rol_destino_id')
        
        rol_origen = get_object_or_404(Group, pk=rol_origen_id)
        rol_destino = get_object_or_404(Group, pk=rol_destino_id)
        
        with transaction.atomic():
            # Eliminar permisos existentes del rol destino
            PermisoRol.objects.filter(rol=rol_destino).delete()
            
            # Copiar permisos del rol origen
            permisos_origen = PermisoRol.objects.filter(rol=rol_origen)
            nuevos_permisos = []
            
            for permiso in permisos_origen:
                nuevos_permisos.append(PermisoRol(
                    rol=rol_destino,
                    submenu_item=permiso.submenu_item,
                    nivel_acceso=permiso.nivel_acceso,
                    puede_ver=permiso.puede_ver,
                    puede_crear=permiso.puede_crear,
                    puede_editar=permiso.puede_editar,
                    puede_eliminar=permiso.puede_eliminar,
                    puede_exportar=permiso.puede_exportar,
                    solo_propios_registros=permiso.solo_propios_registros
                ))
            
            PermisoRol.objects.bulk_create(nuevos_permisos)
        
        return JsonResponse({
            'success': True,
            'message': f'Permisos copiados de {rol_origen.name} a {rol_destino.name}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Vista AJAX para obtener datos de la matriz de permisos
def obtener_matriz_permisos_ajax(request):
    """
    Vista AJAX para obtener los datos necesarios para construir la matriz de permisos.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if not (request.user.is_superuser or 
            request.user.groups.filter(name='Administrador').exists()):
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    try:
        rol_id = request.GET.get('rol_id')
        if not rol_id:
            return JsonResponse({
                'success': False,
                'error': 'Debe especificar un rol'
            })
        
        rol = get_object_or_404(Group, id=rol_id)
        
        # Obtener todos los submenús con sus módulos
        submenus = SubmenuItem.objects.select_related('modulo').filter(
            activo=True
        ).order_by('modulo__orden', 'orden')
        
        # Obtener permisos actuales del rol
        permisos_actuales = PermisoRol.objects.filter(rol=rol).select_related('submenu_item')
        
        # Construir respuesta
        submenus_data = []
        for submenu in submenus:
            submenus_data.append({
                'id': submenu.id,
                'nombre': submenu.nombre,
                'url_pattern': submenu.url_pattern,
                'icono': submenu.icono,
                'modulo_id': submenu.modulo.id,
                'modulo': {
                    'id': submenu.modulo.id,
                    'nombre': submenu.modulo.nombre,
                    'icono': submenu.modulo.icono
                }
            })
        
        permisos_data = []
        for permiso in permisos_actuales:
            permisos_data.append({
                'submenu_id': permiso.submenu_item.id,
                'puede_ver': permiso.puede_ver,
                'puede_crear': permiso.puede_crear,
                'puede_editar': permiso.puede_editar,
                'puede_eliminar': permiso.puede_eliminar,
                'puede_exportar': permiso.puede_exportar
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'rol': {
                    'id': rol.id,
                    'nombre': rol.name,
                    'slug': rol.name.lower().replace(' ', '_')
                },
                'submenus': submenus_data,
                'permisos_actuales': permisos_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# Vista AJAX para guardar la matriz de permisos
def guardar_matriz_permisos_ajax(request):
    """
    Vista AJAX para guardar los permisos configurados en la matriz.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if not (request.user.is_superuser or 
            request.user.groups.filter(name='Administrador').exists()):
        return JsonResponse({'error': 'No tienes permisos'}, status=403)
    
    try:
        import json
        
        rol_id = request.POST.get('rol_id')
        permisos_json = request.POST.get('permisos')
        
        if not rol_id or not permisos_json:
            return JsonResponse({
                'success': False,
                'error': 'Datos incompletos'
            })
        
        rol = get_object_or_404(Group, id=rol_id)
        permisos = json.loads(permisos_json)
        
        with transaction.atomic():
            # Eliminar permisos existentes
            PermisoRol.objects.filter(rol=rol).delete()
            
            # Crear nuevos permisos
            permisos_a_crear = []
            for permiso_data in permisos:
                submenu = get_object_or_404(SubmenuItem, id=permiso_data['submenu_id'])
                
                # Solo crear si al menos un permiso está habilitado
                if any([
                    permiso_data.get('puede_ver', False),
                    permiso_data.get('puede_crear', False),
                    permiso_data.get('puede_editar', False),
                    permiso_data.get('puede_eliminar', False),
                    permiso_data.get('puede_exportar', False)
                ]):
                    # Calcular nivel de acceso basado en permisos
                    nivel = 'lectura'
                    if permiso_data.get('puede_eliminar', False):
                        nivel = 'completo'
                    elif permiso_data.get('puede_editar', False) or permiso_data.get('puede_crear', False):
                        nivel = 'escritura'
                    
                    permisos_a_crear.append(PermisoRol(
                        rol=rol,
                        submenu_item=submenu,
                        nivel_acceso=nivel,
                        puede_ver=permiso_data.get('puede_ver', False),
                        puede_crear=permiso_data.get('puede_crear', False),
                        puede_editar=permiso_data.get('puede_editar', False),
                        puede_eliminar=permiso_data.get('puede_eliminar', False),
                        puede_exportar=permiso_data.get('puede_exportar', False),
                        solo_propios_registros=False  # Por defecto False, se puede ajustar después
                    ))
            
            # Crear en lote para mejor rendimiento
            PermisoRol.objects.bulk_create(permisos_a_crear)
        
        # Registrar en log de auditoría
        LogAcceso.objects.create(
            usuario=request.user,
            modulo_accedido='Administración',
            accion_realizada=f'Configuró permisos para rol {rol.name}',
            ip_address=request.META.get('REMOTE_ADDR', 'unknown'),
            detalles=f'Se configuraron {len(permisos_a_crear)} permisos'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Permisos guardados correctamente. {len(permisos_a_crear)} permisos configurados.',
            'total_permisos': len(permisos_a_crear)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
