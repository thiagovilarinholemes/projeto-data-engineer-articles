"""
====================================================================
SERVICE ETL CONTROL
====================================================================

Responsabilidade
----------------
Controlar e registrar as execuções dos pipelines ETL.

Tabelas:

    silver_etl_control
    gold_etl_control

O serviço NÃO executa ETL.

Ele apenas registra:

    RUNNING
    SUCCESS
    FAILED

Também registra:

    - pipeline
    - execution_id
    - fonte
    - quantidade de registros
    - mensagem de erro
    - início
    - fim

====================================================================
"""

import logging
import uuid

from app.database.database import get_connection


# ====================================================================
# LOG
# ====================================================================

logger = logging.getLogger(__name__)


# ====================================================================
# SILVER ETL CONTROL
# ====================================================================

def create_silver_execution(
    pipeline_name: str,
    source_api: str | None = None,
) -> str:
    """
    Cria uma execução na tabela silver_etl_control.

    Status inicial:

        RUNNING

    Retorna:

        execution_id
    """

    execution_id = str(uuid.uuid4())

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO silver_etl_control (
                pipeline_name,
                execution_id,
                status,
                source_api,
                records_read,
                records_inserted,
                records_updated,
                records_processed,
                records_failed,
                started_at
            )
            VALUES (
                %s,
                %s,
                'RUNNING',
                %s,
                0,
                0,
                0,
                0,
                0,
                CURRENT_TIMESTAMP
            );
            """,
            (
                pipeline_name,
                execution_id,
                source_api,
            ),
        )

        connection.commit()

        logger.info(
            "Silver ETL iniciado. execution_id=%s",
            execution_id,
        )

        return execution_id

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Erro ao criar controle Silver."
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


def finish_silver_execution(
    execution_id: str,
    status: str,
    records_read: int = 0,
    records_inserted: int = 0,
    records_updated: int = 0,
    records_processed: int = 0,
    records_failed: int = 0,
    error_message: str | None = None,
):
    """
    Finaliza uma execução Silver.

    Status esperado:

        SUCCESS
        FAILED
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE silver_etl_control
            SET
                status = %s,
                records_read = %s,
                records_inserted = %s,
                records_updated = %s,
                records_processed = %s,
                records_failed = %s,
                error_message = %s,
                finished_at = CURRENT_TIMESTAMP
            WHERE execution_id = %s;
            """,
            (
                status,
                records_read,
                records_inserted,
                records_updated,
                records_processed,
                records_failed,
                error_message,
                execution_id,
            ),
        )

        connection.commit()

        logger.info(
            "Silver ETL finalizado. "
            "execution_id=%s status=%s",
            execution_id,
            status,
        )

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Erro ao finalizar controle Silver."
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ====================================================================
# GOLD ETL CONTROL
# ====================================================================

def create_gold_execution(
    pipeline_name: str,
    source: str | None = None,
) -> str:
    """
    Cria uma execução na tabela gold_etl_control.

    Status inicial:

        RUNNING

    Retorna:

        execution_id
    """

    execution_id = str(uuid.uuid4())

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO gold_etl_control (
                pipeline_name,
                execution_id,
                status,
                source,
                records_read,
                records_inserted,
                records_updated,
                records_processed,
                records_failed,
                started_at
            )
            VALUES (
                %s,
                %s,
                'RUNNING',
                %s,
                0,
                0,
                0,
                0,
                0,
                CURRENT_TIMESTAMP
            );
            """,
            (
                pipeline_name,
                execution_id,
                source,
            ),
        )

        connection.commit()

        logger.info(
            "Gold ETL iniciado. execution_id=%s",
            execution_id,
        )

        return execution_id

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Erro ao criar controle Gold."
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


def finish_gold_execution(
    execution_id: str,
    status: str,
    records_read: int = 0,
    records_inserted: int = 0,
    records_updated: int = 0,
    records_processed: int = 0,
    records_failed: int = 0,
    error_message: str | None = None,
):
    """
    Finaliza uma execução Gold.

    Status esperado:

        SUCCESS
        FAILED
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE gold_etl_control
            SET
                status = %s,
                records_read = %s,
                records_inserted = %s,
                records_updated = %s,
                records_processed = %s,
                records_failed = %s,
                error_message = %s,
                finished_at = CURRENT_TIMESTAMP
            WHERE execution_id = %s;
            """,
            (
                status,
                records_read,
                records_inserted,
                records_updated,
                records_processed,
                records_failed,
                error_message,
                execution_id,
            ),
        )

        connection.commit()

        logger.info(
            "Gold ETL finalizado. "
            "execution_id=%s status=%s",
            execution_id,
            status,
        )

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Erro ao finalizar controle Gold."
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()