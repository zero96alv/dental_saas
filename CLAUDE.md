# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Dental SaaS** is a comprehensive multi-tenant dental clinic management system built with Django 5.2 and PostgreSQL. Each clinic (tenant) operates in an isolated database schema, ensuring complete data privacy and security. The system manages patients, appointments, clinical history, dental charts (odontograms), inventory, billing with Mexican SAT compliance, and role-based access control.

## Architecture

### Multi-Tenant Design
- **Framework**: django-tenants (schema-based multi-tenancy)
- **Tenant Model**: `tenants.Clinica`
- **URL Routing**: Path-based routing (`/demo/`, `/sgdental/`) instead of subdomain-based
- **Middleware**: `tenants.middleware.PathBasedTenantMiddleware` handles tenant resolution from URL paths
- **Schemas**:
  - `public` schema: Shared data (tenants, domains, global admin)
  - Per-tenant schemas: Isolated data for each clinic (patients, appointments, etc.)

### Key Applications
- **core**: Main application with all business logic, models, views, and templates
- **tenants**: Multi-tenant infrastructure (Clinica and Domain models)

### Database Configuration
- **Development**: Uses `dev` schema by default when accessing via IP
- **Production**: Path-based routing to appropriate tenant schemas
- **Connection**: PostgreSQL with psycopg3
- **Migrations**: Use `migrate_schemas` instead of standard `migrate`

## Development Commands

### Running the Server
```bash
# Standard development server
python manage.py runserver

# Without auto-reload (useful for debugging)
python manage.py runserver --noreload
```

### Database Operations
```bash
# Apply migrations to all schemas (public + all tenants)
python manage.py migrate_schemas

# Apply migrations to public schema only
python manage.py migrate_schemas --schema=public

# Apply migrations to specific tenant
python manage.py migrate_schemas --schema=demo

# Create cache table
python manage.py createcachetable
```

### Tenant Management
```bash
# Create superuser for global admin (public schema)
python manage.py create_superuser_global

# Create users in specific tenant
python manage.py shell
# Then in shell:
from django.db import connection
from tenants.models import Clinica
tenant = Clinica.objects.get(schema_name='demo')
connection.set_tenant(tenant)
# Now create users for this tenant
```

### Utility Scripts
```bash
# Initialize production tenants with demo data
python init_production.py

# Create demo tenant with sample data
python create_sgdental_tenant.py

# Setup SAT catalogs (Mexican tax system)
python setup_sat_tables.py

# Populate demo clinic with test data
python create_demo_users.py
python crear_datos_completos_prueba.py
```

### Testing and Validation
```bash
# Run validation scripts (located in project root)
python validation_patients_module.py
python validation_clinical_system.py
python validation_financial_system.py
python validation_appointments_system.py
```

### Management Commands
```bash
# Send appointment reminders
python manage.py send_reminders

# Send birthday wishes
python manage.py send_birthdays

# Send payment reminders
python manage.py send_payment_reminders

# Initialize permissions system for a tenant
python manage.py init_permisos

# Load COFEPRIS questionnaire (Mexican health compliance)
python manage.py cargar_cuestionario_cofepris
```

## Code Architecture

### URL Structure
- **Public URLs** (`dental_saas/urls_public.py`): Admin panel, setup pages
- **Tenant URLs** (`dental_saas/urls_tenant.py`): Core application URLs
- **Core URLs** (`core/urls.py`): All application endpoints (260+ lines)

URL patterns follow tenant-prefixed routing:
- `/demo/` → demo clinic
- `/demo/pacientes/` → patients list for demo clinic
- `/demo/agenda/` → appointment calendar for demo clinic

### Views Pattern
All views in `core/views.py` (3000+ lines) follow these patterns:
- **Class-Based Views**: Inheriting from Django's generic views (ListView, DetailView, CreateView, UpdateView, DeleteView)
- **Mixins**:
  - `TenantLoginRequiredMixin`: Ensures user authentication and tenant access
  - `TenantSuccessUrlMixin`: Handles success redirects with tenant prefix
  - `SuccessMessageMixin`: Displays success messages after operations
- **API Views**: Function-based views returning JSON for AJAX operations (prefixed with `_api`)

### Models Organization (`core/models.py`)
Models are organized into logical groups:
1. **Base Classes**: `PersonaBase` (abstract base for people)
2. **People**: `Paciente`, `PerfilDentista`
3. **SAT System**: `SatFormaPago`, `SatMetodoPago`, `SatRegimenFiscal`, `SatUsoCFDI`, `DatosFiscales`
4. **Clinical**: `Especialidad`, `Servicio`, `Cita`, `Diagnostico`, `HistorialClinico`, `TratamientoCita`
5. **Dental Chart**: `EstadoDental` (odontogram states)
6. **Financial**: `Pago`, `Factura`
7. **Inventory**: `Proveedor`, `Insumo`, `Compra`
8. **Scheduling**: `HorarioLaboral`, `UnidadDental`
9. **Compliance**: COFEPRIS-related models for questionnaires

### Forms (`core/forms.py`)
- Custom ModelForms with validation logic
- Bootstrap 5 styling via `crispy-bootstrap5`
- Key forms: `PacienteForm`, `CitaForm`, `ServicioForm`, `UsuarioForm`
- Forms include custom `clean_*` methods for business logic validation

### Permissions System
Custom role-based permissions managed through:
- `core/models_permissions.py`: Models for `ModuloSistema`, `SubmenuItem`, `PermisoRol`
- `core/permissions_utils.py`: Utility functions for permission checks
- `core/views_permissions.py`: Views for permission management
- Three predefined roles: Administrador, Dentista, Recepcionista
- Dynamic menu generation based on user permissions

