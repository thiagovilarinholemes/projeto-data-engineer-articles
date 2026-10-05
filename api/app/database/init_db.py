"""
====================================================================
INICIALIZAÇÃO DO BANCO DE DADOS
====================================================================

Responsável pela criação das tabelas utilizadas
pelo projeto de artigos científicos.

Arquitetura:

    APIs Científicas
           |
           v
        BRONZE
       LocalStack S3
           |
           v
          ETL
           |
           v
        SILVER
       PostgreSQL

Tabelas:

    silver_articles
        Dados normalizados dos artigos.

    bronze_etl_control
        Controle dos objetos Bronze processados pelo ETL.

Observação:

    Este arquivo é responsável somente pela criação
    e preparação do schema do PostgreSQL.

    O processamento Bronze -> Silver fica no:

        app/services/service_etl.py

    A persistência dos artigos fica no:

        app/services/service_silver.py
====================================================================
"""

from app.database.database import get_connection


# ==================================================================
# CRIAÇÃO DAS TABELAS
# ==================================================================

def create_tables():
    """
    Cria todas as tabelas necessárias para o projeto.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ==========================================================
        # TABELA SILVER
        # ==========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS silver_articles (

                id BIGSERIAL PRIMARY KEY,

                --------------------------------------------------
                -- IDENTIFICAÇÃO DA ORIGEM
                --------------------------------------------------

                source_api VARCHAR(50) NOT NULL,

                external_id TEXT NOT NULL,

                --------------------------------------------------
                -- IDENTIFICAÇÃO DO ARTIGO
                --------------------------------------------------

                doi TEXT,

                title TEXT,

                authors TEXT[],

                abstract TEXT,

                publication_year INTEGER,

                --------------------------------------------------
                -- PUBLICAÇÃO
                --------------------------------------------------

                container_title TEXT,

                publisher TEXT,

                language VARCHAR(20),

                field_of_study TEXT,

                document_type TEXT,

                --------------------------------------------------
                -- URLs
                --------------------------------------------------

                url TEXT,

                fulltext_urls TEXT[],

                pdf_url TEXT,

                --------------------------------------------------
                -- ACESSO ABERTO
                --------------------------------------------------

                open_access BOOLEAN,

                --------------------------------------------------
                -- CITAÇÕES
                --------------------------------------------------

                reference_count INTEGER,

                is_referenced_by_count INTEGER,

                --------------------------------------------------
                -- CONTROLE
                --------------------------------------------------

                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                --------------------------------------------------
                -- CHAVE ÚNICA
                --------------------------------------------------

                CONSTRAINT uq_silver_source_external
                    UNIQUE (
                        source_api,
                        external_id
                    )

            );
            """
        )


        # ==========================================================
        # ÍNDICES DA SILVER
        # ==========================================================

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_silver_articles_source_api
            ON silver_articles(source_api);
            """
        )


        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_silver_articles_external_id
            ON silver_articles(external_id);
            """
        )


        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_silver_articles_year
            ON silver_articles(publication_year);
            """
        )


        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_silver_articles_doi
            ON silver_articles(doi);
            """
        )


        # ==========================================================
        # TABELA DE CONTROLE DO ETL
        # ==========================================================

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bronze_etl_control (

                id BIGSERIAL PRIMARY KEY,

                --------------------------------------------------
                -- API DE ORIGEM
                --------------------------------------------------

                source_api VARCHAR(50) NOT NULL,

                --------------------------------------------------
                -- OBJETO ORIGINAL NO S3
                --------------------------------------------------

                s3_object_key TEXT NOT NULL,

                --------------------------------------------------
                -- HASH DO OBJETO
                --------------------------------------------------

                object_hash TEXT,

                --------------------------------------------------
                -- STATUS DO ETL
                --------------------------------------------------

                status VARCHAR(20) NOT NULL
                    DEFAULT 'pending',

                --------------------------------------------------
                -- ERRO
                --------------------------------------------------

                error_message TEXT,

                --------------------------------------------------
                -- PROCESSAMENTO
                --------------------------------------------------

                processed_at TIMESTAMP WITH TIME ZONE,

                --------------------------------------------------
                -- CONTROLE DE CRIAÇÃO/ATUALIZAÇÃO
                --------------------------------------------------

                created_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TIMESTAMP WITH TIME ZONE
                    DEFAULT CURRENT_TIMESTAMP,

                --------------------------------------------------
                -- OBJETO ÚNICO
                --------------------------------------------------

                CONSTRAINT uq_bronze_etl_object
                    UNIQUE (
                        source_api,
                        s3_object_key
                    )

            );
            """
        )


        # ==========================================================
        # ÍNDICES DO CONTROLE DO ETL
        # ==========================================================

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_bronze_etl_control_source_api
            ON bronze_etl_control(source_api);
            """
        )


        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_bronze_etl_control_status
            ON bronze_etl_control(status);
            """
        )


        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_bronze_etl_control_processed_at
            ON bronze_etl_control(processed_at);
            """
        )


        # ==========================================================
        # COMMIT
        # ==========================================================

        connection.commit()


        print(
            "=================================================="
        )

        print(
            "Banco de dados inicializado com sucesso."
        )

        print(
            "Tabela verificada: silver_articles"
        )

        print(
            "Tabela verificada: bronze_etl_control"
        )

        print(
            "Arquitetura Bronze -> Silver preparada."
        )

        print(
            "=================================================="
        )


    except Exception as error:

        connection.rollback()

        print(
            "Erro ao criar as tabelas:"
        )

        print(
            error
        )

        raise


    finally:

        cursor.close()
        connection.close()


# ==================================================================
# COMPATIBILIDADE
# ==================================================================

def create_silver_articles_table():
    """
    Mantém compatibilidade com chamadas antigas
    utilizadas pelo projeto.
    """

    create_tables()


# ==================================================================
# EXECUÇÃO DIRETA
# ==================================================================

if __name__ == "__main__":

    create_tables()
