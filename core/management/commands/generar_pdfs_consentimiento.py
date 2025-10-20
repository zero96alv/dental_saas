"""
Comando para generar PDFs reales de consentimiento informado con contenido legal apropiado.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from datetime import date, timedelta
from core import models
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO


class Command(BaseCommand):
    help = 'Generar PDFs reales de consentimiento informado con contenido legal apropiado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--actualizar',
            action='store_true',
            help='Actualizar PDFs existentes',
        )

    def handle(self, *args, **options):
        actualizar = options.get('actualizar', False)
        
        self.stdout.write('Generando PDFs de consentimiento informado...')

        # Estilos para los documentos
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )

        # Documentos a generar
        documentos = [
            {
                'titulo': 'Consentimiento Informado General - Tratamientos Dentales',
                'tipo_documento': 'GENERAL',
                'descripcion': 'Consentimiento general para procedimientos dentales rutinarios según normativas COFEPRIS.',
                'requiere_testigos': False,
                'contenido': self.generar_contenido_general(title_style, subtitle_style, normal_style)
            },
            {
                'titulo': 'Consentimiento Informado para Cirugía Oral',
                'tipo_documento': 'CIRUGIA',
                'descripcion': 'Consentimiento específico para procedimientos quirúrgicos orales según COFEPRIS.',
                'requiere_testigos': True,
                'contenido': self.generar_contenido_cirugia(title_style, subtitle_style, normal_style)
            },
            {
                'titulo': 'Consentimiento Informado para Ortodoncia',
                'tipo_documento': 'ORTODONTICA',
                'descripcion': 'Consentimiento para tratamientos de ortodoncia y ortopedia maxilofacial.',
                'requiere_testigos': False,
                'contenido': self.generar_contenido_ortodoncia(title_style, subtitle_style, normal_style)
            },
            {
                'titulo': 'Consentimiento Informado para Endodoncia',
                'tipo_documento': 'ENDODONCIA',
                'descripcion': 'Consentimiento para tratamientos de conductos radiculares.',
                'requiere_testigos': False,
                'contenido': self.generar_contenido_endodoncia(title_style, subtitle_style, normal_style)
            }
        ]

        actualizados = 0
        creados = 0

        for doc_data in documentos:
            # Verificar si existe
            documento_existente = models.ConsentimientoInformado.objects.filter(
                tipo_documento=doc_data['tipo_documento']
            ).first()

            if documento_existente and not actualizar:
                self.stdout.write(f'⏭ Existe: {doc_data["titulo"]}')
                continue

            # Generar PDF
            pdf_buffer = self.generar_pdf(doc_data['contenido'])
            
            # Crear o actualizar documento
            if documento_existente and actualizar:
                documento = documento_existente
                documento.titulo = doc_data['titulo']
                documento.descripcion = doc_data['descripcion']
                documento.requiere_testigos = doc_data['requiere_testigos']
                # Incrementar versión
                version_parts = documento.version.split('.')
                version_parts[-1] = str(int(version_parts[-1]) + 1)
                documento.version = '.'.join(version_parts)
                actualizados += 1
                action = 'actualizado'
            else:
                documento = models.ConsentimientoInformado(
                    titulo=doc_data['titulo'],
                    tipo_documento=doc_data['tipo_documento'],
                    descripcion=doc_data['descripcion'],
                    version='1.0',
                    fecha_vigencia_inicio=date.today(),
                    fecha_vigencia_fin=date.today() + timedelta(days=365*2),  # 2 años
                    cumple_cofepris=True,
                    requiere_testigos=doc_data['requiere_testigos'],
                    estado='ACTIVO'
                )
                creados += 1
                action = 'creado'

            # Guardar archivo PDF
            filename = f"consentimiento_{doc_data['tipo_documento'].lower()}_v{documento.version}.pdf"
            documento.archivo_pdf.save(
                filename,
                ContentFile(pdf_buffer.getvalue()),
                save=False
            )
            
            documento.save()
            
            self.stdout.write(f'✓ {action.title()}: {documento.titulo} (v{documento.version})')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Proceso completado!\n'
                f'📄 Documentos creados: {creados}\n'
                f'🔄 Documentos actualizados: {actualizados}\n'
                f'📁 Total documentos: {models.ConsentimientoInformado.objects.count()}'
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f'\n📍 UBICACIONES IMPORTANTES:\n'
                f'1. Ver documentos: http://dev.localhost:8000/consentimientos/\n'
                f'2. Crear nuevo: http://dev.localhost:8000/consentimientos/nuevo/\n'
                f'3. Archivos PDF: media/consentimientos/\n'
                f'4. Admin Django: http://dev.localhost:8000/admin/core/consentimientoinformado/'
            )
        )

    def generar_pdf(self, contenido):
        """Genera un PDF con el contenido proporcionado"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, 
                              topMargin=20*mm, bottomMargin=20*mm)
        
        # Construir el documento
        story = contenido
        
        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generar_contenido_general(self, title_style, subtitle_style, normal_style):
        """Contenido para consentimiento general"""
        story = []
        
        # Encabezado
        story.append(Paragraph("CONSENTIMIENTO INFORMADO", title_style))
        story.append(Paragraph("TRATAMIENTOS DENTALES GENERALES", subtitle_style))
        story.append(Spacer(1, 12))
        
        # Información del paciente
        story.append(Paragraph("INFORMACIÓN DEL PACIENTE", subtitle_style))
        patient_table = Table([
            ['Nombre completo:', '_' * 40, 'Fecha:', '_' * 15],
            ['Edad:', '_' * 10, 'Teléfono:', '_' * 20],
            ['Dirección:', '_' * 60]
        ], colWidths=[3*inch, 2*inch, 1*inch, 1.5*inch])
        patient_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Contenido principal
        story.append(Paragraph("1. NATURALEZA DEL TRATAMIENTO", subtitle_style))
        story.append(Paragraph(
            "Por medio del presente documento, declaro que he sido informado(a) de manera clara y comprensible sobre "
            "los procedimientos dentales que requiero, incluyendo: limpieza dental, obturaciones (empastes), "
            "tratamientos preventivos y otros procedimientos conservadores según mi condición oral actual.",
            normal_style
        ))
        
        story.append(Paragraph("2. BENEFICIOS ESPERADOS", subtitle_style))
        story.append(Paragraph(
            "Los tratamientos tienen como objetivo mantener y restaurar la salud oral, prevenir enfermedades "
            "periodontales y dentales, mejorar la función masticatoria y mantener la estética dental.",
            normal_style
        ))
        
        story.append(Paragraph("3. RIESGOS Y COMPLICACIONES", subtitle_style))
        story.append(Paragraph(
            "Como en cualquier procedimiento médico, existen riesgos asociados que incluyen pero no se limitan a:",
            normal_style
        ))
        story.append(Paragraph("• Sensibilidad dental temporal o permanente", normal_style))
        story.append(Paragraph("• Molestias post-tratamiento", normal_style))
        story.append(Paragraph("• Reacciones alérgicas a materiales dentales (poco frecuentes)", normal_style))
        story.append(Paragraph("• Necesidad de tratamientos adicionales", normal_style))
        story.append(Paragraph("• Infección post-tratamiento", normal_style))
        
        story.append(Paragraph("4. ALTERNATIVAS DE TRATAMIENTO", subtitle_style))
        story.append(Paragraph(
            "Se me han explicado las alternativas de tratamiento disponibles, incluyendo la opción de no recibir "
            "tratamiento y las consecuencias de esta decisión.",
            normal_style
        ))
        
        story.append(Paragraph("5. CUIDADOS POST-TRATAMIENTO", subtitle_style))
        story.append(Paragraph(
            "He recibido instrucciones claras sobre el cuidado posterior al tratamiento, incluyendo higiene oral, "
            "medicamentos si son necesarios, y citas de seguimiento.",
            normal_style
        ))
        
        story.append(Paragraph("6. ASPECTOS ECONÓMICOS", subtitle_style))
        story.append(Paragraph(
            "Se me ha informado sobre el costo total del tratamiento y las formas de pago disponibles. "
            "Entiendo que soy responsable del pago según lo acordado.",
            normal_style
        ))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("DECLARACIÓN Y AUTORIZACIÓN", subtitle_style))
        story.append(Paragraph(
            "Declaro que he tenido la oportunidad de hacer preguntas sobre el tratamiento propuesto y todas "
            "han sido respondidas satisfactoriamente. He leído y comprendido la información proporcionada.",
            normal_style
        ))
        
        # Tabla de firmas
        story.append(Spacer(1, 30))
        firma_table = Table([
            ['Firma del Paciente:', '_' * 25, 'Fecha:', '_' * 15],
            ['', '', '', ''],
            ['Nombre:', '_' * 30, '', ''],
            ['', '', '', ''],
            ['Firma del Dentista:', '_' * 25, 'Cédula Prof.:', '_' * 15],
            ['', '', '', ''],
            ['Nombre:', '_' * 30, '', ''],
        ], colWidths=[2*inch, 2.5*inch, 1*inch, 1.5*inch])
        firma_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(firma_table)
        
        return story

    def generar_contenido_cirugia(self, title_style, subtitle_style, normal_style):
        """Contenido para consentimiento de cirugía oral"""
        story = []
        
        story.append(Paragraph("CONSENTIMIENTO INFORMADO", title_style))
        story.append(Paragraph("CIRUGÍA ORAL Y MAXILOFACIAL", subtitle_style))
        story.append(Spacer(1, 12))
        
        # Información del paciente
        story.append(Paragraph("INFORMACIÓN DEL PACIENTE", subtitle_style))
        patient_table = Table([
            ['Nombre completo:', '_' * 40, 'Fecha:', '_' * 15],
            ['Edad:', '_' * 10, 'Teléfono:', '_' * 20],
        ])
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Procedimiento propuesto
        story.append(Paragraph("PROCEDIMIENTO PROPUESTO", subtitle_style))
        proc_table = Table([
            ['☐ Extracción dental simple', '☐ Extracción quirúrgica'],
            ['☐ Cirugía periodontal', '☐ Biopsia'],
            ['☐ Otro:', '_' * 30]
        ])
        story.append(proc_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("1. NATURALEZA DE LA CIRUGÍA", subtitle_style))
        story.append(Paragraph(
            "Se me ha explicado que requiero cirugía oral para el tratamiento de mi condición. El procedimiento "
            "será realizado bajo anestesia local y/o sedación según sea necesario.",
            normal_style
        ))
        
        story.append(Paragraph("2. RIESGOS Y COMPLICACIONES", subtitle_style))
        story.append(Paragraph(
            "Entiendo que, como en cualquier procedimiento quirúrgico, existen riesgos que incluyen:",
            normal_style
        ))
        story.append(Paragraph("• Sangrado prolongado", normal_style))
        story.append(Paragraph("• Infección post-operatoria", normal_style))
        story.append(Paragraph("• Daño a estructuras vecinas (dientes, nervios, senos paranasales)", normal_style))
        story.append(Paragraph("• Parestesia (adormecimiento temporal o permanente)", normal_style))
        story.append(Paragraph("• Fractura de instrumentos", normal_style))
        story.append(Paragraph("• Comunicación oro-antral", normal_style))
        story.append(Paragraph("• Necesidad de procedimientos adicionales", normal_style))
        story.append(Paragraph("• Reacciones adversas a anestesia o medicamentos", normal_style))
        
        story.append(Paragraph("3. CUIDADOS POST-OPERATORIOS", subtitle_style))
        story.append(Paragraph(
            "He recibido y comprendido las instrucciones post-operatorias que incluyen:",
            normal_style
        ))
        story.append(Paragraph("• Aplicar compresas frías las primeras 24 horas", normal_style))
        story.append(Paragraph("• Tomar medicación prescrita según indicaciones", normal_style))
        story.append(Paragraph("• Mantener dieta blanda y fría", normal_style))
        story.append(Paragraph("• Evitar enjuagues vigorosos", normal_style))
        story.append(Paragraph("• Acudir a control post-operatorio según programado", normal_style))
        
        story.append(Paragraph("4. SITUACIONES DE EMERGENCIA", subtitle_style))
        story.append(Paragraph(
            "En caso de sangrado excesivo, dolor severo no controlado con medicación, fiebre alta, o cualquier "
            "complicación, debo contactar inmediatamente a la clínica dental o acudir al servicio de urgencias.",
            normal_style
        ))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("DECLARACIÓN Y AUTORIZACIÓN", subtitle_style))
        
        # Checklist
        check_table = Table([
            ['☐ He leído y comprendido la información proporcionada'],
            ['☐ Se respondieron todas mis preguntas satisfactoriamente'],
            ['☐ Acepto los riesgos explicados'],
            ['☐ Autorizo el procedimiento quirúrgico']
        ])
        story.append(check_table)
        story.append(Spacer(1, 20))
        
        # Tabla de firmas con testigos
        story.append(Paragraph("FIRMAS", subtitle_style))
        firma_table = Table([
            ['Paciente:', '_' * 20, 'Firma:', '_' * 20, 'Fecha:', '_' * 10],
            ['', '', '', '', '', ''],
            ['Testigo 1:', '_' * 20, 'Firma:', '_' * 20, 'Fecha:', '_' * 10],
            ['', '', '', '', '', ''],
            ['Testigo 2:', '_' * 20, 'Firma:', '_' * 20, 'Fecha:', '_' * 10],
            ['', '', '', '', '', ''],
            ['Cirujano:', '_' * 20, 'Firma:', '_' * 20, 'Cédula:', '_' * 10],
        ])
        story.append(firma_table)
        
        return story

    def generar_contenido_ortodoncia(self, title_style, subtitle_style, normal_style):
        """Contenido para consentimiento de ortodoncia"""
        story = []
        
        story.append(Paragraph("CONSENTIMIENTO INFORMADO", title_style))
        story.append(Paragraph("TRATAMIENTO DE ORTODONCIA", subtitle_style))
        story.append(Spacer(1, 12))
        
        # Información del paciente
        story.append(Paragraph("INFORMACIÓN DEL PACIENTE", subtitle_style))
        patient_table = Table([
            ['Nombre completo:', '_' * 40, 'Fecha:', '_' * 15],
            ['Edad:', '_' * 10, 'Teléfono:', '_' * 20],
        ])
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("INFORMACIÓN DEL TRATAMIENTO", subtitle_style))
        story.append(Paragraph(
            "Se me ha explicado que el tratamiento de ortodoncia tiene como objetivo:",
            normal_style
        ))
        story.append(Paragraph("• Corregir la posición de los dientes", normal_style))
        story.append(Paragraph("• Mejorar la función masticatoria", normal_style))
        story.append(Paragraph("• Establecer una oclusión adecuada", normal_style))
        story.append(Paragraph("• Mejorar la estética dental y facial", normal_style))
        
        story.append(Paragraph("DURACIÓN Y PROCEDIMIENTO", subtitle_style))
        duration_table = Table([
            ['Duración estimada:', '_' * 15, 'meses'],
            ['Tipo de aparatología:', '☐ Fija  ☐ Removible  ☐ Mixta'],
            ['Controles mensuales:', 'Cada _____ semanas'],
            ['Posible necesidad de extracciones:', '☐ Sí  ☐ No']
        ])
        story.append(duration_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("RIESGOS Y LIMITACIONES", subtitle_style))
        story.append(Paragraph("• Molestias iniciales y tras cada ajuste", normal_style))
        story.append(Paragraph("• Dificultad para mantener higiene oral adecuada", normal_style))
        story.append(Paragraph("• Descalcificación del esmalte (manchas blancas)", normal_style))
        story.append(Paragraph("• Reabsorción radicular", normal_style))
        story.append(Paragraph("• Recidiva post-tratamiento", normal_style))
        story.append(Paragraph("• Posible necesidad de cirugía ortognática", normal_style))
        story.append(Paragraph("• Problemas de ATM", normal_style))
        
        story.append(Paragraph("RESPONSABILIDADES DEL PACIENTE", subtitle_style))
        story.append(Paragraph("• Asistir puntualmente a todas las citas programadas", normal_style))
        story.append(Paragraph("• Mantener excelente higiene oral", normal_style))
        story.append(Paragraph("• Seguir instrucciones alimentarias", normal_style))
        story.append(Paragraph("• Usar auxiliares según indicaciones (ligas, aparatos)", normal_style))
        story.append(Paragraph("• Informar inmediatamente sobre problemas o molestias", normal_style))
        
        story.append(Paragraph("FASE DE RETENCIÓN", subtitle_style))
        story.append(Paragraph(
            "Se requiere uso de retenedores para mantener los resultados obtenidos:",
            normal_style
        ))
        story.append(Paragraph("• Retenedores fijos y/o removibles según el caso", normal_style))
        story.append(Paragraph("• Uso según indicaciones del ortodoncista", normal_style))
        story.append(Paragraph("• Controles periódicos de por vida", normal_style))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "Acepto el tratamiento propuesto y me comprometo a seguir todas las indicaciones del ortodoncista.",
            normal_style
        ))
        
        # Firmas
        story.append(Spacer(1, 30))
        firma_table = Table([
            ['Paciente/Tutor:', '_' * 25, 'Firma:', '_' * 20, 'Fecha:', '_' * 10],
            ['', '', '', '', '', ''],
            ['Ortodoncista:', '_' * 25, 'Firma:', '_' * 20, 'Cédula:', '_' * 10],
        ])
        story.append(firma_table)
        
        return story

    def generar_contenido_endodoncia(self, title_style, subtitle_style, normal_style):
        """Contenido para consentimiento de endodoncia"""
        story = []
        
        story.append(Paragraph("CONSENTIMIENTO INFORMADO", title_style))
        story.append(Paragraph("TRATAMIENTO DE ENDODONCIA", subtitle_style))
        story.append(Spacer(1, 12))
        
        # Información del paciente
        story.append(Paragraph("INFORMACIÓN DEL PACIENTE", subtitle_style))
        patient_table = Table([
            ['Nombre completo:', '_' * 40, 'Fecha:', '_' * 15],
            ['Diente #:', '_' * 10, 'Diagnóstico:', '_' * 25],
        ])
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("PROCEDIMIENTO", subtitle_style))
        story.append(Paragraph(
            "El tratamiento endodóntico (tratamiento de conductos) consiste en:",
            normal_style
        ))
        story.append(Paragraph("• Acceso a la cámara pulpar", normal_style))
        story.append(Paragraph("• Eliminación del tejido pulpar infectado o necrótico", normal_style))
        story.append(Paragraph("• Limpieza y desinfección del sistema de conductos", normal_style))
        story.append(Paragraph("• Conformación de los conductos radiculares", normal_style))
        story.append(Paragraph("• Obturación hermética de los conductos", normal_style))
        story.append(Paragraph("• Restauración temporal/definitiva", normal_style))
        
        story.append(Paragraph("ALTERNATIVAS", subtitle_style))
        alt_table = Table([
            ['☐ Extracción dental', '☐ No tratamiento (observación)'],
        ])
        story.append(alt_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("PRONÓSTICO", subtitle_style))
        prog_table = Table([
            ['☐ Favorable', '☐ Reservado', '☐ Desfavorable'],
        ])
        story.append(prog_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("RIESGOS Y COMPLICACIONES", subtitle_style))
        story.append(Paragraph("• Fractura de instrumentos dentro del conducto", normal_style))
        story.append(Paragraph("• Perforación radicular", normal_style))
        story.append(Paragraph("• Persistencia de síntomas", normal_style))
        story.append(Paragraph("• Necesidad de retratamiento endodóntico", normal_style))
        story.append(Paragraph("• Fractura dental post-tratamiento", normal_style))
        story.append(Paragraph("• Necesidad de tratamiento quirúrgico (apicectomía)", normal_style))
        story.append(Paragraph("• Pérdida del diente", normal_style))
        
        story.append(Paragraph("CUIDADOS POST-TRATAMIENTO", subtitle_style))
        story.append(Paragraph("• Evitar masticar hasta que pase completamente la anestesia", normal_style))
        story.append(Paragraph("• Tomar analgésicos según prescripción médica", normal_style))
        story.append(Paragraph("• Colocar restauración definitiva en 2-4 semanas", normal_style))
        story.append(Paragraph("• Control radiográfico en 3-6 meses", normal_style))
        story.append(Paragraph("• Posible necesidad de corona dental", normal_style))
        
        story.append(Paragraph("PRONÓSTICO DE ÉXITO", subtitle_style))
        story.append(Paragraph(
            "El tratamiento endodóntico tiene un pronóstico de éxito del 85-95% según la literatura científica, "
            "dependiendo de factores como el diagnóstico inicial, anatomía dental y técnica utilizada.",
            normal_style
        ))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "He comprendido la información proporcionada y autorizo la realización del tratamiento endodóntico.",
            normal_style
        ))
        
        # Firmas
        story.append(Spacer(1, 30))
        firma_table = Table([
            ['Paciente:', '_' * 25, 'Firma:', '_' * 20, 'Fecha:', '_' * 10],
            ['', '', '', '', '', ''],
            ['Endodoncista:', '_' * 25, 'Firma:', '_' * 20, 'Cédula:', '_' * 10],
        ])
        story.append(firma_table)
        
        return story