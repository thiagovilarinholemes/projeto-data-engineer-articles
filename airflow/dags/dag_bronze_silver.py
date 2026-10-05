"""
====================================================================
DAG BRONZE -> SILVER
====================================================================

Processa dados Bronze e carrega a camada Silver.

Controle:

    silver_etl_control
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from app.services.service_etl import (
    process_openalex_bronze,
)

from app.services.service_etl_control import (
    create_silver_execution,
    finish_silver_execution,
)


# ====================================================================
# CONFIGURAÇÕES
# ====================================================================

default_args = {
    "owner": "thiago",

    "depends_on_past": False,

    "retries": 2,

    "retry_delay": timedelta(
        minutes=2
    ),
}


# ====================================================================
# EXECUÇÃO CONTROLADA
# ====================================================================

def executar_etl_silver():

    execution_id = create_silver_execution(
        pipeline_name="bronze_to_silver",
        source_api="openalex",
    )

    try:

        result = process_openalex_bronze()

        # ------------------------------------------------------------
        # O ETL existente continua sendo responsável pelo processamento.
        #
        # Caso ele retorne um inteiro, usamos como quantidade.
        # Caso não retorne nada, consideramos 0.
        # ------------------------------------------------------------

        records_processed = (
            result
            if isinstance(result, int)
            else 0
        )

        finish_silver_execution(
            execution_id=execution_id,

            status="SUCCESS",

            records_read=records_processed,

            records_processed=records_processed,
        )

        return result

    except Exception as exc:

        finish_silver_execution(
            execution_id=execution_id,

            status="FAILED",

            records_failed=1,

            error_message=str(exc),
        )

        raise


# ====================================================================
# DAG
# ====================================================================

with DAG(
    dag_id="bronze_to_silver",

    description=(
        "Processa Bronze para Silver "
        "e registra o controle da execução."
    ),

    default_args=default_args,

    start_date=datetime(
        2026,
        1,
        1,
    ),

    schedule="*/5 * * * *",

    catchup=False,

    max_active_runs=1,

    tags=[
        "bronze",
        "silver",
        "etl",
        "openalex",
    ],

) as dag:

    processar_bronze_silver = PythonOperator(
        task_id="processar_bronze_silver",

        python_callable=executar_etl_silver,
    )


processar_bronze_silver