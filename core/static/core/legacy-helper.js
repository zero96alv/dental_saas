/*!
 * LEGACY HELPER - Compatibilidad con dispositivos antiguos
 * Soporte específico para iOS 9.3, Safari antiguo, Android < 7
 */

(function() {
    'use strict';
    
    // Detectar dispositivo antiguo
    var isOldIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && (
        parseFloat(navigator.appVersion.match(/OS (\d+)_(\d+)/)?.[1] || '10') < 10 ||
        parseFloat(navigator.appVersion.match(/Version\/(\d+\.\d+)/)?.[1] || '10') < 10
    );
    
    var isOldAndroid = /Android/.test(navigator.userAgent) && 
        parseFloat(navigator.userAgent.match(/Android (\d+\.\d+)/)?.[1] || '7') < 7;
    
    var isLegacyDevice = isOldIOS || isOldAndroid;
    
    // Agregar clase CSS si es dispositivo antiguo
    if (isLegacyDevice) {
        document.documentElement.className += ' legacy-device';
    }
    
    // Polyfills básicos para dispositivos antiguos
    if (isLegacyDevice) {
        
        // Polyfill para Array.from
        if (!Array.from) {
            Array.from = function(arrayLike) {
                return Array.prototype.slice.call(arrayLike);
            };
        }
        
        // Polyfill para Object.assign
        if (!Object.assign) {
            Object.assign = function(target) {
                for (var i = 1; i < arguments.length; i++) {
                    var source = arguments[i];
                    for (var key in source) {
                        if (source.hasOwnProperty(key)) {
                            target[key] = source[key];
                        }
                    }
                }
                return target;
            };
        }
        
        // Polyfill para Element.closest
        if (!Element.prototype.closest) {
            Element.prototype.closest = function(s) {
                var el = this;
                do {
                    if (el.matches(s)) return el;
                    el = el.parentElement || el.parentNode;
                } while (el !== null && el.nodeType === 1);
                return null;
            };
        }
        
        // Polyfill para Element.matches
        if (!Element.prototype.matches) {
            Element.prototype.matches = Element.prototype.msMatchesSelector || 
                                      Element.prototype.webkitMatchesSelector;
        }
    }
    
    // Helpers específicos para dispositivos antiguos
    window.LegacyHelper = {
        isLegacyDevice: isLegacyDevice,
        isOldIOS: isOldIOS,
        isOldAndroid: isOldAndroid,
        
        // Inicializar compatibilidad cuando DOM esté listo
        init: function() {
            if (!isLegacyDevice) return;
            
            this.fixNavbar();
            this.fixDropdowns();
            this.fixForms();
            this.fixTouchTargets();
            this.fixScrolling();
            this.optimizePerformance();
        },
        
        // Arreglar navbar para dispositivos antiguos
        fixNavbar: function() {
            var navbar = document.querySelector('.navbar');
            if (!navbar) return;
            
            // Hacer navbar no fijo en dispositivos antiguos
            navbar.style.position = 'relative';
            document.body.style.paddingTop = '0';
            
            // Simplificar collapse behavior
            var toggler = navbar.querySelector('.navbar-toggler');
            var collapse = navbar.querySelector('.navbar-collapse');
            
            if (toggler && collapse) {
                toggler.addEventListener('click', function(e) {
                    e.preventDefault();
                    collapse.style.display = collapse.style.display === 'block' ? 'none' : 'block';
                });
            }
        },
        
        // Arreglar dropdowns para dispositivos antiguos
        fixDropdowns: function() {
            var dropdowns = document.querySelectorAll('.dropdown');
            
            Array.from(dropdowns).forEach(function(dropdown) {
                var toggle = dropdown.querySelector('.dropdown-toggle');
                var menu = dropdown.querySelector('.dropdown-menu');
                
                if (toggle && menu) {
                    toggle.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // Cerrar otros dropdowns
                        Array.from(document.querySelectorAll('.dropdown-menu')).forEach(function(otherMenu) {
                            if (otherMenu !== menu) {
                                otherMenu.style.display = 'none';
                            }
                        });
                        
                        // Toggle este dropdown
                        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
                    });
                }
            });
            
            // Cerrar dropdowns al hacer click fuera
            document.addEventListener('click', function() {
                Array.from(document.querySelectorAll('.dropdown-menu')).forEach(function(menu) {
                    menu.style.display = 'none';
                });
            });
        },
        
        // Optimizar formularios para dispositivos táctiles antiguos
        fixForms: function() {
            // Prevenir zoom en iOS al hacer focus en inputs
            var inputs = document.querySelectorAll('input, select, textarea');
            
            Array.from(inputs).forEach(function(input) {
                if (input.style.fontSize !== '16px') {
                    input.style.fontSize = '16px';
                }
                
                // Mejorar padding para touch
                if (!input.style.padding) {
                    input.style.padding = '12px';
                }
            });
        },
        
        // Mejorar targets táctiles
        fixTouchTargets: function() {
            var touchTargets = document.querySelectorAll('a, button, .btn, .nav-link, .dropdown-item');
            
            Array.from(touchTargets).forEach(function(target) {
                var computedStyle = window.getComputedStyle(target);
                var height = parseInt(computedStyle.height);
                
                // Asegurar mínimo 44px de altura (guía Apple)
                if (height < 44) {
                    target.style.minHeight = '44px';
                    target.style.paddingTop = '12px';
                    target.style.paddingBottom = '12px';
                }
            });
        },
        
        // Mejorar scrolling en dispositivos táctiles
        fixScrolling: function() {
            // Activar smooth scrolling nativo
            var scrollContainers = document.querySelectorAll('.table-responsive, .modal-body, .overflow-auto');
            
            Array.from(scrollContainers).forEach(function(container) {
                container.style.webkitOverflowScrolling = 'touch';
            });
            
            // Fix para momentum scrolling en iOS
            if (isOldIOS) {
                document.body.style.webkitOverflowScrolling = 'touch';
            }
        },
        
        // Optimizaciones de performance para dispositivos antiguos
        optimizePerformance: function() {
            // Deshabilitar animaciones complejas
            var style = document.createElement('style');
            style.textContent = `
                .legacy-device * {
                    transition: none !important;
                    animation: none !important;
                }
                .legacy-device .fade {
                    transition: opacity 0.15s linear !important;
                }
            `;
            document.head.appendChild(style);
            
            // Lazy loading para imágenes
            this.lazyLoadImages();
            
            // Debounce para eventos de scroll/resize
            this.debounceEvents();
        },
        
        // Lazy loading simple para imágenes
        lazyLoadImages: function() {
            var images = document.querySelectorAll('img[data-src]');
            
            Array.from(images).forEach(function(img) {
                var rect = img.getBoundingClientRect();
                if (rect.top < window.innerHeight + 200) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
            });
        },
        
        // Debounce para eventos costosos
        debounceEvents: function() {
            var debounce = function(func, wait) {
                var timeout;
                return function executedFunction() {
                    var context = this;
                    var args = arguments;
                    var later = function() {
                        timeout = null;
                        func.apply(context, args);
                    };
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                };
            };
            
            // Debounce resize events
            window.addEventListener('resize', debounce(function() {
                // Re-evaluar layout si es necesario
                window.LegacyHelper.lazyLoadImages();
            }, 250));
            
            // Debounce scroll events
            window.addEventListener('scroll', debounce(function() {
                window.LegacyHelper.lazyLoadImages();
            }, 100));
        },
        
        // Utilidad para mostrar mensaje de compatibilidad
        showCompatibilityMessage: function() {
            if (!isLegacyDevice) return;
            
            var message = document.createElement('div');
            message.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #fff3cd;
                border-bottom: 1px solid #ffeaa7;
                padding: 10px;
                text-align: center;
                font-size: 14px;
                z-index: 9999;
            `;
            message.innerHTML = `
                <span>📱 Dispositivo detectado: Modo compatibilidad activado</span>
                <button onclick="this.parentNode.style.display='none'" style="float: right; background: none; border: none; font-size: 16px;">&times;</button>
            `;
            
            document.body.insertBefore(message, document.body.firstChild);
            
            // Auto-ocultar después de 5 segundos
            setTimeout(function() {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 5000);
        }
    };
    
    // Auto-inicializar cuando DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.LegacyHelper.init();
        });
    } else {
        window.LegacyHelper.init();
    }
    
})();