from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook

from datetime import datetime
from faker import Faker
import pandas as pd
import random


RUTA_EXCEL_FINAL = "/opt/airflow/dags/dag5_reporte_consolidado.xlsx"
RUTA_LOG_NOTIFICACION = "/opt/airflow/dags/dag5_notificacion.log"

N_CLIENTES = 100
N_PEDIDOS = 400

# GENERAR Y CARGAR CLIENTES
def generar_clientes():
    fake = Faker()
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    clientes = pd.DataFrame([
        {
            "cliente_id": i,
            "nombre": fake.name(),
            "ciudad": fake.city(),
        }
        for i in range(1, N_CLIENTES + 1)
    ])

    clientes.to_sql(name="dag5_clientes", con=engine, if_exists="replace", index=False)
    print(f"Generados y cargados {len(clientes)} clientes en dag5_clientes")


# GENERAR Y CARGAR PEDIDOS
def generar_pedidos():
    fake = Faker()
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    productos = ["Laptop", "Mouse", "Teclado", "Monitor", "Silla", "Escritorio"]

    pedidos = pd.DataFrame([
        {
            "pedido_id": i,
            "cliente_id": random.randint(1, N_CLIENTES),
            "producto": random.choice(productos),
            "monto": round(random.uniform(5, 800), 2),
            "fecha": fake.date_this_year().isoformat(),
        }
        for i in range(1, N_PEDIDOS + 1)
    ])

    pedidos.to_sql(name="dag5_pedidos", con=engine, if_exists="replace", index=False)
    print(f"Generados y cargados {len(pedidos)} pedidos en dag5_pedidos")


# CONSOLIDAR AMBAS FUENTES Y GENERAR REPORTE
def generar_reporte_consolidado():
    hook = MySqlHook(mysql_conn_id="mysql_default")
    engine = hook.get_sqlalchemy_engine()

    clientes = pd.read_sql("SELECT * FROM dag5_clientes", con=engine)
    pedidos = pd.read_sql("SELECT * FROM dag5_pedidos", con=engine)

    resumen_cliente = (
        pedidos.groupby("cliente_id")
        .agg(total_pedidos=("pedido_id", "count"), total_gastado=("monto", "sum"))
        .reset_index()
        .merge(clientes, on="cliente_id", how="right")
        .fillna({"total_pedidos": 0, "total_gastado": 0})
    )

    with pd.ExcelWriter(RUTA_EXCEL_FINAL, engine="openpyxl") as writer:
        resumen_cliente.to_excel(writer, sheet_name="Resumen_Clientes", index=False)
        pedidos.to_excel(writer, sheet_name="Detalle_Pedidos", index=False)

    print(f"Reporte consolidado generado -> {RUTA_EXCEL_FINAL}")


# NOTIFICAR
def notificar():
    mensaje = f"[{datetime.now()}] Reporte generado en {RUTA_EXCEL_FINAL}"
    with open(RUTA_LOG_NOTIFICACION, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")
    print(mensaje)


# DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': 30,
}

with DAG(
    dag_id="dag5_consolidacion_reporte",
    default_args=default_args,
    description="DAG 5: genera sus fuentes clientes/pedidos, las consolida y reporta",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["taller_airflow", "consolidacion", "excel"],
) as dag:

    clientes_task = PythonOperator(
        task_id="generar_clientes",
        python_callable=generar_clientes
    )

    pedidos_task = PythonOperator(
        task_id="generar_pedidos",
        python_callable=generar_pedidos
    )

    consolidar = PythonOperator(
        task_id="generar_reporte_consolidado",
        python_callable=generar_reporte_consolidado
    )

    avisar = PythonOperator(
        task_id="notificar",
        python_callable=notificar
    )

    # ORDEN: las dos fuentes en paralelo -> consolidar -> notificar
    [clientes_task, pedidos_task] >> consolidar >> avisar
