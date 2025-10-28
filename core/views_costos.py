"""
Vistas para el módulo de Gestión de Costos
Separado del inventario físico para mejor organización
"""
from django.views.generic import ListView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from decimal import Decimal

from core import models
from core.mixins import TenantLoginRequiredMixin, tenant_reverse


class ComprasSinCostosView(TenantLoginRequiredMixin, ListView):
    """
    Lista de compras que ya fueron recibidas pero no tienen costos capturados.
    Esta vista es para el módulo de Gestión de Costos.
    """
    model = models.Compra
    template_name = 'core/compras_sin_costos.html'
    context_object_name = 'compras'
    paginate_by = 15

    def get_queryset(self):
        return models.Compra.objects.filter(
            estado='RECIBIDA',
            costos_capturados=False
        ).prefetch_related('detalles__insumo', 'proveedor').order_by('-fecha_compra')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Compras sin Costos Capturados'
        context['total_pendientes'] = self.get_queryset().count()
        return context


class CapturarCostosCompraView(TenantLoginRequiredMixin, TemplateView):
    """
    Vista para capturar los costos de una compra después de recibirla físicamente.
    Se usa cuando la factura llega después de la mercancía.
    """
    template_name = 'core/capturar_costos_compra.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compra = get_object_or_404(models.Compra, pk=kwargs['pk'])

        # Verificar que la compra esté recibida
        if compra.estado != 'RECIBIDA':
            messages.warning(self.request, 'La compra debe estar recibida antes de capturar costos.')
            return context

        # Verificar que no tenga costos ya capturados
        if compra.costos_capturados:
            messages.info(self.request, 'Esta compra ya tiene costos capturados.')

        context['compra'] = compra
        context['detalles'] = compra.detalles.select_related('insumo').prefetch_related('lotes_generados')

        return context

    def post(self, request, *args, **kwargs):
        compra = get_object_or_404(models.Compra, pk=kwargs['pk'])

        # Validaciones
        if compra.estado != 'RECIBIDA':
            messages.error(request, 'La compra debe estar recibida antes de capturar costos.')
            return redirect(tenant_reverse('core:compras_sin_costos', request=request))

        if compra.costos_capturados:
            messages.warning(request, 'Esta compra ya tiene costos capturados.')
            return redirect(tenant_reverse('core:compras_sin_costos', request=request))

        try:
            with transaction.atomic():
                total_compra = Decimal('0.00')
                detalles_actualizados = 0

                # Capturar precio de cada detalle
                for detalle in compra.detalles.all():
                    precio_str = request.POST.get(f'precio_{detalle.id}')

                    if precio_str:
                        try:
                            precio = Decimal(precio_str)

                            if precio < 0:
                                raise ValueError("El precio no puede ser negativo")

                            # Actualizar precio en el detalle
                            detalle.precio_unitario = precio
                            detalle.save()

                            # Calcular subtotal
                            subtotal = detalle.cantidad * precio
                            total_compra += subtotal

                            # Actualizar costo de los lotes generados por este detalle
                            lotes_actualizados = detalle.lotes_generados.update(costo_unitario=precio)

                            detalles_actualizados += 1

                        except (ValueError, Decimal.InvalidOperation) as e:
                            messages.error(request, f'Error en el precio de {detalle.insumo.nombre}: {str(e)}')
                            return redirect(tenant_reverse('core:capturar_costos_compra', request=request, kwargs={'pk': compra.pk}))

                # Guardar total y marcar como capturado
                compra.total = total_compra
                compra.costos_capturados = True
                compra.save()

                messages.success(
                    request,
                    f'✅ Costos capturados exitosamente. Total: ${total_compra:,.2f} ({detalles_actualizados} insumos)'
                )

                return redirect(tenant_reverse('core:compras_sin_costos', request=request))

        except Exception as e:
            messages.error(request, f'Error al capturar costos: {str(e)}')
            return redirect(tenant_reverse('core:capturar_costos_compra', request=request, kwargs={'pk': compra.pk}))


class ReporteValorInventarioView(TenantLoginRequiredMixin, TemplateView):
    """
    Reporte del valor monetario del inventario actual.
    Calcula el valor basado en el costo de cada lote.
    """
    template_name = 'core/reporte_valor_inventario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        insumos = models.Insumo.objects.filter(stock__gt=0).prefetch_related('lotes')

        datos_insumos = []
        valor_total = Decimal('0.00')
        valor_con_costo = Decimal('0.00')
        cantidad_sin_costo = 0

        for insumo in insumos:
            # Calcular valor de los lotes con costo
            lotes_con_costo = insumo.lotes.filter(cantidad__gt=0, costo_unitario__isnull=False)
            valor_insumo = sum(lote.valor_total for lote in lotes_con_costo)

            # Contar lotes sin costo
            lotes_sin_costo = insumo.lotes.filter(cantidad__gt=0, costo_unitario__isnull=True).count()

            if lotes_sin_costo > 0:
                cantidad_sin_costo += 1

            if insumo.stock > 0:
                datos_insumos.append({
                    'nombre': insumo.nombre,
                    'stock': insumo.stock,
                    'unidad_medida': insumo.unidad_medida,
                    'valor_total': valor_insumo,
                    'tiene_costo': lotes_con_costo.exists(),
                    'lotes_sin_costo': lotes_sin_costo,
                    'proveedor': insumo.proveedor.nombre if insumo.proveedor else 'N/A'
                })

                valor_total += valor_insumo
                if lotes_con_costo.exists():
                    valor_con_costo += valor_insumo

        # Ordenar por valor descendente
        datos_insumos.sort(key=lambda x: x['valor_total'], reverse=True)

        context['datos_insumos'] = datos_insumos
        context['valor_total_inventario'] = valor_total
        context['valor_con_costo'] = valor_con_costo
        context['cantidad_items'] = len(datos_insumos)
        context['cantidad_sin_costo'] = cantidad_sin_costo

        return context
