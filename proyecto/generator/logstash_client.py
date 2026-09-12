"""
Envía un evento (dict) a Logstash como una línea JSON por TCP.
Copia independiente de la usada en Airflow: el generador es un
servicio propio, sin dependencia del código de airflow/scripts.
"""
import socket
import json
import os


def enviar_evento(evento, host_env="LOGSTASH_HOST", puerto_env="LOGSTASH_TCP_PORT_INTERNO"):
    host = os.getenv(host_env, "logstash")
    # Puerto interno del contenedor de Logstash (no el mapeado al host)
    port = 5000
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            linea = json.dumps(evento, default=str) + "\n"
            sock.sendall(linea.encode("utf-8"))
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        print(f"No se pudo enviar evento a Logstash ({host}:{port}): {e}")
