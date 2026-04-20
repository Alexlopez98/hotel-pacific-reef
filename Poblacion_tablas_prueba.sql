-- ====================================================================
-- SCRIPT 2: POBLACIÓN DE DATOS Y TESTING CRUD
-- PROYECTO: HOTEL PACIFIC REEF | SEMANA 6
-- ====================================================================

-- 1. CARGA DE DATOS FIDEDIGNOS 
INSERT INTO usuarios (rut, nombre, correo, rol) VALUES ('18.123.456-7', 'Camila Soto', 'camila.soto@gmail.com', 'Turista');
INSERT INTO usuarios (rut, nombre, correo, rol) VALUES ('15.987.654-3', 'Mauricio Tapia', 'mtapia@pacificreef.cl', 'Administrador');

INSERT INTO habitaciones (numero, categoria, capacidad, precio_diario) VALUES ('101', 'Estándar Vista Mar', 2, 65000.00);
INSERT INTO habitaciones (numero, categoria, capacidad, precio_diario) VALUES ('201', 'Suite Premium', 2, 120000.00);

-- Insertar Reserva (Simulando proceso del Usuario Final) 
INSERT INTO reservas (id_usuario, id_habitacion, fecha_ingreso, fecha_salida, estado_reserva, total_estimado) 
VALUES (1, 1, TO_DATE('2026-11-15', 'YYYY-MM-DD'), TO_DATE('2026-11-20', 'YYYY-MM-DD'), 'Pendiente', 325000.00);

-- Insertar Pago del 30% (Simulando proceso clave) 
INSERT INTO pagos (id_reserva, monto_pagado, metodo_pago) VALUES (1, 97500.00, 'Webpay');

COMMIT;

-- 2. CONSULTAS DE VERIFICACIÓN (EVIDENCIA PARA EL VIDEO) 

-- A. Verificar Dashboard del Cliente
SELECT * FROM vw_dashboard_cliente;

-- B. Verificar Dashboard del Administrador
SELECT * FROM vw_dashboard_admin;

-- C. Verificar Gestión Operativa
SELECT * FROM vw_gestion_operativa;