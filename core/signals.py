from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Pago, Cita, LoteInsumo, Insumo
from . import services

@receiver([post_save, post_delete], sender=LoteInsumo)
def actualizar_stock_insumo(sender, instance, **kwargs):
    """
    Esta señal se activa cada vez que un LoteInsumo se guarda o elimina.
    Llama al método del modelo Insumo para recalcular su stock total.
    """
    instance.insumo.actualizar_stock_total()

@receiver([post_save, post_delete], sender=Pago)
def actualizar_saldo_paciente_pago(sender, instance, **kwargs):
    """
    Actualiza el saldo del paciente cuando se crea, modifica o elimina un pago.
    """
    if instance.paciente:
        services.PacienteService.actualizar_saldo_global(instance.paciente)

@receiver(post_save, sender=Cita)
def actualizar_saldo_paciente_cita(sender, instance, created, **kwargs):
    """
    Actualiza el saldo del paciente cuando se modifica una cita,
    especialmente cuando cambia a estado 'COM' (Completada).
    """
    if instance.estado in ['ATN', 'COM'] and instance.paciente_id:
        services.PacienteService.actualizar_saldo_global(instance.paciente)
