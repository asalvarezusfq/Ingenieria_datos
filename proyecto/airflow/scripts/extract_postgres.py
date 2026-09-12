"""
Extrae los viajes desde PostgreSQL, uniendo pasajeros, tiempos e
incidencias en un solo documento por viaje, listo para Logstash.
"""
import os
import psycopg2
import psycopg2.extras


def extraer_viajes():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
        SELECT v.id_viaje, v.id_bus, v.id_ruta, v.fecha, v.hora_salida,
               v.hora_llegada, v.estado,
               p.cantidad_pasajeros,
               t.tiempo_estimado_min, t.tiempo_real_min,
               (t.tiempo_real_min - t.tiempo_estimado_min) AS minutos_retraso
        FROM viajes v
        LEFT JOIN pasajeros_por_viaje p ON p.id_viaje = v.id_viaje
        LEFT JOIN tiempos_viaje t ON t.id_viaje = v.id_viaje
        ORDER BY v.id_viaje
    """)
    viajes = cursor.fetchall()

    cursor.execute("""
        SELECT id_viaje, tipo, descripcion, fecha
        FROM incidencias
    """)
    incidencias_por_viaje = {}
    for inc in cursor.fetchall():
        incidencias_por_viaje.setdefault(inc["id_viaje"], []).append({
            "tipo": inc["tipo"],
            "descripcion": inc["descripcion"],
            "fecha": inc["fecha"],
        })

    cursor.close()
    conn.close()

    registros = []
    for v in viajes:
        registros.append({
            "tipo_evento": "batch_viaje",
            "id_viaje": v["id_viaje"],
            "id_bus": v["id_bus"],
            "id_ruta": v["id_ruta"],
            "fecha": v["fecha"],
            "hora_salida": v["hora_salida"],
            "hora_llegada": v["hora_llegada"],
            "estado": v["estado"],
            "cantidad_pasajeros": v["cantidad_pasajeros"],
            "tiempo_estimado_min": v["tiempo_estimado_min"],
            "tiempo_real_min": v["tiempo_real_min"],
            "minutos_retraso": v["minutos_retraso"],
            "incidencias": incidencias_por_viaje.get(v["id_viaje"], []),
        })

    print(f"Extraídos {len(registros)} viajes de PostgreSQL.")
    return registros


if __name__ == "__main__":
    import json
    print(json.dumps(extraer_viajes(), indent=2, default=str))
