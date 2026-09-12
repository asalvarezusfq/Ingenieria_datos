"""
Coordenadas de las paradas de cada ruta, exactamente las mismas que
se sembraron en mysql/init/01_schema_and_seed.sql, para que el
generador near real-time se mueva sobre corredores coherentes con
el catálogo batch.

Asignación de buses (igual que en la tabla `buses` de MySQL):
  101, 102 -> Ruta 1 (Trolebús: El Recreo -> La Y)
  103      -> Ruta 2 (Ecovía: Río Coca -> La Marín)
  104      -> Ruta 3 (Corredor Central Norte-Sur: Carcelén -> Quitumbe)
  105      -> Ruta 4 (Corredor Sur Oriental: El Playón -> Guamaní)
"""

RUTAS = {
    1: {
        "nombre": "Trolebús - Troncal Central",
        "paradas": [
            (-0.229100, -78.523000),  # El Recreo
            (-0.220000, -78.515000),  # La Magdalena
            (-0.212000, -78.505000),  # La Alameda
            (-0.185000, -78.489000),  # La Y
        ],
    },
    2: {
        "nombre": "Ecovía",
        "paradas": [
            (-0.176000, -78.480000),  # Río Coca
            (-0.192000, -78.487000),  # Naciones Unidas
            (-0.220000, -78.510000),  # La Marín
        ],
    },
    3: {
        "nombre": "Corredor Central Norte-Sur",
        "paradas": [
            (-0.100000, -78.470000),  # Carcelén
            (-0.150000, -78.478000),  # El Labrador
            (-0.220000, -78.510000),  # La Marín
            (-0.300000, -78.548000),  # Quitumbe
        ],
    },
    4: {
        "nombre": "Corredor Sur Oriental",
        "paradas": [
            (-0.230000, -78.520000),  # El Playón
            (-0.270000, -78.540000),  # Chillogallo
            (-0.310000, -78.555000),  # Guamaní
        ],
    },
}

# Bus -> ruta asignada (igual que en MySQL)
BUS_A_RUTA = {
    101: 1,
    102: 1,
    103: 2,
    104: 3,
    105: 4,
}
