"""
Serviço responsável pela camada Silver.

Responsabilidades:

1. Conectar ao PostgreSQL.
2. Criar a tabela silver_articles.
3. Criar a tabela bronze_etl_control.
4. Inserir/atualizar artigos na Silver.
5. Registrar o processamento dos objetos Bronze.
"""

import os
from typing import Any

import psycopg2
from psycopg2.extras import Json


# ============================================================
# CONFIGURAÇÃO DO POSTGRESQL
# ============================================================

POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres"
)

POSTGRES_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432"
    )
)

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "scientific_articles"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "articles_user"
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "articles_password"
)


# ============================================================
# CONEXÃO
# ============================================================

def get_connection():
    """
    Cria uma conexão com o PostgreSQL.
    """

    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


# ============================================================
# CRIAÇÃO DAS TABELAS
# ============================================================

def create_silver_table():
    """
    Cria as tabelas necessárias para a camada Silver.

    Não remove tabelas existentes.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # TABELA SILVER
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS silver_articles (

                id BIGSERIAL PRIMARY KEY,

                source_api VARCHAR(50) NOT NULL,

                external_id TEXT NOT NULL,

                doi TEXT,

                title TEXT,

                authors TEXT[],

                abstract TEXT,

                publication_year INTEGER,

                container_title TEXT,

                publisher TEXT,

                language VARCHAR(20),

                field_of_study TEXT,

                document_type TEXT,

                url TEXT,

                fulltext_urls TEXT[],

                pdf_url TEXT,

                open_access BOOLEAN,

                reference_count INTEGER,

                is_referenced_by_count INTEGER,

                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT uq_silver_source_external
                    UNIQUE (
                        source_api,
                        external_id
                    )
            );
            """
        )

        # ----------------------------------------------------
        # CONTROLE DO BRONZE
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bronze_etl_control (

                id BIGSERIAL PRIMARY KEY,

                source_api VARCHAR(50) NOT NULL,

                s3_object_key TEXT NOT NULL,

                object_hash TEXT,

                status VARCHAR(20) NOT NULL
                    DEFAULT 'pending',

                error_message TEXT,

                processed_at TIMESTAMP WITH TIME ZONE,

                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT uq_bronze_etl_object
                    UNIQUE (
                        source_api,
                        s3_object_key
                    )
            );
            """
        )

        connection.commit()

        print(
            "Tabelas Silver e bronze_etl_control "
            "verificadas/criadas com sucesso."
        )

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        connection.close()


# ============================================================
# NORMALIZAÇÃO DE LISTAS
# ============================================================

def normalize_list(
    value: Any
) -> list[str]:
    """
    Garante que determinado campo seja
    convertido para uma lista de strings.
    """

    if value is None:
        return []

    if isinstance(
        value,
        str
    ):
        return [value]

    if not isinstance(
        value,
        list
    ):
        return []

    return [
        str(item)
        for item in value
        if item is not None
    ]


# ============================================================
# SALVAR ARTIGO NA SILVER
# ============================================================

def save_silver_article(
    article: dict
):
    """
    Insere ou atualiza um artigo na Silver.

    A chave de negócio é:

        source_api + external_id
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        authors = normalize_list(
            article.get("authors")
        )

        fulltext_urls = normalize_list(
            article.get("fulltext_urls")
        )

        cursor.execute(
            """
            INSERT INTO silver_articles (

                source_api,
                external_id,
                doi,
                title,
                authors,
                abstract,
                publication_year,
                container_title,
                publisher,
                language,
                field_of_study,
                document_type,
                url,
                fulltext_urls,
                pdf_url,
                open_access,
                reference_count,
                is_referenced_by_count,
                updated_at

            )
            VALUES (

                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP

            )

            ON CONFLICT (
                source_api,
                external_id
            )

            DO UPDATE SET

                doi =
                    EXCLUDED.doi,

                title =
                    EXCLUDED.title,

                authors =
                    EXCLUDED.authors,

                abstract =
                    EXCLUDED.abstract,

                publication_year =
                    EXCLUDED.publication_year,

                container_title =
                    EXCLUDED.container_title,

                publisher =
                    EXCLUDED.publisher,

                language =
                    EXCLUDED.language,

                field_of_study =
                    EXCLUDED.field_of_study,

                document_type =
                    EXCLUDED.document_type,

                url =
                    EXCLUDED.url,

                fulltext_urls =
                    EXCLUDED.fulltext_urls,

                pdf_url =
                    EXCLUDED.pdf_url,

                open_access =
                    EXCLUDED.open_access,

                reference_count =
                    EXCLUDED.reference_count,

                is_referenced_by_count =
                    EXCLUDED.is_referenced_by_count,

                updated_at =
                    CURRENT_TIMESTAMP
            """,
            (
                article.get("source_api"),
                article.get("external_id"),
                article.get("doi"),
                article.get("title"),
                authors,
                article.get("abstract"),
                article.get("publication_year"),
                article.get("container_title"),
                article.get("publisher"),
                article.get("language"),
                article.get("field_of_study"),
                article.get("document_type"),
                article.get("url"),
                fulltext_urls,
                article.get("pdf_url"),
                article.get("open_access"),
                article.get("reference_count"),
                article.get(
                    "is_referenced_by_count"
                ),
            )
        )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        connection.close()


