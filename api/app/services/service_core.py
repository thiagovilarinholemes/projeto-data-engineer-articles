"""
Serviço responsável pela comunicação
com a API CORE.
"""

import os

import httpx
from fastapi import HTTPException

from app.models.model_core import CoreArticle


CORE_URL = os.getenv(
    "CORE_URL",
    "https://api.core.ac.uk/v3"
)


# ==============================================================
# BUSCAR OBRAS
# ==============================================================

async def fetch_works_raw(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> dict:
    """
    Consulta a API CORE e retorna
    o JSON bruto.
    """

    url = (
        f"{CORE_URL}/search/works/"
    )

    params = {
        "q": query,
        "limit": limit,
        "offset": offset
    }

    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        response = await client.get(
            url,
            params=params
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "error": "core_error",
                "message": response.text
            }
        )

    try:

        return response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail={
                "error": "invalid_core_response",
                "message": (
                    "A CORE retornou "
                    "uma resposta inválida."
                )
            }
        )


# ==============================================================
# NORMALIZAÇÃO
# ==============================================================

def normalize_core_article(
    item: dict
) -> CoreArticle:
    """
    Converte um registro bruto da CORE
    para o modelo normalizado CoreArticle.
    """

    # ==========================================================
    # AUTORES
    # ==========================================================

    authors = []

    for author in item.get(
        "authors",
        []
    ):

        name = author.get(
            "name"
        )

        if name:

            authors.append(
                name
            )

    # ==========================================================
    # IDIOMA
    # ==========================================================

    language_data = item.get(
        "language"
    ) or {}

    language = language_data.get(
        "code"
    )

    # ==========================================================
    # URL DO PDF
    # ==========================================================

    pdf_url = item.get(
        "downloadUrl"
    )

    # ==========================================================
    # TEXTO COMPLETO
    # ==========================================================

    source_fulltext_urls = item.get(
        "sourceFulltextUrls",
        []
    )

    # ==========================================================
    # RETORNO NORMALIZADO
    # ==========================================================

    return CoreArticle(

        # ID da CORE.
        id=str(
            item.get("id")
        ),

        # Título.
        title=item.get(
            "title"
        ),

        # Autores.
        authors=authors,

        # Abstract.
        abstract=item.get(
            "abstract"
        ),

        # Ano.
        publication_year=item.get(
            "yearPublished"
        ),

        # DOI.
        doi=item.get(
            "doi"
        ),

        # Idioma.
        language=language,

        # Área de estudo.
        field_of_study=item.get(
            "fieldOfStudy"
        ),

        # Tipo do documento.
        document_type=item.get(
            "documentType"
        ),

        # Editora.
        publisher=item.get(
            "publisher"
        ),

        # URLs do texto completo.
        source_fulltext_urls=(
            source_fulltext_urls
        )
    )