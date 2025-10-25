# Solución al Problema de Permisos Vacíos en Tenants

## 🔍 Problema

Cuando un usuario administrador ingresa a un nuevo tenant, solo ve la pantalla de login y no tiene acceso a ningún módulo. Esto ocurre porque el sistema de permisos dinámicos requiere configuración inicial.

## ✅ Soluciones Implementadas

### 1. **Menú de Emergencia para Superusuarios** (Automático)

**Archivo modificado:** `core/permissions_utils.py` líneas 151-181

**Qué hace:** Si un superusuario (`is_superuser=True`) ingresa a un tenant sin módulos configurados, se muestra automáticamente un menú de emergencia con:
- Enlace al Admin Django
- Acceso básico a Pacientes y Citas
- Indicación visual de que se requiere configuración

**Ventaja:** Solución inmediata sin necesidad de ejecutar comandos.

---

### 2. **Script de Inicialización Rápida** (Manual)

**Archivo creado:** `init_permisos_tenant.py`

**Uso:**
```bash
# Activar entorno virtual
source venv/bin/activate

# Inicializar permisos para cualquier tenant
python init_permisos_tenant.py <schema_name>

# Ejemplos:
python init_permisos_tenant.py dev
python init_permisos_tenant.py demo
python init_permisos_tenant.py sgdental
```

**Qué hace:**
- Cambia al tenant especificado
- Ejecuta el comando `init_permisos`
- Crea 9 módulos del sistema
- Crea 24 submenús
- Asigna 57 permisos por defecto a los roles:
  - Administrador (acceso completo)
  - Dentista (clínico + pacientes)
  - Recepcionista (administrativo)

**Cuándo usarlo:**
- Después de crear un nuevo tenant
- Cuando un tenant existente no muestra menú
- Para restablecer configuración de permisos

---

### 3. **Auto-inicialización en Script de Creación de Tenants**

**Archivo modificado:** `create_dev_tenant.py` líneas 445-449

**Qué hace:** El script de creación de tenants ahora **automáticamente** inicializa el sistema de permisos al final del proceso.

**Archivos afectados:**
- `create_dev_tenant.py` ✅ Actualizado
- `create_sgdental_tenant.py` (pendiente de actualizar si es necesario)

---

## 🚀 Comandos Útiles

### Verificar Estado de Permisos
```bash
source venv/bin/activate
python manage.py shell -c "
from tenants.models import Clinica
from django.db import connection
from core.models_permissions import ModuloSistema, SubmenuItem

tenant = Clinica.objects.get(schema_name='dev')
connection.set_tenant(tenant)

print(f'Módulos: {ModuloSistema.objects.count()}')
print(f'Submenús: {SubmenuItem.objects.count()}')
"
```

### Inicializar Permisos Manualmente
```bash
# Opción 1: Script rápido (recomendado)
python init_permisos_tenant.py dev

# Opción 2: Management command directo
python manage.py shell -c "
from django.core.management import call_command
from tenants.models import Clinica
from django.db import connection

tenant = Clinica.objects.get(schema_name='dev')
connection.set_tenant(tenant)
call_command('init_permisos')
"
```

### Listar Tenants Disponibles
```bash
python manage.py shell -c "
from tenants.models import Clinica
for c in Clinica.objects.exclude(schema_name='public'):
    print(f'{c.schema_name} - {c.nombre}')
"
```

### Reiniciar Servicio (Después de Cambios)
```bash
sudo systemctl restart dental-saas.service
sudo systemctl status dental-saas.service
```

---

## 📋 Checklist al Crear Nuevo Tenant

1. ✅ Crear tenant con script o comando
2. ✅ Aplicar migraciones (`migrate_schemas`)
3. ✅ Crear usuarios básicos
4. ✅ **Inicializar permisos** (`init_permisos_tenant.py`)
5. ✅ Reiniciar servicio si está en producción
6. ✅ Verificar acceso con usuario admin

---

## 🔐 Usuarios y Credenciales por Tenant

### Tenant: **dev**
- URL: http://142.93.87.37/dev/
- Admin: `admin` / `admin123`
- Dentista: `dentista` / `dentista123`
- Recepción: `recepcion` / `recepcion123`

### Tenant: **demo**
- URL: http://142.93.87.37/demo/
- (Usar credenciales según configuración)

### Tenant: **sgdental**
- URL: http://142.93.87.37/sgdental/
- (Usar credenciales según configuración)

---

## 🛠️ Resolución de Problemas

### Problema: "Usuario ingresa pero no ve menú"
**Solución:**
```bash
python init_permisos_tenant.py <schema_name>
sudo systemctl restart dental-saas.service
```

### Problema: "ModuloSistema.DoesNotExist"
**Causa:** No se han inicializado los permisos
**Solución:** Ejecutar `init_permisos_tenant.py`

### Problema: "Menu vacío incluso después de inicializar"
**Causa:** Usuario no tiene grupo asignado
**Solución:**
1. Ir al Admin Django: `/dev/admin/`
2. Auth > Users > Seleccionar usuario
3. En "Groups", agregar al grupo "Administrador"
4. Guardar

### Problema: "Cambios no se reflejan en el navegador"
**Solución:**
1. Reiniciar servicio: `sudo systemctl restart dental-saas.service`
2. Limpiar caché del navegador (Ctrl+Shift+R)
3. Cerrar sesión y volver a ingresar

---

## 📝 Notas Importantes

1. **Superusuarios siempre tienen acceso:** El sistema verifica `is_superuser=True` antes de validar permisos detallados.

2. **Tres niveles de seguridad:**
   - Superusuario (bypass total)
   - Grupo + PermisoRol (control granular)
   - Fallback (menú de emergencia)

3. **Los permisos son por tenant:** Cada tenant debe tener su propio sistema de permisos inicializado.

4. **El script es idempotente:** Puedes ejecutar `init_permisos_tenant.py` múltiples veces sin problemas.

---

## 🔄 Actualizaciones Futuras

Si agregas nuevos módulos o funcionalidades al sistema:

1. Actualizar `inicializar_permisos_por_defecto()` en `permissions_utils.py`
2. Ejecutar `python init_permisos_tenant.py <schema>` en cada tenant
3. O usar `init_permisos_all.py` para actualizar todos los tenants

---

## 📞 Soporte

Si el problema persiste:
1. Verificar logs del servicio: `sudo journalctl -u dental-saas.service -f`
2. Verificar que el tenant existe: `python init_permisos_tenant.py` (sin argumentos)
3. Revisar que las migraciones estén aplicadas: `python manage.py migrate_schemas`

---

**Última actualización:** 2025-10-24
**Versión del sistema:** 1.0
