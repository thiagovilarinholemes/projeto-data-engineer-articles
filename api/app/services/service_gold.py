"""
====================================================================
SERVICE GOLD
====================================================================

Responsável pelo processamento:

    SILVER
       |
       v
    GOLD

A Silver contém dados normalizados.

A Gold contém dados enriquecidos e preparados
para consumo analítico.
"""

from app.database.database import get_connection


# ==============================================================
# PROCESSAR ARTIGOS
# ==============================================================

def process_gold_articles():

    connection = get_connection()

    cursor = connection.cursor()

    processed = 0

    try:

        # ==========================================================
        # BUSCAR ARTIGOS DA SILVER
        # ==========================================================

        cursor.execute(
            """
            SELECT
                source,
                source_id,
                title,
                authors,
                abstract,
                publication_year,
                doi,
                source_name,
                pdf_url,
                open_access

            FROM silver_articles;
            """
        )

        articles = cursor.fetchall()

        # ==========================================================
        # PROCESSAR CADA ARTIGO
        # ==========================================================

        for article in articles:

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
                open_access
            ) = article

            # ======================================================
            # QUANTIDADE DE AUTORES
            # ======================================================

            author_count = (
                len(authors)
                if authors
                else 0
            )

            # ======================================================
            # TAMANHO DO ABSTRACT
            # ======================================================

            abstract_length = (
                len(abstract)
                if abstract
                else 0
            )

            # ======================================================
            # POSSUI DOI?
            # ======================================================

            has_doi = bool(
                doi
                and doi.strip()
            )

            # ======================================================
            # POSSUI PDF?
            # ======================================================

            has_pdf = bool(
                pdf_url
                and pdf_url.strip()
            )

            # ======================================================
            # DÉCADA
            # ======================================================

            publication_decade = None

            if publication_year:

                publication_decade = (
                    publication_year // 10
                ) * 10

            # ======================================================
            # UPSERT GOLD
            # ======================================================

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
                    CURRENT_TIMESTAMP

                )

                ON CONFLICT (
                    source,
                    source_id
                )

                DO UPDATE SET

                    title = EXCLUDED.title,

                    authors = EXCLUDED.authors,

                    abstract = EXCLUDED.abstract,

                    publication_year =
                        EXCLUDED.publication_year,

                    doi = EXCLUDED.doi,

                    source_name =
                        EXCLUDED.source_name,

                    pdf_url =
                        EXCLUDED.pdf_url,

                    open_access =
                        EXCLUDED.open_access,

                    author_count =
                        EXCLUDED.author_count,

                    abstract_length =
                        EXCLUDED.abstract_length,

                    has_doi =
                        EXCLUDED.has_doi,

                    has_pdf =
                        EXCLUDED.has_pdf,

                    publication_decade =
                        EXCLUDED.publication_decade,

                    updated_at =
                        CURRENT_TIMESTAMP;
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
                    publication_decade
                )
            )

            processed += 1

        connection.commit()

        return processed

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()

        connection.close()


# ==============================================================
# ATUALIZAR RESUMO POR FONTE
# ==============================================================

def process_gold_source_summary():

    connection = get_connection()

    cursor = connection.cursor()

    try:

        # ==========================================================
        # LIMPAR RESUMO
        # ==========================================================

        cursor.execute(
            """
            DELETE FROM gold_source_summary;
            """
        )

        # ==========================================================
        # GERAR MÉTRICAS
        # ==========================================================

        cursor.execute(
            """
            INSERT INTO gold_source_summary (

                source,

                total_articles,

                articles_with_doi,

                articles_with_pdf,

                open_access_articles,

                total_authors,

                average_publication_year,

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
                    WHERE open_access = TRUE
                ) AS open_access_articles,

                COALESCE(
                    SUM(author_count),
                    0
                ) AS total_authors,

                ROUND(
                    AVG(
                        publication_year
                    ),
                    2
                ) AS average_publication_year,

                CURRENT_TIMESTAMP

            FROM gold_articles

            GROUP BY source;
            """
        )

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()

        connection.close()