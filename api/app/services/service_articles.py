"""
Serviço responsável pela persistência dos artigos
normalizados no PostgreSQL.

Neste momento ele representa a primeira versão
da camada SILVER.
"""


# ============================================================
# IMPORTS
# ============================================================

from app.database.database import (
    get_connection
)

from app.models.model_openalex import (
    OpenAlexArticle
)


# ============================================================
# SALVAR ARTIGOS
# ============================================================

def save_articles(
    articles: list[OpenAlexArticle]
) -> int:
    """
    Insere ou atualiza artigos no PostgreSQL.

    Utiliza UPSERT para evitar duplicação.

    Parameters
    ----------
    articles:
        Lista de artigos normalizados.

    Returns
    -------
    int
        Quantidade de artigos processados.
    """

    # --------------------------------------------------------
    # Não há artigos para processar.
    # --------------------------------------------------------

    if not articles:
        return 0


    # --------------------------------------------------------
    # Abre conexão com PostgreSQL.
    # --------------------------------------------------------

    connection = get_connection()


    # --------------------------------------------------------
    # Cria cursor.
    # --------------------------------------------------------

    cursor = connection.cursor()


    # --------------------------------------------------------
    # Contador.
    # --------------------------------------------------------

    saved = 0


    try:

        # ====================================================
        # SQL DE UPSERT
        # ====================================================

        sql = """
            INSERT INTO silver_articles (
                openalex_id,
                title,
                authors,
                abstract,
                publication_year,
                doi,
                source,
                pdf_url,
                open_access
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
                %s
            )
            ON CONFLICT (openalex_id)
            DO UPDATE SET
                title = EXCLUDED.title,
                authors = EXCLUDED.authors,
                abstract = EXCLUDED.abstract,
                publication_year = EXCLUDED.publication_year,
                doi = EXCLUDED.doi,
                source = EXCLUDED.source,
                pdf_url = EXCLUDED.pdf_url,
                open_access = EXCLUDED.open_access,
                updated_at = CURRENT_TIMESTAMP;
        """


        # ====================================================
        # PROCESSA CADA ARTIGO
        # ====================================================

        for article in articles:

            # ------------------------------------------------
            # Valores enviados para o PostgreSQL.
            # ------------------------------------------------

            values = (
                article.id,
                article.title,
                article.authors,
                article.abstract,
                article.publication_year,
                article.doi,
                article.source,
                article.pdf_url,
                article.open_access
            )


            # ------------------------------------------------
            # Executa INSERT / UPDATE.
            # ------------------------------------------------

            cursor.execute(
                sql,
                values
            )


            # ------------------------------------------------
            # Incrementa contador.
            # ------------------------------------------------

            saved += 1


        # ====================================================
        # COMMIT
        # ====================================================

        connection.commit()


    except Exception:

        # ----------------------------------------------------
        # Desfaz transação.
        # ----------------------------------------------------

        connection.rollback()

        # Propaga o erro.
        raise


    finally:

        # ----------------------------------------------------
        # Fecha cursor.
        # ----------------------------------------------------

        cursor.close()


        # ----------------------------------------------------
        # Fecha conexão.
        # ----------------------------------------------------

        connection.close()


    # ========================================================
    # RETORNO
    # ========================================================

    return saved
