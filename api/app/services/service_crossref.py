"""
Serviço responsável pela comunicação
com a API Crossref.
"""

import os

import httpx

from fastapi import HTTPException

from app.models.model_crossref import (
    CrossrefArticle
)


# ==============================================================
# CONFIGURAÇÃO
# ==============================================================

CROSSREF_URL = os.getenv(
    "CROSSREF_URL",
    "https://api.crossref.org/v1"
)


# E-mail opcional utilizado pelo Crossref
# para identificar o cliente.
CROSSREF_MAILTO = os.getenv(
    "CROSSREF_MAILTO"
)


# ==============================================================
# BUSCAR WORKS
# ==============================================================

async def fetch_works_raw(
    query: str,
    rows: int = 10,
    offset: int = 0
) -> dict:
    """
    Consulta a API Crossref e retorna
    o JSON bruto.

    Endpoint:

        /works

    Exemplo:

        /works?query=mining&rows=10
    """

    # ----------------------------------------------------------
    # URL
    # ----------------------------------------------------------

    url = (
        f"{CROSSREF_URL}/works"
    )


    # ----------------------------------------------------------
    # PARÂMETROS
    # ----------------------------------------------------------

    params = {

        # Termo pesquisado.
        "query": query,

        # Quantidade de resultados.
        "rows": rows,

        # Offset.
        "offset": offset
    }


    # ----------------------------------------------------------
    # POLITE POOL
    # ----------------------------------------------------------

    # Se o e-mail estiver configurado,
    # envia o parâmetro mailto.
    if CROSSREF_MAILTO:

        params["mailto"] = (
            CROSSREF_MAILTO
        )


    # ----------------------------------------------------------
    # HTTP
    # ----------------------------------------------------------

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.get(

            url,

            params=params,

            headers={
                "User-Agent": (
                    "ScientificArticlesAPI/1.0"
                )
            }
        )


    # ----------------------------------------------------------
    # ERRO HTTP
    # ----------------------------------------------------------

    if response.status_code != 200:

        raise HTTPException(

            status_code=response.status_code,

            detail={
                "error": "crossref_error",

                "message": response.text
            }
        )


    # ----------------------------------------------------------
    # JSON
    # ----------------------------------------------------------

    try:

        return response.json()

    except ValueError:

        raise HTTPException(

            status_code=502,

            detail={
                "error": (
                    "invalid_crossref_response"
                ),

                "message": (
                    "A Crossref retornou "
                    "uma resposta inválida."
                )
            }
        )


# ==============================================================
# NORMALIZAÇÃO
# ==============================================================

def normalize_crossref_article(
    item: dict
) -> CrossrefArticle:
    """
    Converte um registro bruto do Crossref
    para o modelo normalizado CrossrefArticle.
    """


    # ==========================================================
    # AUTORES
    # ==========================================================

    authors = []


    for author in item.get(
        "author",
        []
    ):

        # Crossref normalmente utiliza
        # given + family.
        given = author.get(
            "given"
        )

        family = author.get(
            "family"
        )


        if given and family:

            authors.append(
                f"{given} {family}"
            )

        elif family:

            authors.append(
                family
            )

        elif given:

            authors.append(
                given
            )


    # ==========================================================
    # TÍTULO
    # ==========================================================

    title = None


    titles = item.get(
        "title",
        []
    )


    if titles:

        title = titles[0]


    # ==========================================================
    # ABSTRACT
    # ==========================================================

    abstract = item.get(
        "abstract"
    )


    # ==========================================================
    # ANO
    # ==========================================================

    publication_year = None


    # Crossref pode disponibilizar
    # diferentes datas.
    published = item.get(
        "published-print"
    ) or item.get(
        "published-online"
    ) or item.get(
        "published"
    )


    if published:

        date_parts = published.get(
            "date-parts",
            []
        )


        if date_parts:

            first_date = date_parts[0]


            if first_date:

                publication_year = (
                    first_date[0]
                )


    # ==========================================================
    # CONTAINER TITLE
    # ==========================================================

    container_title = None


    containers = item.get(
        "container-title",
        []
    )


    if containers:

        container_title = (
            containers[0]
        )


    # ==========================================================
    # ISSN
    # ==========================================================

    issn = item.get(
        "ISSN",
        []
    )


    # ==========================================================
    # FULLTEXT
    # ==========================================================

    fulltext_urls = []


    for link in item.get(
        "link",
        []
    ):

        url = link.get(
            "URL"
        )


        if url:

            fulltext_urls.append(
                url
            )


    # ==========================================================
    # RETORNO
    # ==========================================================

    return CrossrefArticle(

        # DOI.
        doi=item.get(
            "DOI"
        ),

        # Título.
        title=title,

        # Autores.
        authors=authors,

        # Abstract.
        abstract=abstract,

        # Ano.
        publication_year=publication_year,

        # Revista.
        container_title=container_title,

        # Editora.
        publisher=item.get(
            "publisher"
        ),

        # Tipo.
        document_type=item.get(
            "type"
        ),

        # ISSN.
        issn=issn,

        # URL.
        url=item.get(
            "URL"
        ),

        # Texto completo.
        fulltext_urls=fulltext_urls,

        # Referências.
        reference_count=item.get(
            "reference-count"
        ),

        # Citações.
        is_referenced_by_count=item.get(
            "is-referenced-by-count"
        )
    )
