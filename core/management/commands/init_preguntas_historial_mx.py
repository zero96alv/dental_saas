from django.core.management.base import BaseCommand
from core.models import PreguntaHistorial

PREGUNTAS = [
    # Antecedentes personales patológicos
    ("¿Padece diabetes?", 'SI_NO', 10),
    ("¿Padece hipertensión arterial?", 'SI_NO', 20),
    ("¿Padece enfermedades cardíacas?", 'SI_NO', 30),
    ("¿Padece enfermedades respiratorias (asma, EPOC)?", 'SI_NO', 40),
    ("¿Enfermedades infectocontagiosas (hepatitis, VIH)?", 'SI_NO', 50),
    # Alergias y medicamentos
    ("¿Es alérgico a algún medicamento o anestesia?", 'SI_NO', 60),
    ("Describa alergias y reacciones (si aplica)", 'TEXTAREA', 65),
    ("¿Toma actualmente algún medicamento?", 'SI_NO', 70),
    ("Liste medicamentos actuales", 'TEXTAREA', 75),
    # Hábitos
    ("¿Consume tabaco?", 'SI_NO', 80),
    ("¿Consume alcohol?", 'SI_NO', 90),
    # Situaciones especiales
    ("¿Está embarazada o en periodo de lactancia?", 'SI_NO', 100),
    # Dental
    ("Motivo de la consulta", 'TEXTAREA', 110),
    ("Escala de dolor (0-10)", 'TEXT', 120),
]

class Command(BaseCommand):
    help = 'Inicializa preguntas estándar de historial clínico para México'

    def handle(self, *args, **options):
        creadas = 0
        for texto, tipo, orden in PREGUNTAS:
            obj, created = PreguntaHistorial.objects.get_or_create(
                texto=texto,
                defaults={
                    'tipo': tipo,
                    'orden': orden,
                    'activa': True
                }
            )
            if created:
                creadas += 1
        self.stdout.write(self.style.SUCCESS(f'Preguntas inicializadas. Nuevas: {creadas}'))
