from airflow import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime
import pandas as pd
import random


RUTA_CSV_VENTAS = "/opt/airflow/dags/ventas.csv"
RUTA_CSV_METRICAS = "/opt/airflow/dags/ventas_metricas.csv"
RUTA_EXCEL = "/opt/airflow/dags/reporte_ventas.xlsx"

PRODUCTOS = [
    ("Laptop", "Tecnología"),
    ("Mouse", "Tecnología"),
    ("Escritorio", "Muebles"),
    ("Silla", "Muebles"),
    ("Cuaderno", "Papelería"),
    ("Esfero", "Papelería"),
]


# GENERAR DATASET DE VENTAS
def generar_dataset_ventas():
    filas = []
    for _ in range(1000):
        producto, categoria = random.choice(PRODUCTOS)
        cantidad = random.randint(1, 10)
        precio_unitario = round(random.uniform(2, 500), 2)
        fecha = datetime(2026, random.randint(1, 8), random.randint(1, 28))

        filas.append({
            "producto": producto,
            "categoria": categoria,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "fecha": fecha.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(filas)
    df.to_csv(RUTA_CSV_VENTAS, index=False)
    print(f"Dataset de ventas generado -> {RUTA_CSV_VENTAS}")


# CALCULAR METRICAS CON PANDAS
def calcular_metricas():
    df = pd.read_csv(RUTA_CSV_VENTAS)
    df["total_venta"] = df["cantidad"] * df["precio_unitario"]

    resumen = (
        df.groupby("categoria")
        .agg(unidades_vendidas=("cantidad", "sum"), total_categoria=("total_venta", "sum"))
        .reset_index()
    )

    df.to_csv(RUTA_CSV_VENTAS, index=False)  # detalle con columna total_venta
    resumen.to_csv(RUTA_CSV_METRICAS, index=False)
    print("Métricas calculadas por categoría")


# EXPORTAR REPORTE A EXCEL
def exportar_excel():
    detalle = pd.read_csv(RUTA_CSV_VENTAS)
    resumen = pd.read_csv(RUTA_CSV_METRICAS)

    with pd.ExcelWriter(RUTA_EXCEL, engine="openpyxl") as writer:
        detalle.to_excel(writer, sheet_name="Detalle", index=False)
        resumen.to_excel(writer, sheet_name="Resumen_Categoria", index=False)

    print(f"Reporte Excel generado -> {RUTA_EXCEL}")


# DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': 30,
}

with DAG(
    dag_id="dag4_reporte_ventas_excel",
    default_args=default_args,
    description="DAG 4: Dataset ventas -> pandas -> reporte Excel",
    schedule_interval=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["taller_airflow", "pandas", "excel"],
) as dag:

    generar_datos = PythonOperator(
        task_id="generar_dataset_ventas",
        python_callable=generar_dataset_ventas
    )

    metricas = PythonOperator(
        task_id="calcular_metricas",
        python_callable=calcular_metricas
    )

    exportar = PythonOperator(
        task_id="exportar_excel",
        python_callable=exportar_excel
    )

    # ORDEN: generar -> calcular métricas -> exportar
    generar_datos >> metricas >> exportar
