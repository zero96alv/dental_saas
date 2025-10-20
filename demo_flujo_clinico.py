#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMOSTRACIÓN DEL FLUJO CLÍNICO COMPLETO
=====================================

Este script demuestra el flujo clínico exacto que describiste:

1. Paciente llega con dolor en diente 16
2. Se registra la consulta en historial clínico
3. Se diagnostica caries en diente 16 
4. Se actualiza odontograma: Sano → Cariado
5. Se programa tratamiento
6. Se realiza obturación en cita
7. Se actualiza odontograma: Cariado → Obturado
8. Seguimiento completo con fechas y dentista responsable

Ejecutar desde la raíz del proyecto:
python demo_flujo_clinico.py
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from django.utils import timezone

# Configurar Django
sys.path.append('C:\\desarrollo\\dental_saas')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_saas.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from tenants.models import Clinica
from django_tenants.utils import schema_context

User = get_user_model()

class DemostradorFlujoClinical:
    def __init__(self):
        print("=" * 70)
        print("DEMOSTRACIÓN DEL FLUJO CLÍNICO COMPLETO")
        print("=" * 70)
        print(f"Inicio de demostración: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Configurar tenant demo
        try:
            self.tenant = Clinica.objects.get(schema_name='demo')
            print(f"🏥 Usando tenant: {self.tenant.nombre} (schema: {self.tenant.schema_name})")
        except Clinica.DoesNotExist:
            print("❌ Tenant 'demo' no encontrado")
            self.tenant = None
            return
            
        self.paciente = None
        self.dentista = None
        self.cita = None
        self.diagnosticos = {}

    def preparar_datos_base(self):
        """Prepara datos básicos necesarios para la demostración"""
        print("\\n📋 PASO 0: PREPARACIÓN DE DATOS BASE")
        print("-" * 40)
        
        if not self.tenant:
            print("❌ Sin tenant disponible")
            return False
            
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import (
                    Paciente, PerfilDentista, Diagnostico, Servicio, 
                    UnidadDental, Especialidad
                )
                
                # Buscar o crear paciente de prueba
                self.paciente, created = Paciente.objects.get_or_create(
                    nombre='Juan Carlos',
                    apellido='Pérez González',
                    defaults={
                        'email': 'juan.perez@demo.com',
                        'telefono': '555-0123',
                        'fecha_nacimiento': date(1985, 5, 15),
                        'calle': 'Av. Revolución 123',
                        'colonia': 'Centro',
                        'municipio': 'Guadalajara',
                        'estado': 'Jalisco',
                        'codigo_postal': '44100'
                    }
                )
                
                if created:
                    print(f"✓ Paciente creado: {self.paciente}")
                else:
                    print(f"✓ Paciente existente: {self.paciente}")
                
                # Buscar o crear dentista
                try:
                    user_dentista = User.objects.filter(
                        username__icontains='demo'
                    ).first()
                    
                    if user_dentista:
                        self.dentista, created = PerfilDentista.objects.get_or_create(
                            usuario=user_dentista,
                            defaults={
                                'nombre': 'Dr. María Elena',
                                'apellido': 'Rodríguez Silva',
                                'telefono': '555-0456',
                                'cedula_profesional': '12345678'
                            }
                        )
                        print(f"✓ Dentista: {self.dentista}")
                    else:
                        print("⚠️ No se encontró usuario demo - buscando primer dentista disponible")
                        self.dentista = PerfilDentista.objects.first()
                        
                        if not self.dentista:
                            # Crear un usuario y dentista de prueba
                            print("⚠️ No existe ningún dentista - creando dentista de prueba")
                            user_prueba = User.objects.create_user(
                                username='dentista_demo',
                                email='dentista@demo.com',
                                password='demo123'
                            )
                            self.dentista = PerfilDentista.objects.create(
                                usuario=user_prueba,
                                nombre='Dr. María Elena',
                                apellido='Rodríguez Silva',
                                telefono='555-0456',
                                cedula_profesional='12345678'
                            )
                            print(f"✓ Dentista de prueba creado: {self.dentista}")
                        else:
                            print(f"✓ Usando dentista existente: {self.dentista}")
                        
                except Exception as e:
                    print(f"⚠️ Error con dentista: {e}")
                    self.dentista = PerfilDentista.objects.first()
                    
                    if not self.dentista:
                        print("❌ No se pudo obtener o crear un dentista")
                        return False
                
                # Crear o verificar diagnósticos básicos
                diagnosticos_base = [
                    ('Sano', '#4CAF50', '<circle fill="white" stroke="green" stroke-width="2" cx="50%" cy="50%" r="40%"/>'),
                    ('Cariado', '#FF5722', '<path fill="red" d="M20,20 L80,80 M80,20 L20,80"/>'),
                    ('Obturado', '#2196F3', '<rect fill="blue" x="30%" y="30%" width="40%" height="40%"/>'),
                    ('Ausente', '#9E9E9E', '<line stroke="gray" stroke-width="4" x1="20%" y1="50%" x2="80%" y2="50%"/>'),
                    ('Corona', '#FFD700', '<circle fill="gold" stroke="orange" stroke-width="2" cx="50%" cy="50%" r="40%"/>'),
                ]
                
                for nombre, color, icono in diagnosticos_base:
                    diagnostico, created = Diagnostico.objects.get_or_create(
                        nombre=nombre,
                        defaults={
                            'color_hex': color,
                            'icono_svg': icono
                        }
                    )
                    self.diagnosticos[nombre] = diagnostico
                    if created:
                        print(f"✓ Diagnóstico creado: {nombre}")
                
                # Verificar unidad dental
                if not UnidadDental.objects.exists():
                    UnidadDental.objects.create(
                        nombre='Unidad 1',
                        descripcion='Consultorio Principal'
                    )
                    print("✓ Unidad dental creada")
                
                # Verificar servicios
                if not Servicio.objects.exists():
                    especialidad, _ = Especialidad.objects.get_or_create(
                        nombre='Odontología General'
                    )
                    
                    servicios_base = [
                        ('Consulta General', 500.00, 30),
                        ('Obturación Simple', 800.00, 45),
                        ('Obturación Compuesta', 1200.00, 60),
                        ('Limpieza Dental', 600.00, 45),
                    ]
                    
                    for nombre, precio, duracion in servicios_base:
                        Servicio.objects.create(
                            nombre=nombre,
                            precio=precio,
                            duracion_minutos=duracion,
                            especialidad=especialidad,
                            activo=True
                        )
                    print("✓ Servicios base creados")
                
                print("✅ Datos base preparados correctamente")
                return True
                
        except Exception as e:
            print(f"❌ Error preparando datos base: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def paso_1_consulta_inicial(self):
        """Paso 1: Paciente llega con dolor, se registra consulta"""
        print("\\n🩺 PASO 1: CONSULTA INICIAL")
        print("-" * 30)
        
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import crear_entrada_historial_clinico
                
                # Crear entrada de consulta inicial
                entrada_consulta = crear_entrada_historial_clinico(
                    paciente=self.paciente,
                    tipo_registro='CONSULTA',
                    descripcion='Paciente refiere dolor intenso en zona posterior superior derecha. '
                               'Dolor punzante que aumenta con estímulos fríos y calientes. '
                               'Inicio hace 3 días. Escala de dolor: 7/10.',
                    dentista=self.dentista
                )
                
                print(f"✓ Consulta registrada: {entrada_consulta.fecha_evento.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Tipo: {entrada_consulta.get_tipo_registro_display()}")
                print(f"   Registrado por: {entrada_consulta.registrado_por}")
                print(f"   Descripción: {entrada_consulta.descripcion_evento[:100]}...")
                
                return entrada_consulta
                
        except Exception as e:
            print(f"❌ Error en consulta inicial: {e}")
            return None
    
    def paso_2_diagnostico(self):
        """Paso 2: Examen clínico y diagnóstico"""
        print("\\n🔍 PASO 2: EXAMEN Y DIAGNÓSTICO")
        print("-" * 35)
        
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import crear_entrada_historial_clinico, actualizar_estado_diente
                from core.models import Cita, UnidadDental
                
                # Crear cita para el diagnóstico
                unidad = UnidadDental.objects.first()
                self.cita = Cita.objects.create(
                    paciente=self.paciente,
                    dentista=self.dentista,
                    unidad_dental=unidad,
                    fecha_hora=timezone.now(),
                    motivo='Dolor dental - evaluación diente 16',
                    estado='ATN',  # Atendida
                )
                
                print(f"✓ Cita creada: ID {self.cita.id}")
                
                # Registrar diagnóstico en historial
                entrada_diagnostico = crear_entrada_historial_clinico(
                    paciente=self.paciente,
                    tipo_registro='DIAGNOSTICO',
                    descripcion='Examen clínico diente 16: Caries profunda oclusal con compromiso '
                               'pulpar. Prueba de frío: dolor intenso y prolongado. '
                               'Radiografía: radiolucidez extensa en cámara pulpar.',
                    dentista=self.dentista,
                    cita=self.cita
                )
                
                print(f"✓ Diagnóstico registrado: {entrada_diagnostico.fecha_evento.strftime('%d/%m/%Y %H:%M')}")
                
                # Actualizar odontograma: de Sano a Cariado
                estado_actualizado, historial_creado = actualizar_estado_diente(
                    paciente=self.paciente,
                    numero_diente=16,
                    diagnostico_nuevo=self.diagnosticos['Cariado'],
                    cita=self.cita,
                    tratamiento_descripcion='Diagnóstico: Caries profunda oclusal con compromiso pulpar',
                    observaciones='Dolor intenso, requiere tratamiento urgente'
                )
                
                print(f"✓ Odontograma actualizado: Diente 16 → {estado_actualizado.diagnostico.nombre}")
                if historial_creado:
                    print("✓ Historial dental registrado")
                
                return entrada_diagnostico, estado_actualizado
                
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def paso_3_planificacion(self):
        """Paso 3: Planificación del tratamiento"""
        print("\\n📋 PASO 3: PLANIFICACIÓN DEL TRATAMIENTO")
        print("-" * 42)
        
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import crear_entrada_historial_clinico, Servicio
                
                # Obtener servicios
                obturacion = Servicio.objects.filter(nombre__icontains='Obturación').first()
                
                if obturacion:
                    # Asignar servicio planeado a la cita
                    self.cita.servicios_planeados.add(obturacion)
                    
                # Registrar plan de tratamiento
                entrada_plan = crear_entrada_historial_clinico(
                    paciente=self.paciente,
                    tipo_registro='OBSERVACION',
                    descripcion=f'Plan de tratamiento diente 16: '
                               f'1. Anestesia local infiltrativa. '
                               f'2. Remoción de tejido cariado. '
                               f'3. Protección pulpar si es necesario. '
                               f'4. Obturación con resina compuesta. '
                               f'5. Control en 1 semana. '
                               f'Servicio: {obturacion.nombre if obturacion else "Obturación"} - '
                               f'${obturacion.precio if obturacion else "800.00"}',
                    dentista=self.dentista,
                    cita=self.cita
                )
                
                print(f"✓ Plan registrado: {entrada_plan.fecha_evento.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Servicio planeado: {obturacion.nombre if obturacion else 'Obturación'}")
                print(f"   Costo estimado: ${self.cita.costo_estimado}")
                
                return entrada_plan
                
        except Exception as e:
            print(f"❌ Error en planificación: {e}")
            return None
    
    def paso_4_tratamiento(self):
        """Paso 4: Realizar tratamiento y actualizar estado"""
        print("\\n🦷 PASO 4: EJECUCIÓN DEL TRATAMIENTO")
        print("-" * 38)
        
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import procesar_tratamiento_cita, Servicio
                
                # Obtener servicio realizado
                obturacion = Servicio.objects.filter(nombre__icontains='Obturación').first()
                servicios_ids = [obturacion.id] if obturacion else None
                
                # Procesar tratamiento completo
                tratamiento, estados_actualizados, cambios_realizados = procesar_tratamiento_cita(
                    cita=self.cita,
                    dientes_tratados_str='16',
                    descripcion_tratamiento='Obturación con resina compuesta en diente 16. '
                                           'Anestesia infiltrativa 2ml lidocaína 2% con epinefrina. '
                                           'Remoción completa de tejido cariado. '
                                           'Grabado ácido, primer y adhesivo. '
                                           'Resina compuesta fotopolimerizable color A2. '
                                           'Pulido y ajuste oclusal. '
                                           'Paciente tolera bien el procedimiento.',
                    estado_inicial_desc='Caries profunda oclusal con compromiso pulpar, dolor intenso',
                    estado_final_desc='Obturación terminada, sellado hermético, sin dolor',
                    diagnostico_final=self.diagnosticos['Obturado'],
                    servicios_ids=servicios_ids,
                    trabajo_pendiente='Control en 7 días para evaluar sintomatología post-operatoria',
                    requiere_seguimiento=True,
                    fecha_seguimiento=date.today() + timedelta(days=7)
                )
                
                # Marcar cita como completada
                self.cita.estado = 'COM'
                if servicios_ids:
                    self.cita.servicios_realizados.set(servicios_ids)
                self.cita.save()
                
                print(f"✓ Tratamiento registrado: ID {tratamiento.id}")
                print(f"   Fecha: {tratamiento.fecha_registro.strftime('%d/%m/%Y %H:%M')}")
                print(f"   Dientes tratados: {tratamiento.dientes_formateados}")
                print(f"   Cambios en odontograma: {cambios_realizados}")
                print(f"   Estado cita: {self.cita.get_estado_display()}")
                print(f"   Costo real: ${self.cita.costo_real}")
                print(f"   Seguimiento programado: {tratamiento.fecha_seguimiento_sugerida}")
                
                return tratamiento
                
        except Exception as e:
            print(f"❌ Error en tratamiento: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def paso_5_verificacion(self):
        """Paso 5: Verificar el flujo completo"""
        print("\\n📊 PASO 5: VERIFICACIÓN DEL FLUJO COMPLETO")
        print("-" * 46)
        
        try:
            with schema_context(self.tenant.schema_name):
                from core.models import (
                    HistorialClinico, HistorialEstadoDiente, EstadoDiente,
                    obtener_historial_diente, obtener_odontograma_completo
                )
                
                print("🔍 RESUMEN DEL HISTORIAL CLÍNICO:")
                historial = HistorialClinico.objects.filter(
                    paciente=self.paciente
                ).order_by('fecha_evento')
                
                for i, entrada in enumerate(historial, 1):
                    print(f"   {i}. {entrada.fecha_evento.strftime('%d/%m %H:%M')} - "
                          f"{entrada.get_tipo_registro_display()}")
                    print(f"      {entrada.descripcion_evento[:80]}...")
                    if entrada.cita:
                        print(f"      Cita: {entrada.cita.id}")
                    print()
                
                print("🦷 HISTORIAL DENTAL DIENTE 16:")
                historial_diente = obtener_historial_diente(self.paciente, 16)
                
                for i, cambio in enumerate(historial_diente, 1):
                    anterior = cambio.diagnostico_anterior.nombre if cambio.diagnostico_anterior else "Inicial"
                    nuevo = cambio.diagnostico_nuevo.nombre
                    print(f"   {i}. {cambio.fecha_cambio.strftime('%d/%m %H:%M')} - "
                          f"{anterior} → {nuevo}")
                    print(f"      Tratamiento: {cambio.tratamiento_realizado[:60]}...")
                    print(f"      Dentista: {cambio.dentista}")
                    if cambio.observaciones:
                        print(f"      Obs: {cambio.observaciones}")
                    print()
                
                print("🗺️ ODONTOGRAMA ACTUAL:")
                odontograma = obtener_odontograma_completo(self.paciente)
                
                if 16 in odontograma:
                    info_diente = odontograma[16]
                    print(f"   Diente 16: {info_diente['diagnostico']}")
                    print(f"   Color: {info_diente['color']}")
                    print(f"   Última actualización: {info_diente['actualizado_en']}")
                else:
                    print("   Diente 16: Sin información registrada")
                
                print()
                print("📈 ESTADÍSTICAS DEL FLUJO:")
                print(f"   - Total entradas historial clínico: {historial.count()}")
                print(f"   - Total cambios dentales: {historial_diente.count()}")
                print(f"   - Citas del paciente: 1")
                print(f"   - Tratamientos realizados: {self.cita.tratamientos_realizados.count()}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ejecutar_demostracion(self):
        """Ejecuta la demostración completa del flujo clínico"""
        try:
            # Preparar datos
            if not self.preparar_datos_base():
                return False
            
            # Ejecutar flujo paso a paso
            with transaction.atomic():
                
                # Paso 1: Consulta inicial
                consulta = self.paso_1_consulta_inicial()
                if not consulta:
                    return False
                
                # Paso 2: Diagnóstico y actualización odontograma
                diagnostico, estado = self.paso_2_diagnostico()
                if not diagnostico:
                    return False
                
                # Paso 3: Planificación
                plan = self.paso_3_planificacion()
                if not plan:
                    return False
                
                # Paso 4: Tratamiento
                tratamiento = self.paso_4_tratamiento()
                if not tratamiento:
                    return False
                
                # Paso 5: Verificación
                if not self.paso_5_verificacion():
                    return False
            
            print("\\n" + "=" * 70)
            print("✅ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 70)
            print()
            print("🎉 FLUJO CLÍNICO IMPLEMENTADO CORRECTAMENTE:")
            print("   ✓ Paciente llegó con dolor en diente 16")
            print("   ✓ Se registró consulta inicial en historial clínico")
            print("   ✓ Se diagnosticó caries profunda")
            print("   ✓ Se actualizó odontograma: Sano → Cariado")
            print("   ✓ Se planificó tratamiento")
            print("   ✓ Se realizó obturación")
            print("   ✓ Se actualizó odontograma: Cariado → Obturado")
            print("   ✓ Se programó seguimiento")
            print("   ✓ Todas las acciones tienen fecha y dentista responsable")
            print()
            print("📋 DATOS GENERADOS:")
            print(f"   - Paciente: {self.paciente}")
            print(f"   - Dentista: {self.dentista}")
            print(f"   - Cita ID: {self.cita.id if self.cita else 'N/A'}")
            print(f"   - Fecha demostración: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            print()
            return True
            
        except Exception as e:
            print(f"\\n❌ ERROR EN LA DEMOSTRACIÓN: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Función principal"""
    try:
        demo = DemostradorFlujoClinical()
        demo.ejecutar_demostracion()
        
    except Exception as e:
        print(f"❌ Error fatal en demostración: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()