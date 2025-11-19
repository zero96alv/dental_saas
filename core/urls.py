from . import views
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from .views import (
    crear_paciente_ajax,  # Ahora existe
    get_servicios_for_dentista_api,
    DashboardView, DashboardFinancieroView,
    PacienteListView, PacienteDetailView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView,
    SaldosPendientesListView, PacientesPendientesPagoListView, RegistrarPagoPacienteView,
    ServicioListView, ServicioCreateView, ServicioUpdateView, ServicioDeleteView,
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView, UsuarioDeleteView,
    EspecialidadListView, EspecialidadCreateView, EspecialidadUpdateView, EspecialidadDeleteView,
    PagoListView, PagoCreateView, PagoUpdateView, PagoDeleteView,
    ProveedorListView, ProveedorCreateView, ProveedorUpdateView, ProveedorDeleteView,
    InsumoListView, InsumoCreateView, InsumoUpdateView, InsumoDeleteView,
    inventario_exportar_excel, inventario_importar_excel, ajustar_stock_lote,
    CompraListView, CompraCreateView, CompraUpdateView, CompraDeleteView, RecibirCompraView,
    AgendaView, AgendaLegacyView, CitaListView, CitasPendientesPagoListView,  # FinalizarCitaView deprecated
    CitaDetailView, CitaCreateView, CitaUpdateView, CitaDeleteView, CitaManageView,
    CambiarEstadoCitaView,
    ProcesarPagoView, RegistrarPagoView, ReciboPagoView, RegistrarAbonoView, finalizar_cita_form_content,
    HistorialPacienteView, HistorialClinicoCreateView,
    agenda_events,
    cita_detail_api,
    odontograma_api_get,
    odontograma_api_update,
    diagnostico_api_list,
    reporte_ingresos_api,
    reporte_saldos_api,
    ReporteIngresosView, ReporteSaldosView, ReporteFacturacionView,
    ReporteServiciosMasVendidosView, ReporteIngresosPorDentistaView,
    DiagnosticoListView, DiagnosticoCreateView, DiagnosticoUpdateView, DiagnosticoDeleteView,
    exportar_ingresos_excel, exportar_saldos_excel, exportar_facturacion_excel,
    generar_recibo_pdf, generar_servicios_vendidos_pdf,
    DashboardCofeprisView,
    AvisoFuncionamientoListView, AvisoFuncionamientoCreateView, AvisoFuncionamientoUpdateView,
    EquipoListView, EquipoCreateView, EquipoUpdateView, EquipoDeleteView,
    ResiduosListView, ResiduosCreateView, ResiduosUpdateView, ResiduosDeleteView,
    InvitarPacienteView, PacientePagosListView, ResetPasswordView, CuestionarioHistorialView, CuestionarioHistorialMejoradoView,
    PreguntaHistorialListView, PreguntaHistorialCreateView, PreguntaHistorialUpdateView, PreguntaHistorialDeleteView,
    UnidadDentalListView, UnidadDentalDetailView, UnidadDentalCreateView, UnidadDentalUpdateView, UnidadDentalDeleteView,
    GestionarHorarioView, 
    get_horario_dentista_api,
    DentistaListView,
    get_horarios_disponibles_api,
    CustomLogoutView,
    # Nuevas vistas del cuestionario
    CuestionarioHistorialListView, CompletarCuestionarioView, CuestionarioDetalleView,
    CategoriaHistorialListView, CategoriaHistorialCreateView, CategoriaHistorialUpdateView,
    PreguntaHistorialListView, PreguntaHistorialCreateView, PreguntaHistorialUpdateView
)

# Importar vistas de permisos
from .views_permissions import (
    PermisosAdminView, ModuloSistemaListView, ModuloSistemaCreateView, ModuloSistemaUpdateView, ModuloSistemaDeleteView,
    SubmenuItemListView, SubmenuItemCreateView, SubmenuItemUpdateView, SubmenuItemDeleteView,
    PermisosRolMatrizView, LogAccesoListView, inicializar_sistema_permisos, clonar_permisos_rol,
    obtener_matriz_permisos_ajax, guardar_matriz_permisos_ajax
)