### Context Processors
- `core/context_processors.menu_dinamico`: Injects role-based menu into all templates

### Middleware
- `tenants.middleware.PathBasedTenantMiddleware`: Resolves tenant from URL path
- `core.middleware.LocalTimezoneMiddleware`: Forces local timezone
- `core.middleware.NoCacheMiddleware`: Prevents response caching

## Key Features Implementation

### Odontogram (Dental Chart) ⭐ **DECISIÓN CONSOLIDADA**

**Variante Oficial:** `odontograma_movil_optimizado.html`

**Ubicación:** `core/templates/core/partials/odontograma_movil_optimizado.html`

**Razón de elección** (Octubre 2025):
Después de evaluar 28 variantes diferentes, se seleccionó `odontograma_movil_optimizado.html` como estándar oficial por:
- ✅ **Funcionalidad completa:** 32 dientes, multi-selección, paleta de diagnósticos
- ✅ **Responsive:** Optimizado para desktop y móvil
- ✅ **Performance:** Carga rápida y fluida
- ✅ **Integración:** Compatible con API existente (`odontograma_api_get`, `odontograma_api_update`)
- ✅ **Ya en uso:** Implementado en `cita_manage.html`
- ✅ **Mobile-responsive:** Touch support para tablets y smartphones

**Variantes archivadas:** Las otras 27 variantes fueron movidas a:
`core/templates/core/partials/archive_odontogramas/`

**Uso en el sistema:**
- Vista de gestión de citas (`cita_manage.html`) → Tab "Tratamientos"
- Vista de historial del paciente (`historial_paciente.html`)
- Vista de odontograma completo (`odontograma_48.html`)

**API Endpoints:**
- `GET /api/odontograma/<paciente_id>/` - Obtener estados dentales
- `POST /api/odontograma/<paciente_id>/update/` - Actualizar estados
- `GET /api/odontograma/partial/` - Cargar el odontograma estándar

### Appointment System
- Calendar view powered by FullCalendar.js
- States: Programada (PGM), Confirmada (CNF), En Progreso (PRG), Atendida (ATN), Completada (COM), Cancelada (CAN)
- Services can be planned vs. actually performed
- Financial integration: tracks balances per appointment
- API: `agenda_events`, `cita_detail_api`

### Patient Management
- Complete CRUD operations
- Structured address fields (SAT-compliant for invoicing)
- Global balance tracking across all appointments
- Fiscal data management (RFC, tax regime, CFDI usage)
- AJAX patient creation modal from appointment booking

### Financial System
- Payment tracking per patient with global balance
- SAT-compliant invoicing with Mexican tax catalogs
- Payment plans (when authorized by dentist)
- Reports: Income, Pending Balances, Billing
- Export to Excel and PDF

### Inventory Management
**Arquitectura dual**: Inventario Físico (cantidades) + Gestión de Costos (financiero)

#### Módulo de Inventario Físico
- Proveedores con datos fiscales mexicanos
- Insumos con alertas de stock mínimo
- Control por lotes (número de lote, caducidad, COFEPRIS)
- Distribución por unidades dentales
- **Flujo**: Crear Compra (sin precios) → Recibir (distribuir) → Stock actualizado

#### Módulo de Gestión de Costos (Separado)
- **Vista**: `/costos/compras-sin-costos/` - Lista compras recibidas sin costos capturados
- **Vista**: `/costos/compras/<pk>/capturar/` - Formulario para capturar precios de factura
- **Vista**: `/costos/valor-inventario/` - Reporte de valor monetario del stock
- **Campos clave**:
  - `Compra.costos_capturados` (Boolean) - Track si ya se capturaron costos
  - `LoteInsumo.costo_unitario` (Decimal) - Costo de entrada del lote
  - `LoteInsumo.detalle_compra` (FK) - Trazabilidad a la compra original

**Flujo operativo completo**:
1. Personal de almacén recibe mercancía → Registra compra con cantidades (sin precios)
2. Personal distribuye en unidades dentales → Stock actualizado inmediatamente
3. Días después llega factura → Administración captura costos en `/costos/`
4. Sistema actualiza: `Compra.total`, `LoteInsumo.costo_unitario` de lotes generados
5. Reportes financieros muestran valor real del inventario

## Important Patterns and Conventions

### Tenant Context Switching
When working with management commands or scripts that need to operate on specific tenants:
```python
from django.db import connection
from tenants.models import Clinica

# Switch to specific tenant
tenant = Clinica.objects.get(schema_name='demo')
connection.set_tenant(tenant)

# All subsequent DB operations use this tenant's schema
```

### Success URL with Tenant Prefix
Views use `TenantSuccessUrlMixin` to automatically prepend tenant prefix:
```python
def get_success_url(self):
    return reverse('core:paciente_list')  # Automatically becomes /demo/pacientes/
```

### API Response Pattern
API views return JSON with consistent structure:
```python
return JsonResponse({
    'success': True,
    'message': 'Operation completed',
    'data': {...}
})
```

### Template Structure
- Base template: `templates/core/base.html`
- Includes: `templates/core/includes/navbar.html`, `sidebar.html`
- Uses Bootstrap 5.3 with custom CSS in `core/static/core/css/`
- JavaScript in `core/static/core/js/`

## Settings Files
- `dental_saas/settings.py`: Development settings
- `dental_saas/settings_production.py`: Production settings (inherits from base)
- Key settings:
  - `TENANT_MODEL`, `TENANT_DOMAIN_MODEL`: Multi-tenant configuration
  - `SHARED_APPS`, `TENANT_APPS`: App separation for multi-tenancy
  - `PUBLIC_SCHEMA_URLCONF` vs `ROOT_URLCONF`: Different URL configs per schema type

