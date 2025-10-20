from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.shortcuts import redirect

@csrf_exempt
@never_cache
def tenant_switch_view(request):
    """
    Vista simple para mostrar tenants disponibles y permitir cambio
    """
    try:
        from tenants.models import Clinica
        tenants = Clinica.objects.all()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dental SaaS - Cambio de Tenant</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
                .tenant-card { 
                    border: 1px solid #ddd; 
                    padding: 20px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                    background: #f9f9f9; 
                }
                .btn { 
                    display: inline-block; 
                    padding: 10px 20px; 
                    background: #007cba; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 5px;
                }
                .btn:hover { background: #005a87; }
                h1 { color: #333; }
                h2 { color: #007cba; margin-top: 0; }
                .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🦷 Dental SaaS - Selección de Tenant</h1>
                
                <div class="info">
                    <strong>ℹ️ Información:</strong> Como Render no soporta subdominios, usa el parámetro <code>?tenant=SCHEMA</code> para cambiar entre tenants.
                </div>
        """
        
        for tenant in tenants:
            schema = tenant.schema_name
            name = tenant.name
            
            if schema == 'public':
                html += f"""
                <div class="tenant-card">
                    <h2>🏢 {name} (Administración)</h2>
                    <p><strong>Schema:</strong> {schema}</p>
                    <p>Panel de administración principal del sistema.</p>
                    <a href="/admin/" class="btn">Admin Principal</a>
                </div>
                """
            else:
                html += f"""
                <div class="tenant-card">
                    <h2>🏥 {name}</h2>
                    <p><strong>Schema:</strong> {schema}</p>
                    <p>Sistema completo de la clínica dental.</p>
                    <a href="/?tenant={schema}" class="btn">Sistema</a>
                    <a href="/admin/?tenant={schema}" class="btn">Admin</a>
                    <a href="/accounts/login/?tenant={schema}" class="btn">Login</a>
                </div>
                """
        
        html += """
                <div class="info">
                    <strong>🔑 Credenciales Demo:</strong><br>
                    Usuario: <code>admin</code><br>
                    Contraseña: <code>DemoAdmin2025!</code>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)
        
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


@csrf_exempt 
@never_cache
def switch_to_tenant(request, tenant_schema):
    """
    Vista para redirigir a un tenant específico
    """
    return redirect(f"/?tenant={tenant_schema}")