# Quick Reference - Dental SaaS

## ⚡ Comandos Rápidos

```bash
# Activar entorno
source venv/bin/activate

# Migrar schemas (SIEMPRE usar esto, no migrate)
python manage.py migrate_schemas --schema=demo

# Generar datos de prueba
python generar_datos_completos.py

# Reiniciar servidor de producción
sudo systemctl restart dental-saas.service

# Ver logs en tiempo real
sudo journalctl -u dental-saas.service -f

# Estado del servidor
sudo systemctl status dental-saas.service
```

## 🔥 Patrones Críticos

### ❌ NO HACER
```python
# OBSOLETO - servicios_realizados ya NO es campo DB
Cita.objects.prefetch_related('servicios_realizados')
cita.servicios_realizados.all()  # Error en templates
```

### ✅ HACER
```python
# Correcto - prefetch desde tratamientos
Cita.objects.prefetch_related('tratamientos_realizados__servicios')

# En templates (sin .all())
{% for servicio in cita.servicios_realizados %}
```

## 📁 Archivos Clave

| Archivo | Líneas Importantes | Qué hace |
|---------|-------------------|----------|
| `core/models.py` | 470-555 | Modelo Cita con @property servicios_realizados |
| `core/views.py` | 3595-3768 | CitaManageView - gestión de citas |
| `core/templates/core/cita_manage.html` | 1-715 | UI de gestión con odontograma |
| `CLAUDE.md` | 302-411 | Documentación actualizada |
| `SESION_2025_10_23.md` | Todo | Resumen de última sesión |

## 🎯 URLs Importantes

- **Gestión de citas**: http://142.93.87.37/demo/citas/
- **Gestión individual**: http://142.93.87.37/demo/citas/1/gestionar/
- **Pacientes**: http://142.93.87.37/demo/pacientes/
- **Agenda**: http://142.93.87.37/demo/agenda/

## 🗄️ Estructura de Datos

```
Cita
  └─ servicios_realizados (@property) ← Lee desde TratamientoCita

TratamientoCita (FUENTE DE VERDAD)
  ├─ servicios (M2M) ← AQUÍ se guardan servicios
  ├─ dientes_tratados = "16,17,18"
  └─ diagnostico_final

HistorialEstadoDiente (Por cada diente)
  ├─ diagnostico_anterior
  └─ diagnostico_nuevo

EstadoDiente (Estado ACTUAL)
  └─ diagnostico ← El más reciente
```

## 🐛 Debugging Común

### Error: "relation core_cita_servicios_realizados does not exist"
**Causa**: Código usando prefetch_related incorrecto
**Fix**: Cambiar a `prefetch_related('tratamientos_realizados__servicios')`

### Error: Servicios no aparecen en cita
**Causa**: No hay TratamientoCita registrados
**Fix**: Registrar tratamiento desde UI o:
```python
from core.models import TratamientoCita, procesar_tratamiento_cita
# Ver SESION_2025_10_23.md para ejemplo completo
```

### Saldo no actualiza
**Fix**:
```python
paciente.actualizar_saldo_global()
paciente.refresh_from_db()
```

## 📊 Datos de Prueba

Pacientes creados por `generar_datos_completos.py`:

1. **Carlos** - Historial extenso (3 citas completadas)
2. **María** - Endodoncia activa (cita mañana)
3. **Juan** - Caso complejo (cita EN ATENCIÓN) ← Perfecto para demo
4. **Ana** - Paciente nuevo (primera cita programada)
5. **Luis** - Con deuda ($4200 pendiente)

## 🔐 Acceso a Tenants

```python
# En manage.py shell
from django.db import connection
from tenants.models import Clinica

tenant = Clinica.objects.get(schema_name='demo')
connection.set_tenant(tenant)

# Ahora puedes hacer queries del tenant
from core.models import Cita, Paciente
citas = Cita.objects.all()
```

## 🎨 UI Components

### Selector de servicios (multi-select)
```html
<select name="servicios" multiple size="5" required>
  {% for servicio in servicios_disponibles %}
    <option value="{{ servicio.id }}">{{ servicio.nombre }} - ${{ servicio.precio }}</option>
  {% endfor %}
</select>
```

### Botón copiar dientes
```javascript
document.getElementById('btn-copiar-seleccion').addEventListener('click', function(){
  const nums = Array.from(window.odontogramaSelected).sort((a,b)=>a-b).join(',');
  document.getElementById('dientes_tratados').value = nums;
});
```

## 📝 Git Workflow

```bash
# Hacer cambios
git add -A
git commit -m "Descripción clara del cambio"
git push origin main

# Servidor auto-actualiza en algunos minutos
# O forzar reinicio:
sudo systemctl restart dental-saas.service
```

---
**Última actualización**: 23 Octubre 2025
**Lee también**: CLAUDE.md, SESION_2025_10_23.md