## Static Files and Media
```bash
# Collect static files (required for production)
python manage.py collectstatic --no-input

# With production settings
python manage.py collectstatic --no-input --settings=dental_saas.settings_production
```
- Static files served by WhiteNoise in production
- Media uploads go to `media/` directory (per-tenant isolation maintained at app level)

## Testing Approach
- Test files exist but are minimal: `core/tests.py`, `tenants/tests.py`
- Validation scripts in root directory test end-to-end workflows
- Manual testing through demo tenant recommended for feature validation

## Deployment
- **Build script**: `build.sh` (installs deps, collects static, runs migrations, initializes tenants)
- **Process file**: `Procfile` for Render/Heroku deployment
- **WSGI**: `dental_saas/wsgi.py`
- **Web server**: Gunicorn (configured in Procfile)
- Detailed deployment instructions in `DEPLOY_README.md` and `DIGITALOCEAN_DEPLOY.md`

## Common Gotchas

1. **Always use `migrate_schemas`** instead of `migrate` to properly handle multi-tenant migrations
2. **Tenant context matters**: When running scripts, ensure you're in the correct schema context
3. **URL routing**: Remember to include tenant prefix in URLs (handled automatically by middleware and mixins)
4. **Login URLs**: Each tenant has its own login at `/demo/accounts/login/` (not `/accounts/login/`)
5. **Admin panel**: Global admin at `/admin/` uses public schema, tenant-specific admin at `/demo/admin/` uses tenant schema
6. **Session isolation**: Sessions are tenant-specific based on URL path
7. **Static files**: After modifying static files, may need to run `collectstatic` and hard-refresh browser

## File Locations

### Configuration
- Settings: `dental_saas/settings.py`
- URLs: `dental_saas/urls_public.py`, `dental_saas/urls_tenant.py`, `core/urls.py`
- Environment: `.env` (not in git, copy from `.env.example`)

### Main Application Logic
- Models: `core/models.py` (58,000+ lines)
- Views: `core/views.py` (3,000+ lines)
- Forms: `core/forms.py` (700+ lines)
- Templates: `core/templates/core/`
- Static: `core/static/core/`

### Scripts and Utilities
- Root directory: Setup and validation scripts
- Management commands: `core/management/commands/`

## Recent Changes (from git log)

### October 2025 - Refactorización arquitectural servicios_realizados
**CRÍTICO**: Campo `Cita.servicios_realizados` eliminado y convertido a `@property`

#### Motivación
Eliminamos redundancia de datos: antes servicios estaban en dos lugares:
- `Cita.servicios_realizados` (M2M) ← ELIMINADO
- `TratamientoCita.servicios` (M2M) ← Ahora es fuente única de verdad

#### Cambios en modelos (core/models.py)
```python
# ANTES (OBSOLETO)
class Cita(models.Model):
    servicios_realizados = models.ManyToManyField('Servicio', ...)  # ❌ Eliminado

# DESPUÉS (ACTUAL)
class Cita(models.Model):
    @property
    def servicios_realizados(self):
        """Calcula desde TratamientoCita.servicios"""
        servicio_ids = set()
        for tratamiento in self.tratamientos_realizados.all():
            servicio_ids.update(tratamiento.servicios.values_list('id', flat=True))
        return Servicio.objects.filter(id__in=servicio_ids)
```

#### Migración aplicada
- `core/migrations/0033_eliminar_servicios_realizados.py`
- Aplicada a schema demo: ✅

#### Cambios críticos en código
1. **Vistas**: Cambiar `prefetch_related('servicios_realizados')` → `prefetch_related('tratamientos_realizados__servicios')`
2. **Templates**: Remover `.all()` → `{% for s in cita.servicios_realizados %}` (sin .all())
3. **Saldo calculation**: Usar `cita.costo_real` property en lugar de aggregate

#### Scripts de datos
- `generar_datos_completos.py`: Genera 5 escenarios completos de pacientes con historiales
- Ejecutar: `python generar_datos_completos.py` (ya poblado en demo)

### Integración Odontograma + Servicios (Octubre 2025)
Página de gestión de citas (`/citas/X/gestionar/`) ahora permite flujo completo:

#### Funcionalidad agregada
1. **Selector multi-servicio**: Campo `<select multiple>` con servicios planeados pre-seleccionados
2. **Botón "Copiar dientes seleccionados"**: Copia números de dientes desde odontograma a campo de texto
3. **Vinculación automática**: Al registrar tratamiento, servicios se vinculan a `TratamientoCita.servicios`
4. **Visualización**: Lista de tratamientos muestra badges verdes con servicios + precios

#### Template modificado (cita_manage.html)
```html
<!-- Nuevo campo de servicios -->
<select class="form-select" id="servicios" name="servicios" multiple size="5" required>
  {% for servicio in cita.servicios_planeados.all %}
    <option value="{{ servicio.id }}" selected>{{ servicio.nombre }} - ${{ servicio.precio }}</option>
  {% endfor %}
</select>

<!-- Botón de integración -->
<button type="button" id="btn-copiar-seleccion">
  <i class="bi bi-clipboard-check"></i> Copiar dientes seleccionados
</button>

<!-- JavaScript -->
<script>
  window.odontogramaSelected = selected;  // Variable global para comunicación
  document.getElementById('btn-copiar-seleccion').addEventListener('click', ...);
</script>
```

#### Vista actualizada (core/views.py)
```python
class CitaManageView:
    def get_context_data(self, **kwargs):
        context['servicios_disponibles'] = models.Servicio.objects.filter(activo=True)

    def _handle_tratamiento(self, request, cita):
        servicios_ids = [int(sid) for sid in request.POST.getlist('servicios')]
        # Validar al menos un servicio
        # Pasar a procesar_tratamiento_cita(servicios_ids=servicios_ids)
```

