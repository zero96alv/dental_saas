/**
 * ESCALAS DE DOLOR Y HISTORIAL CLÍNICO INTERACTIVO
 * Funcionalidades para escalas de dolor visuales y mejoras del historial
 */

// Variables globales
let dolorSeleccionado = null;
let caraSeleccionada = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    inicializarEscalasDolor();
    inicializarAntecedentesFamiliares();
    inicializarMalosHabitos();
    inicializarSignosVitales();
});

/**
 * ESCALAS DE DOLOR
 */
function inicializarEscalasDolor() {
    // Inicializar escala numérica 0-10
    const numerosEscala = document.querySelectorAll('.dolor-number');
    numerosEscala.forEach(numero => {
        numero.addEventListener('click', function() {
            seleccionarDolor(this);
        });
    });

    // Inicializar escala de caras Wong Baker
    const carasDolor = document.querySelectorAll('.cara-dolor');
    carasDolor.forEach(cara => {
        cara.addEventListener('click', function() {
            seleccionarCara(this);
        });
    });
}

function seleccionarDolor(elemento) {
    // Remover selección anterior
    document.querySelectorAll('.dolor-number').forEach(n => {
        n.classList.remove('selected', 'dolor-selected');
    });

    // Agregar selección al elemento clickeado
    elemento.classList.add('selected', 'dolor-selected');
    
    // Obtener el valor seleccionado
    dolorSeleccionado = parseInt(elemento.dataset.valor);
    
    // Actualizar campo oculto si existe
    const campoOculto = document.getElementById('dolor_numerico_value');
    if (campoOculto) {
        campoOculto.value = dolorSeleccionado;
    }
    
    // Mostrar alerta según el nivel de dolor
    mostrarAlertaDolor(dolorSeleccionado);
    
    // Sincronizar con escala de caras si es posible
    sincronizarCaras(dolorSeleccionado);
    
    console.log('Dolor seleccionado:', dolorSeleccionado);
}

function seleccionarCara(elemento) {
    // Remover selección anterior
    document.querySelectorAll('.cara-dolor').forEach(c => {
        c.classList.remove('selected');
    });

    // Agregar selección al elemento clickeado
    elemento.classList.add('selected');
    
    // Obtener el valor seleccionado
    caraSeleccionada = parseInt(elemento.dataset.valor);
    
    // Actualizar campo oculto si existe
    const campoOculto = document.getElementById('dolor_caras_value');
    if (campoOculto) {
        campoOculto.value = caraSeleccionada;
    }
    
    // Sincronizar con escala numérica
    sincronizarNumeros(caraSeleccionada);
    
    console.log('Cara seleccionada:', caraSeleccionada);
}

function sincronizarCaras(valorNumerico) {
    // Mapear valores numéricos a caras Wong Baker
    const mapeoCaras = {
        0: 0, 1: 0,
        2: 2, 3: 2,
        4: 4, 5: 4,
        6: 6, 7: 6,
        8: 8, 9: 8,
        10: 10
    };
    
    const valorCara = mapeoCaras[valorNumerico];
    const caraElement = document.querySelector(`.cara-dolor[data-valor="${valorCara}"]`);
    
    if (caraElement) {
        document.querySelectorAll('.cara-dolor').forEach(c => c.classList.remove('selected'));
        caraElement.classList.add('selected');
        caraSeleccionada = valorCara;
        
        const campoOculto = document.getElementById('dolor_caras_value');
        if (campoOculto) {
            campoOculto.value = caraSeleccionada;
        }
    }
}

function sincronizarNumeros(valorCara) {
    // Actualizar la escala numérica basada en la cara seleccionada
    const numeroElement = document.querySelector(`.dolor-number[data-valor="${valorCara}"]`);
    
    if (numeroElement) {
        document.querySelectorAll('.dolor-number').forEach(n => {
            n.classList.remove('selected', 'dolor-selected');
        });
        numeroElement.classList.add('selected');
        dolorSeleccionado = valorCara;
        
        const campoOculto = document.getElementById('dolor_numerico_value');
        if (campoOculto) {
            campoOculto.value = dolorSeleccionado;
        }
        
        mostrarAlertaDolor(dolorSeleccionado);
    }
}

