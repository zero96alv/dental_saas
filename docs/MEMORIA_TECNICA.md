# MEMORIA TECNICA - Dental SaaS

Este documento resume la arquitectura, componentes clave y flujos principales del sistema Dental SaaS, incluyendo cambios recientes realizados para gestión de pacientes, agenda y citas.

1. Arquitectura general
- Framework: Django 4.2 con django-tenants (multi-tenant por esquema)
- Apps: tenants (compartida), core (tenant), librerías: crispy_forms, crispy_bootstrap5, django_extensions
- Plantillas: templates global y core/templates/core
- Multi-tenant:
  - TENANT_MODEL: tenants.Clinica
  - TENANT_DOMAIN_MODEL: tenants.Domain
  - PUBLIC_SCHEMA_URLCONF: dental_saas.urls_public
  - ROOT_URLCONF: dental_saas.urls_tenant

2. Modelos relevantes (core)
- Paciente: datos personales, email único, validación de teléfono MX; dirección estructurada (calle, numero_exterior, codigo_postal, colonia, municipio, estado). Campo direccion legacy preservado para compatibilidad. saldo_global para deudas.
- PerfilDentista: perfil extendido para rol dentista; relación con User y especialidades; activo, horarios (HorarioLaboral).
- Cita: relación con paciente, dentista, unidad_dental; estados: PRO, CON, ATN, COM, CAN; servicios_planeados y servicios_realizados (M2M); pagos relacionados.
- Pago: relación con Cita y/o Paciente; usado para reportes de ingresos y cálculo de saldos; recibos en PDF/ticket.
- Insumo, LoteInsumo, Compra, DetalleCompra: inventario y consumos (FEFO);
- Diagnostico, EstadoDiente, HistorialClinico: odontograma y notas clínicas.
- Otros: Especialidad, Servicio, UnidadDental, Residuos, Equipo, AvisoFuncionamiento.

3. Formularios destacados
- PacienteForm: validación de teléfono MX con regex, email obligatorio y único, widgets y placeholders para dirección estructurada.
- CitaForm, FinalizarCitaForm: soportan planeación/realización de servicios y cálculo de duración estimada.
- PagoForm: registro de pagos, opción desea_factura y validaciones básicas; DatosFiscalesForm cuando aplica.
- HorarioLaboralFormSet: administración de horarios por dentista.

4. Vistas y flujos principales
- DashboardView: redirige por rol (Administrador, Dentista, Recepcionista, Paciente). Estadísticas por periodo.
- AgendaView: muestra calendario; context con CitaForm, PacienteForm y dentistas activos. Endpoints API para eventos.
- CitaListView: listado con filtros por estado/dentista/fecha/paciente. Estadísticas y totales.
- CitaManageView: pantalla integral para gestionar una cita con acciones rápidas (cambio de estado, acceso a historial y cuestionario).
- CambiarEstadoCitaView: actualiza estado vía AJAX con validación contra Cita.ESTADOS_CITA.
- CitasPendientesPagoListView/ProcesarPagoView: flujo de cierre y caja; actualiza saldo_global del paciente.
- HistorialPacienteView/HistorialClinicoCreateView: odontograma y notas clínicas, cálculo y mapeo de posiciones dentales.
- Ajax en agenda: crear paciente en línea (crear_paciente_ajax), cargar datos de cita en modal (cita_detail_api) y disponibilidad de horarios.
- Sistema de permisos/menú dinámico: core/context_processors.menu_dinamico + templates/core/partials/menu_dinamico.html. Entradas visibles por rol.

5. URLs clave (core/urls.py)
Importante: estas rutas son relativas al tenant actual (subdominio). En desarrollo use http://{subdominio}.localhost:8000/ en lugar de http://127.0.0.1:8000/.
- /agenda/ (AgendaView)
- /citas/ (CitaListView) y /citas/<id>/gestionar/ (CitaManageView)
- /pacientes/ (CRUD completo y cuestionario/historial)
- /usuarios/ (CRUD de usuarios) y /dentistas/ (DentistaListView)
- API: /api/pacientes/crear/, /api/citas/, /api/citas/<id>/, /api/dentista/<id>/horarios-disponibles/, /api/odontograma/... entre otros.
- Reportes: ingresos, saldos, facturación; exportación a Excel y recibo en PDF/ticket.