#### Flujo de usuario
1. Abrir `/demo/citas/1/gestionar/` → Pestaña "Tratamientos"
2. Click en dientes del odontograma (multi-selección)
3. Click "Copiar dientes seleccionados" → campo se llena
4. Seleccionar servicios del multi-select (Ctrl+Click)
5. Completar descripción, estado inicial/final, diagnóstico
6. Registrar tratamiento → odontograma actualiza + servicios vinculados

### Servidor de producción
- **Servicio**: `dental-saas.service` (systemd)
- **Reiniciar**: `sudo systemctl restart dental-saas.service`
- **Ver logs**: `sudo journalctl -u dental-saas.service -f`
- **URL**: http://142.93.87.37/demo/

### Comandos útiles después de cambios
```bash
# Activar entorno
source venv/bin/activate

# Migrar schemas
python manage.py migrate_schemas --schema=demo

# Reiniciar servidor
sudo systemctl restart dental-saas.service

# Ver estado
sudo systemctl status dental-saas.service
```

### October 2025 - Corrección Crítica de Tenant Context Loss
**CRÍTICO**: Se corrigieron 26 redirects que perdían el prefijo del tenant, enviando a usuarios no autenticados al login sin contexto.

#### Problema Identificado
Múltiples vistas usaban `redirect('core:view_name')` que genera URLs sin el prefijo del tenant:
```python
# ANTES (PROBLEMÁTICO)
return redirect('core:paciente_detail', pk=paciente.pk)
# Resultado: /pacientes/1/ (sin /dev/)
# Django redirige a: /accounts/login/?next=/pacientes/1/
```

#### Solución Implementada: `tenant_reverse()`
Nueva función helper en `core/mixins.py` que siempre incluye el prefijo del tenant:

```python
from core.mixins import tenant_reverse

# DESPUÉS (CORRECTO)
return redirect(tenant_reverse('core:paciente_detail', request=request, kwargs={'pk': paciente.pk}))
# Resultado: /dev/pacientes/1/
# Django redirige a: /dev/accounts/login/?next=/dev/pacientes/1/
```

**Uso de `tenant_reverse()`:**
```python
# Sin parámetros
url = tenant_reverse('core:dashboard', request=request)
# → /dev/

# Con kwargs
url = tenant_reverse('core:paciente_detail', request=request, kwargs={'pk': 1})
# → /dev/pacientes/1/

# Con args
url = tenant_reverse('core:cita_detail', request=request, args=[5])
# → /dev/citas/5/

# En success_url de vistas
def get_success_url(self):
    return tenant_reverse('core:paciente_list', request=self.request)
```

#### Archivos Modificados (2025-10-25)
1. **core/mixins.py**
   - Agregada función `tenant_reverse(viewname, request=None, tenant=None, ...)`
   - Mejorado `TenantLoginRequiredMixin.get_login_url()` para construir tenant_prefix desde `request.tenant.schema_name`
   - Mejorado `@tenant_login_required` decorator con misma lógica

2. **core/views.py**
   - 25 redirects corregidos en views como:
     - `UsuarioDeleteView`, `DatosFiscalesView`, `OdontogramaView`
     - Múltiples redirects a `paciente_detail`
     - `ProcesarPagoView.get_success_url()`
     - `RegistrarPagoPacienteView` y más

3. **core/views_laboratorio.py**
   - 1 redirect corregido en `TrabajoLaboratorioDeleteView.delete()`

4. **Templates** (Auditoría completada)
   - ✅ 522 usos de `{% tenant_url %}` encontrados
   - ✅ 0 usos problemáticos de `{% url 'core:...' %}`
   - Todos los templates correctamente configurados

#### Regla de Oro para Redirects
**NUNCA usar:**
```python
redirect('core:view_name')  # ❌ Pierde tenant
redirect('core:view_name', pk=1)  # ❌ Pierde tenant
```

**SIEMPRE usar:**
```python
redirect(tenant_reverse('core:view_name', request=request))  # ✅
redirect(tenant_reverse('core:view_name', request=request, kwargs={'pk': 1}))  # ✅
```

**Excepciones:**
- Views con `TenantSuccessUrlMixin` que usan `reverse_lazy()` en `success_url` class attribute → El mixin se encarga
- Templates → Usar `{% tenant_url 'core:view_name' %}` (ya implementado en todo el sistema)

---

## Security and Credentials

**📄 Documentación completa:** Ver `SEGURIDAD_Y_CREDENCIALES.md` para:
- Auditoría de seguridad de base de datos PostgreSQL
- Credenciales del sistema (DB, usuarios por tenant)
- Configuración de autenticación y permisos
- Recomendaciones de seguridad
- Comandos de administración

**Resumen de seguridad:**
- ✅ PostgreSQL solo escucha en localhost (127.0.0.1:5432)
- ✅ Autenticación SCRAM-SHA-256 (segura)
- ✅ Aislamiento completo por schemas (cgdental, demo, dev, sgdental)
- ✅ Sistema de permisos granulares por rol
- ✅ Todos los redirects mantienen tenant context
- ✅ Templates usando `{% tenant_url %}`

**Acceso rápido a credentials:**
```bash
# Ver .env (credenciales DB)
cat /root/dental_saas/.env

# Listar usuarios de un tenant
python manage.py shell
>>> from django.db import connection
>>> from tenants.models import Clinica
>>> tenant = Clinica.objects.get(schema_name='dev')
>>> connection.set_tenant(tenant)
>>> from django.contrib.auth.models import User
>>> User.objects.values_list('username', 'email', 'is_superuser')
```

