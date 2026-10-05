"""
====================================================================
ETL SILVER -> GOLD
====================================================================

Responsabilidade:
    Ler artigos da tabela silver_articles,
    calcular métricas derivadas e carregar gold_articles.

ORIGEM - SILVER
----------------
silver_articles possui:

    source_api
    external_id
    title
    authors
    abstract
    publication_year
    doi
    pdf_url
    open_access

DESTINO - GOLD
--------------
gold_articles possui:

    source
    source_id
    title
    authors
    abstract
    publication_year
    doi
    source_name
    pdf_url
    open_access
    author_count
    abstract_length
    has_doi
    has_pdf
    publication_decade

IMPORTANTE
----------
Não buscamos source_name na Silver.

O valor de source_name é derivado de source_api.
"""

import logging

from app.database.database import get_connection


# ====================================================================
# LOG
# ====================================================================

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# ====================================================================
# FUNÇÕES AUXILIARES
# ====================================================================

def calculate_author_count(authors):
    """
    Calcula a quantidade de autores.
    """

    if not authors:
        return 0

    if isinstance(authors, (list, tuple)):
        return len(authors)

    return 0


def calculate_abstract_length(abstract):
    """
    Calcula a quantidade de caracteres do resumo.
    """

    if not abstract:
        return 0

    return len(abstract)


def calculate_has_doi(doi):
    """
    Informa se o artigo possui DOI.
    """

    return bool(doi and str(doi).strip())


def calculate_has_pdf(pdf_url):
    """
    Informa se o artigo possui URL para PDF.
    """

    return bool(pdf_url and str(pdf_url).strip())


def calculate_publication_decade(publication_year):
    """
    Calcula a década da publicação.

    Exemplo:

        2024 -> 2020
        2018 -> 2010
        1997 -> 1990
    """

    if not publication_year:
        return None

    try:
        year = int(publication_year)
        return (year // 10) * 10

    except (TypeError, ValueError):
        return None


# ====================================================================
# PROCESSAMENTO SILVER -> GOLD
# ====================================================================

def process_silver_to_gold() -> int:
    """
    Processa os artigos da Silver e grava na Gold.

    Retorna:
        Quantidade de registros processados.
    """

    connection = None
    cursor = None

    processed = 0
    inserted = 0
    updated = 0

    try:

        # ------------------------------------------------------------
        # CONEXÃO
        # ------------------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        logger.info(
            "Iniciando processamento Silver -> Gold."
        )

        # ------------------------------------------------------------
        # LEITURA DA SILVER
        # ------------------------------------------------------------
        #
        # ATENÇÃO:
        # source_name NÃO EXISTE NA SILVER.
        #
        # Usamos somente colunas existentes em silver_articles.
        # ------------------------------------------------------------

        cursor.execute(
            """
            SELECT
                source_api,
                external_id,
                title,
                authors,
                abstract,
                publication_year,
                doi,
                pdf_url,
                open_access
            FROM silver_articles
            ORDER BY id;
            """
        )

        articles = cursor.fetchall()

        logger.info(
            "Artigos encontrados na Silver: %s",
            len(articles),
        )

        # ------------------------------------------------------------
        # PROCESSAMENTO
        # ------------------------------------------------------------

        for article in articles:

            (
                source_api,
                external_id,
                title,
                authors,
                abstract,
                publication_year,
                doi,
                pdf_url,
                open_access,
            ) = article

            # --------------------------------------------------------
            # MAPEAMENTO
            # --------------------------------------------------------
            #
            # Silver:
            #
            # source_api
            # external_id
            #
            # Gold:
            #
            # source
            # source_id
            # --------------------------------------------------------

            source = source_api
            source_id = external_id

            # --------------------------------------------------------
            # source_name NÃO vem da Silver.
            #
            # Ele é criado aqui a partir de source_api.
            # --------------------------------------------------------

            source_name = source_api

            # --------------------------------------------------------
            # CAMPOS DERIVADOS
            # --------------------------------------------------------

            author_count = calculate_author_count(
                authors
            )

            abstract_length = calculate_abstract_length(
                abstract
            )

            has_doi = calculate_has_doi(
                doi
            )

            has_pdf = calculate_has_pdf(
                pdf_url
            )

            publication_decade = calculate_publication_decade(
                publication_year
            )

            # --------------------------------------------------------
            # PRIMEIRO TENTA ATUALIZAR
            # --------------------------------------------------------

            cursor.execute(
                """
                UPDATE gold_articles
                SET
                    title = %s,
                    authors = %s,
                    abstract = %s,
                    publication_year = %s,
                    doi = %s,
                    source_name = %s,
                    pdf_url = %s,
                    open_access = %s,
                    author_count = %s,
                    abstract_length = %s,
                    has_doi = %s,
                    has_pdf = %s,
                    publication_decade = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    source = %s
                    AND source_id = %s;
                """,
                (
                    title,
                    authors,
                    abstract,
                    publication_year,
                    doi,
                    source_name,
                    pdf_url,
                    open_access,
                    author_count,
                    abstract_length,
                    has_doi,
                    has_pdf,
                    publication_decade,
                    source,
                    source_id,
                ),
            )

            # --------------------------------------------------------
            # SE EXISTE, FOI ATUALIZADO
            # --------------------------------------------------------

            if cursor.rowcount > 0:

                updated += 1
                processed += 1

                continue

            # --------------------------------------------------------
            # SE NÃO EXISTE, INSERE
            # --------------------------------------------------------

            cursor.execute(
                """
                INSERT INTO gold_articles (
                    source,
                    source_id,
                    title,
                    authors,
                    abstract,
                    publication_year,
                    doi,
                    source_name,
                    pdf_url,
                    open_access,
                    author_count,
                    abstract_length,
                    has_doi,
                    has_pdf,
                    publication_decade,
                    created_at,
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
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                );
                """,
                (
                    source,
                    source_id,
                    title,
                    authors,
                    abstract,
                    publication_year,
                    doi,
                    source_name,
                    pdf_url,
                    open_access,
                    author_count,
                    abstract_length,
                    has_doi,
                    has_pdf,
                    publication_decade,
                ),
            )

            inserted += 1
            processed += 1

        # ------------------------------------------------------------
        # COMMIT
        # ------------------------------------------------------------

        connection.commit()

        logger.info(
            "Processamento Silver -> Gold concluído."
        )

        logger.info(
            "Total processado: %s",
            processed,
        )

        logger.info(
            "Registros inseridos: %s",
            inserted,
        )

        logger.info(
            "Registros atualizados: %s",
            updated,
        )

        return processed

    except Exception:

        if connection:
            connection.rollback()

        logger.exception(
            "Erro durante processamento Silver -> Gold."
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

def process_gold_articles() -> int:
    """
    Mantém compatibilidade com chamadas antigas.
    """

    return process_silver_to_gold()