"""
====================================================================
DAG SILVER -> GOLD
====================================================================

Processa Silver e carrega Gold.

Controle:

    gold_etl_control
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from app.services.service_gold_etl import (
    process_silver_to_gold,
)

from app.services.service_etl_control import (
    create_gold_execution,
    finish_gold_execution,
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

def executar_silver_gold():

    execution_id = create_gold_execution(
        pipeline_name="silver_to_gold",
    )

    try:

        result = process_silver_to_gold()

        # ------------------------------------------------------------
        # Caso o serviço retorne a quantidade processada.
        # ------------------------------------------------------------

        records_processed = (
            result
            if isinstance(result, int)
            else 0
        )

        finish_gold_execution(
            execution_id=execution_id,

            status="SUCCESS",

            records_read=records_processed,

            records_processed=records_processed,
        )

        return result

    except Exception as exc:

        finish_gold_execution(
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
    dag_id="silver_to_gold",

    description=(
        "Processa Silver para Gold "
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
        "silver",
        "gold",
        "etl",
        "scientific-articles",
    ],

) as dag:

    processar_silver_gold = PythonOperator(
        task_id="processar_silver_gold",

        python_callable=executar_silver_gold,
    )


processar_silver_gold