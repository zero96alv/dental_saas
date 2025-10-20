# Generated manually to fix HistorialClinico paciente field

from django.db import migrations, models
import django.db.models.deletion


def clean_historial_null_patients(apps, schema_editor):
    """
    Eliminar registros de HistorialClinico que tengan paciente_id NULL
    """
    db_alias = schema_editor.connection.alias
    with schema_editor.connection.cursor() as cursor:
        # Primero verificamos si hay registros con paciente_id NULL
        cursor.execute("SELECT COUNT(*) FROM core_historialclinico WHERE paciente_id IS NULL")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"Eliminando {null_count} registros de HistorialClinico con paciente_id NULL...")
            # Eliminar registros huérfanos
            cursor.execute("DELETE FROM core_historialclinico WHERE paciente_id IS NULL")
            print(f"Se eliminaron {null_count} registros huérfanos.")


def reverse_clean_historial(apps, schema_editor):
    """
    No es posible restaurar datos eliminados
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', 'rename_cliente_to_paciente'),
    ]

    operations = [
        # Primero limpiar datos NULL
        migrations.RunPython(
            clean_historial_null_patients,
            reverse_clean_historial
        ),
        
        # Luego cambiar el campo a non-nullable
        migrations.AlterField(
            model_name='historialclinico',
            name='paciente',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, 
                related_name='historial_clinico', 
                to='core.paciente'
            ),
        ),
    ]
