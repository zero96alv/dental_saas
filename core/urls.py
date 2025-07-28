from django.urls import path
from .views import (
    DashboardView,
    PacienteListView, PacienteDetailView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView,
    ServicioListView, ServicioCreateView, ServicioUpdateView, ServicioDeleteView,
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView,
    EspecialidadListView, EspecialidadCreateView, EspecialidadUpdateView, EspecialidadDeleteView,
    PagoListView, PagoCreateView, PagoUpdateView, PagoDeleteView,
    ProveedorListView, ProveedorCreateView, ProveedorUpdateView, ProveedorDeleteView,
    InsumoListView, InsumoCreateView, InsumoUpdateView, InsumoDeleteView,
    CompraListView, CompraCreateView, CompraUpdateView, CompraDeleteView, RecibirCompraView,
    AgendaView, CitaListView, CitasPendientesPagoListView, FinalizarCitaView, 
    CambiarEstadoCitaView,
    ProcesarPagoView, RegistrarPagoView, ReciboPagoView,  # ← AGREGADOS AQUÍ
    HistorialPacienteView, HistorialClinicoCreateView,
    agenda_events,
    cita_create_api,
    cita_detail_api,
    cita_update_api,
    cita_delete_api,
    odontograma_api_get,
    odontograma_api_update,
    diagnostico_api_list,
    reporte_ingresos_api,
    reporte_saldos_api,
    ReporteIngresosView, ReporteSaldosView, ReporteFacturacionView,
    ReporteServiciosMasVendidosView, ReporteIngresosPorDentistaView,
    DiagnosticoListView, DiagnosticoCreateView, DiagnosticoUpdateView, DiagnosticoDeleteView,
    exportar_ingresos_excel, exportar_saldos_excel, exportar_facturacion_excel,
    generar_recibo_pdf,
    DashboardCofeprisView,
    AvisoFuncionamientoListView, AvisoFuncionamientoCreateView, AvisoFuncionamientoUpdateView,
    EquipoListView, EquipoCreateView, EquipoUpdateView, EquipoDeleteView,
    ResiduosListView, ResiduosCreateView, ResiduosUpdateView, ResiduosDeleteView,
    InvitarPacienteView, PacientePagosListView, ResetPasswordView, CuestionarioHistorialView,
    PreguntaHistorialListView, PreguntaHistorialCreateView, PreguntaHistorialUpdateView, PreguntaHistorialDeleteView
)

