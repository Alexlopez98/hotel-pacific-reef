document.addEventListener('DOMContentLoaded', function () {
    
    // 1. LÓGICA DE FECHAS Y PRECIOS
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');
    const nochesText = document.getElementById('noches-text');
    
    // Capturamos todos los contenedores de precio de las tarjetas
    const contenedoresPrecio = document.querySelectorAll('[data-precio]');

    const formateadorCLP = new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP',
        maximumFractionDigits: 0
    });

    // Configurar fecha mínima de check-in (hoy)
    const hoy = new Date().toISOString().split('T')[0];
    if (checkinInput) checkinInput.setAttribute('min', hoy);

    function actualizarPrecios() {
        if (!checkinInput || !checkoutInput) return;

        const checkinDate = new Date(checkinInput.value);
        const checkoutDate = new Date(checkoutInput.value);
        let diasEstadia = 0;

        if (checkinInput.value && checkoutInput.value) {
            const diferencia = checkoutDate.getTime() - checkinDate.getTime();
            diasEstadia = Math.ceil(diferencia / (1000 * 3600 * 24));
        }

        if (diasEstadia > 0) {
            nochesText.textContent = diasEstadia === 1 ? '1 noche' : `${diasEstadia} noches`;
            
            // Recorrer todas las tarjetas y actualizar su precio
            contenedoresPrecio.forEach(contenedor => {
                const precioBase = parseInt(contenedor.getAttribute('data-precio'));
                const total = precioBase * diasEstadia;
                
                contenedor.querySelector('.precio-display').textContent = formateadorCLP.format(total);
                contenedor.querySelector('.text-noche').textContent = `Total (${diasEstadia} noches)`;
            });
        } else {
            // Volver al estado por defecto si las fechas son inválidas o están vacías
            nochesText.textContent = "0 noches";
            contenedoresPrecio.forEach(contenedor => {
                const precioBase = parseInt(contenedor.getAttribute('data-precio'));
                contenedor.querySelector('.precio-display').textContent = formateadorCLP.format(precioBase);
                contenedor.querySelector('.text-noche').textContent = "/ noche";
            });
        }
    }

    if (checkinInput && checkoutInput) {
        checkinInput.addEventListener('change', function() {
            // Forzar que el checkout sea al menos 1 día después del checkin
            if(checkinInput.value) {
                let minCheckout = new Date(checkinInput.value);
                minCheckout.setDate(minCheckout.getDate() + 1);
                checkoutInput.setAttribute('min', minCheckout.toISOString().split('T')[0]);
            }
            actualizarPrecios();
        });
        checkoutInput.addEventListener('change', actualizarPrecios);
    }

    // 2. LÓGICA DEL BUSCADOR EN EL NAV
    const buscador = document.getElementById('buscador'); // Asegúrate de ponerle id="buscador" al input del nav
    const tarjetas = document.querySelectorAll('.habitacion-card');

    if (buscador) {
        buscador.addEventListener('keyup', function(e) {
            const textoBusqueda = e.target.value.toLowerCase();

            tarjetas.forEach(tarjeta => {
                const nombreHabitacion = tarjeta.querySelector('.nombre-hab').textContent.toLowerCase();
                
                if (nombreHabitacion.includes(textoBusqueda)) {
                    tarjeta.style.display = 'block'; // Mostrar
                } else {
                    tarjeta.style.display = 'none'; // Ocultar
                }
            });
        });
    }
});