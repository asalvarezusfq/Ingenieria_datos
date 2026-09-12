"""
Generador near real-time: simula 5 buses moviéndose por corredores
reales de Quito, emitiendo posiciones y eventos cada
GENERATOR_INTERVAL_SECONDS segundos hacia Logstash.

No usa datos GPS reales de operadores; interpola entre las paradas
definidas en rutas_quito.py (las mismas que en el catálogo de MySQL).
"""
import os
import time
import random
from datetime import datetime, timezone

from rutas_quito import RUTAS, BUS_A_RUTA
from logstash_client import enviar_evento

INTERVALO = int(os.getenv("GENERATOR_INTERVAL_SECONDS", 7))
PASO_INTERPOLACION = 0.25  # fracción de segmento avanzada por tick
PROB_DETENIDO = 0.10
PROB_RETRASADO = 0.10


def interpolar(p1, p2, t):
    lat = p1[0] + (p2[0] - p1[0]) * t
    lon = p1[1] + (p2[1] - p1[1]) * t
    return lat, lon


class EstadoBus:
    """Mantiene el progreso de un bus a lo largo de su ruta."""

    def __init__(self, id_bus, id_ruta):
        self.id_bus = id_bus
        self.id_ruta = id_ruta
        self.paradas = RUTAS[id_ruta]["paradas"]
        self.segmento = 0       # índice de la parada de origen del tramo actual
        self.avance = 0.0       # progreso dentro del tramo actual [0,1]
        self.iniciado = False

    def siguiente_evento(self):
        # Primer evento del ciclo
        if not self.iniciado:
            self.iniciado = True
            lat, lon = self.paradas[0]
            return self._evento(lat, lon, "INICIA_RECORRIDO", velocidad=0)

        # Ocasionalmente el bus se detiene o reporta retraso sin avanzar
        r = random.random()
        if r < PROB_DETENIDO:
            lat, lon = interpolar(
                self.paradas[self.segmento],
                self.paradas[self.segmento + 1],
                self.avance,
            )
            return self._evento(lat, lon, "DETENIDO", velocidad=0)
        elif r < PROB_DETENIDO + PROB_RETRASADO:
            lat, lon = interpolar(
                self.paradas[self.segmento],
                self.paradas[self.segmento + 1],
                self.avance,
            )
            return self._evento(lat, lon, "RETRASADO", velocidad=round(random.uniform(5, 15), 1))

        # Avance normal
        self.avance += PASO_INTERPOLACION
        if self.avance >= 1.0:
            self.avance = 0.0
            self.segmento += 1
            lat, lon = self.paradas[self.segmento]

            if self.segmento == len(self.paradas) - 1:
                # Llegó a la última parada: fin de recorrido, reinicia el ciclo
                evento = self._evento(lat, lon, "FINALIZA_RECORRIDO", velocidad=0)
                self.segmento = 0
                self.avance = 0.0
                self.iniciado = False
                return evento
            else:
                return self._evento(lat, lon, "LLEGA_PARADA", velocidad=0)

        lat, lon = interpolar(
            self.paradas[self.segmento],
            self.paradas[self.segmento + 1],
            self.avance,
        )
        return self._evento(lat, lon, "EN_RUTA", velocidad=round(random.uniform(20, 45), 1))

    def _evento(self, lat, lon, estado, velocidad):
        return {
            "tipo_evento": "realtime_evento",
            "id_bus": self.id_bus,
            "id_ruta": self.id_ruta,
            "latitud": round(lat, 6),
            "longitud": round(lon, 6),
            "velocidad": velocidad,
            "estado": estado,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def main():
    buses = [EstadoBus(id_bus, id_ruta) for id_bus, id_ruta in BUS_A_RUTA.items()]
    print(f"Generador iniciado: {len(buses)} buses, intervalo {INTERVALO}s.")

    while True:
        for bus in buses:
            evento = bus.siguiente_evento()
            enviar_evento(evento)
            print(evento)
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
