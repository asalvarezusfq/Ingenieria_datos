"""
Utilidad compartida: envía una lista de registros (dicts) a Logstash
como líneas JSON independientes por un socket TCP.

Logstash está escuchando en LOGSTASH_HOST:5000 con codec json_lines
(ver logstash/pipeline/00-temporal.conf, se formaliza en la Fase 6).
"""
import socket
import json
import os


def enviar_a_logstash(registros, puerto_env="LOGSTASH_TCP_PORT", puerto_default=5000):
    host = os.getenv("LOGSTASH_HOST", "logstash")
    port = int(os.getenv(puerto_env, puerto_default))

    if not registros:
        print("No hay registros para enviar, se omite conexión a Logstash.")
        return

    with socket.create_connection((host, port), timeout=10) as sock:
        for registro in registros:
            linea = json.dumps(registro, default=str) + "\n"
            sock.sendall(linea.encode("utf-8"))

    print(f"Enviados {len(registros)} registros a Logstash ({host}:{port}).")
