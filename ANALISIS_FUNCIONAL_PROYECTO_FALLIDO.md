# Análisis Funcional y Consideraciones Técnicas del Proyecto Fallido "Dental Clinic"

**Fecha de Análisis:** 25 de Julio de 2025

**Propósito del Documento:** Este documento desglosa las funcionalidades, formularios y estructura del proyecto "Dental Clinic" archivado. Su objetivo es servir como referencia y guía para el rediseño y reconstrucción de un nuevo sistema, evitando los errores arquitectónicos que llevaron al fracaso del intento anterior.

---

## 1. Lecciones Aprendidas y Consideraciones Críticas para el Nuevo Proyecto

El fracaso del proyecto anterior se debió a un **problema irresoluble de dependencia circular en las migraciones de Django** al intentar implementar `django-tenants`. Para el nuevo proyecto, es **imperativo** seguir estas directrices:

1.  **Arquitectura Multi-Tenant Primero:** La configuración de `django-tenants` debe ser lo **primero** que se haga. Crear el esquema público, el modelo del Tenant, y asegurarse de que las migraciones iniciales funcionen **antes** de añadir cualquier otra aplicación.
2.  **Separación Estricta de Apps:**
    *   Crear una app para los modelos del **esquema público** (ej. `tenants_app` para el modelo del Tenant y el `User`).
    *   Crear una app separada para los modelos del **esquema del tenant** (ej. `clinic_app` para Pacientes, Citas, etc.).
    *   No mezclar modelos públicos y de tenant en la misma app.
3.  **Evitar Migraciones de Datos Complejas al Inicio:** El error fatal fue causado por una migración de datos (`RunPython` en `0002_crear_grupos_iniciales.py`) que intentaba usar el framework `contenttypes` antes de que estuviera listo en el esquema del tenant.
    *   **Solución:** No usar `RunPython` para crear datos iniciales como Grupos o Permisos. En su lugar, utilizar **comandos de gestión (`management commands`)** que se ejecutan *después* de que todas las migraciones se hayan completado. Un comando como `python manage.py setup_initial_data` es seguro y desacoplado del proceso de migración.
4.  **Planificación de Modelos y Relaciones:**
    *   Las `ForeignKey` entre modelos de tenant y modelos públicos (como `User` que reside en el esquema público) son un punto delicado. Hay que planificar cuidadosamente cómo se relacionarán los datos y considerar el impacto en el rendimiento de las consultas.
    *   **Precaución con Signals:** Las señales de Django (`post_save`, `post_delete`) que operan sobre modelos de tenant deben ser escritas cuidadosamente para no intentar acceder a datos de otros tenants o del esquema público de forma inesperada.
5.  **Flujo de Trabajo de Desarrollo Sugerido (Corregido):**
    1.  `django-admin startproject ...`
    2.  Configurar `django-tenants` y la base de datos.
    3.  Crear la app `tenants_app` con el modelo del Tenant y el del Dominio.
    4.  Ejecutar `makemigrations` y `migrate_schemas --shared` para crear el esquema público.
    5.  Crear el primer tenant (el tenant "público" o de gestión) y su dominio.
    6.  Crear la app `clinic_app` para los modelos del tenant (Paciente, Cita, etc.).
    7.  Añadir los modelos a `clinic_app` **sin `ForeignKey` complejas al principio**.
    8.  Ejecutar `makemigrations` y `migrate_schemas --tenant` para aplicar las migraciones a los tenants existentes.
    9.  **Solo después de que todo lo anterior funcione**, empezar a añadir la lógica de negocio, formularios, vistas y APIs.

---

## 2. Análisis Funcional por Módulo

### Módulo 1: Gestión de Pacientes (Clientes)

*   **Descripción:** CRUD completo para la información de los pacientes, incluyendo datos personales, historial médico y datos fiscales.
*   **Modelos Principales:** `Cliente`, `User`. Se usa un modelo abstracto `PersonaBase` para evitar duplicar campos.
*   **Formularios:** `ClienteForm` (incluye validaciones de formato para `CURP` y `RFC` con expresiones regulares).
*   **URLs y Vistas:**
    *   `/clientes/`: Listado de todos los pacientes (`cliente_list`).
    *   `/clientes/nuevo/`: Crear un nuevo paciente (`cliente_nuevo`).
    *   `/clientes/<id>/editar/`: Editar un paciente existente (`cliente_editar`).
    *   `/clientes/<id>/eliminar/`: Eliminar un paciente (`cliente_eliminar`).
    *   `/clientes/<id>/detalle/`: Vista 360° de un paciente con sus citas, pagos e historial (`cliente_detalle`).

