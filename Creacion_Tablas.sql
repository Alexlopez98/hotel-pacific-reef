-- ====================================================================
-- SCRIPT 1: INFRAESTRUCTURA (TABLAS Y VISTAS)
-- PROYECTO: HOTEL PACIFIC REEF | SEMANA 6
-- ====================================================================

-- LIMPIEZA PREVIA (Opcional, para ejecutar el script desde cero)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE pagos CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE reservas CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE habitaciones CASCADE CONSTRAINTS';
    EXECUTE IMMEDIATE 'DROP TABLE usuarios CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- 1. CREACIÓN DE TABLAS 
CREATE TABLE usuarios (
    id_usuario NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rut VARCHAR2(12) UNIQUE NOT NULL,
    nombre VARCHAR2(100) NOT NULL,
    correo VARCHAR2(100) UNIQUE NOT NULL,
    rol VARCHAR2(20) DEFAULT 'Turista' CHECK (rol IN ('Turista', 'Administrador'))
);

CREATE TABLE habitaciones (
    id_habitacion NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero VARCHAR2(10) UNIQUE NOT NULL,
    categoria VARCHAR2(50) NOT NULL, 
    capacidad NUMBER NOT NULL CHECK (capacidad BETWEEN 1 AND 6),
    precio_diario NUMBER(10, 2) NOT NULL CHECK (precio_diario >= 45000),
    estado VARCHAR2(20) DEFAULT 'Disponible' CHECK (estado IN ('Disponible', 'Ocupada', 'Mantenimiento'))
);

CREATE TABLE reservas (
    id_reserva NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario NUMBER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    id_habitacion NUMBER REFERENCES habitaciones(id_habitacion),
    fecha_ingreso DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    estado_reserva VARCHAR2(20) DEFAULT 'Pendiente' CHECK (estado_reserva IN ('Pendiente', 'Confirmada', 'Cancelada', 'Finalizada')),
    total_estimado NUMBER(10, 2) NOT NULL CHECK (total_estimado > 0),
    CONSTRAINT check_fechas CHECK (fecha_salida > fecha_ingreso)
);

CREATE TABLE pagos (
    id_pago NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_reserva NUMBER REFERENCES reservas(id_reserva) ON DELETE CASCADE,
    monto_pagado NUMBER(10, 2) NOT NULL CHECK (monto_pagado > 0),
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR2(50) NOT NULL
);

-- 2. CREACIÓN DE VISTAS PARA SPRINT-REVIEW 

-- Vista para el Cliente (Turista)
CREATE OR REPLACE VIEW vw_dashboard_cliente AS
SELECT r.id_reserva, h.numero AS habitacion, h.categoria, r.fecha_ingreso, r.fecha_salida, 
       r.estado_reserva, r.total_estimado, NVL(p.monto_pagado, 0) AS anticipo_pagado
FROM reservas r
JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
LEFT JOIN pagos p ON r.id_reserva = p.id_reserva;

-- Vista para el Administrador (Métricas)
CREATE OR REPLACE VIEW vw_dashboard_admin AS
SELECT (SELECT COUNT(*) FROM habitaciones WHERE estado = 'Disponible') AS disponibles,
       (SELECT COUNT(*) FROM reservas WHERE estado_reserva = 'Pendiente') AS pendientes,
       (SELECT SUM(monto_pagado) FROM pagos) AS recaudacion_total
FROM DUAL;

-- Vista de Proceso Clave: Gestión Operativa
CREATE OR REPLACE VIEW vw_gestion_operativa AS
SELECT r.id_reserva, u.nombre AS cliente, h.numero AS hab, r.fecha_ingreso, r.estado_reserva, p.monto_pagado
FROM reservas r
JOIN usuarios u ON r.id_usuario = u.id_usuario
JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
LEFT JOIN pagos p ON r.id_reserva = p.id_reserva;

COMMIT;