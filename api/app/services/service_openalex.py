"""
Serviço responsável pela comunicação com a API OpenAlex.

Responsabilidades:

1. Consultar a OpenAlex.
2. Validar erros da API.
3. Normalizar os artigos.
4. Disponibilizar o JSON original para a camada Bronze.
"""


# ============================================================
# IMPORTS
# ============================================================

import math
import os

import httpx
from fastapi import HTTPException

from app.models.model_openalex import (
    OpenAlexArticle,
    OpenAlexSearchResponse
)


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# URL da API OpenAlex.
OPENALEX_URL = os.getenv(
    "OPENALEX_URL",
    # "https://api.openalex.org/works"
)


# Chave da API OpenAlex.
OPENALEX_API_KEY = os.getenv(
     "OPENALEX_KEY",
) 

# Validando a chave da API.
if not OPENALEX_API_KEY:
    raise RuntimeError(
        "OPENALEX_API_KEY não configurada."
    )
# OPENALEX_API_KEY = "NVrcIaJozfxc1tmUfbyn1H"

# ============================================================
# ABSTRACT
# ============================================================

def extract_abstract(
    abstract_inverted_index: dict | None
) -> str | None:
    """
    Converte o formato inverted index da OpenAlex
    em um texto normal.

    A OpenAlex pode retornar o resumo neste formato:

        {
            "This": [0],
            "paper": [1],
            "presents": [2]
        }

    Esta função reconstrói:

        This paper presents
    """

    # Se não houver resumo, retorna None.
    if not abstract_inverted_index:
        return None

    # Lista temporária contendo:
    #
    # (posição, palavra)
    words = []

    # Percorre as palavras do inverted index.
    for word, positions in (
        abstract_inverted_index.items()
    ):

        # Uma palavra pode possuir uma ou
        # mais posições.
        for position in positions:

            words.append(
                (
                    position,
                    word
                )
            )

    # Ordena pela posição original.
    words.sort(
        key=lambda item: item[0]
    )

    # Reconstrói o texto.
    return " ".join(
        word
        for _, word in words
    )


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalize_article(
    item: dict
) -> OpenAlexArticle:
    """
    Converte um registro bruto da OpenAlex
    para o modelo normalizado da aplicação.
    """

    # Lista de autores.
    authors = []

    # Percorre os autores do artigo.
    for authorship in item.get(
        "authorships",
        []
    ):

        # Obtém o objeto author.
        author = authorship.get(
            "author"
        )

        # Verifica se existe autor.
        if author:

            # Obtém o nome.
            name = author.get(
                "display_name"
            )

            # Adiciona se existir.
            if name:
                authors.append(
                    name
                )

    # Obtém a localização principal.
    primary_location = (
        item.get(
            "primary_location"
        )
        or {}
    )

    # Obtém informações da fonte.
    source_data = (
        primary_location.get(
            "source"
        )
        or {}
    )

    # Nome da revista/fonte.
    source = source_data.get(
        "display_name"
    )

    # URL do PDF.
    pdf_url = primary_location.get(
        "pdf_url"
    )

    # Obtém informações de Open Access.
    open_access_data = (
        item.get(
            "open_access"
        )
        or {}
    )

    # Verifica se é Open Access.
    open_access = open_access_data.get(
        "is_oa",
        False
    )

    # Cria o objeto normalizado.
    return OpenAlexArticle(

        # ID da OpenAlex.
        id=item.get(
            "id"
        ),

        # Título.
        title=item.get(
            "title"
        ),

        # Autores.
        authors=authors,

        # Abstract reconstruído.
        abstract=extract_abstract(
            item.get(
                "abstract_inverted_index"
            )
        ),

        # Ano.
        publication_year=item.get(
            "publication_year"
        ),

        # DOI.
        doi=item.get(
            "doi"
        ),

        # Fonte/revista.
        source=source,

        # PDF.
        pdf_url=pdf_url,

        # Open Access.
        open_access=open_access
    )


# ============================================================
# CONSULTA BRUTA
# ============================================================

async def fetch_articles_raw(
    query: str,
    page: int = 1,
    per_page: int = 10,
    year: int | None = None,
    open_access: bool | None = None,
    sort: str | None = None
) -> dict:
    """
    Consulta a OpenAlex e retorna o JSON original.

    Esta função é importante para a arquitetura
    Bronze.

    Fluxo:

        OpenAlex
            ↓
        JSON original
            ↓
        MinIO
    """

    # Verifica se a chave existe.
    if not OPENALEX_API_KEY:

        raise HTTPException(
            status_code=500,
            detail=(
                "OPENALEX_API_KEY "
                "não configurada."
            )
        )

    # Parâmetros enviados para a OpenAlex.
    params = {

        # Termo da pesquisa.
        "search": query,

        # Página.
        "page": page,

        # Quantidade por página.
        "per-page": per_page,

        # Chave da API.
        "api_key": OPENALEX_API_KEY
    }

    # Filtro por ano.
    if year is not None:

        params["filter"] = (
            f"publication_year:{year}"
        )

    # Filtro Open Access.
    if open_access is True:

        if "filter" in params:

            params["filter"] += (
                ",is_oa:true"
            )

        else:

            params["filter"] = (
                "is_oa:true"
            )

    # Ordenação.
    if sort:
        params["sort"] = sort

    # Cria cliente HTTP assíncrono.
    async with httpx.AsyncClient(
        timeout=30
    ) as client:

        # Faz a requisição.
        response = await client.get(

            # Endpoint.
            OPENALEX_URL,

            # Query parameters.
            params=params
        )

    # Trata rate limit.
    if response.status_code == 429:

        raise HTTPException(
            status_code=429,
            detail={
                "error": (
                    "openalex_rate_limit"
                ),
                "message": (
                    "A OpenAlex recusou "
                    "a requisição por "
                    "limite de requisições."
                )
            }
        )

    # Trata outros erros.
    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "error": "openalex_error",
                "message": response.text
            }
        )

    # Converte a resposta para JSON.
    try:

        data = response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail={
                "error": (
                    "invalid_openalex_response"
                ),
                "message": (
                    "A OpenAlex retornou "
                    "uma resposta inválida."
                )
            }
        )

    # Retorna o JSON original.
    return data


# ============================================================
# PESQUISA NORMALIZADA
# ============================================================

async def search_articles(
    query: str,
    page: int = 1,
    per_page: int = 10,
    year: int | None = None,
    open_access: bool | None = None,
    sort: str | None = None
) -> OpenAlexSearchResponse:
    """
    Pesquisa artigos na OpenAlex.

    Esta função utiliza a consulta bruta
    e depois transforma os resultados
    para o modelo normalizado.
    """

    # Busca os dados originais.
    data = await fetch_articles_raw(

        query=query,

        page=page,

        per_page=per_page,

        year=year,

        open_access=open_access,

        sort=sort
    )

    # Obtém metadados.
    meta = data.get(
        "meta",
        {}
    )

    # Quantidade total.
    total = meta.get(
        "count",
        0
    )

    # Lista normalizada.
    results = []

    # Percorre os artigos.
    for item in data.get(
        "results",
        []
    ):

        # Normaliza.
        article = normalize_article(
            item
        )

        # Adiciona à lista.
        results.append(
            article
        )

    # Calcula quantidade de páginas.
    pages = (
        math.ceil(
            total / per_page
        )
        if total
        else 0
    )

    # Retorna resposta normalizada.
    return OpenAlexSearchResponse(

        total=total,

        page=page,

        per_page=per_page,

        pages=pages,

        results=results
    )
