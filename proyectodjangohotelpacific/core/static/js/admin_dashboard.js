document.addEventListener('DOMContentLoaded', function () {

    // Configuración de Seguridad para Django Fetch
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const fetchHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    };

    // --- 1. TABS NAVEGACIÓN ---
    const links = document.querySelectorAll('.nav-link-admin');
    const sections = document.querySelectorAll('.content-section');

    links.forEach(link => {
        link.addEventListener('click', function (e) {
            // No intervenir si el botón es el de "Cerrar Sesión" (type submit)
            if (this.closest('form')) return;

            e.preventDefault();
            links.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.getAttribute('data-target')).classList.add('active');
        });
    });

// --- 2. AJAX: CAMBIAR ESTADO ---
    document.querySelectorAll('.status-select').forEach(select => {
        select.addEventListener('change', function() {
            const idReserva = this.getAttribute('data-id');
            const nuevoEstado = this.value;
            
            fetch('/api/admin/cambiar-estado/', {
                method: 'POST',
                headers: fetchHeaders,
                body: JSON.stringify({ id_reserva: idReserva, nuevo_estado: nuevoEstado })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    this.style.backgroundColor = '#d4edda'; 
                    
                    if(data.nuevo_estado === 'Finalizada') {
                        
                        // --- NUEVA ALERTA DE RESUMEN ---
                        alert(`✅ CHECK-OUT COMPLETADO\n\n` +
                              `👤 Cliente: ${data.cliente}\n` +
                              `🛏️ Habitación Liberada: ${data.hab_numero} (${data.hab_categoria})\n` +
                              `💰 Saldo Cobrado: ${data.saldo_cobrado}`);
                        // -------------------------------

                        const fila = document.getElementById(`fila-reserva-${idReserva}`);
                        fila.style.opacity = '0';
                        setTimeout(() => window.location.reload(), 600);
                        
                    } else if (data.nuevo_estado === 'Cancelada') {
                        const fila = document.getElementById(`fila-reserva-${idReserva}`);
                        fila.style.opacity = '0';
                        setTimeout(() => window.location.reload(), 600);
                        
                    } else {
                        setTimeout(() => this.style.backgroundColor = '', 1000);
                    }
                } else {
                    alert('Error al cambiar el estado.');
                }
            });
        });
    });
    // --- 3. AJAX: ELIMINAR RESERVA ---
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', function () {
            if (!confirm('¿Seguro que deseas eliminar esta reserva permanentemente?')) return;

            const idReserva = this.getAttribute('data-id');

            fetch('/api/admin/eliminar-reserva/', {
                method: 'POST',
                headers: fetchHeaders,
                body: JSON.stringify({ id_reserva: idReserva })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Animamos la eliminación de la fila visualmente
                        const fila = document.getElementById(`fila-reserva-${idReserva}`);
                        fila.style.opacity = '0';
                        setTimeout(() => fila.remove(), 600);
                    } else {
                        alert('Error al eliminar.');
                    }
                });
        });
    });

    // --- 4. AJAX: BUSCAR HISTORIAL ---
    const formBuscar = document.getElementById('form-buscar-cliente');
    const tablaHistorial = document.querySelector('#tabla-historial tbody');

    if (formBuscar) {
        formBuscar.addEventListener('submit', function (e) {
            e.preventDefault();
            const query = document.getElementById('input-busqueda').value;
            if (!query) return;

            tablaHistorial.innerHTML = '<tr><td colspan="7" class="text-center py-4"><i class="fas fa-spinner fa-spin me-2"></i>Buscando...</td></tr>';

            fetch(`/api/admin/buscar-historial/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    tablaHistorial.innerHTML = '';
                    if (data.reservas.length === 0) {
                        tablaHistorial.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4 fw-bold">No se encontraron reservas.</td></tr>';
                        return;
                    }
                    data.reservas.forEach(r => {
                        // Asignamos un color al badge según su estado
                        let badgeClass = 'bg-danger';
                        if (r.estado === 'Confirmada') badgeClass = 'bg-success';
                        if (r.estado === 'Pendiente') badgeClass = 'bg-warning text-dark';
                        if (r.estado === 'Finalizada') badgeClass = 'bg-secondary';

                        const fila = `
                        <tr>
                            <td class="text-muted">#${r.id_reserva}</td>
                            <td class="fw-bold">${r.cliente}</td>
                            <td class="small">${r.rut}</td>
                            <td>${r.habitacion}</td>
                            <td>${r.ingreso}</td>
                            <td>${r.salida}</td> <!-- DIBUJAMOS LA SALIDA -->
                            <td>
                                <div class="text-muted small">Tarifa: ${r.total_estimado}</div>
                                <div class="text-success fw-bold">Pagado: ${r.total_pagado}</div>
                            </td>
                            <td><span class="badge ${badgeClass}">${r.estado}</span></td>
                        </tr>
                    `;
                        tablaHistorial.insertAdjacentHTML('beforeend', fila);
                    });
                });
        });
    }

    // --- 5. CHART.JS (GRÁFICOS DE INGRESOS) ---
    const chartDataElement = document.getElementById('chart-data');
    if (chartDataElement) {
        const datosDB = JSON.parse(chartDataElement.textContent);
        const ctx = document.getElementById('graficoIngresos').getContext('2d');

        let chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: datosDB.mensual.labels,
                datasets: [{
                    label: 'Ingresos',
                    data: datosDB.mensual.data,
                    backgroundColor: '#99CBCE',
                    borderRadius: 4
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });

        document.getElementById('filtro-tiempo').addEventListener('change', function () {
            const periodo = this.value; // 'diario', 'mensual', 'anual'
            chartInstance.data.labels = datosDB[periodo].labels;
            chartInstance.data.datasets[0].data = datosDB[periodo].data;
            chartInstance.update();
        });
    }
});