from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

@csrf_exempt
@never_cache
def landing_page(request):
    """
    Página de landing que muestra todas las clínicas disponibles
    """
    try:
        from tenants.models import Clinica
        
        # Obtener todas las clínicas (excluyendo public)
        clinicas = Clinica.objects.exclude(schema_name='public').order_by('nombre')
        
        # Si no hay clínicas, mostrar setup
        if not clinicas.exists():
            return render(request, 'landing/no_clinics.html')
        
        context = {
            'clinicas': clinicas,
            'total_clinicas': clinicas.count(),
        }
        
        return render(request, 'landing/clinic_selector.html', context)
        
    except Exception as e:
        # Si hay error, mostrar página simple
        return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dental SaaS Platform</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                .error {{ color: red; margin: 20px; }}
                .setup {{ background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px; }}
            </style>
        </head>
        <body>
            <h1>🦷 Dental SaaS Platform</h1>
            <div class="error">Error cargando clínicas: {e}</div>
            
            <div class="setup">
                <h3>Configuración Inicial Requerida</h3>
                <p>Parece que el sistema necesita configuración inicial.</p>
                <a href="/simple-setup/?key=DentalSaaS2025Setup!">🚀 Ejecutar Setup</a>
            </div>
            
            <div class="setup">
                <h3>Acceso Directo (si ya está configurado)</h3>
                <a href="/demo/">🏥 Demo Clínica</a> | 
                <a href="/admin/">⚙️ Admin</a>
            </div>
        </body>
        </html>
        """, content_type='text/html; charset=utf-8')


@csrf_exempt
@never_cache  
def clinic_not_found(request, clinic_slug):
    """
    Vista que se muestra cuando se accede a una clínica que no existe
    """
    try:
        from tenants.models import Clinica
        
        # Obtener clínicas disponibles
        available_clinics = Clinica.objects.exclude(schema_name='public').values_list('schema_name', 'nombre')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Clínica No Encontrada - Dental SaaS</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; background: #f8f9fa; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .error {{ color: #dc3545; margin: 20px 0; }}
                .clinic-list {{ text-align: left; margin: 20px 0; }}
                .clinic-item {{ padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; }}
                .clinic-item a {{ text-decoration: none; color: #007cba; font-weight: bold; }}
                .clinic-item a:hover {{ color: #005a87; }}
                .back-home {{ margin-top: 20px; }}
                .back-home a {{ display: inline-block; padding: 10px 20px; background: #007cba; color: white; text-decoration: none; border-radius: 5px; }}
                .back-home a:hover {{ background: #005a87; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🦷 Dental SaaS</h1>
                
                <div class="error">
                    <h2>❌ Clínica "{clinic_slug}" no encontrada</h2>
                    <p>La clínica que buscas no existe o no está disponible.</p>
                </div>
                
                <h3>🏥 Clínicas Disponibles:</h3>
                <div class="clinic-list">
        """
        
        for schema, name in available_clinics:
            html += f"""
                    <div class="clinic-item">
                        <a href="/{schema}/">🏥 {name}</a>
                        <small style="color: #666; margin-left: 10px;">/{schema}/</small>
                    </div>
            """
        
        if not available_clinics:
            html += """
                    <div class="clinic-item">
                        <em>No hay clínicas configuradas aún.</em>
                    </div>
            """
        
        html += f"""
                </div>
                
                <div class="back-home">
                    <a href="/">🏠 Volver al Inicio</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html, status=404)
        
    except Exception as e:
        return HttpResponse(f"""
        <h1>Error</h1>
        <p>Clínica '{clinic_slug}' no encontrada.</p>
        <p>Error del sistema: {e}</p>
        <a href="/">Volver al inicio</a>
        """, status=404)