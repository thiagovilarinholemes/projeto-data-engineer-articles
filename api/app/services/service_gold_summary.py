"""
====================================================================
GOLD SOURCE SUMMARY
====================================================================

Responsabilidade
----------------
Gerar a tabela agregada:

    gold_source_summary

Origem dos dados
----------------
EXCLUSIVAMENTE:

    gold_articles

Este serviço NÃO consulta:

    - APIs
    - Bronze
    - Silver
    - LocalStack
    - silver_articles

Fluxo:

    gold_articles
          |
          v
    agregações por source
          |
          v
    gold_source_summary


Campos utilizados da gold_articles
-----------------------------------

    source
    source_id
    title
    abstract
    authors
    publication_year
    doi
    pdf_url
    open_access
    author_count
    abstract_length
    has_doi
    has_pdf
    publication_decade


Resumo gerado por fonte
-----------------------

    total_articles
    articles_with_doi
    articles_with_pdf
    articles_with_abstract
    open_access_articles
    total_authors
    avg_author_count
    avg_abstract_length
    first_publication_year
    last_publication_year
    total_publication_decades
"""

import logging

from app.database.database import get_connection


# ====================================================================
# CONFIGURAÇÃO DE LOG
# ====================================================================

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# ====================================================================
# FUNÇÃO PRINCIPAL
# ====================================================================

def process_gold_source_summary() -> int:
    """
    Gera/atualiza a tabela gold_source_summary.

    A única origem dos dados é:

        gold_articles

    Retorna:
        Quantidade de fontes processadas.
    """

    connection = None
    cursor = None

    try:

        # ------------------------------------------------------------
        # CONEXÃO
        # ------------------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        logger.info(
            "Iniciando geração do resumo Gold por fonte."
        )

        # ------------------------------------------------------------
        # GARANTE QUE A TABELA EXISTE
        # ------------------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_source_summary (
                id SERIAL PRIMARY KEY,

                source TEXT NOT NULL UNIQUE,

                total_articles INTEGER DEFAULT 0,

                articles_with_doi INTEGER DEFAULT 0,

                articles_with_pdf INTEGER DEFAULT 0,

                articles_with_abstract INTEGER DEFAULT 0,

                open_access_articles INTEGER DEFAULT 0,

                total_authors INTEGER DEFAULT 0,

                avg_author_count NUMERIC(10, 2) DEFAULT 0,

                avg_abstract_length NUMERIC(12, 2) DEFAULT 0,

                first_publication_year INTEGER,

                last_publication_year INTEGER,

                total_publication_decades INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # ------------------------------------------------------------
        # LIMPA O RESUMO ATUAL
        # ------------------------------------------------------------
        #
        # O resumo é derivado de gold_articles.
        #
        # Como gold_articles é a fonte oficial da Gold,
        # reconstruímos completamente a tabela.
        #
        # Isso evita:
        #
        # - dados antigos
        # - fontes removidas
        # - valores acumulados incorretamente
        # ------------------------------------------------------------

        cursor.execute(
            """
            TRUNCATE TABLE gold_source_summary;
            """
        )

        # ------------------------------------------------------------
        # AGREGAÇÃO
        # ------------------------------------------------------------
        #
        # IMPORTANTE:
        #
        # A consulta abaixo utiliza SOMENTE:
        #
        #     gold_articles
        #
        # ------------------------------------------------------------

        cursor.execute(
            """
            INSERT INTO gold_source_summary (
                source,
                total_articles,
                articles_with_doi,
                articles_with_pdf,
                articles_with_abstract,
                open_access_articles,
                total_authors,
                avg_author_count,
                avg_abstract_length,
                first_publication_year,
                last_publication_year,
                total_publication_decades,
                created_at,
                updated_at
            )
            SELECT
                source,

                COUNT(*) AS total_articles,

                COUNT(*) FILTER (
                    WHERE has_doi = TRUE
                ) AS articles_with_doi,

                COUNT(*) FILTER (
                    WHERE has_pdf = TRUE
                ) AS articles_with_pdf,

                COUNT(*) FILTER (
                    WHERE abstract IS NOT NULL
                      AND TRIM(abstract) <> ''
                ) AS articles_with_abstract,

                COUNT(*) FILTER (
                    WHERE open_access = TRUE
                ) AS open_access_articles,

                COALESCE(
                    SUM(author_count),
                    0
                ) AS total_authors,

                ROUND(
                    COALESCE(
                        AVG(author_count),
                        0
                    ),
                    2
                ) AS avg_author_count,

                ROUND(
                    COALESCE(
                        AVG(abstract_length),
                        0
                    ),
                    2
                ) AS avg_abstract_length,

                MIN(publication_year)
                    AS first_publication_year,

                MAX(publication_year)
                    AS last_publication_year,

                COUNT(
                    DISTINCT publication_decade
                ) FILTER (
                    WHERE publication_decade IS NOT NULL
                ) AS total_publication_decades,

                CURRENT_TIMESTAMP,

                CURRENT_TIMESTAMP

            FROM gold_articles

            GROUP BY source

            ORDER BY total_articles DESC;
            """
        )

        # ------------------------------------------------------------
        # QUANTIDADE DE FONTES
        # ------------------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM gold_source_summary;
            """
        )

        result = cursor.fetchone()

        total_sources = result[0] if result else 0

        # ------------------------------------------------------------
        # COMMIT
        # ------------------------------------------------------------

        connection.commit()

        logger.info(
            "Resumo Gold gerado com sucesso."
        )

        logger.info(
            "Fontes processadas: %s",
            total_sources,
        )

        return total_sources

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Erro ao gerar gold_source_summary."
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ====================================================================
# COMPATIBILIDADE
# ====================================================================

def process_gold_summary() -> int:
    """
    Alias de compatibilidade.

    Permite que a DAG utilize:

        process_gold_summary()

    """

    return process_gold_source_summary()