---

## Best Practices for Multi-Tenant Development

### 1. Always Maintain Tenant Context
```python
# En vistas basadas en clase
class MiVista(TenantLoginRequiredMixin, ListView):
    # TenantLoginRequiredMixin ya maneja tenant context en login
    pass

# En redirects
return redirect(tenant_reverse('core:mi_vista', request=request))

# En templates
<a href="{% tenant_url 'core:mi_vista' %}">Link</a>
```

### 2. Testing con Múltiples Tenants
```python
# En Django shell
from django.db import connection
from tenants.models import Clinica

# Cambiar tenant para testing
for schema in ['demo', 'dev', 'sgdental']:
    tenant = Clinica.objects.get(schema_name=schema)
    connection.set_tenant(tenant)
    # Ejecutar queries o operaciones
    print(f"Tenant {schema}: {User.objects.count()} usuarios")
```

### 3. Migraciones Multi-Tenant
```bash
# Siempre usar migrate_schemas
python manage.py migrate_schemas

# Para tenant específico
python manage.py migrate_schemas --schema=dev

# Para schema público solamente
python manage.py migrate_schemas --schema=public
```

### 4. Debugging Tenant Issues
```python
# En cualquier vista o código, inspeccionar tenant actual
print(f"Tenant actual: {request.tenant.schema_name}")
print(f"Tenant prefix: {getattr(request, 'tenant_prefix', 'NO DEFINIDO')}")

# Verificar si usuario está en tenant correcto
from django.db import connection
print(f"Schema actual en DB: {connection.schema_name}")
```

---

## Troubleshooting Common Issues

### Issue: Usuario redirigido a /accounts/login/ sin tenant
**Causa:** Redirect sin `tenant_reverse()`
**Solución:** Usar `tenant_reverse()` como se documenta arriba

### Issue: Templates generan URLs sin prefijo de tenant
**Causa:** Uso de `{% url %}` en lugar de `{% tenant_url %}`
**Solución:**
```django
{# ANTES #}
<a href="{% url 'core:paciente_list' %}">Pacientes</a>

{# DESPUÉS #}
{% load tenant_urls %}
<a href="{% tenant_url 'core:paciente_list' %}">Pacientes</a>
```

### Issue: Migraciones no se aplican a todos los tenants
**Causa:** Uso de `manage.py migrate` en lugar de `migrate_schemas`
**Solución:** Siempre usar `python manage.py migrate_schemas`

### Issue: Datos aparecen mezclados entre tenants
**Causa:** No establecer tenant context en scripts o comandos
**Solución:**
```python
from django.db import connection
from tenants.models import Clinica

tenant = Clinica.objects.get(schema_name='demo')
connection.set_tenant(tenant)
# Ahora todas las queries usan schema 'demo'
```

---

## Changelog Principal

### 2025-11-19 (Sesión 2)
- ✅ **[FEATURE]** Rediseño completo del módulo de Insumos
  - **Formulario profesional** (`insumo_form.html`):
    - Header con gradiente púrpura-azul y diseño moderno
    - Listas desplegables para `unidad_medida` (15 opciones) y `unidad_empaque` (9 opciones)
    - 4 secciones organizadas: Información Básica, Unidades y Empaque, Stock y Precios, Control Sanitario
    - JavaScript para ocultar/mostrar campos condicionales
    - Ejemplos visuales en alertas informativas
    - Card de ayuda con consejos útiles
  - **Lista optimizada** (`insumo_list.html`):
    - Cambio de tabla con modales anidados a vista de tarjetas (cards)
    - Solución al problema de HTML inválido (modals dentro de `<tbody>`)
    - Cards con distribución de stock por unidades dentales
    - Vista responsive: 3 columnas (desktop), 2 (tablet), 1 (móvil)
    - Efectos hover y sombras profesionales
  - **Form class** (`core/forms.py:1593-1714`):
    - Creado `InsumoForm` con choices para unidades
    - Validación mejorada de campos
  - **Vistas actualizadas** (`core/views.py:3915-3927`):
    - `InsumoCreateView` y `InsumoUpdateView` ahora usan `form_class`

- ✅ **[FEATURE]** Rediseño completo del módulo de Proveedores
  - **Formulario profesional** (`proveedor_form.html`):
    - Header con gradiente y diseño moderno
    - Validación en tiempo real de RFC (Persona Moral/Física)
    - Preview de formato de teléfono: (55) 1234-5678
    - Auto-mayúsculas en campo RFC
    - Secciones organizadas: Información de la Empresa + Información de Contacto
    - Card de consejos útiles
  - **Lista escalable con tabla** (`proveedor_list.html`):
    - **Problema resuelto**: Cards no escalables para 20+ proveedores
    - **Solución**: Tabla compacta con modales de detalles
    - Búsqueda en tiempo real (filtra sin recargar página)
    - Click en fila → abre modal con información completa
    - Modal con header degradado y secciones organizadas
    - Links funcionales: `tel:` y `mailto:`
    - Responsive: tabla se adapta a móvil
    - **Performance**: 7.5x más eficiente que vista de cards (800px vs 6000px de scroll)
  - **Form class** (`core/forms.py:1717-1786`):
    - Creado `ProveedorForm` con validación de RFC
    - Clean method para RFC (12 o 13 caracteres)
    - Validación de formato de teléfono
  - **Vistas actualizadas** (`core/views.py:3795-3807`):
    - `ProveedorCreateView` y `ProveedorUpdateView` ahora usan `form_class`
    - Mensajes de éxito personalizados

