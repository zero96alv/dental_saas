# core/context_processors.py
from .permissions_utils import get_menu_for_user

def menu_dinamico(request):
    """
    Context processor que proporciona el menú dinámico basado en permisos.
    Además agrega un agregado 'reportes_menu' con todos los enlaces de reportes
    a fin de mostrarlos bajo un solo dropdown.
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        menu = get_menu_for_user(request.user)
    else:
        menu = []

    # Construir lista consolidada de reportes visibles para el usuario
    reportes_menu = []
    try:
        # Excluir versiones no-período que ya no queremos mostrar
        excluir_urls = {
            'core:reporte_ingresos_dentista',
            'core:reporte_servicios_vendidos',
        }
        for item in menu:
            submenus = item.get('submenus', [])
            for sm in submenus:
                url_name = getattr(sm, 'url_name', '') or ''
                nombre = getattr(sm, 'nombre', '') or ''
                # Incluir solo vistas de reporte (no APIs ni exportaciones)
                if url_name.startswith('core:reporte_') and url_name not in excluir_urls:
                    icono = getattr(sm, 'icono', '') or 'bi bi-graph-up'
                    reportes_menu.append({
                        'nombre': nombre,
                        'url_name': url_name,
                        'icono': icono,
                    })
        # Ordenar alfabéticamente por nombre
        reportes_menu.sort(key=lambda r: r['nombre'].lower())
    except Exception:
        # No bloquear la carga de la página por un error en el agregado
        reportes_menu = []
    
    # Construir menú sin reportes para evitar duplicados (p. ej. en Finanzas)
    menu_sin_reportes = []
    def _is_report(submenu):
        url_name = getattr(submenu, 'url_name', '') or ''
        return isinstance(url_name, str) and url_name.startswith('core:reporte_')

    for item in menu:
        modulo = item.get('modulo')
        submenus = item.get('submenus', [])
        sub_no_report = [sm for sm in submenus if not _is_report(sm)]
        if sub_no_report:
            menu_sin_reportes.append({'modulo': modulo, 'submenus': sub_no_report})

    # Orden personalizado de módulos para mejor UX
    orden_custom = {
        'Dashboard': 1,
        'Pacientes': 2,
        'Citas': 3,
        'Servicios': 4,
        'Consentimientos': 5,
        'Finanzas': 6,
        'Inventario': 7,
        'COFEPRIS': 8,
        'Personal': 9,
        'Configuración': 10,
        'Administración': 11,
    }
    def _orden_mod(item):
        modulo = item.get('modulo')
        nombre = getattr(modulo, 'nombre', '')
        return (orden_custom.get(nombre, 99), getattr(modulo, 'orden', 99), nombre)
    menu_sin_reportes.sort(key=_orden_mod)

    # Fallback: agregar reportes conocidos aunque no estén en SubmenuItem (solo admin)
    known_reportes = [
        {'url_name': 'core:reporte_ingresos', 'nombre': 'Ingresos', 'icono': 'bi bi-graph-up-arrow'},
        {'url_name': 'core:reporte_saldos', 'nombre': 'Saldos Pendientes', 'icono': 'bi bi-cash-stack'},
        {'url_name': 'core:reporte_facturacion', 'nombre': 'Facturación', 'icono': 'bi bi-receipt'},
        {'url_name': 'core:reporte_servicios_vendidos_periodo', 'nombre': 'Servicios más vendidos (periodo)', 'icono': 'bi bi-bar-chart-line'},
        {'url_name': 'core:reporte_ingresos_dentista_periodo', 'nombre': 'Ingresos por dentista (periodo)', 'icono': 'bi bi-people-fill'},
    ]
    # Evitar duplicados por url_name
    existentes = set(r['url_name'] for r in reportes_menu)
    # Solo admins ven los fallback si no estaban ya presentes
    try:
        es_admin = request.user.is_superuser or request.user.groups.filter(nombre='Administrador').exists()
    except Exception:
        es_admin = False
    if es_admin:
        for r in known_reportes:
            if r['url_name'] not in existentes:
                reportes_menu.append(r)

    return {
        'menu_dinamico': menu,
        'menu_filtrado': menu_sin_reportes,
        'reportes_menu': reportes_menu,
    }