# ============================================================
# CONTROLE BRONZE
# ============================================================

def get_bronze_control(
    source_api: str,
    s3_object_key: str
):
    """
    Retorna o registro de controle de um
    objeto Bronze.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                source_api,
                s3_object_key,
                object_hash,
                status,
                error_message,
                processed_at
            FROM bronze_etl_control
            WHERE source_api = %s
              AND s3_object_key = %s
            LIMIT 1
            """,
            (
                source_api,
                s3_object_key,
            )
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()


def start_bronze_processing(
    source_api: str,
    s3_object_key: str,
    object_hash: str | None = None
):
    """
    Cria ou atualiza o controle do objeto Bronze
    para o estado processing.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO bronze_etl_control (

                source_api,
                s3_object_key,
                object_hash,
                status,
                error_message,
                processed_at,
                updated_at

            )
            VALUES (

                %s,
                %s,
                %s,
                'processing',
                NULL,
                NULL,
                CURRENT_TIMESTAMP

            )

            ON CONFLICT (
                source_api,
                s3_object_key
            )

            DO UPDATE SET

                object_hash =
                    EXCLUDED.object_hash,

                status =
                    'processing',

                error_message =
                    NULL,

                processed_at =
                    NULL,

                updated_at =
                    CURRENT_TIMESTAMP
            """,
            (
                source_api,
                s3_object_key,
                object_hash,
            )
        )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        connection.close()


def mark_bronze_processed(
    source_api: str,
    s3_object_key: str,
    object_hash: str | None = None
):
    """
    Marca o objeto Bronze como processado.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO bronze_etl_control (

                source_api,
                s3_object_key,
                object_hash,
                status,
                processed_at,
                updated_at

            )
            VALUES (

                %s,
                %s,
                %s,
                'processed',
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP

            )

            ON CONFLICT (
                source_api,
                s3_object_key
            )

            DO UPDATE SET

                object_hash =
                    EXCLUDED.object_hash,

                status =
                    'processed',

                error_message =
                    NULL,

                processed_at =
                    CURRENT_TIMESTAMP,

                updated_at =
                    CURRENT_TIMESTAMP
            """,
            (
                source_api,
                s3_object_key,
                object_hash,
            )
        )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        connection.close()


def mark_bronze_error(
    source_api: str,
    s3_object_key: str,
    error_message: str,
    object_hash: str | None = None
):
    """
    Marca o objeto Bronze como erro.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO bronze_etl_control (

                source_api,
                s3_object_key,
                object_hash,
                status,
                error_message,
                processed_at,
                updated_at

            )
            VALUES (

                %s,
                %s,
                %s,
                'error',
                %s,
                NULL,
                CURRENT_TIMESTAMP

            )

            ON CONFLICT (
                source_api,
                s3_object_key
            )

            DO UPDATE SET

                object_hash =
                    EXCLUDED.object_hash,

                status =
                    'error',

                error_message =
                    EXCLUDED.error_message,

                processed_at =
                    NULL,

                updated_at =
                    CURRENT_TIMESTAMP
            """,
            (
                source_api,
                s3_object_key,
                object_hash,
                error_message,
            )
        )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        connection.close()


# ============================================================
# VERIFICAR SE JÁ FOI PROCESSADO
# ============================================================

def is_bronze_processed(
    source_api: str,
    s3_object_key: str
) -> bool:
    """
    Retorna True quando o objeto já foi
    processado com sucesso.
    """

    record = get_bronze_control(
        source_api,
        s3_object_key
    )

    if not record:
        return False

    status = record[4]

    return status == "processed"