- ✅ **[DOCUMENTATION]** Actualización de CLAUDE.md con todos los cambios de la sesión

### 2025-11-19 (Sesión 1)
- ✅ **[FIX]** Corregido error JavaScript en módulo de compras (`compra_form.html`)
  - Error: `Cannot read properties of null (reading 'value')` al agregar insumos
  - Solución: Búsqueda robusta del campo `TOTAL_FORMS` usando `querySelector('[name$="-TOTAL_FORMS"]')`
  - Archivo modificado: `core/templates/core/compra_form.html:73-106`

- ✅ **[FEATURE]** Mejora visual del módulo de compras
  - Cambio de tabla simple a vista de tarjetas (cards) con Bootstrap 5
  - Muestra lista de insumos por compra con badges
  - Mejor visualización de estados (Pendiente, Recibida, Cancelada)
  - Vista responsive para móvil y desktop
  - Optimización de queries: agregado `prefetch_related('detalles__insumo')` en `CompraListView`
  - Archivos modificados:
    - `core/templates/core/compra_list.html:20-127`
    - `core/views.py:1161` (CompraListView.get_queryset)

- ✅ **[FEATURE]** Sistema dinámico de servicios en gestión de citas
  - **Problema resuelto**: Antes solo se podían usar servicios planeados inicialmente
  - **Solución**: Modal para agregar servicios adicionales durante la atención de la cita
  - **Funcionalidad**:
    - Botón "Agregar Servicio" en pestaña "Resumen" de gestionar cita
    - Modal con selector múltiple de servicios disponibles
    - Cálculo en tiempo real del costo adicional y nuevo total
    - Actualización automática de `cita.costo_real` y `cita.saldo_pendiente`
    - Los servicios se agregan a `servicios_planeados` y quedan disponibles para tratamientos
  - **Archivos modificados**:
    - `core/templates/core/cita_manage.html:65-106` (UI mejorada de servicios)
    - `core/templates/core/cita_manage.html:608-655` (Modal de agregar servicios)
    - `core/templates/core/cita_manage.html:856-954` (JavaScript para agregar servicios)
    - `core/views.py:4662-4672` (CitaManageView.post - nuevo action)
    - `core/views.py:4714-4767` (Nuevo método `_handle_agregar_servicios`)
  - **Flujo de usuario**:
    1. Dentista atiende cita con servicio de "Valoración"
    2. Durante la cita, detecta necesidad de "Limpieza" o "Extracción"
    3. Click en "Agregar Servicio" → Selecciona servicios → Confirma
    4. Sistema actualiza costo total y saldo a deber del paciente
    5. Servicios quedan disponibles para registrar en tratamientos

- ✅ **[DOCUMENTATION]** Documentación de historial clínico en gestión de citas
  - El sistema ya tiene implementación completa y funcional:
    - Formulario rápido en pestaña "Historial" de gestionar cita
    - Muestra últimas 5 entradas del historial del paciente
    - Botones de acceso rápido a historial completo y cuestionario
    - Tipos de registro: CONSULTA, DIAGNOSTICO, TRATAMIENTO, SEGUIMIENTO, OBSERVACION, EMERGENCIA
  - No requiere modificaciones adicionales

- ✅ **[FIX]** Corrección crítica de vista de insumos (`insumo_list.html`)
  - **Problema identificado**: HTML inválido con modales dentro de `<tbody>` causaba:
    - Segundo insumo renderizado fuera de la tabla
    - Elementos no interactuables
    - Estructura visual inconsistente
  - **Causa raíz**: Modales de lotes generados dentro del loop `{% for insumo %}` pero dentro de `<tbody>`
  - **Solución implementada**:
    - Template completamente rediseñado (1,256 líneas → 359 líneas)
    - Cambio de tabla expandible a **vista de cards** (similar a compras)
    - Eliminación de modales anidados problemáticos
    - HTML válido y semántico
  - **Mejoras funcionales**:
    - ✅ Vista de tarjetas responsive con Bootstrap 5
    - ✅ **Distribución por unidad dental visible directamente** (antes requería modal)
    - ✅ Stock con barra de progreso visual
    - ✅ Badges de estado con colores (crítico=rojo, bajo=amarillo, normal=verde)
    - ✅ Información de lotes con fechas de caducidad resaltadas
    - ✅ Estadísticas dashboard mantenidas (6 métricas)
    - ✅ Filtros funcionales (búsqueda, proveedor, estado de stock)
    - ✅ Eliminación de 900+ líneas de JavaScript innecesario
  - **Archivos modificados**:
    - `core/templates/core/insumo_list.html` (reescrito completamente)
    - Respaldo creado: `core/templates/core/insumo_list_backup_YYYYMMDD_HHMMSS.html`
  - **Acceso**: http://142.93.87.37/dev/insumos/

