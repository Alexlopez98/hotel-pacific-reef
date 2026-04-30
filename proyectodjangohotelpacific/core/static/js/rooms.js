document.addEventListener('DOMContentLoaded', function () {
    const checkinInput = document.getElementById('checkin');
    const checkoutInput = document.getElementById('checkout');
    const nochesText = document.getElementById('noches-text');
    const contenedoresPrecio = document.querySelectorAll('[data-precio]');
    const buscador = document.getElementById('buscador');
    const tarjetas = document.querySelectorAll('.habitacion-card');

    const formateadorCLP = new Intl.NumberFormat('es-CL', {
        style: 'currency', currency: 'CLP', maximumFractionDigits: 0
    });

    // 1. LÓGICA DE FECHAS
    const hoy = new Date().toISOString().split('T')[0];
    if (checkinInput) checkinInput.setAttribute('min', hoy);

    function actualizarPrecios() {
        if (!checkinInput.value || !checkoutInput.value) return;

        const checkinDate = new Date(checkinInput.value);
        const checkoutDate = new Date(checkoutInput.value);
        const diferencia = checkoutDate.getTime() - checkinDate.getTime();
        const diasEstadia = Math.ceil(diferencia / (1000 * 3600 * 24));

        if (diasEstadia > 0) {
            nochesText.textContent = `${diasEstadia} ${diasEstadia === 1 ? 'noche' : 'noches'}`;
            
            // Guardar fechas en el navegador para la siguiente página
            sessionStorage.setItem('fecha_llegada', checkinInput.value);
            sessionStorage.setItem('fecha_salida', checkoutInput.value);

            contenedoresPrecio.forEach(contenedor => {
                const precioBase = parseInt(contenedor.getAttribute('data-precio'));
                contenedor.querySelector('.precio-display').textContent = formateadorCLP.format(precioBase * diasEstadia);
                contenedor.querySelector('.text-noche').textContent = `Total (${diasEstadia} noches)`;
            });
        }
    }

    if (checkinInput && checkoutInput) {
        checkinInput.addEventListener('change', () => {
            let minOut = new Date(checkinInput.value);
            minOut.setDate(minOut.getDate() + 1);
            checkoutInput.setAttribute('min', minOut.toISOString().split('T')[0]);
            actualizarPrecios();
        });
        checkoutInput.addEventListener('change', actualizarPrecios);
    }

    // 2. BUSCADOR
    if (buscador) {
        buscador.addEventListener('keyup', (e) => {
            const term = e.target.value.toLowerCase();
            tarjetas.forEach(t => {
                const nombre = t.querySelector('.nombre-hab').textContent.toLowerCase();
                t.style.display = nombre.includes(term) ? 'block' : 'none';
            });
        });
    }
});