function mostrarAlertaDolor(nivel) {
    // Remover alertas anteriores
    const alertasExistentes = document.querySelectorAll('.alerta-dolor');
    alertasExistentes.forEach(alerta => alerta.remove());
    
    // Determinar tipo de alerta
    let tipoAlerta, mensaje;
    
    if (nivel >= 0 && nivel <= 3) {
        tipoAlerta = 'nivel-bajo';
        mensaje = '💚 Dolor leve o ausente. Continuar con evaluación de rutina.';
    } else if (nivel >= 4 && nivel <= 6) {
        tipoAlerta = 'nivel-medio';
        mensaje = '⚠️ Dolor moderado. Considerar manejo del dolor y evaluación más detallada.';
    } else if (nivel >= 7 && nivel <= 10) {
        tipoAlerta = 'nivel-alto';
        mensaje = '🚨 DOLOR SEVERO. Requiere atención inmediata y manejo del dolor.';
    }
    
    // Crear y mostrar la alerta
    const alerta = document.createElement('div');
    alerta.className = `alerta-dolor ${tipoAlerta}`;
    alerta.innerHTML = mensaje;
    
    // Insertar después de la escala de dolor
    const escalaDolor = document.querySelector('.escala-dolor-numerica');
    if (escalaDolor) {
        escalaDolor.parentNode.insertBefore(alerta, escalaDolor.nextSibling);
    }
}

/**
 * ANTECEDENTES FAMILIARES
 */
function inicializarAntecedentesFamiliares() {
    // Manejar cambios en estados familiares
    const estadosRadio = document.querySelectorAll('input[name*="estado_"]');
    estadosRadio.forEach(radio => {
        radio.addEventListener('change', function() {
            const parentesco = this.name.split('_')[1];
            toggleEnfermedadesFamiliares(parentesco, this.value);
        });
    });
    
    // Manejar checkboxes de enfermedades
    const checkboxesEnfermedades = document.querySelectorAll('.enfermedad-checkbox input');
    checkboxesEnfermedades.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            actualizarResumenAntecedentes();
        });
    });
}

function toggleEnfermedadesFamiliares(parentesco, estado) {
    const enfermedadesContainer = document.getElementById(`enfermedades_${parentesco}`);
    
    if (enfermedadesContainer) {
        if (estado === 'FALLECIDO') {
            // Si está fallecido, mostrar todas las opciones
            enfermedadesContainer.style.display = 'block';
            enfermedadesContainer.style.opacity = '1';
        } else if (estado === 'VIVO') {
            // Si está vivo, mostrar opciones
            enfermedadesContainer.style.display = 'block';
            enfermedadesContainer.style.opacity = '1';
        } else {
            // Si es desconocido, ocultar opciones
            enfermedadesContainer.style.display = 'none';
            // Limpiar selecciones
            const checkboxes = enfermedadesContainer.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = false);
        }
    }
}

function actualizarResumenAntecedentes() {
    // Lógica para actualizar resumen de antecedentes familiares
    const enfermedadesSeleccionadas = {};
    const checkboxes = document.querySelectorAll('.enfermedad-checkbox input:checked');
    
    checkboxes.forEach(checkbox => {
        const parentesco = checkbox.dataset.parentesco;
        const enfermedad = checkbox.value;
        
        if (!enfermedadesSeleccionadas[enfermedad]) {
            enfermedadesSeleccionadas[enfermedad] = [];
        }
        enfermedadesSeleccionadas[enfermedad].push(parentesco);
    });
    
    console.log('Antecedentes familiares:', enfermedadesSeleccionadas);
}

/**
 * MALOS HÁBITOS ORALES
 */
