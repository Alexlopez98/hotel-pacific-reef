// static/js/index.js

// Esperamos a que el DOM (todo el HTML) esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    
    // Capturamos los botones por su ID
    const btnAcceder = document.getElementById('btn-acceder');
    const btnRegistrarse = document.getElementById('btn-registrarse');

    // Le agregamos el evento de clic al botón de Acceder
    if (btnAcceder) {
        btnAcceder.addEventListener('click', function() {
            // Redirige usando la variable definida en el HTML
            window.location.href = urlAcceder;
        });
    }

    // Le agregamos el evento de clic al botón de Registrarse
    if (btnRegistrarse) {
        btnRegistrarse.addEventListener('click', function() {
            // Redirige usando la variable definida en el HTML
            window.location.href = urlRegistrarse;
        });
    }
});