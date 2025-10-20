# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_residuos_manifiesto_pdf_and_more'),
    ]

    operations = [
        # Renombrar campo en Cita
        migrations.RenameField(
            model_name='cita',
            old_name='cliente',
            new_name='paciente',
        ),
        
        # Renombrar campo en HistorialClinico
        migrations.RenameField(
            model_name='historialclinico',
            old_name='cliente',
            new_name='paciente',
        ),
        
        # Renombrar campo en EstadoDiente
        migrations.RenameField(
            model_name='estadodiente',
            old_name='cliente',
            new_name='paciente',
        ),
    ]
