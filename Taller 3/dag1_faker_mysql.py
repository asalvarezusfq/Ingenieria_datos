from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

from datetime import datetime
from faker import Faker
import csv


RUTA_CSV = "/opt/airflow/dags/datos_faker.csv"
N_REGISTROS = 5000  # reducido para que el taller


# GENERAR CSV CON FAKER
def generar_csv():
    fake = Faker()

    with open(RUTA_CSV, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["nombre", "correo", "direccion", "telefono"])

        for _ in range(N_REGISTROS):
            writer.writerow([
                fake.name(),
                fake.email(),
                fake.address(),
                fake.phone_number()
            ])

    print(f"CSV generado en {RUTA_CSV} con {N_REGISTROS} registros")

# INSERTAR A MYSQL
def insertar_mysql():
    hook = MySqlHook(mysql_conn_id="mysql_default")
    conn = hook.get_conn()
    cursor = conn.cursor()

    with open(RUTA_CSV, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO estudiantes (nombre, correo, direccion, telefono)
                VALUES (%s, %s, %s, %s)
            """, (
                row["nombre"],
                row["correo"],
                row["direccion"],
                row["telefono"]
            ))

    conn.commit()
    cursor.close()
    print("Datos insertados en MySQL (tabla estudiantes)")


# DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': 20,
}

with DAG(
    dag_id="dag1_faker_mysql",
    default_args=default_args,
    description="DAG 1: Faker -> CSV -> MySQL",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["taller_airflow", "faker", "mysql"],
) as dag:

    crear_tabla = MySqlOperator(
        task_id="crear_tabla",
        mysql_conn_id="mysql_default",
        sql="""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            correo VARCHAR(100),
            direccion TEXT,
            telefono VARCHAR(50),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    generar_csv_task = PythonOperator(
        task_id="generar_csv",
        python_callable=generar_csv
    )

    insertar_mysql_task = PythonOperator(
        task_id="insertar_mysql",
        python_callable=insertar_mysql
    )

# ORDEN: crear tabla -> generar datos -> insertar
    crear_tabla >> generar_csv_task >> insertar_mysql_task