- ✅ **[FEATURE]** Nueva interfaz de administración de servicios en gestión de citas
  - **Mejora solicitada**: Interfaz más intuitiva para gestionar servicios de la cita
  - **Antes**: Select múltiple confuso con Ctrl+Click
  - **Ahora**: Interfaz dual-list profesional estilo administración
  - **Características implementadas**:
    - ✅ **Modal de tamaño XL** con dos columnas (disponibles vs seleccionados)
    - ✅ **Búsqueda en tiempo real** por nombre de servicio
    - ✅ **Transferencia de servicios** con botones de flechas
    - ✅ **Doble click** para mover servicios rápidamente
    - ✅ **Botones "Agregar/Quitar Todos"** para selección masiva
    - ✅ **Contadores dinámicos** de servicios disponibles y seleccionados
    - ✅ **Cálculo de costos en tiempo real**:
      - Costo actual de la cita
      - Diferencia (+/- en verde/rojo)
      - Nuevo total
    - ✅ **Reemplazo completo** de servicios (no solo agregar)
    - ✅ **Vista clara de precios** en cada servicio
  - **Cambios en UI**:
    - Botón renombrado: "Agregar Servicio" → "Administrar Servicios"
    - Icono cambiado: plus-circle → gear-fill (engranaje)
    - Header del modal en azul primario
  - **Cambios en backend** (`core/views.py:4714-4771`):
    - `_handle_agregar_servicios()` ahora usa `.clear()` y `.set()`
    - Permite quitar servicios (antes solo agregaba)
    - Mensaje actualizado: "X servicio(s) asignado(s) a la cita"
  - **Archivos modificados**:
    - `core/templates/core/cita_manage.html:70-72` (botón)
    - `core/templates/core/cita_manage.html:608-761` (modal dual-list)
    - `core/templates/core/cita_manage.html:962-1204` (JavaScript completo)
    - `core/views.py:4714-4771` (vista actualizada)
  - **Acceso**: http://142.93.87.37/dev/citas/5/gestionar/ → Botón "Administrar Servicios"

- ✅ **[FIX]** Botones de estado de cita ahora responsive
  - **Problema**: Botones se encimaban en pantallas pequeñas
  - **Solución**: Cambio de `btn-group` a `d-grid gap-2 d-md-flex flex-md-wrap`
  - **Mejoras**:
    - En móvil: Botones en columna (100% ancho)
    - En desktop: Botones en fila con wrap
    - Agregados iconos a cada botón para mejor identificación
  - **Archivo modificado**: `core/templates/core/cita_manage.html:45-61`

- ✅ **[FEATURE]** Sistema Dual de Historial Clínico implementado
  - **Problema**: Confusión entre múltiples URLs de historial (3 versiones diferentes)
  - **Solución**: Sistema organizado en dos flujos claros:

  **1. VISUALIZACIÓN** (Azul - Solo Lectura):
  - `Ver Cronología + Odontograma` → `/pacientes/<pk>/history/`
    - Muestra timeline de eventos del `HistorialClinico`
    - Incluye odontograma interactivo
    - Para consulta rápida de historial existente

  - `Odontograma Detallado` → `/pacientes/<pk>/odontograma_48/`
    - Vista completa de 48 dientes
    - Para análisis dental específico

  **2. CAPTURA** (Verde - Formularios):
  - `Antecedentes Completos` → `/pacientes/<pk>/historial-mejorado/`
    - **Escalas de dolor** (numérica 0-10 + Wong Baker con emojis)
    - **Antecedentes familiares** organizados
    - **Hábitos orales** (bruxismo, tabaco, etc.)
    - Formulario estructurado con formsets

  - `Cuestionario Estructurado` → `/cuestionarios/paciente/<pk>/completar/`
    - Cuestionario por categorías
    - Para captura sistemática de datos

  **3. NOTAS RÁPIDAS** (En gestión de cita):
  - Formulario rápido en pestaña "Historial"
  - Para notas durante la atención
  - Vinculado automáticamente a la cita

  **Archivos modificados**:
  - `core/templates/core/cita_manage.html:122-135` (botones + explicación)
  - `core/templates/core/cita_manage.html:167-178` (formulario rápido mejorado)
  - `core/templates/core/paciente_detail.html:58-129` (card de sistema dual)

  **Beneficios**:
  - ✅ Separación clara entre visualizar y capturar
  - ✅ Botones abren en nueva pestaña (target="_blank")
  - ✅ Alertas informativas explicando cada sección
  - ✅ UI organizada con colores distintivos (azul/verde)
  - ✅ Deprecación implícita de la ruta `/cuestionario/` simple

  **Accesos**:
  - Gestión de cita: http://142.93.87.37/dev/citas/5/gestionar/ → Pestaña "Historial"
  - Detalle paciente: http://142.93.87.37/dev/pacientes/1/ → Card "Sistema de Historial Clínico"

- ✅ **[FEATURE]** Formulario mejorado de Insumos con choices y UI profesional
  - **Problema**: Unidad de medida y empaque eran campos de texto libre, causando inconsistencias
  - **Solución**: Formulario personalizado con listas desplegables predefinidas

  **Mejoras implementadas**:

  **1. Choices para Unidad de Medida** (15 opciones):
  - Pieza, Caja, Paquete
  - Líquidos: Litro, Mililitro
  - Peso: Kilogramo, Gramo
  - Longitud: Metro, Centímetro
  - Otros: Rollo, Frasco, Tubo, Ampolleta, Sobre, Unidad

  **2. Choices para Unidad de Empaque** (9 opciones + vacío):
  - Sin empaque (venta individual)
  - Caja, Paquete, Bulto, Display, Pack, Estuche, Bolsa, Contenedor

  **3. UI Mejorada con secciones**:
  - **Header con gradiente** morado/azul
  - **4 Secciones organizadas**:
    - Información Básica
    - Unidades y Empaque (con ejemplo visual)
    - Stock y Precios
    - Control Sanitario (COFEPRIS)
  - **Alertas informativas** con ejemplos prácticos
  - **Link rápido** para crear proveedor
  - **Card de ayuda** al final con próximos pasos

  **4. JavaScript inteligente**:
  - Oculta "Cantidad por Empaque" si no hay empaque seleccionado
  - Oculta "Registro Sanitario" si no se marca checkbox COFEPRIS
  - Valores por defecto: cantidad_por_empaque=1

  **5. Validaciones mejoradas**:
  - Campos numéricos con min/max
  - Placeholders descriptivos
  - Help texts claros en cada campo

  **Archivos modificados**:
  - `core/forms.py:1593-1714` (nuevo InsumoForm con 130 líneas)
  - `core/views.py:3915-3927` (InsumoCreateView + InsumoUpdateView usan form_class)
  - `core/templates/core/insumo_form.html` (reescrito completamente con 233 líneas)

  **Beneficios**:
  - ✅ Datos consistentes (no más "pza", "pieza", "pzas")
  - ✅ UI profesional con gradientes y secciones
  - ✅ Ejemplos visuales para evitar confusiones
  - ✅ Campos condicionales (solo muestra lo necesario)
  - ✅ Experiencia guiada para el usuario

  **Acceso**: http://142.93.87.37/dev/insumos/new/

