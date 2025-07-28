from django.core.management.base import BaseCommand
from core.models import PreguntaHistorial

class Command(BaseCommand):
    help = 'Carga las preguntas estándar del historial clínico para México.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando la carga de preguntas base...'))

        preguntas = [
            # Antecedentes Heredofamiliares
            {'texto': '¿Alguno de sus familiares directos (padres, hermanos) padece o ha padecido diabetes?', 'tipo': 'SI_NO', 'orden': 10},
            {'texto': '¿Alguno de sus familiares directos padece o ha padecido hipertensión arterial?', 'tipo': 'SI_NO', 'orden': 20},
            {'texto': '¿Alguno de sus familiares directos padece o ha padecido problemas cardíacos?', 'tipo': 'SI_NO', 'orden': 30},

            # Antecedentes Personales Patológicos
            {'texto': '¿Padece actualmente alguna de las siguientes enfermedades?', 'tipo': 'MULTIPLE', 'opciones': 'Diabetes,Hipertensión,Problemas Cardíacos,Problemas Renales,Cáncer,VIH/SIDA,Hepatitis,Otra,Ninguna', 'orden': 40},
            {'texto': 'Si seleccionó "Otra", por favor especifique:', 'tipo': 'TEXT', 'orden': 50},
            {'texto': '¿Está actualmente bajo algún tratamiento médico?', 'tipo': 'SI_NO', 'orden': 60},
            {'texto': 'Si su respuesta fue sí, describa cuál:', 'tipo': 'TEXTAREA', 'orden': 70},
            {'texto': '¿Es alérgico a algún medicamento (ej. penicilina, anestesia)?', 'tipo': 'SI_NO', 'orden': 80},
            {'texto': 'Si su respuesta fue sí, especifique a cuáles:', 'tipo': 'TEXTAREA', 'orden': 90},
            {'texto': '¿Ha tenido alguna reacción anormal a la anestesia dental previamente?', 'tipo': 'SI_NO', 'orden': 100},
            {'texto': '¿Ha tenido hemorragias o problemas de coagulación?', 'tipo': 'SI_NO', 'orden': 110},

            # Antecedentes Personales No Patológicos
            {'texto': '¿Fuma?', 'tipo': 'SI_NO', 'orden': 120},
            {'texto': '¿Consume bebidas alcohólicas con regularidad?', 'tipo': 'SI_NO', 'orden': 130},
            {'texto': '¿Cuántas veces al día cepilla sus dientes?', 'tipo': 'MULTIPLE', 'opciones': '1,2,3,Más de 3', 'orden': 140},
            {'texto': '¿Utiliza hilo dental?', 'tipo': 'SI_NO', 'orden': 150},

            # Específico para Pacientes Femeninos
            {'texto': '¿Está usted embarazada o sospecha estarlo?', 'tipo': 'SI_NO', 'orden': 160},
        ]

        for p_data in preguntas:
            pregunta, created = PreguntaHistorial.objects.get_or_create(
                texto=p_data['texto'],
                defaults=p_data
            )
            if created:
                self.stdout.write(f"  - Creada: '{pregunta.texto}'")
            else:
                self.stdout.write(f"  - Ya existía: '{pregunta.texto}'")
        
        self.stdout.write(self.style.SUCCESS('Carga de preguntas completada.'))