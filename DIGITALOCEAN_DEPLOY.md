# 🚀 DESPLIEGUE EN DIGITALOCEAN APP PLATFORM

## Guía completa para desplegar Dental SaaS Multi-Tenant

---

## 📋 PRE-REQUISITOS

1. **Cuenta de DigitalOcean** con App Platform habilitado
2. **Repositorio en GitHub** con el código
3. **CLI de DigitalOcean** (opcional pero recomendado)

```bash
# Instalar CLI (opcional)
snap install doctl
# o
brew install doctl
```

---

## 🚀 PROCESO DE DESPLIEGUE

### Paso 1: Preparar el Repositorio

Asegúrate de que tu repositorio tenga estos archivos:
- `.do/app.yaml` ✅
- `requirements.txt` ✅
- `.env.example` ✅
- `scripts/digitalocean_setup.py` ✅

### Paso 2: Crear App en DigitalOcean

#### Opción A: Desde la Consola Web
1. Ve a [DigitalOcean Apps](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Selecciona **GitHub** como fuente
4. Autoriza DigitalOcean a acceder a tu repo
5. Selecciona el repositorio `dental_saas`
6. Selecciona branch `main`
7. DigitalOcean detectará automáticamente el archivo `.do/app.yaml`

#### Opción B: Desde CLI
```bash
# Autenticar
doctl auth init

# Crear app
doctl apps create --spec .do/app.yaml
```

### Paso 3: Configurar Variables de Entorno

En el dashboard de DigitalOcean, ve a tu app → **Settings** → **Environment Variables**:

**Variables requeridas:**
```
DJANGO_SECRET_KEY = [GENERAR UNA NUEVA CLAVE SECRETA]
DEBUG = False
ALLOWED_HOSTS = .ondigitalocean.app,localhost,127.0.0.1
```

**⚠️ IMPORTANTE:** Marca `DJANGO_SECRET_KEY` como **ENCRYPTED**

### Paso 4: Generar Secret Key

```python
# En tu terminal local
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Paso 5: Deploy

Una vez configuradas las variables:
1. Guarda los cambios
2. DigitalOcean iniciará el deploy automáticamente
3. Monitor the build logs

---

## ⚙️ POST-DEPLOY SETUP

### 1. Ejecutar Setup Inicial

Una vez desplegado, accede a:
```
https://tu-app-name.ondigitalocean.app/simple-setup/?key=DentalSaaS2025Setup!
```

### 2. Verificar Funcionamiento

**URLs de prueba:**
- Landing: `https://tu-app.ondigitalocean.app/`
- Demo: `https://tu-app.ondigitalocean.app/?tenant=demo`
- SG Dental: `https://tu-app.ondigitalocean.app/?tenant=sgdental`
- CG Dental: `https://tu-app.ondigitalocean.app/?tenant=cgdental`

**Credenciales:**
- Usuario: `admin`
- Contraseña: `DemoAdmin2025!`

---

## 🌐 CONFIGURAR DOMINIO PERSONALIZADO (OPCIONAL)

### 1. Comprar Dominio
Ejemplo: `dental-saas.com`

### 2. Configurar DNS
En tu proveedor de DNS:
```
A Record: @ → [IP de DigitalOcean]
CNAME: * → tu-app.ondigitalocean.app
CNAME: www → tu-app.ondigitalocean.app
```

### 3. Agregar Dominio en DigitalOcean
1. Ve a tu app → **Settings** → **Domains**
2. Add Domain: `dental-saas.com`
3. Add Domain: `*.dental-saas.com` (wildcard)

### 4. Actualizar ALLOWED_HOSTS
```
ALLOWED_HOSTS = .dental-saas.com,.ondigitalocean.app,localhost
```

---

## 🔧 CONFIGURACIÓN DE BASE DE DATOS

DigitalOcean configurará automáticamente:
- **PostgreSQL 15** managed database
- Variable `DATABASE_URL` auto-configurada
- Backups automáticos
- SSL habilitado

---

## 📊 MONITOREO Y LOGS

### Ver Logs en Tiempo Real
```bash
# Con CLI
doctl apps logs tu-app-id --follow

# O desde la consola web
Apps → tu-app → Runtime Logs
```

### Métricas
- CPU, Memory, Request Rate disponibles en el dashboard
- Alertas configurables

---

## 💰 COSTOS ESTIMADOS

| Recurso | Tamaño | Costo/Mes |
|---------|--------|-----------|
| **Web App** | Basic XXS | $5.00 |
| **Database** | Basic | $15.00 |
| **Worker** (opcional) | Basic XXS | $5.00 |
| **Total** | | **~$20-25/mes** |

---

## 🛠️ COMANDOS ÚTILES

### Restart App
```bash
doctl apps create-deployment tu-app-id --force-rebuild
```

### Scale App
```bash
# Cambiar instance size
doctl apps update tu-app-id --spec .do/app.yaml
```

### Database Access
```bash
# Obtener string de conexión
doctl databases connection tu-db-id
```

---

## 🐛 TROUBLESHOOTING

### Error: Build Failed
- Revisa `requirements.txt`
- Verifica que `DJANGO_SECRET_KEY` esté configurada
- Mira los build logs

### Error: Database Connection
- Verifica que `DATABASE_URL` esté configurada automáticamente
- Revisa que PostgreSQL esté running

### Error: Static Files
- Ejecuta `python manage.py collectstatic` en build command
- Verifica configuración de WhiteNoise

### Error: Tenant Not Found
- Ejecuta el setup inicial: `/simple-setup/?key=DentalSaaS2025Setup!`
- Verifica que las clínicas estén creadas en la DB

---

## 📞 SOPORTE

- **DigitalOcean**: [Documentación oficial](https://docs.digitalocean.com/products/app-platform/)
- **Django-tenants**: [GitHub repo](https://github.com/django-tenants/django-tenants)
- **Este proyecto**: Revisa los logs y código fuente

---

## ✅ CHECKLIST DE DESPLIEGUE

- [ ] Repositorio subido a GitHub
- [ ] Archivo `.do/app.yaml` configurado
- [ ] Variables de entorno configuradas en DigitalOcean
- [ ] `DJANGO_SECRET_KEY` generada y marcada como encrypted
- [ ] App desplegada exitosamente
- [ ] Setup inicial ejecutado (`/simple-setup/`)
- [ ] Clínicas accesibles con `?tenant=nombre`
- [ ] Login funcionando con credenciales de prueba
- [ ] (Opcional) Dominio personalizado configurado

**¡Listo! Tu aplicación multi-tenant está funcionando en DigitalOcean! 🎉**