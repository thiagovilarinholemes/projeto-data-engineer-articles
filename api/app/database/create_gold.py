"""
====================================================================
CRIAÇÃO DAS TABELAS GOLD
====================================================================

Responsável pela criação das tabelas utilizadas
pela camada GOLD.

Arquitetura:

    BRONZE
       |
       v
    SILVER
       |
       v
     GOLD

A GOLD contém dados preparados para:

    - dashboards
    - BI
    - relatórios
    - consultas analíticas
    - APIs de consumo
    - aplicações

Tabelas:

    gold_articles
        Dados enriquecidos dos artigos.

    gold_source_summary
        Métricas agregadas por fonte.
"""

from app.database.database import get_connection


def create_gold_tables():

    connection = get_connection()

    cursor = connection.cursor()

    try:

        # ==========================================================
        # GOLD ARTICLES
        # ==========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_articles (

                id SERIAL PRIMARY KEY,

                source TEXT NOT NULL,

                source_id TEXT NOT NULL,

                title TEXT,

                authors TEXT[],

                abstract TEXT,

                publication_year INTEGER,

                doi TEXT,

                source_name TEXT,

                pdf_url TEXT,

                open_access BOOLEAN DEFAULT FALSE,

                author_count INTEGER DEFAULT 0,

                abstract_length INTEGER DEFAULT 0,

                has_doi BOOLEAN DEFAULT FALSE,

                has_pdf BOOLEAN DEFAULT FALSE,

                publication_decade INTEGER,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE (
                    source,
                    source_id
                )
            );
            """
        )

        # ==========================================================
        # GOLD SOURCE SUMMARY
        # ==========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS gold_source_summary (

                id SERIAL PRIMARY KEY,

                source TEXT NOT NULL UNIQUE,

                total_articles INTEGER DEFAULT 0,

                articles_with_doi INTEGER DEFAULT 0,

                articles_with_pdf INTEGER DEFAULT 0,

                open_access_articles INTEGER DEFAULT 0,

                total_authors INTEGER DEFAULT 0,

                average_publication_year NUMERIC(10,2),

                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        connection.commit()

        print(
            "Tabelas GOLD criadas/verificadas com sucesso."
        )

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()

        connection.close()