### Módulo 2: Agenda y Citas

*   **Descripción:** Sistema de agendamiento visual con FullCalendar, gestión del ciclo de vida de las citas y lógica de negocio para la disponibilidad.
*   **Modelos Principales:** `Cita`, `Servicio`, `HorarioAtencion`, `User` (Dentista).
*   **Lógica Clave:**
    *   El formulario `CitaForm` valida que la especialidad del dentista sea compatible con la requerida por el servicio.
    *   Los campos `total_cobrar` y `saldo` de la `Cita` se actualizan **automáticamente mediante señales** cuando se añaden/eliminan tratamientos o pagos, garantizando la integridad de los datos.
*   **URLs y Vistas:**
    *   `/agenda/`: Vista principal del calendario (`agenda_view`).
    *   `/citas/`: Listado tabular de todas las citas (`cita_list`).
    *   `/citas/<id>/detalle/`: Vista detallada de la cita con sus cargos y pagos (`cita_detalle`).
    *   `/mis-citas/`: Portal del paciente para ver su historial de citas (`mis_citas`).

### Módulo 3: Historial Clínico y Odontograma

*   **Descripción:** Gestión del historial médico del paciente, incluyendo un odontograma interactivo para registrar el estado de cada pieza dental.
*   **Arquitectura de Datos:**
    *   `EstadoDiente`: Representa el **estado actual y "vivo"** del odontograma de un paciente.
    *   `HistorialClinico`: Funciona como un **registro inmutable (log)**. Cada vez que se modifica un `EstadoDiente`, se crea una nueva entrada aquí para registrar el cambio, quién lo hizo y cuándo.
*   **Modelos Principales:** `HistorialClinico`, `AdjuntoHistorial`, `Diente`, `EstadoDiente`, `Diagnostico`.
*   **URLs y Vistas:**
    *   `/clientes/<id>/historial/nuevo/`: Añade una nueva nota de evolución, permitiendo adjuntar archivos (`nota_evolucion_nueva`).
    *   `/odontograma/<id_cliente>/`: Vista del odontograma interactivo (`odontograma_view`).

### Módulo 4: Flujo de Cobro y Pagos

*   **Descripción:** Sistema para gestionar los cargos generados en una cita y registrar los pagos correspondientes.
*   **Lógica Clave:**
    *   La vista `finalizar_cita` permite modificar los servicios realmente prestados, que pueden ser diferentes al servicio con el que se agendó la cita.
    *   Se usan `TratamientoRealizado` y `TrabajoTecnico` para registrar todos los cargos.
    *   Las vistas de pago y finalización usan `transaction.atomic()` para garantizar que las operaciones en la base de datos sean completas o no se realicen en absoluto.
*   **Modelos Principales:** `Cita`, `Pago`, `TratamientoRealizado`, `TrabajoTecnico`, `PlanPago`.
*   **URLs y Vistas:**
    *   `/citas/<id>/finalizar/`: Interfaz para confirmar servicios y generar los cargos (`finalizar_cita`).
    *   `/citas/<id>/pagar/`: Formulario para registrar un nuevo pago a una cita (`pago_nuevo`).
    *   `/pagos/<id>/recibo/`: Genera un recibo en PDF (con lógica para formato carta o ticket) (`generar_recibo_pdf`).

### Módulo 5: Gestión de Inventario y Compras

*   **Descripción:** Control de stock de insumos, gestión de proveedores y ciclo de compras.
*   **Lógica Clave:**
    *   El formulario de compras usa `inlineformset_factory`, el patrón correcto en Django para editar un objeto principal (compra) y sus detalles en la misma página.
    *   El modelo `ServicioInsumo` vincula qué insumos y en qué cantidad se usan por servicio. Esto permite la **deducción automática del stock** cuando una cita se marca como 'completada'.
