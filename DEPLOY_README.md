# 🚀 Despliegue de Dental SaaS en Render

Este documento te guiará para desplegar tu sistema Dental SaaS en **Render** de forma gratuita.

## 📋 Requisitos Previos

1. **Cuenta en GitHub** (para subir el código)
2. **Cuenta en Render** (gratuita): https://render.com
3. **Base de datos PostgreSQL** (Render incluye una gratuita)

## 🎯 Paso a Paso

### **1. Preparar el Repositorio en GitHub**

```bash
# Inicializar git si no está inicializado
git init

# Agregar archivos
git add .
git commit -m "Preparar para despliegue en Render"

# Crear repositorio en GitHub y subirlo
git remote add origin https://github.com/tu-usuario/dental-saas.git
git push -u origin main
```

### **2. Crear Base de Datos en Render**

1. Ve a tu [Dashboard de Render](https://dashboard.render.com/)
2. Click en **"New +"** → **"PostgreSQL"**
3. Configura:
   - **Name**: `dental-saas-db`
   - **Database**: `dental_saas`
   - **User**: `dental_user`
   - **Region**: Oregon (más cerca)
   - **Plan**: Free
4. Click **"Create Database"**
5. **¡IMPORTANTE!** Guarda la **External Database URL** que aparece

### **3. Crear Web Service en Render**

1. En tu Dashboard, click **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configura:
   - **Name**: `dental-saas`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT dental_saas.wsgi:application`
   - **Plan**: Free

### **4. Configurar Variables de Entorno**

En la sección **Environment** del Web Service, agregar:

```env
SECRET_KEY=tu-clave-secreta-super-larga-y-aleatoria-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=dental_saas.settings_production
DATABASE_URL=[pegar-la-url-de-tu-base-de-datos-postgresql]
RENDER_EXTERNAL_HOSTNAME=tu-app-name.onrender.com
```

#### 🔑 **Generar SECRET_KEY Segura**
```python
# Ejecutar en Python para generar una clave segura
import secrets
print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))
```

### **5. Deploy**

1. Click **"Create Web Service"**
2. Render iniciará el build automáticamente
3. El proceso tomará 5-10 minutos la primera vez
4. Si todo está bien, verás ✅ **"Your service is live"**

## 🌐 URLs Disponibles

Una vez desplegado:
- **Principal**: `https://tu-app-name.onrender.com/`
- **Admin**: `https://tu-app-name.onrender.com/admin/`
- **Demo**: `https://demo.tu-app-name.onrender.com/` (si configuraste subdominio)

## 🔐 Credenciales Iniciales

### **Superusuario Principal**
- **Usuario**: `admin`
- **Contraseña**: `DentalSaaS2025!`

### **Usuario Demo**
- **Usuario**: `admin`
- **Contraseña**: `DemoAdmin2025!`

## 🏥 Configurar Tenants Adicionales

Después del deploy, puedes crear tenants adicionales:

```bash
# Ejecutar comando en la consola de Render
python setup_production_tenants.py
```

## 🔧 Comandos Útiles de Mantenimiento

### **Ver Logs**
En tu Dashboard de Render → Tu servicio → "Logs"

### **Ejecutar Comandos Django**
```bash
# Crear superusuario
python manage.py createsuperuser --settings=dental_saas.settings_production

# Aplicar migraciones
python manage.py migrate --settings=dental_saas.settings_production

# Recolectar archivos estáticos
python manage.py collectstatic --settings=dental_saas.settings_production
```

### **Crear Nuevo Tenant**
```python
from tenants.models import Clinica, Domain

# Crear tenant
tenant = Clinica(
    schema_name='clinica-nueva',
    nombre='Nueva Clínica Dental'
)
tenant.save()

# Crear dominio
domain = Domain(
    domain='nueva-clinica.tu-app-name.onrender.com',
    tenant=tenant,
    is_primary=True
)
domain.save()
```

## 📊 Monitoreo y Mantenimiento

### **Plan Gratuito de Render incluye:**
- ✅ 500 horas de cómputo/mes
- ✅ SSL/TLS automático
- ✅ CDN global
- ✅ Base de datos PostgreSQL gratuita (1GB)
- ✅ Backups automáticos

### **Limitaciones del Plan Gratuito:**
- ⏸️ Se suspende después de 15 min de inactividad
- 🐌 Reinicio lento (cold start)
- 📊 1GB de base de datos máximo

### **Upgrade a Plan Pago ($7/mes):**
- 🚀 Sin suspensión
- ⚡ Reinicio instantáneo
- 📈 Más recursos

## 🆘 Solución de Problemas

### **Build Failed**
```bash
# Verificar logs de build en Render Dashboard
# Problemas comunes:
# - Dependencias faltantes en requirements.txt
# - Errores en build.sh
# - Variables de entorno mal configuradas
```

### **Database Connection Error**
```bash
# Verificar que DATABASE_URL esté correcta
# Formato: postgresql://user:password@host:port/database
```

### **Static Files No Cargan**
```bash
# Ejecutar collectstatic manualmente
python manage.py collectstatic --settings=dental_saas.settings_production
```

## 🎉 ¡Felicitaciones!

Tu sistema Dental SaaS está ahora en línea y accesible desde cualquier parte del mundo. 

**Funcionalidades disponibles:**
- ✅ Sistema multi-tenant completo
- ✅ Gestión de pacientes y citas
- ✅ Historial clínico avanzado (NUEVO)
- ✅ Registro de tratamientos detallado (NUEVO)
- ✅ Odontograma interactivo
- ✅ Facturación con SAT
- ✅ Control de inventarios
- ✅ SSL/HTTPS automático
- ✅ Backups automáticos

## 📞 Soporte

Si necesitas ayuda adicional:
1. Revisa los logs en Render Dashboard
2. Consulta la documentación de Django
3. Verifica las variables de entorno
4. Revisa la conectividad a la base de datos

¡Tu sistema dental está listo para ser usado en producción! 🚀