function inicializarMalosHabitos() {
    const selectsFrecuencia = document.querySelectorAll('.frecuencia-select');
    
    selectsFrecuencia.forEach(select => {
        select.addEventListener('change', function() {
            const habito = this.dataset.habito;
            const frecuencia = this.value;
            
            // Resaltar si la frecuencia es preocupante
            const habitoItem = this.closest('.habito-item');
            if (frecuencia === 'FRECUENTEMENTE' || frecuencia === 'SIEMPRE') {
                habitoItem.style.borderColor = '#ef4444';
                habitoItem.style.backgroundColor = '#fef2f2';
            } else if (frecuencia === 'ALGUNAS_VECES') {
                habitoItem.style.borderColor = '#eab308';
                habitoItem.style.backgroundColor = '#fffbeb';
            } else {
                habitoItem.style.borderColor = '#fed7aa';
                habitoItem.style.backgroundColor = 'white';
            }
            
            actualizarResumenHabitos();
        });
    });
}

function actualizarResumenHabitos() {
    const habitosProblematicos = [];
    const selects = document.querySelectorAll('.frecuencia-select');
    
    selects.forEach(select => {
        if (select.value === 'FRECUENTEMENTE' || select.value === 'SIEMPRE') {
            const habito = select.dataset.habito;
            habitosProblematicos.push({
                habito: habito,
                frecuencia: select.value
            });
        }
    });
    
    if (habitosProblematicos.length > 0) {
        mostrarAlertaHabitos(habitosProblematicos);
    } else {
        ocultarAlertaHabitos();
    }
    
    console.log('Hábitos problemáticos:', habitosProblematicos);
}

function mostrarAlertaHabitos(habitos) {
    // Similar a mostrarAlertaDolor pero para hábitos
    let alertaExistente = document.querySelector('.alerta-habitos');
    
    if (!alertaExistente) {
        alertaExistente = document.createElement('div');
        alertaExistente.className = 'alerta-dolor nivel-medio alerta-habitos';
        
        const habitosContainer = document.querySelector('.habitos-orales');
        if (habitosContainer) {
            habitosContainer.appendChild(alertaExistente);
        }
    }
    
    const habitosTexto = habitos.map(h => h.habito.replace('_', ' ')).join(', ');
    alertaExistente.innerHTML = `⚠️ Hábitos frecuentes detectados: ${habitosTexto}. Considerar seguimiento ortodóncico.`;
}

function ocultarAlertaHabitos() {
    const alerta = document.querySelector('.alerta-habitos');
    if (alerta) {
        alerta.remove();
    }
}

/**
 * SIGNOS VITALES
 */
function inicializarSignosVitales() {
    const inputsSignos = document.querySelectorAll('.signo-input');
    
    inputsSignos.forEach(input => {
        input.addEventListener('blur', function() {
            validarSignoVital(this);
        });
        
        input.addEventListener('input', function() {
            // Solo números y algunos caracteres especiales para presión arterial
            if (this.dataset.tipo !== 'presion') {
                this.value = this.value.replace(/[^0-9.]/g, '');
            } else {
                this.value = this.value.replace(/[^0-9/]/g, '');
            }
        });
    });
}

function validarSignoVital(input) {
    const tipo = input.dataset.tipo;
    const valor = input.value;
    const signoContainer = input.closest('.signo-vital');
    
    // Resetear estilos
    signoContainer.style.borderColor = '#bae6fd';
    signoContainer.style.backgroundColor = 'white';
    
    if (!valor) return;
    
    let esAnormal = false;
    
    switch (tipo) {
        case 'pulso':
            const pulso = parseInt(valor);
            if (pulso < 60 || pulso > 100) {
                esAnormal = true;
            }
            break;
            
        case 'presion':
            const presion = valor.split('/');
            if (presion.length === 2) {
                const sistolica = parseInt(presion[0]);
                const diastolica = parseInt(presion[1]);
                if (sistolica > 140 || diastolica > 90 || sistolica < 90 || diastolica < 60) {
                    esAnormal = true;
                }
            }
            break;
            
        case 'temperatura':
            const temp = parseFloat(valor);
            if (temp < 36 || temp > 37.5) {
                esAnormal = true;
            }
            break;
            
        case 'frecuencia_respiratoria':
            const fr = parseInt(valor);
            if (fr < 12 || fr > 20) {
                esAnormal = true;
            }
            break;
    }
    
    if (esAnormal) {
        signoContainer.style.borderColor = '#ef4444';
        signoContainer.style.backgroundColor = '#fef2f2';
    }
}