# Importar vistas de prueba
from .views_prueba import (
    prueba_odontograma_anatomico, prueba_aplicar_diagnostico
)

# Importar vistas de laboratorio
from .views_laboratorio import (
    TrabajoLaboratorioListView, TrabajoLaboratorioDetailView,
    TrabajoLaboratorioCreateView, TrabajoLaboratorioUpdateView, TrabajoLaboratorioDeleteView,
    trabajo_laboratorio_cambiar_estado_api, trabajo_laboratorio_obtener_costo_api,
    obtener_citas_paciente_api
)

# Importar vistas de gestión de costos (separado del inventario físico)
from .views_costos import (
    ComprasSinCostosView, CapturarCostosCompraView, ReporteValorInventarioView
)


app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  # Alias para compatibilidad
    
    # Dashboard Financiero
    path('finanzas/', DashboardFinancieroView.as_view(), name='dashboard_financiero'),
    
    # Autenticación
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Rutas de Reportes
    path('reportes/ingresos/', ReporteIngresosView.as_view(), name='reporte_ingresos'),
    path('reportes/ingresos/export/', exportar_ingresos_excel, name='exportar_ingresos_excel'),
    path('reportes/saldos/', ReporteSaldosView.as_view(), name='reporte_saldos'),
    path('reportes/saldos/export/', exportar_saldos_excel, name='exportar_saldos_excel'),
    path('reportes/facturacion/', ReporteFacturacionView.as_view(), name='reporte_facturacion'),
    path('reportes/facturacion/export/', exportar_facturacion_excel, name='exportar_facturacion_excel'),
    path('reportes/servicios-vendidos/', ReporteServiciosMasVendidosView.as_view(), name='reporte_servicios_vendidos'),
    path('reportes/servicios-vendidos/pdf/', generar_servicios_vendidos_pdf, name='reporte_servicios_vendidos_pdf'),
    path('reportes/servicios-vendidos/periodo/', views.ReporteServiciosVendidosPeriodoView.as_view(), name='reporte_servicios_vendidos_periodo'),
    path('reportes/ingresos-dentista/', ReporteIngresosPorDentistaView.as_view(), name='reporte_ingresos_dentista'),
    path('reportes/ingresos-dentista/periodo/', views.ReporteIngresosDentistaPeriodoView.as_view(), name='reporte_ingresos_dentista_periodo'),

    # Rutas de la API
    path('api/pacientes/', views.pacientes_api, name='pacientes_api'),
    path('api/pacientes/crear/', crear_paciente_ajax, name='crear_paciente_ajax'),
    path('api/pacientes/<int:paciente_id>/saldo/', views.paciente_saldo_api, name='paciente_saldo_api'),
    path('api/pacientes/<int:paciente_id>/pagos/', views.paciente_pagos_api, name='paciente_pagos_api'),
    path('api/citas/', agenda_events, name='agenda_events'),
    path('api/citas/<int:pk>/', cita_detail_api, name='cita_detail_api'),
    path('api/odontograma/<int:cliente_id>/', odontograma_api_get, name='odontograma_api_get'),
    path('api/odontograma/<int:cliente_id>/update/', odontograma_api_update, name='odontograma_api_update'),
    path('api/diagnosticos/', diagnostico_api_list, name='diagnostico_api_list'),
    path('api/odontograma/partial/', views.odontograma_partial, name='odontograma_partial'),
    path('api/reportes/ingresos/', reporte_ingresos_api, name='reporte_ingresos_api'),
    path('api/dentista/<int:dentista_id>/servicios/', get_servicios_for_dentista_api, name='api_servicios_por_dentista'),
    path('api/dentista/<int:dentista_id>/horario/', get_horario_dentista_api, name='api_horario_dentista'),
    path('dentistas/', DentistaListView.as_view(), name='dentista_list'),
    path('api/dentista/<int:dentista_id>/horarios-disponibles/', get_horarios_disponibles_api, name='api_horarios_disponibles'),
    path('api/reportes/saldos/', reporte_saldos_api, name='reporte_saldos_api'),

    # Rutas de la aplicación
    path('agenda/', AgendaView.as_view(), name='agenda'),
    path('agenda/legacy/', views.AgendaLegacyView.as_view(), name='agenda_legacy'),
    path('citas/pendientes/', CitasPendientesPagoListView.as_view(), name='citas_pendientes_pago'),
    path('pacientes/pendientes/', PacientesPendientesPagoListView.as_view(), name='pacientes_pendientes_pago'),
    path('citas/<int:pk>/procesar-pago/', ProcesarPagoView.as_view(), name='procesar_pago'),
    path('citas/', CitaListView.as_view(), name='cita_list'),
    path('citas/<int:pk>/estado/', CambiarEstadoCitaView.as_view(), name='cita_cambiar_estado'),
    # path('citas/<int:pk>/finalizar/', FinalizarCitaView.as_view(), name='cita_finalizar'),  # DEPRECATED
    path('citas/<int:pk>/finalizar/content/', finalizar_cita_form_content, name='finalizar_cita_form_content'),
    path('citas/<int:cita_id>/enviar-a-caja/', views.enviar_a_caja_api, name='enviar_a_caja_api'),
    path('citas/<int:pk>/', CitaDetailView.as_view(), name='cita_detail'),
    path('citas/<int:pk>/gestionar/', CitaManageView.as_view(), name='cita_manage'),

    # Rutas para el formulario de Citas en el modal de la agenda
    path('citas/new/', CitaCreateView.as_view(), name='cita_create'),
    path('citas/<int:pk>/update/', CitaUpdateView.as_view(), name='cita_update'),
    path('citas/<int:pk>/delete/', CitaDeleteView.as_view(), name='cita_delete'),

    
    path('pacientes/', PacienteListView.as_view(), name='paciente_list'),
    path('pacientes/new/', PacienteCreateView.as_view(), name='paciente_create'),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name='paciente_detail'),
    path('pacientes/<int:pk>/edit/', PacienteUpdateView.as_view(), name='paciente_edit'),
    path('pacientes/<int:pk>/delete/', PacienteDeleteView.as_view(), name='paciente_delete'),
    path('pacientes/<int:pk>/history/', HistorialPacienteView.as_view(), name='paciente_history'),
    path('pacientes/<int:pk>/invitar/', InvitarPacienteView.as_view(), name='paciente_invitar'),
    path('pacientes/<int:pk>/cuestionario/', CuestionarioHistorialView.as_view(), name='paciente_cuestionario'),
    path('pacientes/<int:pk>/historial-mejorado/', CuestionarioHistorialMejoradoView.as_view(), name='paciente_historial_mejorado'),
    path('pacientes/<int:cliente_id>/odontograma/', views.odontograma_48_view, name='odontograma_48'),
    path('pacientes/<int:pk>/datos-fiscales/', views.PacienteDatosFiscalesView.as_view(), name='paciente_datos_fiscales'),
    path('pacientes/<int:cliente_id>/history/add/', HistorialClinicoCreateView.as_view(), name='historial_create'),
    path('saldos-pendientes/', SaldosPendientesListView.as_view(), name='saldos_pendientes'),
    path('pacientes/<int:paciente_id>/registrar-pago/', RegistrarPagoPacienteView.as_view(), name='registrar_pago_paciente'),

    path('services/', ServicioListView.as_view(), name='service_list'),
    path('services/new/', ServicioCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', ServicioUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', ServicioDeleteView.as_view(), name='service_delete'),

    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/new/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/edit/', UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('usuarios/<int:pk>/delete/', UsuarioDeleteView.as_view(), name='usuario_delete'),
    path('usuarios/<int:pk>/reset-password/', ResetPasswordView.as_view(), name='usuario_reset_password'),
    path('dentistas/<int:dentista_id>/horario/', GestionarHorarioView.as_view(), name='gestionar_horario'),

    path('especialidades/', EspecialidadListView.as_view(), name='especialidad_list'),
    path('especialidades/new/', EspecialidadCreateView.as_view(), name='especialidad_create'),
    path('especialidades/<int:pk>/edit/', EspecialidadUpdateView.as_view(), name='especialidad_edit'),
    path('especialidades/<int:pk>/delete/', EspecialidadDeleteView.as_view(), name='especialidad_delete'),

    path('diagnosticos/', DiagnosticoListView.as_view(), name='diagnostico_list'),
    path('diagnosticos/new/', DiagnosticoCreateView.as_view(), name='diagnostico_create'),
    path('diagnosticos/<int:pk>/edit/', DiagnosticoUpdateView.as_view(), name='diagnostico_edit'),
    path('diagnosticos/<int:pk>/delete/', DiagnosticoDeleteView.as_view(), name='diagnostico_delete'),

    # URLs de Finanzas - Reorganizadas
    path('finanzas/pagos/', PagoListView.as_view(), name='pago_list'),
    path('finanzas/pagos/registrar/', RegistrarPagoView.as_view(), name='pago_create'),
    path('finanzas/pagos/registrar-abono/', RegistrarAbonoView.as_view(), name='registrar_abono'),
    path('finanzas/pagos/registrar/paciente/<int:paciente_id>/', RegistrarPagoView.as_view(), name='pago_create_paciente'),
    path('finanzas/pagos/registrar/cita/<int:cita_id>/', RegistrarPagoView.as_view(), name='pago_create_cita'),
    path('finanzas/pagos/<int:pk>/edit/', PagoUpdateView.as_view(), name='pago_edit'),
    path('finanzas/pagos/<int:pk>/delete/', PagoDeleteView.as_view(), name='pago_delete'),
    path('finanzas/pagos/<int:pk>/recibo/', ReciboPagoView.as_view(), name='recibo_pago'),
    path('finanzas/pagos/<int:pk>/recibo/pdf/', generar_recibo_pdf, name='generar_recibo_pdf'),
    
    # Redirección de compatibilidad
    path('pagos/', lambda request: redirect('/finanzas/', permanent=True)),

    path('proveedores/', ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/new/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/edit/', ProveedorUpdateView.as_view(), name='proveedor_edit'),
    path('proveedores/<int:pk>/delete/', ProveedorDeleteView.as_view(), name='proveedor_delete'),

    path('insumos/', InsumoListView.as_view(), name='insumo_list'),
    path('insumos/new/', InsumoCreateView.as_view(), name='insumo_create'),
    path('insumos/<int:pk>/edit/', InsumoUpdateView.as_view(), name='insumo_edit'),
    path('insumos/<int:pk>/delete/', InsumoDeleteView.as_view(), name='insumo_delete'),
    path('insumos/exportar/', inventario_exportar_excel, name='inventario_exportar'),
    path('insumos/importar/', inventario_importar_excel, name='inventario_importar'),
    path('insumos/lote/<int:lote_id>/ajustar/', ajustar_stock_lote, name='ajustar_stock_lote'),

    path('compras/', CompraListView.as_view(), name='compra_list'),
    path('compras/new/', CompraCreateView.as_view(), name='compra_create'),
    path('compras/<int:pk>/edit/', CompraUpdateView.as_view(), name='compra_edit'),
    path('compras/<int:pk>/delete/', CompraDeleteView.as_view(), name='compra_delete'),
    path('compras/<int:pk>/recibir/', RecibirCompraView.as_view(), name='compra_recibir'),

    # Rutas de Gestión de Costos (módulo separado)
    path('costos/compras-sin-costos/', ComprasSinCostosView.as_view(), name='compras_sin_costos'),
    path('costos/compras/<int:pk>/capturar/', CapturarCostosCompraView.as_view(), name='capturar_costos_compra'),
    path('costos/valor-inventario/', ReporteValorInventarioView.as_view(), name='reporte_valor_inventario'),

    # Rutas de COFEPRIS
    path('cofepris/', DashboardCofeprisView.as_view(), name='dashboard_cofepris'),
    path('cofepris/aviso/', AvisoFuncionamientoListView.as_view(), name='aviso_list'),
    path('cofepris/aviso/registrar/', AvisoFuncionamientoCreateView.as_view(), name='aviso_create'),
    path('cofepris/aviso/<int:pk>/editar/', AvisoFuncionamientoUpdateView.as_view(), name='aviso_edit'),

    path('cofepris/equipos/', EquipoListView.as_view(), name='equipo_list'),
    path('cofepris/equipos/registrar/', EquipoCreateView.as_view(), name='equipo_create'),
    path('cofepris/equipos/<int:pk>/editar/', EquipoUpdateView.as_view(), name='equipo_edit'),
    path('cofepris/equipos/<int:pk>/eliminar/', EquipoDeleteView.as_view(), name='equipo_delete'),

    path('cofepris/residuos/', ResiduosListView.as_view(), name='residuos_list'),
    path('cofepris/residuos/registrar/', ResiduosCreateView.as_view(), name='residuos_create'),
    path('cofepris/residuos/<int:pk>/editar/', ResiduosUpdateView.as_view(), name='residuos_edit'),
    path('cofepris/residuos/<int:pk>/eliminar/', ResiduosDeleteView.as_view(), name='residuos_delete'),

    # Rutas del Portal del Paciente
    path('portal/pagos/', PacientePagosListView.as_view(), name='portal_pagos'),
    path('portal/historial/', views.PortalHistorialPacienteView.as_view(), name='portal_historial'),
    path('portal/historial/completar/', views.PortalCompletarHistorialView.as_view(), name='portal_completar_historial'),

    # === RUTAS CUESTIONARIO DE HISTORIAL CLÍNICO ===
    
    # Cuestionarios para pacientes
    path('cuestionarios/', CuestionarioHistorialListView.as_view(), name='cuestionario_lista'),
    path('cuestionarios/paciente/<int:paciente_id>/completar/', CompletarCuestionarioView.as_view(), name='cuestionario_completar'),
    path('cuestionarios/paciente/<int:paciente_id>/detalle/', CuestionarioDetalleView.as_view(), name='cuestionario_detalle'),
    
    # Administración del cuestionario
    path('admin-cuestionario/categorias/', CategoriaHistorialListView.as_view(), name='categoria_historial_list'),
    path('admin-cuestionario/categorias/nueva/', CategoriaHistorialCreateView.as_view(), name='categoria_historial_create'),
    path('admin-cuestionario/categorias/<int:pk>/editar/', CategoriaHistorialUpdateView.as_view(), name='categoria_historial_edit'),
    
    path('admin-cuestionario/preguntas/', PreguntaHistorialListView.as_view(), name='pregunta_historial_list'),
    path('admin-cuestionario/preguntas/nueva/', PreguntaHistorialCreateView.as_view(), name='pregunta_historial_create'),
    path('admin-cuestionario/preguntas/<int:pk>/editar/', PreguntaHistorialUpdateView.as_view(), name='pregunta_historial_edit'),

    # Rutas para Gestión de Unidades Dentales
    path('unidades/', UnidadDentalListView.as_view(), name='unidad_dental_list'),
    path('unidades/nueva/', UnidadDentalCreateView.as_view(), name='unidad_dental_create'),
    path('unidades/<int:pk>/', UnidadDentalDetailView.as_view(), name='unidad_dental_detail'),
    path('unidades/<int:pk>/editar/', UnidadDentalUpdateView.as_view(), name='unidad_dental_edit'),
    path('unidades/<int:pk>/eliminar/', UnidadDentalDeleteView.as_view(), name='unidad_dental_delete'),

    path('configuracion/preguntas/', PreguntaHistorialListView.as_view(), name='pregunta_list'),
    path('configuracion/preguntas/nueva/', PreguntaHistorialCreateView.as_view(), name='pregunta_create'),
    path('configuracion/preguntas/<int:pk>/editar/', PreguntaHistorialUpdateView.as_view(), name='pregunta_edit'),
    path('configuracion/preguntas/<int:pk>/eliminar/', PreguntaHistorialDeleteView.as_view(), name='pregunta_delete'),

    # Configuración SAT
    path('configuracion/sat/forma-pago/', views.SatFormaPagoListView.as_view(), name='sat_forma_pago_list'),
    path('configuracion/sat/forma-pago/nueva/', views.SatFormaPagoCreateView.as_view(), name='sat_forma_pago_create'),
    path('configuracion/sat/forma-pago/<int:pk>/editar/', views.SatFormaPagoUpdateView.as_view(), name='sat_forma_pago_edit'),
    path('configuracion/sat/forma-pago/<int:pk>/eliminar/', views.SatFormaPagoDeleteView.as_view(), name='sat_forma_pago_delete'),

    path('configuracion/sat/metodo-pago/', views.SatMetodoPagoListView.as_view(), name='sat_metodo_pago_list'),
    path('configuracion/sat/metodo-pago/nuevo/', views.SatMetodoPagoCreateView.as_view(), name='sat_metodo_pago_create'),
    path('configuracion/sat/metodo-pago/<int:pk>/editar/', views.SatMetodoPagoUpdateView.as_view(), name='sat_metodo_pago_edit'),
    path('configuracion/sat/metodo-pago/<int:pk>/eliminar/', views.SatMetodoPagoDeleteView.as_view(), name='sat_metodo_pago_delete'),

    path('configuracion/sat/regimen-fiscal/', views.SatRegimenFiscalListView.as_view(), name='sat_regimen_fiscal_list'),
    path('configuracion/sat/regimen-fiscal/nuevo/', views.SatRegimenFiscalCreateView.as_view(), name='sat_regimen_fiscal_create'),
    path('configuracion/sat/regimen-fiscal/<int:pk>/editar/', views.SatRegimenFiscalUpdateView.as_view(), name='sat_regimen_fiscal_edit'),
    path('configuracion/sat/regimen-fiscal/<int:pk>/eliminar/', views.SatRegimenFiscalDeleteView.as_view(), name='sat_regimen_fiscal_delete'),

    path('configuracion/sat/uso-cfdi/', views.SatUsoCFDIListView.as_view(), name='sat_uso_cfdi_list'),
    path('configuracion/sat/uso-cfdi/nuevo/', views.SatUsoCFDICreateView.as_view(), name='sat_uso_cfdi_create'),
    path('configuracion/sat/uso-cfdi/<int:pk>/editar/', views.SatUsoCFDIUpdateView.as_view(), name='sat_uso_cfdi_edit'),
    path('configuracion/sat/uso-cfdi/<int:pk>/eliminar/', views.SatUsoCFDIDeleteView.as_view(), name='sat_uso_cfdi_delete'),

    path('citas/cancelar/<int:cita_id>/', views.cancelar_cita_api, name='cancelar_cita_api'),
    
    # === RUTAS DEL SISTEMA DE PERMISOS DINÁMICOS ===
    
    # Panel principal de administración de permisos
    path('admin/permisos/', PermisosAdminView.as_view(), name='admin_permisos'),
    
    # Gestión de módulos
    path('admin/permisos/modulos/', ModuloSistemaListView.as_view(), name='modulo_list'),
    path('admin/permisos/modulos/crear/', ModuloSistemaCreateView.as_view(), name='modulo_create'),
    path('admin/permisos/modulos/<int:pk>/editar/', ModuloSistemaUpdateView.as_view(), name='modulo_edit'),
    path('admin/permisos/modulos/<int:pk>/eliminar/', ModuloSistemaDeleteView.as_view(), name='modulo_delete'),
    
    # Gestión de submenús
    path('admin/permisos/submenus/', SubmenuItemListView.as_view(), name='submenu_list'),
    path('admin/permisos/submenus/crear/', SubmenuItemCreateView.as_view(), name='submenu_create'),
    path('admin/permisos/submenus/<int:pk>/editar/', SubmenuItemUpdateView.as_view(), name='submenu_edit'),
    path('admin/permisos/submenus/<int:pk>/eliminar/', SubmenuItemDeleteView.as_view(), name='submenu_delete'),
    
    # Matriz de permisos
    path('admin/permisos/matriz/', PermisosRolMatrizView.as_view(), name='permisos_matriz'),
    
    # Logs de acceso
    path('admin/permisos/logs/', LogAccesoListView.as_view(), name='log_acceso_list'),
    
    # APIs AJAX para permisos
    path('api/permisos/inicializar/', inicializar_sistema_permisos, name='api_inicializar_permisos'),
    path('api/permisos/clonar/', clonar_permisos_rol, name='api_clonar_permisos'),
    path('api/permisos/matriz/obtener/', obtener_matriz_permisos_ajax, name='admin_permisos_obtener_matriz'),
    path('api/permisos/matriz/guardar/', guardar_matriz_permisos_ajax, name='admin_permisos_guardar_matriz'),

    # === RUTAS PARA CONSENTIMIENTO INFORMADO ===
    
    # Gestión de documentos de consentimiento
    path('consentimientos/', views.ConsentimientoInformadoListView.as_view(), name='consentimiento_list'),
    path('consentimientos/nuevo/', views.ConsentimientoInformadoCreateView.as_view(), name='consentimiento_create'),
    path('consentimientos/<int:pk>/', views.ConsentimientoInformadoDetailView.as_view(), name='consentimiento_detail'),
    path('consentimientos/<int:pk>/editar/', views.ConsentimientoInformadoUpdateView.as_view(), name='consentimiento_edit'),
    path('consentimientos/<int:consentimiento_id>/descargar/', views.descargar_consentimiento_pdf, name='descargar_consentimiento_pdf'),
    
    # Gestión de consentimientos de pacientes
    path('pacientes-consentimientos/', views.PacienteConsentimientoListView.as_view(), name='paciente_consentimiento_list'),
    path('pacientes-consentimientos/<int:pk>/', views.PacienteConsentimientoDetailView.as_view(), name='paciente_consentimiento_detail'),
    path('pacientes-consentimientos/<int:paciente_consentimiento_id>/firmar/', views.firmar_consentimiento, name='firmar_consentimiento'),
    
    # Integración con cuestionario
    path('cuestionarios/<int:cuestionario_id>/presentar-consentimiento/', views.presentar_consentimiento_desde_cuestionario, name='presentar_consentimiento_desde_cuestionario'),
    path('pacientes/<int:paciente_id>/cuestionario-consentimiento/', views.cuestionario_con_consentimiento, name='cuestionario_con_consentimiento'),

    # Configuración de clínica
    path('configuracion/', views.configuracion_clinica, name='configuracion_clinica'),

    # === RUTAS DE TRABAJOS DE LABORATORIO ===

    # Listado y detalle
    path('trabajos-laboratorio/', TrabajoLaboratorioListView.as_view(), name='trabajo_laboratorio_list'),
    path('trabajos-laboratorio/<int:pk>/', TrabajoLaboratorioDetailView.as_view(), name='trabajo_laboratorio_detail'),

    # Creación y edición
    path('trabajos-laboratorio/nuevo/', TrabajoLaboratorioCreateView.as_view(), name='trabajo_laboratorio_create'),
    path('trabajos-laboratorio/<int:pk>/editar/', TrabajoLaboratorioUpdateView.as_view(), name='trabajo_laboratorio_update'),
    path('trabajos-laboratorio/<int:pk>/eliminar/', TrabajoLaboratorioDeleteView.as_view(), name='trabajo_laboratorio_delete'),

    # Crear desde cita o paciente
    path('citas/<int:cita_id>/trabajo-laboratorio/nuevo/', TrabajoLaboratorioCreateView.as_view(), name='trabajo_laboratorio_create_desde_cita'),
    path('pacientes/<int:paciente_id>/trabajo-laboratorio/nuevo/', TrabajoLaboratorioCreateView.as_view(), name='trabajo_laboratorio_create_desde_paciente'),

    # APIs
    path('api/trabajos-laboratorio/<int:pk>/cambiar-estado/', trabajo_laboratorio_cambiar_estado_api, name='trabajo_laboratorio_cambiar_estado_api'),
    path('api/trabajos-laboratorio/obtener-costo/', trabajo_laboratorio_obtener_costo_api, name='trabajo_laboratorio_obtener_costo_api'),
    path('api/pacientes/<int:paciente_id>/citas/', obtener_citas_paciente_api, name='obtener_citas_paciente_api'),
]

# ============================================================================
# RUTAS DE DEBUG Y DESARROLLO
# ============================================================================
# Solo incluir en modo desarrollo (DEBUG=True)
# Estas rutas NO deben estar disponibles en producción

from django.conf import settings

if settings.DEBUG:
    from .urls_debug import debug_patterns
    urlpatterns += debug_patterns
