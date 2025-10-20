# Migración personalizada para sincronizar modelos de permisos con base de datos
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_modulosistema_alter_cita_dentista_and_more'),
    ]

    operations = [
        # 1. Agregar campos faltantes a ModuloSistema
        migrations.AddField(
            model_name='modulosistema',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modulosistema',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # 2. Agregar campos faltantes a SubmenuItem
        migrations.AddField(
            model_name='submenuitem',
            name='url_pattern',
            field=models.CharField(blank=True, help_text='Patrón de URL (ej: /pacientes/)', max_length=200),
        ),
        migrations.AddField(
            model_name='submenuitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submenuitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # 3. Corregir choices de PermisoRol
        migrations.AlterField(
            model_name='permisorol',
            name='nivel_acceso',
            field=models.CharField(
                choices=[
                    ('lectura', 'Solo Lectura'),
                    ('escritura', 'Lectura y Escritura'),
                    ('completo', 'Acceso Completo'),
                ], 
                default='lectura', 
                max_length=20
            ),
        ),
        
        # 4. Agregar campos timestamp a PermisoRol
        migrations.AddField(
            model_name='permisorol',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permisorol',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # 5. Corregir modelo LogAcceso para que coincida con nuestros modelos
        migrations.AddField(
            model_name='logacceso',
            name='modulo_accedido',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='logacceso',
            name='accion_realizada',
            field=models.CharField(max_length=200, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='logacceso',
            name='detalles',
            field=models.TextField(blank=True, default=''),
        ),
        
        # 6. Hacer que usuario y submenu_item sean opcionales en LogAcceso (como en nuestro modelo)
        migrations.AlterField(
            model_name='logacceso',
            name='usuario',
            field=models.ForeignKey(on_delete=models.SET_NULL, to='auth.User', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='logacceso',
            name='submenu_item',
            field=models.ForeignKey(on_delete=models.SET_NULL, to='core.submenuitem', null=True, blank=True),
        ),
        
        # 7. Renombrar fecha_acceso para mantener consistencia
        migrations.AlterField(
            model_name='logacceso',
            name='ip_address',
            field=models.CharField(max_length=45, blank=True),
        ),
        
        # 8. Asegurarnos de que las db_table están correctamente configuradas
        migrations.AlterModelTable(
            name='modulosistema',
            table='core_modulosistema',
        ),
        migrations.AlterModelTable(
            name='submenuitem',
            table='core_submenuitem',
        ),
        migrations.AlterModelTable(
            name='permisorol',
            table='core_permisorol',
        ),
        migrations.AlterModelTable(
            name='logacceso',
            table='core_logacceso',
        ),
    ]
