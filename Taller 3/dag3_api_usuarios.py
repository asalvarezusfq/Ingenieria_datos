from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

from datetime import datetime
import requests
import pandas as pd
import json


API_URL = "https://jsonplaceholder.typicode.com/users"
RUTA_JSON = "/opt/airflow/dags/usuarios_api.json"
RUTA_CSV = "/opt/airflow/dags/usuarios_api.csv"


# CONSUMIR DE LA API
def extraer_api():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    datos = response.json()

    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"Datos obtenidos de la API ({len(datos)} usuarios) -> {RUTA_JSON}")


# TRANSFORMAR JSON A CSV CON PANDAS

def transformar_json():
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        datos = json.load(f)

    df = pd.json_normalize(datos)

    # Nos quedamos solo con columnas de interés y renombramos
    df = df[["id", "name", "username", "email", "phone", "address.city", "company.name"]]
    df.columns = ["id", "nombre", "usuario", "correo", "telefono", "ciudad", "empresa"]

    df.to_csv(RUTA_CSV, index=False)
    print(f"JSON transformado a CSV -> {RUTA_CSV}")


# CARGAR A MYSQL
def cargar_mysql():
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    df = pd.read_csv(RUTA_CSV)
    df.to_sql(
        name="usuarios_api",
        con=engine,
        if_exists="replace",
        index=False
    )
    print("Tabla usuarios_api cargada en MySQL")


# DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': 30,
}

with DAG(
    dag_id="dag3_api_usuarios",
    default_args=default_args,
    description="DAG 3: API pública -> JSON -> pandas -> MySQL",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["taller_airflow", "api", "mysql"],
) as dag:

    crear_tabla = MySqlOperator(
        task_id="crear_tabla",
        mysql_conn_id="mysql_default",
        sql="""
        CREATE TABLE IF NOT EXISTS usuarios_api (
            id INT PRIMARY KEY,
            nombre VARCHAR(150),
            usuario VARCHAR(100),
            correo VARCHAR(150),
            telefono VARCHAR(100),
            ciudad VARCHAR(100),
            empresa VARCHAR(150)
        );
        """
    )

    extraer = PythonOperator(
        task_id="extraer_api",
        python_callable=extraer_api
    )

    transformar = PythonOperator(
        task_id="transformar_json",
        python_callable=transformar_json
    )

    cargar = PythonOperator(
        task_id="cargar_mysql",
        python_callable=cargar_mysql
    )

    # ORDEN: crear tabla -> extraer API -> transformar -> cargar
    crear_tabla >> extraer >> transformar >> cargar