/**
 * UTILIDADES GENERALES
 */
function validarFormularioCompleto() {
    const errores = [];
    
    // Validar dolor si está presente
    if (document.querySelector('.escala-dolor-numerica') && dolorSeleccionado === null) {
        errores.push('Debe seleccionar un nivel de dolor');
    }
    
    // Validar signos vitales obligatorios
    const signosObligatorios = document.querySelectorAll('.signo-input[required]');
    signosObligatorios.forEach(input => {
        if (!input.value.trim()) {
            errores.push(`El campo ${input.dataset.label || 'signo vital'} es obligatorio`);
        }
    });
    
    return errores;
}

function guardarDatosHistorial() {
    const datos = {
        dolor_numerico: dolorSeleccionado,
        dolor_caras: caraSeleccionada,
        antecedentes_familiares: {},
        malos_habitos: {},
        signos_vitales: {}
    };
    
    // Recopilar antecedentes familiares
    const checkboxesAntecedentes = document.querySelectorAll('.enfermedad-checkbox input:checked');
    checkboxesAntecedentes.forEach(checkbox => {
        const parentesco = checkbox.dataset.parentesco;
        const enfermedad = checkbox.value;
        
        if (!datos.antecedentes_familiares[parentesco]) {
            datos.antecedentes_familiares[parentesco] = [];
        }
        datos.antecedentes_familiares[parentesco].push(enfermedad);
    });
    
    // Recopilar hábitos
    const selectsHabitos = document.querySelectorAll('.frecuencia-select');
    selectsHabitos.forEach(select => {
        if (select.value && select.value !== 'NUNCA') {
            datos.malos_habitos[select.dataset.habito] = select.value;
        }
    });
    
    // Recopilar signos vitales
    const inputsSignos = document.querySelectorAll('.signo-input');
    inputsSignos.forEach(input => {
        if (input.value.trim()) {
            datos.signos_vitales[input.dataset.tipo] = input.value.trim();
        }
    });
    
    console.log('Datos recopilados del historial:', datos);
    return datos;
}

// Agregar evento al formulario principal si existe
document.addEventListener('DOMContentLoaded', function() {
    const formulario = document.querySelector('#formulario-historial');
    if (formulario) {
        formulario.addEventListener('submit', function(e) {
            const errores = validarFormularioCompleto();
            
            if (errores.length > 0) {
                e.preventDefault();
                alert('Por favor corrija los siguientes errores:\n\n' + errores.join('\n'));
                return false;
            }
            
            // Guardar datos en campos ocultos antes del envío
            const datosJson = JSON.stringify(guardarDatosHistorial());
            
            let campoOcultoJson = document.getElementById('datos_historial_json');
            if (!campoOcultoJson) {
                campoOcultoJson = document.createElement('input');
                campoOcultoJson.type = 'hidden';
                campoOcultoJson.id = 'datos_historial_json';
                campoOcultoJson.name = 'datos_historial_json';
                formulario.appendChild(campoOcultoJson);
            }
            
            campoOcultoJson.value = datosJson;
        });
    }
});

// Funciones de exportación si se necesitan en otros archivos
window.HistorialClinico = {
    seleccionarDolor,
    seleccionarCara,
    guardarDatosHistorial,
    validarFormularioCompleto
};