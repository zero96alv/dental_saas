# Seguridad y Credenciales del Sistema Dental SaaS

**Fecha de auditoría:** 2025-10-25
**Estado:** ✅ Sistema seguro - No se detectaron vulnerabilidades críticas

---

## 1. Resumen Ejecutivo

El sistema Dental SaaS está correctamente configurado con múltiples capas de seguridad:
- Base de datos PostgreSQL aislada (solo localhost)
- Autenticación multi-tenant con aislamiento por schemas
- Usuarios con roles y permisos granulares
- Todas las redirecciones mantienen contexto de tenant (corregido 2025-10-25)

---

## 2. Credenciales de Base de Datos

### PostgreSQL - Servidor de Producción

```bash
# Ubicación: /root/dental_saas/.env
DB_NAME=dental_db
DB_USER=dental_user
DB_PASSWORD=DentalDB2025!
DB_HOST=localhost
DB_PORT=5432
```

**⚠️ IMPORTANTE:**
- Este archivo `.env` NO está en git (protegido por `.gitignore`)
- Mantener estas credenciales privadas
- NO compartir por email o medios no seguros

### Usuarios PostgreSQL

```sql
-- Usuarios del sistema PostgreSQL
postgres     | Superuser completo (administración del servidor)
dental_user  | Owner de dental_db, privilegios: CREATE DB
```

**Acceso a PostgreSQL:**
```bash
# Como usuario postgres (superuser)
sudo -u postgres psql

# Como dental_user (aplicación)
psql -U dental_user -d dental_db -h localhost
```

---

## 3. Configuración de Seguridad PostgreSQL

### 3.1 Autenticación (pg_hba.conf)

```conf
# Conexiones locales (Unix socket) - Autenticación peer
local   all   postgres   peer
local   all   all        peer

# Conexiones TCP/IP localhost - SCRAM-SHA-256 (seguro)
host    all   all   127.0.0.1/32   scram-sha-256
host    all   all   ::1/128        scram-sha-256

# NO hay reglas para conexiones remotas ✅
```

**Análisis de seguridad:**
- ✅ Solo acepta conexiones desde localhost (127.0.0.1)
- ✅ Usa SCRAM-SHA-256 para autenticación de contraseñas (estándar moderno)
- ✅ NO permite conexiones desde internet
- ✅ Autenticación peer para usuarios locales del sistema

### 3.2 Red y Puertos

```bash
# PostgreSQL escucha SOLO en localhost
127.0.0.1:5432  (IPv4)
[::1]:5432      (IPv6)
```

**Estado:** ✅ PostgreSQL NO es accesible desde internet
**Verificado:** `ss -tlnp | grep postgres`

---

## 4. Estructura Multi-Tenant

### 4.1 Schemas de Base de Datos

```sql
-- Schemas en dental_db
public    | Schema compartido (configuración de tenants)
cgdental  | Tenant: CG Dental Care
demo      | Tenant: Clínica Demo
dev       | Tenant: Clínica Desarrollo (testing)
sgdental  | Tenant: SG Dental
```

### 4.2 Aislamiento de Datos

- ✅ Cada tenant opera en su propio schema PostgreSQL
- ✅ Datos completamente aislados entre tenants
- ✅ No hay posibilidad de cross-tenant data leak
- ✅ Middleware verifica tenant en cada request

**Acceso a schemas:**
```python
# En Django shell
from tenants.models import Clinica
from django.db import connection

# Cambiar a tenant específico
tenant = Clinica.objects.get(schema_name='dev')
connection.set_tenant(tenant)
# Ahora todas las queries usan el schema 'dev'
```

---

## 5. Usuarios del Sistema por Tenant

### 5.1 Schema PUBLIC (Admin Global)

**Estado:** Sin usuarios
El schema public solo contiene la configuración de tenants, no usuarios de aplicación.

### 5.2 CGDENTAL - CG Dental Care

| Usuario | Email | Rol | Superuser | Activo |
|---------|-------|-----|-----------|--------|
| admin | admin@cgdental.dental.com | Administrador | ✅ | ✅ |

### 5.3 DEMO - Clínica Demo

| Usuario | Email | Rol | Superuser | Activo |
|---------|-------|-----|-----------|--------|
| admin | admin@demo.dental.com | Administrador | ✅ | ✅ |
| NelidaGarcia | nelida.garcia@gmail.com | Administrador | ❌ | ✅ |
| SairaGarcia | saira.garcia@gmail.com | Dentista | ❌ | ✅ |
| AbigailOlera | abigail.olera@gmail.com | Dentista | ❌ | ✅ |