*   **Modelos Principales:** `Insumo`, `ServicioInsumo`, `Proveedor`, `Compra`, `DetalleCompra`.
*   **URLs y Vistas:**
    *   **Insumos, Proveedores:** CRUDs completos en `/insumos/` y `/proveedores/`.
    *   `/compras/nueva/`: Registrar una nueva compra y sus detalles (`compra_nueva`).
    *   `/compras/<id>/recibir/`: Marcar una compra como recibida, lo que dispara la actualización del stock de insumos (`compra_marcar_recibida`).

### Módulo 6: Administración y Configuración

*   **Descripción:** Módulo para la gestión de personal, catálogos del sistema y configuración general.
*   **Lógica Clave:** La vista `dashboard` principal redirige a diferentes plantillas según el rol del usuario (Administrador, Dentista, Recepcionista), mostrando información relevante para cada uno.
*   **Modelos Principales:** `User`, `Group`, `PerfilDentista`, `Especialidad`, `Servicio`, `Laboratorio`, `ConfiguracionReporte`.
*   **URLs y Vistas:**
    *   `/usuarios/`: CRUD de usuarios, con lógica para asignar grupos y especialidades a dentistas a través de su `PerfilDentista`.
    *   `/servicios/<id>/editar/`: Permite asociar los insumos que consume un servicio.
    *   `/horarios/`: CRUD para definir los horarios de atención de los dentistas.

### Módulo 7: Reportes y Facturación

*   **Descripción:** Generación de reportes de negocio y un módulo para preparar la información para facturación externa.
*   **Lógica Clave:** Las vistas de exportación usan `OpenPyXL` para generar archivos Excel `.xlsx` dinámicamente a partir de los datos filtrados.
*   **Modelos Principales:** `Cita`, `Pago`, `Cliente`.
*   **URLs y Vistas:**
    *   `/reportes/*`: Vistas para reportes de ingresos, servicios, consumo de insumos y saldos pendientes.
    *   `/reportes/facturacion/`: Agrupa todas las citas marcadas para facturar.
    *   `/citas/<id>/solicitar-factura/`: Marca una cita para ser facturada. Valida que el cliente tenga datos fiscales completos antes de permitir la acción.
    *   `/reportes/*/exportar/`: Endpoints para descargar los reportes en formato Excel.

---

## 3. Automatización y Procesos en Segundo Plano (`core/tasks.py`)

El sistema utiliza tareas asíncronas (probablemente con Django-Q) para ejecutar procesos sin afectar la experiencia del usuario.

*   **Recordatorios de Cita:** Una tarea diaria busca citas para el día siguiente y envía un email de recordatorio al paciente.
*   **Felicitaciones de Cumpleaños:** Una tarea diaria busca pacientes que cumplen años y les envía una felicitación.
*   **Recordatorios de Saldo Pendiente:** Una tarea periódica revisa las citas completadas con saldo pendiente y envía un recordatorio de pago al paciente. Esta función se puede activar/desactivar por cita.

---

## 4. Resumen de Endpoints de la API REST

*   `GET /api/citas/`: **(Para FullCalendar)** Lista citas como eventos para ser mostradas en el calendario.
*   `GET /api/dentistas-por-servicio/?servicio_id=<id>`: **(Para Formulario de Citas)** Devuelve los dentistas cuya especialidad coincide con la requerida por un servicio.
*   `GET /api/horarios-disponibles/?...`: **(Para Formulario de Citas)** Calcula y devuelve los slots de tiempo libres de un dentista para una fecha y servicio específicos.
*   `POST /api/clientes/nuevo/`: **(Para Formulario de Citas)** Permite dar de alta un cliente rápidamente desde la misma interfaz de agendamiento.
*   `GET /api/clientes/<id>/odontograma/`: **(Para Odontograma)** Devuelve el estado dental actual de un paciente para renderizar el odontograma.
*   `POST /api/clientes/<id_cliente>/diente/<num_diente>/actualizar/`: **(Para Odontograma)** Modifica el diagnóstico de un diente específico.
*   `GET /api/diagnosticos/`: **(Para Odontograma)** Devuelve la lista de posibles diagnósticos para poblar el selector en la interfaz.
