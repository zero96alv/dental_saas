from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

@login_required
def prueba_odontograma_anatomico(request):
    """
    Vista de prueba para el nuevo odontograma anatómico realista.
    Esta vista es independiente del sistema principal para permitir pruebas seguras.
    """
    context = {
        'titulo': 'Prueba - Odontogramas Profesionales',
        'descripcion': 'Comparación y prueba de odontograma Boca Abierta vs Sistema FDI Universal',
        'paciente_demo': {
            'nombre': 'Paciente Demo',
            'numero_identificacion': '12345678',
        },
        # Datos demo para mostrar algunos diagnósticos
        'diagnosticos_demo': [
            {'numero': 1, 'diagnostico': 'sano'},
            {'numero': 3, 'diagnostico': 'caries'},
            {'numero': 8, 'diagnostico': 'obturada'},
            {'numero': 11, 'diagnostico': 'corona'},
            {'numero': 16, 'diagnostico': 'extraida'},
            {'numero': 22, 'diagnostico': 'implante'},
            {'numero': 28, 'diagnostico': 'endodoncia'},
            {'numero': 33, 'diagnostico': 'sano'},  # supernumerario
        ]
    }
    
    return render(request, 'core/prueba_odontograma_anatomico.html', context)

@login_required
def prueba_aplicar_diagnostico(request):
    """
    Endpoint de prueba para simular la aplicación de diagnósticos
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            numero_diente = data.get('numero_diente')
            diagnostico = data.get('diagnostico')
            
            # Simular respuesta exitosa
            return JsonResponse({
                'success': True,
                'message': f'Diagnóstico "{diagnostico}" aplicado al diente {numero_diente} (DEMO)',
                'diente': numero_diente,
                'diagnostico_aplicado': diagnostico
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error en prueba: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método no permitido'
    })