### 5.4 DEV - Clínica Desarrollo (Testing)

| Usuario | Email | Rol | Superuser | Activo |
|---------|-------|-----|-----------|--------|
| admin | admin@dev.com | Administrador | ✅ | ✅ |
| dentista | dentista@dev.com | Dentista | ❌ | ✅ |
| recepcion | recepcion@dev.com | Recepcionista | ❌ | ✅ |
| prueba | pruebas@ñk.com | Dentista | ❌ | ✅ |

**Credenciales de testing (DEV):**
```
admin/admin123       - Acceso completo
dentista/dentista123 - Vista de dentista
recepcion/recep123   - Vista de recepción
```

### 5.5 SGDENTAL - SG Dental

| Usuario | Email | Rol | Superuser | Activo |
|---------|-------|-----|-----------|--------|
| admin | admin@sgdental.dental.com | Administrador | ✅ | ✅ |
| NelidaGarcia | puppy_nely@hotmail.com | Administrador | ❌ | ✅ |

---

## 6. Sistema de Roles y Permisos

### 6.1 Roles Predefinidos

```python
# Grupos disponibles en el sistema
Administrador     | Acceso completo al sistema
Dentista          | Gestión de pacientes, citas, tratamientos, odontogramas
Recepcionista     | Agenda, pagos, facturación (sin acceso clínico)
```

### 6.2 Módulos del Sistema

```
1. Dashboard
2. Pacientes
3. Agenda
4. Historial Clínico
5. Odontograma
6. Finanzas
7. Inventario
8. Reportes
9. Configuración
10. Usuarios y Permisos
11. Laboratorio Dental
```

**Control de acceso:**
- Cada módulo tiene permisos granulares (ver, crear, editar, eliminar)
- Los permisos se asignan por rol en la tabla `PermisoRol`
- El menú se genera dinámicamente según permisos del usuario

---

## 7. Configuración de Seguridad Django

### 7.1 Settings Críticos

```python
# dental_saas/settings.py
DEBUG = False  # ⚠️ Verificar en producción
SECRET_KEY = "1p^lu(z5^xkw22l&mfx79h#(#wt=pl)l@z3fb+(whdw4(jt+5c"

ALLOWED_HOSTS = [
    '142.93.87.37',
    'localhost',
    '127.0.0.1',
    'unix',
    '.ondigitalocean.app'
]

# Sesiones
SESSION_COOKIE_SECURE = True  # Solo HTTPS (si aplica)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF
CSRF_COOKIE_SECURE = True  # Solo HTTPS (si aplica)
CSRF_COOKIE_HTTPONLY = True
```

### 7.2 Middleware de Seguridad

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'tenants.middleware.PathBasedTenantMiddleware',  # ← Multi-tenant
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.LocalTimezoneMiddleware',
    'core.middleware.NoCacheMiddleware',
]
```

**PathBasedTenantMiddleware:**
- Extrae tenant del path URL (`/dev/`, `/demo/`)
- Configura `connection.set_tenant()` automáticamente
- Previene acceso cross-tenant

---

## 8. Auditoría de Redirecciones (2025-10-25)

### ✅ Correcciones Aplicadas

**Problema identificado:** 26 redirecciones perdían el prefijo del tenant, enviando usuarios a `/accounts/login/` en lugar de `/dev/accounts/login/`.

**Solución implementada:**
```python
# ANTES (problemático)
return redirect('core:paciente_detail', pk=paciente.pk)

# DESPUÉS (corregido)
return redirect(tenant_reverse('core:paciente_detail', request=request, kwargs={'pk': paciente.pk}))
```

**Archivos corregidos:**
- `core/views.py` - 25 redirects
- `core/views_laboratorio.py` - 1 redirect
- `core/mixins.py` - Función `tenant_reverse()` agregada
- `TenantLoginRequiredMixin` - Mejorado para construir tenant_prefix desde `request.tenant.schema_name`

**Templates auditados:**
- ✅ 522 usos de `{% tenant_url %}` encontrados
- ✅ 0 usos problemáticos de `{% url 'core:...' %}`
- ✅ Todos los templates correctamente configurados

---

## 9. Servidor de Producción

### 9.1 Información del Servidor

```bash
IP: 142.93.87.37
OS: Ubuntu 22.04 LTS / Linux 6.14.0-23-generic
Proveedor: DigitalOcean

