from django.core.management.base import BaseCommand
from core.models import CategoriaHistorial, PreguntaHistorial

class Command(BaseCommand):
    help = 'Carga las categorías y preguntas estándar del cuestionario de historial clínico odontológico según normas COFEPRIS México'

    def handle(self, *args, **options):
        self.stdout.write('Cargando cuestionario de historial clínico COFEPRIS...')

        # Crear categorías
        categorias_data = [
            {
                'nombre': 'Datos Personales y Demográficos',
                'descripcion': 'Información personal básica del paciente',
                'icono': 'fas fa-user',
                'color': '#007bff',
                'orden': 1
            },
            {
                'nombre': 'Motivo de Consulta',
                'descripcion': 'Razón principal de la visita odontológica',
                'icono': 'fas fa-comment-medical',
                'color': '#17a2b8',
                'orden': 2
            },
            {
                'nombre': 'Historia de la Enfermedad Actual',
                'descripcion': 'Descripción del padecimiento actual',
                'icono': 'fas fa-notes-medical',
                'color': '#28a745',
                'orden': 3
            },
            {
                'nombre': 'Antecedentes Heredo-Familiares',
                'descripcion': 'Enfermedades familiares relevantes',
                'icono': 'fas fa-users',
                'color': '#ffc107',
                'orden': 4
            },
            {
                'nombre': 'Antecedentes Personales Patológicos',
                'descripcion': 'Enfermedades y condiciones médicas previas',
                'icono': 'fas fa-heartbeat',
                'color': '#dc3545',
                'orden': 5
            },
            {
                'nombre': 'Antecedentes Odontológicos',
                'descripcion': 'Historia dental y tratamientos previos',
                'icono': 'fas fa-tooth',
                'color': '#6f42c1',
                'orden': 6
            },
            {
                'nombre': 'Medicamentos y Alergias',
                'descripcion': 'Medicamentos actuales y reacciones alérgicas',
                'icono': 'fas fa-pills',
                'color': '#e83e8c',
                'orden': 7
            },
            {
                'nombre': 'Hábitos Nocivos',
                'descripcion': 'Hábitos que afectan la salud oral',
                'icono': 'fas fa-smoking-ban',
                'color': '#fd7e14',
                'orden': 8
            },
            {
                'nombre': 'Revisión por Aparatos y Sistemas',
                'descripcion': 'Evaluación de sistemas corporales',
                'icono': 'fas fa-stethoscope',
                'color': '#20c997',
                'orden': 9
            },
            {
                'nombre': 'Evaluación de Riesgo COFEPRIS',
                'descripcion': 'Preguntas específicas para cumplimiento normativo',
                'icono': 'fas fa-shield-alt',
                'color': '#6c757d',
                'orden': 10
            }
        ]

        # Crear o actualizar categorías
        for categoria_data in categorias_data:
            categoria, created = CategoriaHistorial.objects.get_or_create(
                nombre=categoria_data['nombre'],
                defaults=categoria_data
            )
            if created:
                self.stdout.write(f'  ✓ Categoría creada: {categoria.nombre}')
            else:
                self.stdout.write(f'  → Categoría ya existe: {categoria.nombre}')

        # Obtener categorías para las preguntas
        categorias = {cat.nombre: cat for cat in CategoriaHistorial.objects.all()}

        # Preguntas por categoría
        preguntas_data = [
            # Datos Personales y Demográficos
            {
                'categoria': 'Datos Personales y Demográficos',
                'preguntas': [
                    {
                        'texto': 'Edad al momento de la consulta',
                        'subtitulo': 'Confirme la edad actual del paciente',
                        'tipo': 'NUMERO',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 1
                    },
                    {
                        'texto': 'Ocupación actual',
                        'subtitulo': 'Actividad laboral o profesional principal',
                        'tipo': 'TEXT',
                        'obligatoria': True,
                        'importancia': 'BAJA',
                        'orden': 2
                    },
                    {
                        'texto': 'Estado civil',
                        'tipo': 'MULTIPLE',
                        'opciones': 'Soltero(a), Casado(a), Divorciado(a), Viudo(a), Unión libre',
                        'obligatoria': False,
                        'importancia': 'BAJA',
                        'orden': 3
                    },
                ]
            },
            # Motivo de Consulta
            {
                'categoria': 'Motivo de Consulta',
                'preguntas': [
                    {
                        'texto': '¿Cuál es el motivo principal de su visita?',
                        'subtitulo': 'Describa con sus propias palabras por qué busca atención dental',
                        'tipo': 'TEXTAREA',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'orden': 1
                    },
                    {
                        'texto': '¿Presenta dolor dental actualmente?',
                        'subtitulo': 'Dolor en dientes, encías o mandíbula',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 2
                    },
                    {
                        'texto': 'Si presenta dolor, califique su intensidad del 1 al 10',
                        'subtitulo': 'Donde 1 es molestia mínima y 10 es dolor insoportable',
                        'tipo': 'NUMERO',
                        'obligatoria': False,
                        'importancia': 'ALTA',
                        'orden': 3
                    },
                ]
            },
            # Historia de la Enfermedad Actual
            {
                'categoria': 'Historia de la Enfermedad Actual',
                'preguntas': [
                    {
                        'texto': '¿Cuándo comenzaron los síntomas actuales?',
                        'tipo': 'TEXT',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 1
                    },
                    {
                        'texto': '¿Los síntomas han empeorado, mejorado o permanecen igual?',
                        'tipo': 'MULTIPLE',
                        'opciones': 'Han empeorado, Han mejorado, Permanecen igual, Varían',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 2
                    },
                    {
                        'texto': '¿Qué hace que los síntomas mejoren?',
                        'tipo': 'TEXTAREA',
                        'obligatoria': False,
                        'importancia': 'MEDIA',
                        'orden': 3
                    },
                    {
                        'texto': '¿Qué hace que los síntomas empeoren?',
                        'tipo': 'TEXTAREA',
                        'obligatoria': False,
                        'importancia': 'MEDIA',
                        'orden': 4
                    },
                ]
            },
            # Antecedentes Heredo-Familiares
            {
                'categoria': 'Antecedentes Heredo-Familiares',
                'preguntas': [
                    {
                        'texto': '¿Algún familiar ha padecido diabetes?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 1
                    },
                    {
                        'texto': '¿Algún familiar ha padecido hipertensión arterial?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 2
                    },
                    {
                        'texto': '¿Algún familiar ha padecido enfermedades del corazón?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 3
                    },
                    {
                        'texto': '¿Algún familiar ha padecido cáncer?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 4
                    },
                    {
                        'texto': '¿Hay antecedentes familiares de problemas de coagulación?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 5
                    },
                ]
            },
            # Antecedentes Personales Patológicos
            {
                'categoria': 'Antecedentes Personales Patológicos',
                'preguntas': [
                    {
                        'texto': '¿Padece o ha padecido diabetes?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 1
                    },
                    {
                        'texto': '¿Padece o ha padecido hipertensión arterial?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 2
                    },
                    {
                        'texto': '¿Padece o ha padecido enfermedades del corazón?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 3
                    },
                    {
                        'texto': '¿Ha tenido problemas de coagulación o sangrado excesivo?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 4
                    },
                    {
                        'texto': '¿Padece epilepsia o convulsiones?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 5
                    },
                    {
                        'texto': '¿Ha sido diagnosticado con VIH/SIDA?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 6
                    },
                    {
                        'texto': '¿Ha padecido hepatitis (A, B, C)?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 7
                    },
                    {
                        'texto': '¿Padece asma o problemas respiratorios?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 8
                    },
                    {
                        'texto': '¿Ha recibido radioterapia en cabeza o cuello?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 9
                    },
                    {
                        'texto': '¿Ha recibido quimioterapia?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 10
                    },
                ]
            },
            # Antecedentes Odontológicos
            {
                'categoria': 'Antecedentes Odontológicos',
                'preguntas': [
                    {
                        'texto': '¿Cuándo fue su última visita al dentista?',
                        'tipo': 'TEXT',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 1
                    },
                    {
                        'texto': '¿Qué tratamiento recibió en su última visita?',
                        'tipo': 'TEXTAREA',
                        'obligatoria': False,
                        'importancia': 'MEDIA',
                        'orden': 2
                    },
                    {
                        'texto': '¿Ha tenido reacciones adversas a tratamientos dentales?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 3
                    },
                    {
                        'texto': '¿Ha tenido complicaciones con anestesia dental?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 4
                    },
                    {
                        'texto': '¿Le han extraído dientes anteriormente?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 5
                    },
                    {
                        'texto': '¿Usa prótesis dentales (parciales o totales)?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 6
                    },
                ]
            },
            # Medicamentos y Alergias
            {
                'categoria': 'Medicamentos y Alergias',
                'preguntas': [
                    {
                        'texto': '¿Está tomando algún medicamento actualmente?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 1
                    },
                    {
                        'texto': 'Liste todos los medicamentos que toma (incluyendo dosis)',
                        'subtitulo': 'Incluya vitaminas, suplementos y medicamentos sin receta',
                        'tipo': 'TEXTAREA',
                        'obligatoria': False,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'orden': 2
                    },
                    {
                        'texto': '¿Es alérgico a algún medicamento?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 3
                    },
                    {
                        'texto': 'Liste todas las alergias a medicamentos',
                        'subtitulo': 'Incluya el medicamento y el tipo de reacción',
                        'tipo': 'TEXTAREA',
                        'obligatoria': False,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'orden': 4
                    },
                    {
                        'texto': '¿Es alérgico al látex?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 5
                    },
                    {
                        'texto': '¿Es alérgico a algún metal (níquel, cromo, etc.)?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 6
                    },
                ]
            },
            # Hábitos Nocivos
            {
                'categoria': 'Hábitos Nocivos',
                'preguntas': [
                    {
                        'texto': '¿Fuma o ha fumado?',
                        'tipo': 'MULTIPLE',
                        'opciones': 'No fumo, Fumo actualmente, Dejé de fumar hace menos de 1 año, Dejé de fumar hace más de 1 año',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 1
                    },
                    {
                        'texto': '¿Cuántos cigarrillos fuma al día? (si aplica)',
                        'tipo': 'NUMERO',
                        'obligatoria': False,
                        'importancia': 'ALTA',
                        'orden': 2
                    },
                    {
                        'texto': '¿Consume bebidas alcohólicas?',
                        'tipo': 'MULTIPLE',
                        'opciones': 'No consumo, Ocasionalmente, Fin de semana, Diariamente',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'requiere_seguimiento': True,
                        'orden': 3
                    },
                    {
                        'texto': '¿Se muerde las uñas o los labios?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 4
                    },
                    {
                        'texto': '¿Aprieta o rechina los dientes?',
                        'subtitulo': 'Especialmente durante la noche (bruxismo)',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 5
                    },
                    {
                        'texto': '¿Usa los dientes para abrir o cortar objetos?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 6
                    },
                ]
            },
            # Revisión por Aparatos y Sistemas
            {
                'categoria': 'Revisión por Aparatos y Sistemas',
                'preguntas': [
                    {
                        'texto': '¿Ha experimentado pérdida de peso inexplicable recientemente?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 1
                    },
                    {
                        'texto': '¿Ha notado cambios en su apetito?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'MEDIA',
                        'orden': 2
                    },
                    {
                        'texto': '¿Ha tenido fiebre o escalofríos recientemente?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 3
                    },
                    {
                        'texto': '¿Ha notado inflamación en ganglios del cuello?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 4
                    },
                    {
                        'texto': '¿Tiene dificultad para tragar?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 5
                    },
                    {
                        'texto': '¿Ha notado cambios en su voz o ronquera persistente?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 6
                    },
                ]
            },
            # Evaluación de Riesgo COFEPRIS
            {
                'categoria': 'Evaluación de Riesgo COFEPRIS',
                'preguntas': [
                    {
                        'texto': '¿Ha estado en contacto con personas con enfermedades infecciosas en los últimos 30 días?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 1
                    },
                    {
                        'texto': '¿Ha viajado fuera del país en los últimos 6 meses?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 2
                    },
                    {
                        'texto': '¿Ha recibido transfusiones sanguíneas?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'requiere_seguimiento': True,
                        'alerta_cofepris': True,
                        'orden': 3
                    },
                    {
                        'texto': '¿Ha sido hospitalizado en el último año?',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'ALTA',
                        'requiere_seguimiento': True,
                        'orden': 4
                    },
                    {
                        'texto': 'Autoriza el tratamiento odontológico después de haber leído y comprendido los riesgos',
                        'subtitulo': 'Consentimiento informado para procedimientos odontológicos',
                        'tipo': 'SI_NO',
                        'obligatoria': True,
                        'importancia': 'CRITICA',
                        'alerta_cofepris': True,
                        'orden': 5
                    },
                ]
            },
        ]

        # Crear preguntas
        total_preguntas = 0
        for grupo in preguntas_data:
            categoria = categorias[grupo['categoria']]
            self.stdout.write(f'\n  Procesando categoría: {categoria.nombre}')
            
            for pregunta_data in grupo['preguntas']:
                pregunta_data['categoria'] = categoria
                pregunta, created = PreguntaHistorial.objects.get_or_create(
                    categoria=categoria,
                    texto=pregunta_data['texto'],
                    defaults=pregunta_data
                )
                if created:
                    total_preguntas += 1
                    self.stdout.write(f'    ✓ Pregunta creada: {pregunta_data["texto"][:50]}...')
                else:
                    self.stdout.write(f'    → Pregunta ya existe: {pregunta_data["texto"][:50]}...')

        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS(f'✅ Cuestionario COFEPRIS cargado exitosamente'))
        self.stdout.write(f'📊 Categorías: {CategoriaHistorial.objects.count()}')
        self.stdout.write(f'📋 Preguntas totales: {PreguntaHistorial.objects.count()}')
        self.stdout.write(f'🆕 Preguntas nuevas: {total_preguntas}')
        self.stdout.write('='*80)