6. Cambios recientes y mejoras
- Paciente: dirección estructurada, validación fuerte de teléfono y email único.
- Agenda: eventClick para editar; modal para crear pacientes; precarga de datos en modal; AJAX para persistir y recargar.
- Citas: botones de cambio de estado (Programada, Confirmada, Atendida, Completada, Cancelada) con AJAX y notificaciones.
- Menú: etiqueta actualizada a “Gestión de Citas”; visibilidad por rol (Administrador/Recepcionista/Dentista).
- Correcciones en templates y tags: control de grupos más robusto y limpieza de bloques duplicados en agenda.
- Logging en vistas: se agregaron logs de depuración en UsuarioListView y AgendaView para ayudar a inspeccionar fallas.

7. Inventario y consumos (resumen)
- Recepción de compras actualiza stock por LoteInsumo.
- FinalizarCita: consume insumos según FEFO y registra eventos en historial clínico.

8. Facturación y pagos
- ProcesarPagoView: crea pagos ligados a la cita; soporta flujo de datos fiscales cuando desea_factura.
- Recibos: generación en PDF tamaño carta y ticket, con logo del tenant.

9. Multi-tenant, subdominios y autenticación/sesión
- Esquema multi-tenant con django-tenants: cada clínica vive en su propio esquema (public, demo, etc.).
- Resolución por subdominio: las rutas de tenant se sirven con ROOT_URLCONF=dental_saas.urls_tenant y las públicas con PUBLIC_SCHEMA_URLCONF=dental_saas.urls_public. Al probar, use el subdominio del tenant (ej.: http://demo.localhost:8000/), no rutas sin dominio.
- Evitar hardcodear rutas: use {% url 'core:...' %} y reverse('core:...') para que el host/subdominio actual se respete.
- En desarrollo, agregue entradas demo.localhost -> 127.0.0.1 en el archivo hosts o configure tenants.Domain.
- Tenant en request (request.tenant) se usa para branding y filtros (COFEPRIS).
- Logout reforzado (CustomLogoutView) limpia sesión y cookies y fuerza headers no-cache.

10. Activación de DEBUG y logging
- DEBUG por variable de entorno: DEBUG=true en .env para desarrollo.
- LOG_LEVEL configurable (por defecto DEBUG en dev, INFO en prod). Directorio de logs: BASE_DIR/logs.
- Loggers: django (INFO), core y core.views (LOG_LEVEL), console y archivo rotativo.

11. Cómo habilitar logs detallados temporalmente en producción
- Establecer LOG_LEVEL=DEBUG y asegurar handlers de file estén activos.
- Limitar tiempo de activación y revertir a INFO para evitar volúmenes grandes.

12. Próximos pasos sugeridos (ACTUALIZADO 25 Agosto 2025)

### PRIORIDADES INMEDIATAS (Próxima sesión)
1. **Probar las correcciones implementadas**:
   - Verificar visualización correcta de especialidades en formularios
   - Probar creación/edición de servicios con ServicioForm
   - Validar mensajes de error en CitaForm para incompatibilidades
   - Confirmar funcionamiento del botón "Nuevo Paciente"

2. **Completar datos maestros**:
   - Crear especialidades por defecto (General, Ortodoncia, Endodoncia, etc.)
   - Asignar especialidades a dentistas existentes
   - Verificar que no existan servicios huérfanos sin especialidad

### MEJORAS FUTURAS (Medio plazo)
- Migrar completamente a dirección estructurada (deprecando campo direccion legacy)
- Tests unitarios para endpoints AJAX críticos (crear_paciente_ajax, cambio de estado de citas, disponibilidad de horarios)
- Auditoría de permisos por rol en menús dinámicos y vistas sensibles
- Implementar validación frontend para formularios críticos
- Mejorar mensajes de error en español para mejor UX

### OBSERVACIONES TÉCNICAS CRÍTICAS
- **ServicioForm**: Requiere que existan especialidades en BD antes de crear servicios
- **CitaForm**: Validación de especialidades es estricta, puede generar confusión si no hay datos maestros
- **Template de agenda**: Botón "Nuevo Paciente" puede necesitar verificación de funcionalidad AJAX
- **Especialidades**: El método __str__ es crítico para UX, verificar en otros modelos similares

Anexos
- Variables de entorno relevantes (.env):
  - DEBUG=true|false
  - LOG_LEVEL=DEBUG|INFO|WARNING
  - DJANGO_SECRET_KEY, DB_*, EMAIL_*

