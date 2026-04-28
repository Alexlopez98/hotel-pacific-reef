document.addEventListener('DOMContentLoaded', function () {
    
    // --- 1. LÓGICA PARA MOSTRAR/OCULTAR CONTRASEÑA ---
    const togglePassword = document.querySelector('#togglePassword');
    const password = document.querySelector('#password');
    const eyeIcon = document.querySelector('#eyeIcon');

    if (togglePassword) {
        togglePassword.addEventListener('click', function (e) {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            eyeIcon.classList.toggle('fa-eye');
            eyeIcon.classList.toggle('fa-eye-slash');
        });
    }

    // --- 2. LÓGICA PARA EL MANEJO Y VALIDACIÓN DEL RUT ---
    const rutCuerpo = document.getElementById('rut_cuerpo');
    const rutDv = document.getElementById('rut_dv');
    const form = document.getElementById('form-registro');
    const rutError = document.getElementById('rut-error');

    // Restringir el cuerpo del RUT para que solo acepte números
    if (rutCuerpo) {
        rutCuerpo.addEventListener('input', function (e) {
            this.value = this.value.replace(/[^0-9]/g, ''); 
        });
    }

    // Restringir el DV para que solo acepte números o la letra K (y forzar mayúscula)
    if (rutDv) {
        rutDv.addEventListener('input', function (e) {
            this.value = this.value.replace(/[^0-9kK]/g, '').toUpperCase();
        });
    }

    // Validar matemáticamente el RUT antes de enviar el formulario a Django
    if (form) {
        form.addEventListener('submit', function (e) {
            if (rutCuerpo.value && rutDv.value) {
                if (!esRutValido(rutCuerpo.value, rutDv.value)) {
                    e.preventDefault(); // Detiene el envío del formulario
                    rutError.classList.remove('d-none'); // Muestra el mensaje de error
                    rutCuerpo.focus(); // Devuelve el cursor al RUT
                } else {
                    rutError.classList.add('d-none'); // Oculta el error si es correcto
                }
            }
        });
    }

    // Función que aplica el algoritmo de Módulo 11 para validar el RUT
    function esRutValido(cuerpo, dv) {
        let suma = 0;
        let multiplo = 2;
        
        // Recorrer el cuerpo del RUT de atrás hacia adelante
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += multiplo * cuerpo.charAt(i);
            multiplo = multiplo < 7 ? multiplo + 1 : 2;
        }
        
        const dvEsperado = 11 - (suma % 11);
        let dvCalculado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString();
        
        return dv === dvCalculado;
    }
});