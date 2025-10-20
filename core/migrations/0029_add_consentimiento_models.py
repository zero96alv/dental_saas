# Generated manually for ConsentimientoInformado models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_fix_categoria_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsentimientoInformado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Título descriptivo del documento', max_length=200)),
                ('tipo_documento', models.CharField(choices=[('GENERAL', 'Consentimiento General'), ('CIRUGIA', 'Consentimiento Cirugía Oral'), ('ORTODONTICA', 'Consentimiento Ortodoncia'), ('ENDODONCIA', 'Consentimiento Endodoncia'), ('IMPLANTES', 'Consentimiento Implantes'), ('ESTETICA', 'Consentimiento Estética Dental'), ('PERIODONCIA', 'Consentimiento Periodoncia'), ('PROTESIS', 'Consentimiento Prótesis'), ('PEDIATRICA', 'Consentimiento Odontología Pediátrica'), ('OTROS', 'Otros Procedimientos')], default='GENERAL', max_length=20)),
                ('descripcion', models.TextField(blank=True, help_text='Descripción del contenido del documento')),
                ('archivo_pdf', models.FileField(help_text='Documento PDF del consentimiento informado', upload_to='consentimientos/')),
                ('nombre_archivo_original', models.CharField(blank=True, max_length=255)),
                ('tamaño_archivo', models.PositiveIntegerField(blank=True, help_text='Tamaño en bytes', null=True)),
                ('version', models.CharField(default='1.0', max_length=20)),
                ('estado', models.CharField(choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo'), ('ARCHIVADO', 'Archivado')], default='ACTIVO', max_length=20)),
                ('fecha_vigencia_inicio', models.DateField(help_text='Fecha de inicio de vigencia')),
                ('fecha_vigencia_fin', models.DateField(blank=True, help_text='Fecha de fin de vigencia (opcional)', null=True)),
                ('cumple_cofepris', models.BooleanField(default=True, help_text='Cumple con normativas COFEPRIS')),
                ('requiere_testigos', models.BooleanField(default=False, help_text='Requiere firma de testigos')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('actualizado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consentimientos_actualizados', to=settings.AUTH_USER_MODEL)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consentimientos_creados', to=settings.AUTH_USER_MODEL)),
                ('version_anterior', models.ForeignKey(blank=True, help_text='Versión anterior de este documento', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='versiones_posteriores', to='core.consentimientoinformado')),
            ],
            options={
                'verbose_name': 'Consentimiento Informado',
                'verbose_name_plural': 'Consentimientos Informados',
                'ordering': ['-creado_en'],
            },
        ),
        migrations.CreateModel(
            name='PacienteConsentimiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('FIRMADO', 'Firmado'), ('RECHAZADO', 'Rechazado'), ('VENCIDO', 'Vencido')], default='PENDIENTE', max_length=20)),
                ('fecha_presentado', models.DateTimeField(auto_now_add=True)),
                ('fecha_firmado', models.DateTimeField(blank=True, null=True)),
                ('firma_paciente', models.ImageField(blank=True, help_text='Firma digital del paciente', null=True, upload_to='firmas_consentimiento/')),
                ('firma_testigo1', models.ImageField(blank=True, help_text='Firma del primer testigo', null=True, upload_to='firmas_consentimiento/')),
                ('firma_testigo2', models.ImageField(blank=True, help_text='Firma del segundo testigo', null=True, upload_to='firmas_consentimiento/')),
                ('nombre_testigo1', models.CharField(blank=True, max_length=200)),
                ('nombre_testigo2', models.CharField(blank=True, max_length=200)),
                ('notas', models.TextField(blank=True, help_text='Observaciones sobre el proceso de consentimiento')),
                ('cita', models.ForeignKey(blank=True, help_text='Cita asociada al consentimiento', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.cita')),
                ('consentimiento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.consentimientoinformado')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consentimientos', to='core.paciente')),
                ('presentado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consentimientos_presentados', to='core.perfildentista')),
            ],
            options={
                'verbose_name': 'Consentimiento de Paciente',
                'verbose_name_plural': 'Consentimientos de Pacientes',
                'ordering': ['-fecha_presentado'],
            },
        ),
    ]