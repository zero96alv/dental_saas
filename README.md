# Dental SaaS - Sistema de Gestión para Clínicas Dentales

Este proyecto es un sistema de gestión integral para clínicas dentales, construido con Django y diseñado bajo una arquitectura multi-tenant utilizando `django-tenants`. Permite a múltiples clínicas operar de forma independiente y segura en la misma plataforma.

## Estado del Proyecto: COMPLETADO (Versión 1.0)

El sistema ha sido desarrollado a través de un plan incremental y ahora cuenta con una base funcional completa, incluyendo gestión de pacientes, agenda, un odontograma interactivo, control de inventario y roles de usuario.

---

## Características Principales

- **Arquitectura Multi-Tenant:** Cada clínica (tenant) tiene su propio esquema de base de datos aislado, garantizando la privacidad y seguridad de los datos.
- **Gestión de Roles:** Sistema de permisos predefinido para `Administrador`, `Dentista` y `Recepcionista`, con una interfaz y menús que se adaptan dinámicamente a cada rol.
- **Dashboard Inteligente:** Panel de control para administradores con KPIs (Indicadores Clave de Rendimiento) en tiempo real, como ingresos del día, citas y alertas de stock bajo.
- **Módulo de Pacientes:** CRUD completo para la gestión de la información de los pacientes.
- **Odontograma Interactivo:** Herramienta visual profesional para registrar el estado dental de los pacientes de forma general, con una interfaz intuitiva basada en popovers.
- **Agenda de Citas:** Calendario funcional para la gestión de citas.
- **Módulo de Inventario:**
    - Gestión de Proveedores con datos fiscales de México.
    - Gestión de Insumos con control de stock mínimo.
    - Ciclo de Compras completo con cálculo automático de totales y capacidad para adjuntar facturas.
    - Lógica de negocio para la actualización automática del stock al recibir compras o completar citas.
- **Módulo Financiero:** Registro de pagos y cálculo automático de saldos pendientes en las citas.
- **Módulo de Reportes:** Reportes de Ingresos y Saldos Pendientes para la toma de decisiones.
- **Automatización:** Comandos de gestión para enviar recordatorios de citas, felicitaciones de cumpleaños y avisos de pago por email.
- **Diseño Responsivo:** La interfaz está construida con Bootstrap 5 y es adaptable a dispositivos móviles, tablets y escritorio.

---

## Guía de Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.10+
- PostgreSQL

### Pasos de Instalación

1.  **Clonar el Repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd dental_saas
    ```

2.  **Crear y Activar Entorno Virtual:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos:**
    - Asegúrate de que tu servidor de PostgreSQL esté corriendo.
    - Crea una base de datos (ej. `dental_db`).
    - **Importante:** La aplicación está configurada para conectarse a la base de datos `dental_db` con el usuario `postgres` y la contraseña `admin12345`. Si tus credenciales son diferentes, modifícalas en `dental_saas/settings.py`.

5.  **Configurar Variables de Entorno:**
    - Crea una copia del archivo `.env.example` y renómbrala a `.env`.
    - Abre el archivo `.env` y rellena tus credenciales de Gmail para el envío de correos:
      ```
      EMAIL_HOST_USER=tu_email@gmail.com
      EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion_de_16_caracteres
      ```

6.  **Aplicar Migraciones:**
    - Este comando preparará la base de datos, creará las tablas para el esquema público y para cada tenant.
    ```bash
    python manage.py migrate_schemas
    ```

7.  **Crear un Superusuario:**
    - Este usuario será el administrador global del sistema.
    ```bash
    python manage.py create_superuser_global
    ```
    - Sigue las instrucciones para crear tu usuario.

8.  **Ejecutar el Servidor de Desarrollo:**
    ```bash
    python manage.py runserver
    ```

### Acceder a la Aplicación

-   **Panel de Admin Global:** Para crear nuevas clínicas, ve a `http://127.0.0.1:8000/admin/`.
-   **Acceso a una Clínica:** Para usar la aplicación de una clínica, necesitas acceder a través de su dominio configurado (ej. `http://demo.localhost:8000/`).
-   **Crear tu Primera Clínica:**
    1.  Desde el panel de admin global, ve a la sección "TENANTS" y haz clic en "Clinicas".
    2.  Crea una nueva clínica (ej. Nombre: "Mi Clínica", Schema Name: "miclinica").
    3.  Luego, ve a "Domains" y añade un dominio para esa clínica (ej. Domain: "miclinica.localhost", Tenant: "Mi Clínica").
    4.  ¡Ahora puedes acceder a tu clínica en `http://miclinica.localhost:8000/`!