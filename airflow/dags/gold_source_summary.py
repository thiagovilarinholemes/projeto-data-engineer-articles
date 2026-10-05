"""
====================================================================
DAG GOLD SOURCE SUMMARY
====================================================================

Objetivo
--------
Gerar a tabela de resumo:

    gold_source_summary

Origem
------
EXCLUSIVAMENTE:

    gold_articles

Fluxo
-----
    gold_articles
          |
          v
    service_gold_summary.py
          |
          v
    gold_source_summary
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from app.services.service_gold_summary import (
    process_gold_source_summary,
)


# ====================================================================
# CONFIGURAÇÕES PADRÃO
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
# DEFINIÇÃO DA DAG
# ====================================================================

with DAG(
    dag_id="gold_source_summary",

    description=(
        "Gera resumo estatístico por fonte "
        "utilizando exclusivamente gold_articles."
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
        "gold",
        "summary",
        "scientific-articles",
    ],

) as dag:

    # ================================================================
    # TASK
    # ================================================================

    generate_gold_source_summary = PythonOperator(
        task_id="generate_gold_source_summary",

        python_callable=process_gold_source_summary,
    )


# ====================================================================
# DEPENDÊNCIAS
# ====================================================================

generate_gold_source_summary