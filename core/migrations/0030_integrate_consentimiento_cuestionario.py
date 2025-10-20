# Generated manually for integrating ConsentimientoInformado with CuestionarioCompletado

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_add_consentimiento_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuestionariocompletado',
            name='consentimiento_requerido',
            field=models.BooleanField(default=True, help_text='¿Se requiere consentimiento informado después del cuestionario?'),
        ),
        migrations.AddField(
            model_name='cuestionariocompletado',
            name='consentimiento_presentado',
            field=models.ForeignKey(blank=True, help_text='Consentimiento informado presentado al paciente', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cuestionarios_relacionados', to='core.pacienteconsentimiento'),
        ),
    ]