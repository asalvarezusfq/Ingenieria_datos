-- ============================================================
-- Esquema MySQL: datos maestros/estáticos del sistema de
-- transporte público de Quito
-- ============================================================

CREATE TABLE rutas (
    id_ruta     INT PRIMARY KEY AUTO_INCREMENT,
    nombre      VARCHAR(100) NOT NULL,
    origen      VARCHAR(100) NOT NULL,
    destino     VARCHAR(100) NOT NULL
);

CREATE TABLE buses (
    id_bus      INT PRIMARY KEY,
    placa       VARCHAR(10) NOT NULL,
    modelo      VARCHAR(50) NOT NULL,
    capacidad   INT NOT NULL,
    id_ruta     INT NOT NULL,
    FOREIGN KEY (id_ruta) REFERENCES rutas(id_ruta)
);

CREATE TABLE conductores (
    id_conductor    INT PRIMARY KEY AUTO_INCREMENT,
    nombre          VARCHAR(100) NOT NULL,
    licencia        VARCHAR(20) NOT NULL,
    id_bus_asignado INT NOT NULL,
    FOREIGN KEY (id_bus_asignado) REFERENCES buses(id_bus)
);

CREATE TABLE paradas (
    id_parada   INT PRIMARY KEY AUTO_INCREMENT,
    id_ruta     INT NOT NULL,
    nombre      VARCHAR(100) NOT NULL,
    orden       INT NOT NULL,
    latitud     DECIMAL(9,6) NOT NULL,
    longitud    DECIMAL(9,6) NOT NULL,
    FOREIGN KEY (id_ruta) REFERENCES rutas(id_ruta)
);

-- ============================================================
-- Datos semilla — rutas basadas en corredores reales de Quito
-- ============================================================

INSERT INTO rutas (id_ruta, nombre, origen, destino) VALUES
(1, 'Trolebús - Troncal Central', 'El Recreo', 'La Y'),
(2, 'Ecovía', 'Río Coca', 'La Marín'),
(3, 'Corredor Central Norte-Sur', 'Carcelén', 'Quitumbe'),
(4, 'Corredor Sur Oriental', 'El Playón', 'Guamaní');

INSERT INTO buses (id_bus, placa, modelo, capacidad, id_ruta) VALUES
(101, 'PBA-1001', 'Volvo B7R', 90, 1),
(102, 'PBB-1002', 'Volvo B7R', 90, 1),
(103, 'PBC-1003', 'Mercedes-Benz O500', 85, 2),
(104, 'PBD-1004', 'Hino AK8', 80, 3),
(105, 'PBE-1005', 'Hino AK8', 80, 4);

INSERT INTO conductores (nombre, licencia, id_bus_asignado) VALUES
('Carlos Andrade', 'LIC-EC-10234', 101),
('Mónica Cevallos', 'LIC-EC-10567', 102),
('Luis Guaman', 'LIC-EC-10891', 103),
('Paola Espín', 'LIC-EC-11045', 104),
('Jorge Tituaña', 'LIC-EC-11322', 105);

-- Paradas aproximadas siguiendo cada corredor (norte -> sur o el sentido del recorrido)
INSERT INTO paradas (id_ruta, nombre, orden, latitud, longitud) VALUES
-- Ruta 1: Trolebús (El Recreo -> La Y)
(1, 'El Recreo', 1, -0.229100, -78.523000),
(1, 'La Magdalena', 2, -0.220000, -78.515000),
(1, 'La Alameda', 3, -0.212000, -78.505000),
(1, 'La Y', 4, -0.185000, -78.489000),
-- Ruta 2: Ecovía (Río Coca -> La Marín)
(2, 'Río Coca', 1, -0.176000, -78.480000),
(2, 'Naciones Unidas', 2, -0.192000, -78.487000),
(2, 'La Marín', 3, -0.220000, -78.510000),
-- Ruta 3: Corredor Central Norte-Sur (Carcelén -> Quitumbe)
(3, 'Carcelén', 1, -0.100000, -78.470000),
(3, 'El Labrador', 2, -0.150000, -78.478000),
(3, 'La Marín', 3, -0.220000, -78.510000),
(3, 'Quitumbe', 4, -0.300000, -78.548000),
-- Ruta 4: Corredor Sur Oriental (El Playón -> Guamaní)
(4, 'El Playón', 1, -0.230000, -78.520000),
(4, 'Chillogallo', 2, -0.270000, -78.540000),
(4, 'Guamaní', 3, -0.310000, -78.555000);
