from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LoteInsumo

@receiver([post_save, post_delete], sender=LoteInsumo)
def actualizar_stock_insumo(sender, instance, **kwargs):
    """
    Esta señal se activa cada vez que un LoteInsumo se guarda o elimina.
    Llama al método del modelo Insumo para recalcular su stock total.
    """
    instance.insumo.actualizar_stock_total()