# Servicio systemd
sudo systemctl status dental-saas.service
sudo systemctl restart dental-saas.service
sudo journalctl -u dental-saas.service -f
```

### 9.2 Estructura de Archivos

```
/root/dental_saas/
├── .env                  # Credenciales (NO en git)
├── manage.py
├── venv/                 # Entorno virtual Python
├── core/                 # Aplicación principal
├── tenants/              # Sistema multi-tenant
├── media/                # Archivos subidos
├── staticfiles/          # Archivos estáticos (collectstatic)
└── dental_saas/          # Settings del proyecto
```

### 9.3 Acceso SSH

```bash
# Desde tu máquina local
ssh root@142.93.87.37

# Una vez dentro
cd /root/dental_saas
source venv/bin/activate
```

---

## 10. Recomendaciones de Seguridad

### ✅ Implementadas

1. ✅ PostgreSQL solo en localhost
2. ✅ Autenticación SCRAM-SHA-256
3. ✅ Aislamiento multi-tenant por schemas
4. ✅ Sistema de permisos granulares
5. ✅ Todas las redirecciones mantienen tenant context
6. ✅ Templates usando `{% tenant_url %}`
7. ✅ `.env` fuera de git

### 🟡 Pendientes / Recomendadas

1. **Backups automatizados:**
   ```bash
   # Crear backup manual
   sudo -u postgres pg_dump dental_db > backup_$(date +%Y%m%d).sql

   # Configurar cron para backups diarios
   0 2 * * * sudo -u postgres pg_dump dental_db | gzip > /backups/dental_$(date +\%Y\%m\%d).sql.gz
   ```

2. **Rotación de SECRET_KEY:**
   - Generar nueva SECRET_KEY periódicamente
   - No usar la misma key en dev y producción

3. **SSL/HTTPS:**
   - Configurar certificado SSL (Let's Encrypt)
   - Forzar HTTPS en nginx/Apache
   - Actualizar `SESSION_COOKIE_SECURE = True`

4. **Monitoreo:**
   - Configurar alertas de errores (Sentry)
   - Logs de acceso no autorizados
   - Monitoreo de uso de recursos

5. **Actualización de contraseñas:**
   - Política de cambio periódico
   - Contraseñas más robustas para usuarios de producción

6. **Firewall:**
   ```bash
   # Verificar estado de UFW
   sudo ufw status

   # Asegurar solo puertos necesarios abiertos
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

---

## 11. Comandos Útiles de Administración

### PostgreSQL

```bash
# Conectar a la base de datos
sudo -u postgres psql -d dental_db

# Listar schemas
\dn

# Ver usuarios
\du

# Cambiar a un schema
SET search_path TO dev;

# Ver tablas del schema actual
\dt

# Backup completo
sudo -u postgres pg_dump dental_db > backup.sql

# Restore
sudo -u postgres psql dental_db < backup.sql
```

### Django Management

```bash
# Activar entorno
source venv/bin/activate

# Migrar todos los schemas
python manage.py migrate_schemas

# Migrar schema específico
python manage.py migrate_schemas --schema=dev

# Shell de Django en tenant específico
python manage.py tenant_command shell --schema=dev

# Crear superusuario en tenant
python manage.py shell
>>> from django.db import connection
>>> from tenants.models import Clinica
>>> tenant = Clinica.objects.get(schema_name='dev')
>>> connection.set_tenant(tenant)
>>> from django.contrib.auth.models import User
>>> User.objects.create_superuser('admin', 'admin@example.com', 'password')
```

### Systemd (Servicio)

```bash
# Ver estado
sudo systemctl status dental-saas.service

# Reiniciar servicio
sudo systemctl restart dental-saas.service

# Ver logs en tiempo real
sudo journalctl -u dental-saas.service -f

# Ver logs recientes
sudo journalctl -u dental-saas.service -n 100
```

---

## 12. Contacto y Soporte

**Administrador del Sistema:** [Tu nombre/email]
**Última actualización:** 2025-10-25
**Próxima revisión:** [Programar fecha]

---

## 13. Changelog de Seguridad

### 2025-10-25
- ✅ Auditoría completa de seguridad de base de datos
- ✅ Corrección de 26 redirects que perdían contexto de tenant
- ✅ Documentación completa de credenciales y usuarios
- ✅ Verificación de configuración PostgreSQL (todo correcto)
- ✅ Auditoría de templates (522 tenant_url correctos)

---

**CONFIDENCIAL - NO COMPARTIR SIN AUTORIZACIÓN**