- ✅ **[FEATURE]** Lista y formulario de Proveedores completamente rediseñados
  - **Problema**: Lista de proveedores era tabla simple sin información visual
  - **Solución**: Vista de cards + formulario profesional similar a insumos

  **Mejoras en Lista de Proveedores**:

  **1. Vista de Cards** (reemplazo de tabla):
  - Cards con efecto hover (elevan al pasar mouse)
  - Icono de edificio grande por card
  - Badge de RFC o "Sin RFC" con colores
  - **Información visible**:
    - Nombre/Razón Social (título)
    - RFC con badge
    - Nombre de contacto con icono de persona
    - Teléfono clickeable (tel:)
    - Email clickeable (mailto:)
    - Dirección fiscal truncada
  - Botones Editar/Eliminar agrupados
  - Grid responsive: 1 columna (móvil), 2 (tablet), 3 (desktop)

  **2. Estadística**: Contador de total de proveedores

  **Mejoras en Formulario de Proveedor**:

  **1. UI Profesional** (igual que insumos):
  - Header con gradiente morado/azul
  - 2 Secciones organizadas:
    - Información de la Empresa
    - Información de Contacto (con fondo gris)

  **2. Validaciones en Tiempo Real**:
  - **RFC**: Detecta si es Persona Moral (12 chars) o Física (13 chars)
    - ✅ "RFC Persona Moral válido" (verde)
    - ✅ "RFC Persona Física válido" (verde)
    - ❌ "RFC debe tener 12 o 13 caracteres" (rojo)
    - Auto-mayúsculas al escribir
  - **Teléfono**: Preview con formato
    - Entrada: `5512345678`
    - Preview: `(55) 1234-5678` ✅
    - Contador: `10/10 dígitos`

  **3. Validación de Backend**:
  - RFC: Validación de longitud 12/13, conversión a mayúsculas
  - Teléfono: Limpieza de caracteres no numéricos
  - Nombre obligatorio con alerta si está vacío

  **4. Card de Ayuda** con consejos:
  - Cuándo capturar RFC
  - Importancia del contacto
  - Para qué sirve la dirección fiscal
  - Qué hacer después de registrar

  **Archivos modificados**:
  - `core/templates/core/proveedor_list.html` (reescrito, 154 líneas)
  - `core/templates/core/proveedor_form.html` (reescrito, 197 líneas)
  - `core/forms.py:1717-1786` (nuevo ProveedorForm con 70 líneas)
  - `core/views.py:3795-3807` (vistas usan form_class + success_message)

  **Beneficios**:
  - ✅ RFC siempre en mayúsculas y validado
  - ✅ Teléfonos limpios (solo números)
  - ✅ Vista más visual y profesional
  - ✅ Feedback inmediato al usuario
  - ✅ Validación antes de submit
  - ✅ Experiencia consistente con módulo de insumos

  **Accesos**:
  - Lista: http://142.93.87.37/dev/proveedores/
  - Nuevo: http://142.93.87.37/dev/proveedores/new/

### 2025-10-28
- ✅ **[FEATURE]** Separación de Inventario Físico y Gestión de Costos
- ✅ Precios opcionales en Insumo, DetalleCompra y Compra
- ✅ Nuevo campo `Compra.costos_capturados` para tracking
- ✅ Nuevo campo `LoteInsumo.costo_unitario` para rastrear costo por lote
- ✅ Nuevo campo `LoteInsumo.detalle_compra` para trazabilidad
- ✅ Nuevo módulo `core/views_costos.py` con:
  - `ComprasSinCostosView`: Lista compras recibidas sin costos capturados
  - `CapturarCostosCompraView`: Formulario para capturar costos cuando llega la factura
  - `ReporteValorInventarioView`: Reporte de valor monetario del inventario actual
- ✅ Nuevos templates: `compras_sin_costos.html`, `capturar_costos_compra.html`, `reporte_valor_inventario.html`
- ✅ Nuevas rutas en `/costos/` para el módulo de gestión financiera
- ✅ Migración `0038_separar_inventario_y_costos.py` aplicada al schema dev

### 2025-10-25
- ✅ **[CRÍTICO]** Corregidos 26 redirects que perdían tenant context
- ✅ Agregada función `tenant_reverse()` en `core/mixins.py`
- ✅ Mejorados `TenantLoginRequiredMixin` y `@tenant_login_required`
- ✅ Auditoría completa de templates (522 tenant_url correctos)
- ✅ Documentación de seguridad y credenciales (`SEGURIDAD_Y_CREDENCIALES.md`)
- ✅ Dashboard financiero: corregidos cálculos y imports
- ✅ Corregidas gráficas excesivamente grandes en reportes
- ✅ Mejorado template de registro de pagos con info de citas pendientes
- ✅ Agregado módulo de Laboratorio Dental

### 2025-10 (anterior)
- Refactorización de `Cita.servicios_realizados` a `@property`
- Integración odontograma + servicios en gestión de citas
- Sistema de permisos granulares por módulo y rol

---
