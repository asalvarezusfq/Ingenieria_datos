"""
Consulta el clima actual de Quito usando Open-Meteo (API pública,
no requiere API key). Devuelve un único documento normalizado.
"""
import os
import requests
from datetime import datetime, timezone

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Mapa simplificado de weathercode de Open-Meteo a una condición legible.
# (Documentación completa: https://open-meteo.com/en/docs -> WMO Weather codes)
CONDICIONES = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Neblina", 48: "Neblina con escarcha",
    51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna intensa",
    61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa",
    80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos intensos",
    95: "Tormenta",
}


def extraer_clima():
    lat = os.getenv("QUITO_LAT", "-0.1807")
    lon = os.getenv("QUITO_LON", "-78.4678")

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "relative_humidity_2m,precipitation",
        "timezone": "America/Guayaquil",
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    actual = data["current_weather"]
    # humedad/precipitación vienen por hora; tomamos la hora más cercana a "ahora"
    hora_actual = actual["time"]
    horas = data.get("hourly", {}).get("time", [])
    idx = horas.index(hora_actual) if hora_actual in horas else 0
    humedad = data.get("hourly", {}).get("relative_humidity_2m", [None])[idx]
    precipitacion = data.get("hourly", {}).get("precipitation", [None])[idx]

    registro = {
        "tipo_evento": "batch_clima",
        "ciudad": "Quito",
        "latitud": float(lat),
        "longitud": float(lon),
        "temperatura_c": actual["temperature"],
        "velocidad_viento_kmh": actual["windspeed"],
        "condicion": CONDICIONES.get(actual["weathercode"], "Desconocida"),
        "humedad_pct": humedad,
        "precipitacion_mm": precipitacion,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    print(f"Clima extraído: {registro['temperatura_c']}°C, {registro['condicion']}")
    return [registro]


if __name__ == "__main__":
    import json
    print(json.dumps(extraer_clima(), indent=2, default=str))
