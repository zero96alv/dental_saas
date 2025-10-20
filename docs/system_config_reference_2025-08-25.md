# Referencia Rápida del Sistema - 25 Agosto 2025

## 🏗️ Arquitectura Multi-Tenant

### Esquemas de Base de Datos
```
public          - Tablas compartidas (auth, tenants, permisos)
dev             - Tenant desarrollo (tablas de aplicación)  
demo            - Tenant demo
standard        - Tenant producción
```

### Acceso a Tenant Específico
```python
from django_tenants.utils import tenant_context
from tenants.models import Clinica

tenant_dev = Clinica.objects.get(schema_name='dev')
with tenant_context(tenant_dev):
    # Consultas específicas del tenant
    datos = models.DatosFiscales.objects.all()
```

## 📊 Estado de Base de Datos

### Tablas Críticas en Schema `dev`
```
core_paciente               (51 registros)   - Pacientes
core_cita                   (158 registros)  - Citas médicas  
core_pago                   (114 registros)  - Pagos
core_datosfiscales          (14 registros)   - ✅ CORREGIDA - Datos fiscales
core_satformapago           (4 registros)    - Códigos SAT forma de pago
core_satmetodopago          (2 registros)    - Códigos SAT método de pago
core_satregimenfiscal       (3 registros)    - Regímenes fiscales SAT
core_satusocfdi             (3 registros)    - Usos CFDI SAT
```

### Migración Crítica Aplicada
- **Campo corregido**: `core_datosfiscales.uso_cfdi` → `uso_cfdi_id` (ForeignKey)
- **Registros migrados**: 2/14 registros tenían datos SAT
- **Integridad**: ✅ Mantenida con tablas SAT

## 🔧 Servicios Implementados

### SatMappingService (`core/services.py`)
```python
# Mapeo automático activo
SatMappingService.mapear_forma_pago('Tarjeta de crédito')  # → SAT 04
SatMappingService.mapear_metodo_pago()                     # → PUE
SatMappingService.aplicar_mapeo_automatico(pago_instance)  # → Auto-mapeo
```

### Métodos de Pago en Formularios
```python
# PagoForm y AbonoForm - Opciones específicas
choices = [
    ('Efectivo', 'Efectivo'),                    # → SAT 01
    ('Tarjeta de crédito', 'Tarjeta de crédito'), # → SAT 04  
    ('Tarjeta de débito', 'Tarjeta de débito'),   # → SAT 28
    ('Transferencia', 'Transferencia'),           # → SAT 03
]
```

## 🚀 URLs y Endpoints

### Procesamiento de Pagos
```
http://dev.localhost:8000/citas/141/procesar-pago/   # ✅ FUNCIONAL
```

### Administración SAT
```
/admin/core/satformapago/     # Formas de pago SAT
/admin/core/satmetodopago/    # Métodos de pago SAT  
/admin/core/datosfiscales/    # Datos fiscales pacientes
```

## 🧪 Scripts de Utilidad

### Diagnóstico
```bash
python list_dev_tables.py              # Listar tablas en tenant dev
python check_datosfiscales_dev.py      # Verificar estructura fiscal  
python test_datosfiscales_access.py    # Probar acceso a modelo
```

### Pruebas SAT
```bash  
python test_mapeo_formularios.py       # Validar mapeo automático
python demo_mapeo_sat.py               # Demo completo de mapeo
```

### Migración (YA APLICADA)
```bash
python fix_uso_cfdi_field.py          # ✅ APLICADO - Corregir campo uso_cfdi
```

## 🔐 Códigos SAT Activos

### Formas de Pago
```
01 - Efectivo
03 - Transferencia electrónica de fondos  
04 - Tarjeta de crédito
28 - Tarjeta de débito
```

### Métodos de Pago  
```
PUE - Pago en una sola exhibición
PPD - Pago en parcialidades o diferido  
```

### Regímenes Fiscales
```
612 - Personas Físicas con Actividades Empresariales y Profesionales
601 - General de Ley Personas Morales  
605 - Sueldos y Salarios e Ingresos Asimilados a Salarios
```

### Usos CFDI
```
G01 - Adquisición de mercancías
G03 - Gastos en general
D01 - Honorarios médicos, dentales y gastos hospitalarios
```

## ⚠️ Notas Importantes

### Multi-Tenant
- Siempre usar `tenant_context()` para consultas de aplicación
- Las tablas de aplicación NO están en schema `public`
- Verificar schema correcto al diagnosticar problemas

### Datos Fiscales
- Mantener `DatosFiscales` como tabla separada (decisión arquitectónica confirmada)
- Relación 1:1 opcional con `Paciente`
- Solo crear registros cuando se requiere facturación

### Mapeo SAT
- Formularios ya implementan opciones específicas (no genéricas)
- Fallback automático para casos edge funciona correctamente
- Aplicación automática activa en formularios con `desea_factura=True`

---

**Última actualización**: 25 Agosto 2025  
**Estado del sistema**: ✅ Totalmente funcional  
**Próxima revisión**: Según necesidades de desarrollo
