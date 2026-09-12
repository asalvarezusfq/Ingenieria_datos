"""
Extrae el catálogo de buses (join con rutas y conductores) desde MySQL
y lo normaliza a una lista de dicts listos para enviar a Logstash.
"""
import os
import mysql.connector


def extraer_buses():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.id_bus, b.placa, b.modelo, b.capacidad,
               r.id_ruta, r.nombre AS nombre_ruta, r.origen, r.destino,
               c.nombre AS nombre_conductor
        FROM buses b
        JOIN rutas r ON b.id_ruta = r.id_ruta
        LEFT JOIN conductores c ON c.id_bus_asignado = b.id_bus
    """)
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    registros = []
    for fila in filas:
        registros.append({
            "tipo_evento": "batch_bus",
            "id_bus": fila["id_bus"],
            "placa": fila["placa"],
            "modelo": fila["modelo"],
            "capacidad": fila["capacidad"],
            "id_ruta": fila["id_ruta"],
            "nombre_ruta": fila["nombre_ruta"],
            "origen": fila["origen"],
            "destino": fila["destino"],
            "conductor": fila["nombre_conductor"],
        })

    print(f"Extraídos {len(registros)} buses de MySQL.")
    return registros


if __name__ == "__main__":
    import json
    print(json.dumps(extraer_buses(), indent=2, default=str))
