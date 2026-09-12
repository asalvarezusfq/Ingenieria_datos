"""
DAG: flujo Batch del sistema de monitoreo de transporte público.

Orquesta 3 tareas independientes entre sí (no comparten datos):
  1. Extraer catálogo de buses de MySQL  -> enviar a Logstash
  2. Extraer viajes de PostgreSQL         -> enviar a Logstash
  3. Extraer clima actual (Open-Meteo)    -> enviar a Logstash

Se ejecuta manualmente durante el desarrollo/demo (schedule=None).
Cuando quieras automatizarlo, cambia schedule="@hourly" o similar.
"""
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append("/opt/airflow/scripts")

from extract_mysql import extraer_buses          # noqa: E402
from extract_postgres import extraer_viajes      # noqa: E402
from extract_clima import extraer_clima          # noqa: E402
from send_to_logstash import enviar_a_logstash   # noqa: E402


def tarea_batch_mysql():
    registros = extraer_buses()
    enviar_a_logstash(registros)


def tarea_batch_postgres():
    registros = extraer_viajes()
    enviar_a_logstash(registros)


def tarea_batch_clima():
    registros = extraer_clima()
    enviar_a_logstash(registros)


with DAG(
    dag_id="batch_transporte_quito",
    description="Extrae buses (MySQL), viajes (PostgreSQL) y clima (Open-Meteo) hacia Logstash/Elasticsearch",
    start_date=datetime(2026, 1, 1),
    schedule=None,       # manual para desarrollo y demo; cambiar a "@hourly" si se desea automatizar
    catchup=False,
    tags=["transporte", "batch"],
) as dag:

    extraer_mysql = PythonOperator(
        task_id="extraer_y_enviar_mysql",
        python_callable=tarea_batch_mysql,
    )

    extraer_postgres = PythonOperator(
        task_id="extraer_y_enviar_postgres",
        python_callable=tarea_batch_postgres,
    )

    extraer_clima_task = PythonOperator(
        task_id="extraer_y_enviar_clima",
        python_callable=tarea_batch_clima,
    )

    # Las 3 tareas son independientes entre sí (no hay dependencia de datos),
    # así que corren en paralelo dentro del mismo DAG run.
