from django.core.management.base import BaseCommand
from core.models import CategoriaHistorial, PreguntaHistorial


class Command(BaseCommand):
    help = 'Poblar el cuestionario de historial clínico con preguntas específicas para México'

    def handle(self, *args, **options):
        self.stdout.write('Creando categorías y preguntas de historial clínico para México...')
        
        # Crear categorías
        categorias_data = [
            {
                'nombre': 'Datos Personales',
                'descripcion': 'Información básica del paciente',
                'icono': 'fas fa-user',
                'color': '#007bff',
                'orden': 1
            },
            {
                'nombre': 'Antecedentes Médicos',
                'descripcion': 'Historial médico general del paciente',
                'icono': 'fas fa-file-medical',
                'color': '#dc3545',
                'orden': 2
            },
            {
                'nombre': 'Antecedentes Odontológicos',
                'descripcion': 'Historia dental específica',
                'icono': 'fas fa-tooth',
                'color': '#28a745',
                'orden': 3
            },
            {
                'nombre': 'Hábitos y Estilo de Vida',
                'descripcion': 'Hábitos que pueden afectar la salud bucal',
                'icono': 'fas fa-smoking',
                'color': '#ffc107',
                'orden': 4
            },
            {
                'nombre': 'Medicamentos Actuales',
                'descripcion': 'Medicamentos que está tomando el paciente',
                'icono': 'fas fa-pills',
                'color': '#17a2b8',
                'orden': 5
            },
            {
                'nombre': 'Alergias y Reacciones',
                'descripcion': 'Alergias conocidas y reacciones adversas',
                'icono': 'fas fa-exclamation-triangle',
                'color': '#fd7e14',
                'orden': 6
            }
        ]
        
        categorias = {}
        for cat_data in categorias_data:
            categoria, created = CategoriaHistorial.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults=cat_data
            )
            categorias[cat_data['nombre']] = categoria
            if created:
                self.stdout.write(f'  ✓ Categoría creada: {categoria.nombre}')
            else:
                self.stdout.write(f'  - Categoría existe: {categoria.nombre}')
        
        # Crear preguntas por categoría
        preguntas_data = {
            'Datos Personales': [
                {
                    'texto': '¿Cuál es su nombre completo?',
                    'tipo': 'TEXT',
                    'obligatoria': True,
                    'importancia': 'BAJA',
                    'orden': 1
                },
                {
                    'texto': '¿Cuál es su fecha de nacimiento?',
                    'tipo': 'FECHA',
                    'obligatoria': True,
                    'importancia': 'BAJA',
                    'orden': 2
                },
                {
                    'texto': '¿Cuál es su número de teléfono?',
                    'tipo': 'TELEFONO',
                    'obligatoria': True,
                    'importancia': 'BAJA',
                    'orden': 3
                },
                {
                    'texto': 'En caso de emergencia, ¿a quién debemos contactar?',
                    'subtitulo': 'Incluya nombre completo y número de teléfono',
                    'tipo': 'TEXTAREA',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 4
                }
            ],
            'Antecedentes Médicos': [
                {
                    'texto': '¿Padece o ha padecido diabetes?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'requiere_seguimiento': True,
                    'orden': 1
                },
                {
                    'texto': '¿Tiene problemas cardíacos?',
                    'subtitulo': 'Incluye hipertensión, arritmias, infartos previos',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'requiere_seguimiento': True,
                    'orden': 2
                },
                {
                    'texto': '¿Padece hipertensión arterial?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'ALTA',
                    'requiere_seguimiento': True,
                    'orden': 3
                },
                {
                    'texto': '¿Ha tenido hepatitis o problemas hepáticos?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'alerta_cofepris': True,
                    'orden': 4
                },
                {
                    'texto': '¿Padece VIH/SIDA?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'alerta_cofepris': True,
                    'requiere_seguimiento': True,
                    'orden': 5
                },
                {
                    'texto': '¿Está embarazada o sospecha estarlo?',
                    'tipo': 'SI_NO',
                    'obligatoria': False,
                    'importancia': 'ALTA',
                    'requiere_seguimiento': True,
                    'orden': 6
                },
                {
                    'texto': '¿Tiene problemas de coagulación sanguínea?',
                    'subtitulo': 'Hemofilia, toma anticoagulantes, etc.',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'orden': 7
                },
                {
                    'texto': '¿Ha sido sometido a alguna cirugía recientemente?',
                    'subtitulo': 'En los últimos 6 meses',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 8
                },
                {
                    'texto': 'Si respondió sí a la pregunta anterior, especifique qué tipo de cirugía',
                    'tipo': 'TEXTAREA',
                    'obligatoria': False,
                    'importancia': 'MEDIA',
                    'orden': 9
                }
            ],
            'Antecedentes Odontológicos': [
                {
                    'texto': '¿Cuándo fue su última visita al dentista?',
                    'tipo': 'FECHA',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 1
                },
                {
                    'texto': '¿Ha tenido experiencias negativas previas en tratamientos dentales?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 2
                },
                {
                    'texto': '¿Presenta dolor dental actualmente?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'ALTA',
                    'orden': 3
                },
                {
                    'texto': 'Del 1 al 10, ¿qué nivel de dolor tiene?',
                    'subtitulo': '1 = sin dolor, 10 = dolor insoportable',
                    'tipo': 'NUMERO',
                    'obligatoria': False,
                    'importancia': 'ALTA',
                    'orden': 4
                },
                {
                    'texto': '¿Sangran sus encías al cepillarse?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 5
                },
                {
                    'texto': '¿Ha perdido algún diente por caries o enfermedad periodontal?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 6
                },
                {
                    'texto': '¿Usa prótesis dentales (dentadura postiza, parciales)?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'BAJA',
                    'orden': 7
                },
                {
                    'texto': '¿Rechina o aprieta los dientes?',
                    'subtitulo': 'Especialmente por la noche (bruxismo)',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 8
                }
            ],
            'Hábitos y Estilo de Vida': [
                {
                    'texto': '¿Fuma cigarrillos?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'ALTA',
                    'orden': 1
                },
                {
                    'texto': 'Si fuma, ¿cuántos cigarrillos al día aproximadamente?',
                    'tipo': 'NUMERO',
                    'obligatoria': False,
                    'importancia': 'ALTA',
                    'orden': 2
                },
                {
                    'texto': '¿Consume alcohol regularmente?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 3
                },
                {
                    'texto': '¿Con qué frecuencia se cepilla los dientes?',
                    'tipo': 'MULTIPLE',
                    'opciones': 'Una vez al día, Dos veces al día, Tres veces al día, Ocasionalmente, Nunca',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 4
                },
                {
                    'texto': '¿Usa hilo dental?',
                    'tipo': 'MULTIPLE',
                    'opciones': 'Diariamente, Algunas veces por semana, Rara vez, Nunca',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 5
                },
                {
                    'texto': '¿Consume bebidas azucaradas frecuentemente?',
                    'subtitulo': 'Refrescos, jugos procesados, bebidas energéticas',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'BAJA',
                    'orden': 6
                }
            ],
            'Medicamentos Actuales': [
                {
                    'texto': '¿Está tomando algún medicamento actualmente?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'ALTA',
                    'orden': 1
                },
                {
                    'texto': 'Liste todos los medicamentos que toma (incluya dosis y frecuencia)',
                    'tipo': 'TEXTAREA',
                    'obligatoria': False,
                    'importancia': 'ALTA',
                    'orden': 2
                },
                {
                    'texto': '¿Toma anticoagulantes?',
                    'subtitulo': 'Warfarina, aspirina, clopidogrel, etc.',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'orden': 3
                },
                {
                    'texto': '¿Toma medicamentos para la presión arterial?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'ALTA',
                    'orden': 4
                },
                {
                    'texto': '¿Usa medicamentos para la ansiedad o depresión?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 5
                }
            ],
            'Alergias y Reacciones': [
                {
                    'texto': '¿Es alérgico a algún medicamento?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'orden': 1
                },
                {
                    'texto': 'Si es alérgico, especifique a qué medicamentos y qué tipo de reacción presenta',
                    'tipo': 'TEXTAREA',
                    'obligatoria': False,
                    'importancia': 'CRITICA',
                    'orden': 2
                },
                {
                    'texto': '¿Es alérgico a la penicilina?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'orden': 3
                },
                {
                    'texto': '¿Es alérgico al látex?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'ALTA',
                    'orden': 4
                },
                {
                    'texto': '¿Ha tenido reacciones adversas a la anestesia local dental?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'CRITICA',
                    'orden': 5
                },
                {
                    'texto': '¿Tiene alergias alimentarias conocidas?',
                    'tipo': 'SI_NO',
                    'obligatoria': True,
                    'importancia': 'MEDIA',
                    'orden': 6
                },
                {
                    'texto': 'Si tiene alergias alimentarias, especifique cuáles',
                    'tipo': 'TEXTAREA',
                    'obligatoria': False,
                    'importancia': 'MEDIA',
                    'orden': 7
                }
            ]
        }
        
        # Crear las preguntas
        total_preguntas = 0
        for categoria_nombre, preguntas_lista in preguntas_data.items():
            categoria = categorias[categoria_nombre]
            
            for pregunta_data in preguntas_lista:
                pregunta_data['categoria'] = categoria
                
                pregunta, created = PreguntaHistorial.objects.get_or_create(
                    texto=pregunta_data['texto'],
                    categoria=categoria,
                    defaults=pregunta_data
                )
                
                if created:
                    total_preguntas += 1
                    self.stdout.write(f'    ✓ Pregunta creada: {pregunta.texto[:50]}...')
                else:
                    self.stdout.write(f'    - Pregunta existe: {pregunta.texto[:50]}...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Cuestionario mexicano creado exitosamente!\n'
                f'- {len(categorias)} categorías\n'
                f'- {total_preguntas} nuevas preguntas creadas\n'
                f'- Total de preguntas en el sistema: {PreguntaHistorial.objects.count()}'
            )
        )
        
        # Información adicional
        self.stdout.write(
            self.style.WARNING(
                f'\nPara acceder al cuestionario:\n'
                f'1. Ve a Cuestionarios de Historial\n'
                f'2. Selecciona un paciente\n'
                f'3. Completa el cuestionario\n\n'
                f'Para administrar preguntas:\n'
                f'1. Ve a Admin Cuestionario > Categorías\n'
                f'2. Ve a Admin Cuestionario > Preguntas'
            )
        )