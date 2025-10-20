"""
Comando para poblar la base de datos con documentos de consentimiento informado de ejemplo.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import date, timedelta
from core import models


class Command(BaseCommand):
    help = 'Poblar la base de datos con documentos de consentimiento informado de ejemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sobreescribir',
            action='store_true',
            help='Sobreescribir documentos existentes',
        )

    def handle(self, *args, **options):
        sobreescribir = options.get('sobreescribir', False)
        
        # Si hay documentos existentes y no se especifica sobreescribir
        if models.ConsentimientoInformado.objects.exists() and not sobreescribir:
            self.stdout.write(
                self.style.WARNING(
                    'Ya existen documentos de consentimiento. '
                    'Use --sobreescribir para reemplazarlos.'
                )
            )
            return

        if sobreescribir:
            # Eliminar documentos existentes
            models.ConsentimientoInformado.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Documentos existentes eliminados.')
            )

        # Crear documentos de consentimiento informado
        documentos = [
            {
                'titulo': 'Consentimiento Informado General - Tratamientos Dentales',
                'tipo_documento': 'GENERAL',
                'descripcion': 'Consentimiento general para procedimientos dentales rutinarios según normativas COFEPRIS.',
                'version': '1.0',
                'cumple_cofepris': True,
                'requiere_testigos': False,
                'contenido_ejemplo': '''
CONSENTIMIENTO INFORMADO PARA TRATAMIENTOS DENTALES GENERALES

Por medio del presente documento, yo __________________________, identificado(a) con ____________, 
declaro que he sido informado(a) de manera clara y comprensible sobre:

1. NATURALEZA DEL TRATAMIENTO
Los procedimientos dentales que requiero incluyen diagnóstico, limpieza, obturaciones, 
y otros tratamientos conservadores según mi condición oral actual.

2. BENEFICIOS ESPERADOS
Los tratamientos tienen como objetivo mantener y restaurar la salud oral, 
prevenir enfermedades y mejorar la función masticatoria.

3. RIESGOS Y COMPLICACIONES
- Sensibilidad temporal
- Molestias post-tratamiento
- Reacciones alérgicas (poco frecuentes)
- Necesidad de tratamientos adicionales

4. ALTERNATIVAS DE TRATAMIENTO
Se me han explicado las alternativas disponibles y las consecuencias de no recibir tratamiento.

5. CUIDADOS POST-TRATAMIENTO
He recibido instrucciones claras sobre el cuidado posterior al tratamiento.

Declaro que he tenido la oportunidad de hacer preguntas y todas han sido respondidas satisfactoriamente.

AUTORIZACIÓN
Autorizo al Dr./Dra. __________________ a realizar los tratamientos explicados.

Fecha: ___________
Paciente: ___________________ Firma: ___________________
Testigo: ____________________ Firma: ___________________
Dentista: ___________________ Firma: ___________________
                '''
            },
            {
                'titulo': 'Consentimiento Informado para Cirugía Oral',
                'tipo_documento': 'CIRUGIA',
                'descripcion': 'Consentimiento específico para procedimientos quirúrgicos orales según COFEPRIS.',
                'version': '1.0',
                'cumple_cofepris': True,
                'requiere_testigos': True,
                'contenido_ejemplo': '''
CONSENTIMIENTO INFORMADO PARA CIRUGÍA ORAL

Paciente: __________________________ Fecha: ______________

PROCEDIMIENTO PROPUESTO:
□ Extracción dental simple    □ Extracción quirúrgica
□ Cirugía periodontal        □ Biopsia
□ Otro: _________________________________

INFORMACIÓN DEL PROCEDIMIENTO:
1. NATURALEZA DE LA CIRUGÍA
Se me ha explicado que requiero cirugía oral para [descripción específica].

2. RIESGOS Y COMPLICACIONES
- Sangrado prolongado
- Infección
- Daño a estructuras vecinas
- Parestesia (adormecimiento temporal o permanente)
- Fractura de instrumentos
- Comunicación oro-antral (en extracciones superiores)
- Necesidad de procedimientos adicionales

3. CUIDADOS POST-OPERATORIOS
- Compresas frías las primeras 24 horas
- Medicación prescrita según indicaciones
- Dieta blanda y fría
- No enjuagues vigorosos
- Control post-operatorio en _____ días

4. SITUACIONES DE EMERGENCIA
En caso de sangrado excesivo, dolor severo o fiebre, contactar inmediatamente.

DECLARACIÓN Y AUTORIZACIÓN:
□ He leído y comprendido la información proporcionada
□ Se respondieron todas mis preguntas
□ Acepto los riesgos explicados
□ Autorizo el procedimiento

Paciente: _________________ Firma: _________ Fecha: _______
Testigo 1: ________________ Firma: _________ Fecha: _______
Testigo 2: ________________ Firma: _________ Fecha: _______
Cirujano: _________________ Firma: _________ Fecha: _______
                '''
            },
            {
                'titulo': 'Consentimiento Informado para Ortodoncia',
                'tipo_documento': 'ORTODONTICA',
                'descripcion': 'Consentimiento para tratamientos de ortodoncia y ortopedia maxilofacial.',
                'version': '1.0',
                'cumple_cofepris': True,
                'requiere_testigos': False,
                'contenido_ejemplo': '''
CONSENTIMIENTO INFORMADO PARA TRATAMIENTO DE ORTODONCIA

INFORMACIÓN DEL TRATAMIENTO:
Se me ha explicado que el tratamiento de ortodoncia tiene como objetivo:
- Corregir la posición de los dientes
- Mejorar la función masticatoria
- Establecer una oclusión adecuada
- Mejorar la estética dental

DURACIÓN Y PROCEDIMIENTO:
- Duración estimada: _______ meses
- Controles mensuales regulares
- Uso de aparatología fija/removible
- Posible necesidad de extracciones

RIESGOS Y LIMITACIONES:
- Molestias iniciales y tras ajustes
- Dificultad para mantener higiene
- Descalcificación del esmalte
- Reabsorción radicular
- Recidiva post-tratamiento
- Necesidad de cirugía ortognática

RESPONSABILIDADES DEL PACIENTE:
- Asistir a citas programadas
- Mantener excelente higiene oral
- Seguir instrucciones alimentarias
- Usar auxiliares según indicaciones
- Informar sobre problemas o molestias

FASE DE RETENCIÓN:
Se requiere uso de retenedores para mantener resultados:
- Retenedores fijos y/o removibles
- Uso según indicaciones del ortodoncista
- Controles periódicos de por vida

Acepto el tratamiento propuesto y me comprometo a seguir las indicaciones.

Paciente/Tutor: _____________ Firma: ________ Fecha: _____
Ortodoncista: ______________ Firma: ________ Fecha: _____
                '''
            },
            {
                'titulo': 'Consentimiento Informado para Endodoncia',
                'tipo_documento': 'ENDODONCIA',
                'descripcion': 'Consentimiento para tratamientos de conductos radiculares.',
                'version': '1.0',
                'cumple_cofepris': True,
                'requiere_testigos': False,
                'contenido_ejemplo': '''
CONSENTIMIENTO INFORMADO PARA TRATAMIENTO DE ENDODONCIA

DIAGNÓSTICO:
Diente #: _____ Diagnóstico: _________________________

PROCEDIMIENTO:
El tratamiento endodóntico (conductos) consiste en:
- Acceso a la cámara pulpar
- Eliminación del tejido pulpar
- Desinfección del sistema de conductos
- Obturación hermética de los conductos
- Restauración temporal/definitiva

ALTERNATIVAS:
□ Extracción dental    □ No tratamiento

PRONÓSTICO:
□ Favorable    □ Reservado    □ Desfavorable

RIESGOS Y COMPLICACIONES:
- Fractura de instrumentos
- Perforación radicular
- Persistencia de síntomas
- Necesidad de retratamiento
- Fractura dental post-tratamiento
- Necesidad de tratamiento quirúrgico
- Pérdida del diente

CUIDADOS POST-TRATAMIENTO:
- Evitar masticar hasta que pase la anestesia
- Analgésicos según prescripción
- Restauración definitiva en 2-4 semanas
- Control radiográfico en 3-6 meses

PRONÓSTICO DE ÉXITO: 85-95% según literatura científica

He comprendido la información y autorizo el tratamiento.

Paciente: _________________ Firma: _________ Fecha: _______
Endodoncista: _____________ Firma: _________ Fecha: _______
                '''
            }
        ]

        creados = 0
        for doc_data in documentos:
            contenido_ejemplo = doc_data.pop('contenido_ejemplo', '')
            
            # Crear archivo PDF ficticio (en producción sería un PDF real)
            nombre_archivo = f"consentimiento_{doc_data['tipo_documento'].lower()}.pdf"
            archivo_contenido = f"Contenido PDF para {doc_data['titulo']}\n\n{contenido_ejemplo}".encode('utf-8')
            
            documento = models.ConsentimientoInformado.objects.create(
                titulo=doc_data['titulo'],
                tipo_documento=doc_data['tipo_documento'],
                descripcion=doc_data['descripcion'],
                version=doc_data['version'],
                fecha_vigencia_inicio=date.today(),
                fecha_vigencia_fin=date.today() + timedelta(days=365),  # Vigente por 1 año
                cumple_cofepris=doc_data['cumple_cofepris'],
                requiere_testigos=doc_data['requiere_testigos'],
                estado='ACTIVO'
            )
            
            # Simular archivo PDF (en producción se cargarían PDFs reales)
            documento.archivo_pdf.save(
                nombre_archivo,
                ContentFile(archivo_contenido),
                save=True
            )
            
            creados += 1
            
            self.stdout.write(
                f'✓ Creado: {documento.titulo} (v{documento.version})'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Éxito! Se crearon {creados} documentos de consentimiento informado.'
            )
        )

        # Mostrar estadísticas
        total_documentos = models.ConsentimientoInformado.objects.count()
        activos = models.ConsentimientoInformado.objects.filter(estado='ACTIVO').count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nEstadísticas:\n'
                f'- Total documentos: {total_documentos}\n'
                f'- Documentos activos: {activos}\n'
                f'- Tipos disponibles: {len(set([doc["tipo_documento"] for doc in documentos]))}'
            )
        )

        # Instrucciones adicionales
        self.stdout.write(
            self.style.WARNING(
                f'\nNOTA IMPORTANTE:\n'
                f'- Los archivos PDF son de ejemplo. En producción debe cargar PDFs reales.\n'
                f'- Revise y actualice el contenido según sus necesidades específicas.\n'
                f'- Verifique el cumplimiento de normativas COFEPRIS locales.\n'
                f'- Configure adecuadamente las fechas de vigencia.'
            )
        )