app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),

    # Rutas de Reportes
    path('reportes/ingresos/', ReporteIngresosView.as_view(), name='reporte_ingresos'),
    path('reportes/ingresos/export/', exportar_ingresos_excel, name='exportar_ingresos_excel'),
    path('reportes/saldos/', ReporteSaldosView.as_view(), name='reporte_saldos'),
    path('reportes/saldos/export/', exportar_saldos_excel, name='exportar_saldos_excel'),
    path('reportes/facturacion/', ReporteFacturacionView.as_view(), name='reporte_facturacion'),
    path('reportes/facturacion/export/', exportar_facturacion_excel, name='exportar_facturacion_excel'),
    path('reportes/servicios-vendidos/', ReporteServiciosMasVendidosView.as_view(), name='reporte_servicios_vendidos'),
    path('reportes/ingresos-dentista/', ReporteIngresosPorDentistaView.as_view(), name='reporte_ingresos_dentista'),

    # Rutas de la API
    path('api/citas/', agenda_events, name='agenda_events'),
    path('api/citas/create/', cita_create_api, name='cita_create_api'),
    path('api/citas/<int:pk>/', cita_detail_api, name='cita_detail_api'),
    path('api/citas/<int:pk>/update/', cita_update_api, name='cita_update_api'),
    path('api/citas/<int:pk>/delete/', cita_delete_api, name='cita_delete_api'),
    path('api/odontograma/<int:cliente_id>/', odontograma_api_get, name='odontograma_api_get'),
    path('api/odontograma/<int:cliente_id>/update/', odontograma_api_update, name='odontograma_api_update'),
    path('api/diagnosticos/', diagnostico_api_list, name='diagnostico_api_list'),
    path('api/reportes/ingresos/', reporte_ingresos_api, name='reporte_ingresos_api'),
    path('api/reportes/saldos/', reporte_saldos_api, name='reporte_saldos_api'),

    # Rutas de la aplicación
    path('agenda/', AgendaView.as_view(), name='agenda'),
    path('citas/pendientes/', CitasPendientesPagoListView.as_view(), name='citas_pendientes_pago'),
    path('citas/<int:pk>/procesar-pago/', ProcesarPagoView.as_view(), name='procesar_pago'),
    path('citas/', CitaListView.as_view(), name='cita_list'),
    path('citas/<int:pk>/estado/', CambiarEstadoCitaView.as_view(), name='cita_cambiar_estado'), 
    path('citas/<int:pk>/finalizar/', FinalizarCitaView.as_view(), name='cita_finalizar'),
    
    path('pacientes/', PacienteListView.as_view(), name='paciente_list'),
    path('pacientes/new/', PacienteCreateView.as_view(), name='paciente_create'),
    path('pacientes/<int:pk>/', PacienteDetailView.as_view(), name='paciente_detail'),
    path('pacientes/<int:pk>/edit/', PacienteUpdateView.as_view(), name='paciente_edit'),
    path('pacientes/<int:pk>/delete/', PacienteDeleteView.as_view(), name='paciente_delete'),
    path('pacientes/<int:pk>/history/', HistorialPacienteView.as_view(), name='paciente_history'),
    path('pacientes/<int:pk>/invitar/', InvitarPacienteView.as_view(), name='paciente_invitar'),
    path('pacientes/<int:pk>/cuestionario/', CuestionarioHistorialView.as_view(), name='paciente_cuestionario'),
    path('pacientes/<int:cliente_id>/history/add/', HistorialClinicoCreateView.as_view(), name='historial_create'),

    path('services/', ServicioListView.as_view(), name='service_list'),
    path('services/new/', ServicioCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', ServicioUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', ServicioDeleteView.as_view(), name='service_delete'),

    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/new/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/edit/', UsuarioUpdateView.as_view(), name='usuario_edit'),
    path('usuarios/<int:pk>/reset-password/', ResetPasswordView.as_view(), name='usuario_reset_password'),

    path('especialidades/', EspecialidadListView.as_view(), name='especialidad_list'),
    path('especialidades/new/', EspecialidadCreateView.as_view(), name='especialidad_create'),
    path('especialidades/<int:pk>/edit/', EspecialidadUpdateView.as_view(), name='especialidad_edit'),
    path('especialidades/<int:pk>/delete/', EspecialidadDeleteView.as_view(), name='especialidad_delete'),

    path('diagnosticos/', DiagnosticoListView.as_view(), name='diagnostico_list'),
    path('diagnosticos/new/', DiagnosticoCreateView.as_view(), name='diagnostico_create'),
    path('diagnosticos/<int:pk>/edit/', DiagnosticoUpdateView.as_view(), name='diagnostico_edit'),
    path('diagnosticos/<int:pk>/delete/', DiagnosticoDeleteView.as_view(), name='diagnostico_delete'),

    path('pagos/', PagoListView.as_view(), name='pago_list'),
    path('pagos/registrar/', RegistrarPagoView.as_view(), name='pago_create'),
    path('pagos/registrar/paciente/<int:paciente_id>/', RegistrarPagoView.as_view(), name='pago_create_paciente'),
    path('pagos/registrar/cita/<int:cita_id>/', RegistrarPagoView.as_view(), name='pago_create_cita'),
    path('pagos/<int:pk>/edit/', PagoUpdateView.as_view(), name='pago_edit'),
    path('pagos/<int:pk>/delete/', PagoDeleteView.as_view(), name='pago_delete'),
    path('pagos/<int:pk>/recibo/', ReciboPagoView.as_view(), name='recibo_pago'),
    path('pagos/<int:pk>/recibo/pdf/', generar_recibo_pdf, name='generar_recibo_pdf'),

    path('proveedores/', ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/new/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/edit/', ProveedorUpdateView.as_view(), name='proveedor_edit'),
    path('proveedores/<int:pk>/delete/', ProveedorDeleteView.as_view(), name='proveedor_delete'),

    path('insumos/', InsumoListView.as_view(), name='insumo_list'),
    path('insumos/new/', InsumoCreateView.as_view(), name='insumo_create'),
    path('insumos/<int:pk>/edit/', InsumoUpdateView.as_view(), name='insumo_edit'),
    path('insumos/<int:pk>/delete/', InsumoDeleteView.as_view(), name='insumo_delete'),

    path('compras/', CompraListView.as_view(), name='compra_list'),
    path('compras/new/', CompraCreateView.as_view(), name='compra_create'),
    path('compras/<int:pk>/edit/', CompraUpdateView.as_view(), name='compra_edit'),
    path('compras/<int:pk>/delete/', CompraDeleteView.as_view(), name='compra_delete'),
    path('compras/<int:pk>/recibir/', RecibirCompraView.as_view(), name='compra_recibir'),

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

    # Rutas de Configuración del Cuestionario
    path('configuracion/preguntas/', PreguntaHistorialListView.as_view(), name='pregunta_list'),
    path('configuracion/preguntas/nueva/', PreguntaHistorialCreateView.as_view(), name='pregunta_create'),
    path('configuracion/preguntas/<int:pk>/editar/', PreguntaHistorialUpdateView.as_view(), name='pregunta_edit'),
    path('configuracion/preguntas/<int:pk>/eliminar/', PreguntaHistorialDeleteView.as_view(), name='pregunta_delete'),
]