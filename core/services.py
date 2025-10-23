"""
Servicios de negocio para el core de la aplicación.
Esta capa separa la lógica de negocio de los modelos y vistas.
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from . import models


class PacienteService:
    """Servicios relacionados con la gestión de pacientes"""
    
    @staticmethod
    def actualizar_saldo_global(paciente):
        """
        Actualiza el saldo global del paciente calculándolo desde cero.
        Este método debe ser llamado después de cambios en citas o pagos.
        """
        with transaction.atomic():
            # Calcular total de cargos de citas atendidas/completadas
            # Como servicios_realizados ahora es @property, iteramos las citas
            citas_facturables = models.Cita.objects.filter(
                paciente=paciente,
                estado__in=['ATN', 'COM']
            )

            total_cargos = Decimal('0.00')
            for cita in citas_facturables:
                total_cargos += Decimal(str(cita.costo_real))

            # Calcular total de pagos
            total_pagos = paciente.pagos.aggregate(
                total=Sum('monto')
            )['total'] or Decimal('0.00')

            # Actualizar saldo
            paciente.saldo_global = total_cargos - total_pagos
            paciente.save(update_fields=['saldo_global'])

            return paciente.saldo_global


class CitaService:
    """Servicios relacionados con la gestión de citas"""
    
    @staticmethod
    def validar_disponibilidad_unidad(unidad_dental, fecha_hora, duracion_minutos, cita_excluir=None):
        """
        Valida que una unidad dental esté disponible en el horario solicitado.
        
        Args:
            unidad_dental: Instancia de UnidadDental
            fecha_hora: datetime de inicio de la cita
            duracion_minutos: duración estimada en minutos
            cita_excluir: Cita a excluir de la validación (para edición)
            
        Returns:
            bool: True si está disponible, False si hay conflicto
        """
        from datetime import timedelta
        
        fecha_fin = fecha_hora + timedelta(minutes=duracion_minutos)
        
        # Buscar citas conflictivas en la misma unidad
        citas_conflictivas = models.Cita.objects.filter(
            unidad_dental=unidad_dental,
            fecha_hora__lt=fecha_fin,
            fecha_hora__gte=fecha_hora - timedelta(minutes=30),  # Buffer de 30 min
            estado__in=['PRO', 'CON', 'ATN']  # Estados activos
        )
        
        if cita_excluir:
            citas_conflictivas = citas_conflictivas.exclude(pk=cita_excluir.pk)
            
        return not citas_conflictivas.exists()
    
    @staticmethod
    def completar_cita(cita, servicios_realizados=None, insumos_consumidos=None):
        """
        Completa una cita y actualiza el inventario automáticamente.
        
        Args:
            cita: Instancia de Cita
            servicios_realizados: Lista de servicios realmente prestados
            insumos_consumidos: Dict con insumos consumidos {insumo_id: cantidad}
        """
        with transaction.atomic():
            # Actualizar servicios realizados
            if servicios_realizados:
                cita.servicios_realizados.set(servicios_realizados)
            
            # Cambiar estado a completada
            cita.estado = 'COM'
            cita.save()
            
            # Descontar insumos del inventario
            if insumos_consumidos:
                InventarioService.descontar_insumos(insumos_consumidos)
            
            # Actualizar saldo del paciente
            PacienteService.actualizar_saldo_global(cita.paciente)


class InventarioService:
    """Servicios relacionados con la gestión de inventario"""
    
    @staticmethod
    def descontar_insumos(insumos_consumidos):
        """
        Descuenta insumos del inventario por consumo en servicios.
        
        Args:
            insumos_consumidos: Dict {insumo_id: cantidad_consumida}
        """
        with transaction.atomic():
            for insumo_id, cantidad in insumos_consumidos.items():
                try:
                    insumo = models.Insumo.objects.get(pk=insumo_id)
                    
                    # Si requiere seguimiento por lote
                    if insumo.requiere_lote_caducidad:
                        # Consumir de los lotes más antiguos primero (FIFO)
                        lotes = insumo.lotes.filter(cantidad__gt=0).order_by('fecha_caducidad')
                        
                        cantidad_restante = cantidad
                        for lote in lotes:
                            if cantidad_restante <= 0:
                                break
                                
                            if lote.cantidad >= cantidad_restante:
                                lote.cantidad -= cantidad_restante
                                cantidad_restante = 0
                            else:
                                cantidad_restante -= lote.cantidad
                                lote.cantidad = 0
                            
                            lote.save()
                    
                    # Actualizar stock total
                    insumo.actualizar_stock_total()
                    
                except models.Insumo.DoesNotExist:
                    continue  # Insumo no encontrado, continuar con el siguiente
    
    @staticmethod
    def alertas_stock_bajo():
        """
        Retorna lista de insumos con stock por debajo del mínimo.
        """
        return models.Insumo.objects.filter(
            stock__lte=models.F('stock_minimo')
        ).select_related('proveedor')
    
    @staticmethod 
    def alertas_caducidad(dias=30):
        """
        Retorna lotes próximos a caducar en los próximos N días.
        """
        from datetime import date, timedelta
        
        fecha_limite = date.today() + timedelta(days=dias)
        
        return models.LoteInsumo.objects.filter(
            fecha_caducidad__lte=fecha_limite,
            cantidad__gt=0
        ).select_related('insumo', 'unidad_dental').order_by('fecha_caducidad')


class PagoService:
    """Servicios relacionados con la gestión de pagos"""
    
    @staticmethod
    def registrar_pago(paciente, monto, metodo_pago='Efectivo', cita=None):
        """
        Registra un nuevo pago y actualiza automáticamente el saldo del paciente.
        """
        with transaction.atomic():
            pago = models.Pago.objects.create(
                paciente=paciente,
                cita=cita,
                monto=monto,
                metodo_pago=metodo_pago
            )
            
            # Actualizar saldo del paciente
            PacienteService.actualizar_saldo_global(paciente)
            
            return pago


class SatMappingService:
    """
    Servicio para mapeo automático de métodos de pago locales a códigos SAT.
    Simplifica el proceso de facturación electrónica.
    """
    
    # Mapeo de métodos de pago locales a códigos SAT de Forma de Pago
    FORMA_PAGO_MAPPING = {
        'Efectivo': '01',           # Efectivo
        'Cheque': '02',             # Cheque nominativo
        'Transferencia': '03',       # Transferencia electrónica de fondos
        'Tarjeta de crédito': '04', # Tarjeta de crédito
        'Tarjeta de débito': '28',  # Tarjeta de débito
        'Monedero electrónico': '05', # Monedero electrónico
        'Dinero electrónico': '06', # Dinero electrónico
        'Vales de despensa': '08',  # Vales de despensa
        'Dación en pago': '12',     # Dación en pago
        'Pago por subrogación': '13', # Pago por subrogación
        'Pago por consignación': '14', # Pago por consignación
        'Condonación': '15',        # Condonación
        'Compensación': '17',       # Compensación
        'Novación': '23',          # Novación
        'Confusión': '24',         # Confusión
        'Remisión de deuda': '25', # Remisión de deuda
        'Prescripción o caducidad': '26', # Prescripción o caducidad
        'A satisfacción del acreedor': '27', # A satisfacción del acreedor
        'Tarjeta de servicios': '29', # Tarjeta de servicios
        'Por definir': '99',       # Por definir
    }
    
    # Método de pago por defecto (PUE = Pago en una sola exhibición)
    DEFAULT_METODO_PAGO = 'PUE'  # Código más común para pagos inmediatos
    
    @staticmethod
    def mapear_forma_pago(metodo_pago_local):
        """
        Mapea un método de pago local a su código SAT de Forma de Pago correspondiente.
        
        Args:
            metodo_pago_local (str): Método de pago en el sistema local
            
        Returns:
            SatFormaPago|None: Instancia del modelo SAT correspondiente o None si no se encuentra
        """
        # Normalizar el método de pago (eliminar espacios y convertir a título)
        metodo_normalizado = metodo_pago_local.strip().title() if metodo_pago_local else ''
        
        # Buscar en el mapeo
        codigo_sat = SatMappingService.FORMA_PAGO_MAPPING.get(metodo_normalizado)
        
        if codigo_sat:
            return models.SatFormaPago.objects.filter(codigo=codigo_sat, activo=True).first()
        
        # Si no encuentra mapeo exacto, intentar mapeos alternativos
        metodo_lower = metodo_normalizado.lower()
        
        if 'efectivo' in metodo_lower or 'cash' in metodo_lower:
            return models.SatFormaPago.objects.filter(codigo='01', activo=True).first()
        elif 'tarjeta' in metodo_lower and ('crédito' in metodo_lower or 'credito' in metodo_lower):
            return models.SatFormaPago.objects.filter(codigo='04', activo=True).first()
        elif 'tarjeta' in metodo_lower and ('débito' in metodo_lower or 'debito' in metodo_lower):
            return models.SatFormaPago.objects.filter(codigo='28', activo=True).first()
        elif 'tarjeta' in metodo_lower:  # Cualquier tarjeta sin especificar → crédito por defecto
            return models.SatFormaPago.objects.filter(codigo='04', activo=True).first()
        elif 'transferencia' in metodo_lower or 'spei' in metodo_lower:
            return models.SatFormaPago.objects.filter(codigo='03', activo=True).first()
        elif 'cheque' in metodo_lower:
            return models.SatFormaPago.objects.filter(codigo='02', activo=True).first()
        
        # Si no encuentra nada, devolver None
        return None
    
    @staticmethod
    def mapear_metodo_pago(metodo_pago_local=None):
        """
        Obtiene el método de pago SAT por defecto (PUE - Pago en una sola exhibición).
        
        Args:
            metodo_pago_local (str, optional): Método de pago local (por ahora no se usa, siempre devuelve PUE)
            
        Returns:
            SatMetodoPago|None: Instancia del modelo SAT correspondiente o None si no se encuentra
        """
        # Por simplicidad, siempre devolver PUE (Pago en una sola exhibición)
        # En el futuro se puede expandir para mapear PPD (pagos diferidos) según el contexto
        return models.SatMetodoPago.objects.filter(
            codigo=SatMappingService.DEFAULT_METODO_PAGO, 
            activo=True
        ).first()
    
    @staticmethod
    def aplicar_mapeo_automatico(pago):
        """
        Aplica el mapeo automático SAT a un pago existente.
        
        Args:
            pago (Pago): Instancia del modelo Pago
            
        Returns:
            bool: True si se aplicó el mapeo exitosamente, False en caso contrario
        """
        # Solo aplicar si no tiene ya valores SAT asignados
        if pago.forma_pago_sat or pago.metodo_sat:
            return False
        
        # Mapear forma de pago
        forma_sat = SatMappingService.mapear_forma_pago(pago.metodo_pago)
        
        # Mapear método de pago
        metodo_sat = SatMappingService.mapear_metodo_pago()
        
        # Aplicar si se encontraron ambos
        if forma_sat and metodo_sat:
            pago.forma_pago_sat = forma_sat
            pago.metodo_sat = metodo_sat
            
            # Solo guardar si el pago ya tiene ID (está en la BD)
            if pago.pk:
                pago.save(update_fields=['forma_pago_sat', 'metodo_sat'])
            
            return True
        
        return False
    
    @staticmethod
    def obtener_mapeos_disponibles():
        """
        Obtiene un diccionario con todos los mapeos disponibles para mostrar en UI.
        
        Returns:
            dict: Diccionario con métodos locales como llaves y códigos SAT como valores
        """
        return SatMappingService.FORMA_PAGO_MAPPING.copy()
    
    @staticmethod
    def sincronizar_pagos_existentes():
        """
        Aplica el mapeo automático a todos los pagos que no tienen valores SAT asignados.
        Útil para migrar datos existentes.
        
        Returns:
            tuple: (pagos_actualizados, total_pagos_procesados)
        """
        pagos_sin_sat = models.Pago.objects.filter(
            forma_pago_sat__isnull=True,
            metodo_sat__isnull=True
        )
        
        actualizados = 0
        total = pagos_sin_sat.count()
        
        for pago in pagos_sin_sat:
            if SatMappingService.aplicar_mapeo_automatico(pago):
                actualizados += 1
        
        return actualizados, total
