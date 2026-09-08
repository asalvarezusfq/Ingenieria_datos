from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
import random
import re
import csv


RUTA_CRUDO = "/opt/airflow/dags/dag2_contactos_crudos.csv"
RUTA_EXTRAIDO = "/opt/airflow/dags/dag2_temp_extraido.csv"
RUTA_TRANSFORMADO = "/opt/airflow/dags/dag2_temp_limpio.csv"
N_REGISTROS = 500

# Formatos de teléfono para simular datos
FORMATOS_SUCIOS = [
    lambda n: f"0{n}",              # 09xxxxxxxx
    lambda n: f"{n}",               # 9xxxxxxxx
    lambda n: f"(09{n[1:]}) {n[1:4]}-{n[4:]}",  # con paréntesis y guiones
    lambda n: f"593-{n}",           # con prefijo de país sin +
]


def limpiar_telefono(tel):
    if pd.isna(tel):
        return None

    tel = re.sub(r"\D", "", str(tel))

    if len(tel) == 10 and tel.startswith("0"):
        return "+593" + tel[1:]

    if len(tel) == 9 and tel.startswith("9"):
        return "+593" + tel

    # Si viene con 593 al inicio ya sin '+'
    if len(tel) == 12 and tel.startswith("593"):
        return "+" + tel

    return tel


# GENERAR DATOS CRUDOS CON FAKER
def generar_datos_crudos():
    fake = Faker()

    with open(RUTA_CRUDO, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nombre", "correo", "telefono"])

        for _ in range(N_REGISTROS):
            numero_base = str(random.randint(900000000, 999999999))  # 9 dígitos
            formato = random.choice(FORMATOS_SUCIOS)
            writer.writerow([fake.name(), fake.email(), formato(numero_base)])

    print(f"Datos crudos -> {RUTA_CRUDO}")


# CARGAR CRUDOS A MYSQL
def cargar_datos_crudos():
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    df = pd.read_csv(RUTA_CRUDO)
    df.to_sql(name="dag2_contactos_crudos", con=engine, if_exists="replace", index=False)
    print("Datos crudos cargados en tabla dag2_contactos_crudos")


# EXTRAER DESDE MYSQL
def extraer_datos():
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    df = pd.read_sql("SELECT * FROM dag2_contactos_crudos", con=engine)
    df.to_csv(RUTA_EXTRAIDO, index=False)
    print(f"Extraídos {len(df)} registros desde MySQL")


# TRANSFORMAR DATOS CON PANDAS
def transformar_telefonos():
    df = pd.read_csv(RUTA_EXTRAIDO)
    df["telefono"] = df["telefono"].apply(limpiar_telefono)
    df.to_csv(RUTA_TRANSFORMADO, index=False)
    print("Teléfonos estandarizados")


# CARGAR TABLA LIMPIA
def cargar_datos():
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    df = pd.read_csv(RUTA_TRANSFORMADO)
    df.to_sql(name="dag2_contactos_limpios", con=engine, if_exists="replace", index=False)
    print("Tabla dag2_contactos_limpios actualizada en MySQL")


# DAG
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": 30,
}

with DAG(
    dag_id="dag2_limpieza_telefonos",
    default_args=default_args,
    description="DAG 2: genera datos crudos, los sube a MySQL, limpia teléfonos con pandas y carga tabla limpia",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["taller_airflow", "pandas", "mysql"],
) as dag:

    generar_crudos = PythonOperator(
        task_id="generar_datos_crudos",
        python_callable=generar_datos_crudos
    )

    cargar_crudos = PythonOperator(
        task_id="cargar_datos_crudos",
        python_callable=cargar_datos_crudos
    )

    extraer = PythonOperator(
        task_id="extraer_datos",
        python_callable=extraer_datos
    )

    transformar = PythonOperator(
        task_id="transformar_telefonos",
        python_callable=transformar_telefonos
    )

    cargar = PythonOperator(
        task_id="cargar_datos",
        python_callable=cargar_datos
    )

    # ORDEN: generar datos crudos -> cargar -> extraer -> transformar -> cargar limpio
    generar_crudos >> cargar_crudos >> extraer >> transformar >> cargar
