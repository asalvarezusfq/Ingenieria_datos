-- ============================================================
-- Esquema PostgreSQL: datos transaccionales/históricos del
-- sistema de transporte público de Quito
--
-- Nota: id_bus / id_ruta referencian conceptualmente a las
-- tablas buses/rutas de MySQL. No hay FK real porque son
-- motores de base de datos distintos (limitación esperada
-- en una arquitectura políglota).
-- ============================================================

CREATE TABLE viajes (
    id_viaje     SERIAL PRIMARY KEY,
    id_bus       INT NOT NULL,
    id_ruta      INT NOT NULL,
    fecha        DATE NOT NULL,
    hora_salida  TIME NOT NULL,
    hora_llegada TIME NOT NULL,
    estado       VARCHAR(20) NOT NULL  -- COMPLETADO, RETRASADO, CANCELADO
);

CREATE TABLE pasajeros_por_viaje (
    id_viaje           INT PRIMARY KEY,
    cantidad_pasajeros INT NOT NULL,
    FOREIGN KEY (id_viaje) REFERENCES viajes(id_viaje)
);

CREATE TABLE incidencias (
    id_incidencia SERIAL PRIMARY KEY,
    id_viaje      INT NOT NULL,
    tipo          VARCHAR(50) NOT NULL,  -- MECANICA, TRAFICO, ACCIDENTE, OTRO
    descripcion   TEXT,
    fecha         DATE NOT NULL,
    FOREIGN KEY (id_viaje) REFERENCES viajes(id_viaje)
);

CREATE TABLE tiempos_viaje (
    id_viaje            INT PRIMARY KEY,
    tiempo_estimado_min INT NOT NULL,
    tiempo_real_min     INT NOT NULL,
    FOREIGN KEY (id_viaje) REFERENCES viajes(id_viaje)
);

-- ============================================================
-- Datos semilla — 15 viajes distribuidos entre los 5 buses
-- (id_bus 101-105, id_ruta 1-4, igual que en MySQL) a lo largo
-- de 3 días, con algunos retrasos e incidencias para poder
-- calcular los indicadores del dashboard.
-- ============================================================

INSERT INTO viajes (id_bus, id_ruta, fecha, hora_salida, hora_llegada, estado) VALUES
(101, 1, '2026-09-08', '06:00', '06:45', 'COMPLETADO'),
(102, 1, '2026-09-08', '07:00', '07:50', 'RETRASADO'),
(103, 2, '2026-09-08', '06:30', '07:10', 'COMPLETADO'),
(104, 3, '2026-09-08', '06:15', '07:20', 'COMPLETADO'),
(105, 4, '2026-09-08', '06:45', '07:35', 'RETRASADO'),
(101, 1, '2026-09-09', '06:05', '06:50', 'COMPLETADO'),
(102, 1, '2026-09-09', '07:05', '07:45', 'COMPLETADO'),
(103, 2, '2026-09-09', '06:35', '07:30', 'RETRASADO'),
(104, 3, '2026-09-09', '06:20', '07:25', 'COMPLETADO'),
(105, 4, '2026-09-09', '06:50', '07:40', 'COMPLETADO'),
(101, 1, '2026-09-10', '06:00', '06:48', 'COMPLETADO'),
(102, 1, '2026-09-10', '07:10', '08:05', 'RETRASADO'),
(103, 2, '2026-09-10', '06:30', '07:12', 'COMPLETADO'),
(104, 3, '2026-09-10', '06:15', '07:18', 'COMPLETADO'),
(105, 4, '2026-09-10', '06:40', '07:22', 'CANCELADO');

INSERT INTO pasajeros_por_viaje (id_viaje, cantidad_pasajeros) VALUES
(1, 72), (2, 65), (3, 58), (4, 80), (5, 60),
(6, 75), (7, 70), (8, 62), (9, 78), (10, 66),
(11, 74), (12, 68), (13, 55), (14, 82), (15, 0);

INSERT INTO incidencias (id_viaje, tipo, descripcion, fecha) VALUES
(2, 'TRAFICO', 'Congestión en Av. 10 de Agosto por manifestación', '2026-09-08'),
(5, 'MECANICA', 'Falla en sistema de frenos, revisión menor', '2026-09-08'),
(8, 'TRAFICO', 'Cierre parcial de vía por mantenimiento', '2026-09-09'),
(12, 'TRAFICO', 'Accidente de tercero bloqueando carril', '2026-09-10'),
(15, 'MECANICA', 'Bus fuera de servicio por falla de motor, viaje cancelado', '2026-09-10');

INSERT INTO tiempos_viaje (id_viaje, tiempo_estimado_min, tiempo_real_min) VALUES
(1, 45, 45), (2, 40, 50), (3, 40, 40), (4, 60, 65), (5, 45, 50),
(6, 45, 45), (7, 40, 40), (8, 40, 55), (9, 60, 65), (10, 45, 50),
(11, 45, 48), (12, 40, 55), (13, 40, 42), (14, 60, 63), (15, 45, 0);
