"""
Rotas relacionadas à pesquisa de artigos científicos
utilizando a API Crossref.
"""


# ============================================================
# IMPORTS
# ============================================================

from fastapi import APIRouter, Query


# ============================================================
# SERVIÇOS
# ============================================================

from app.services.service_crossref import (
    fetch_works_raw,
    normalize_crossref_article
)


from app.services.service_s3 import (
    save_bronze
)


# ============================================================
# ROUTER
# ============================================================

router_crossref = APIRouter(

    prefix="/api/v1/crossref",

    tags=["Crossref"]
)


# ============================================================
# GET
# ============================================================

@router_crossref.get(
    "/search"
)
async def search_crossref(

    # Termo da pesquisa.
    query: str = Query(
        ...,
        min_length=2
    ),

    # Quantidade.
    rows: int = Query(
        10,
        ge=1,
        le=100
    ),

    # Offset.
    offset: int = Query(
        0,
        ge=0
    )
):
    """
    Pesquisa artigos na API Crossref.

    Esta rota apenas consulta a Crossref.

    Não salva dados no S3
    nem no PostgreSQL.

    Para importar utilize:

        POST /api/v1/crossref/import
    """


    # --------------------------------------------------------
    # BUSCAR DADOS
    # --------------------------------------------------------

    raw_data = await fetch_works_raw(

        query=query,

        rows=rows,

        offset=offset
    )


    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    message = raw_data.get(
        "message",
        {}
    )


    results = message.get(
        "items",
        []
    )


    # --------------------------------------------------------
    # NORMALIZAÇÃO
    # --------------------------------------------------------

    articles = []


    for item in results:

        article = normalize_crossref_article(
            item
        )


        articles.append(
            article
        )


    # --------------------------------------------------------
    # RETORNO
    # --------------------------------------------------------

    return {

        "source": "Crossref",

        "query": query,

        "rows": rows,

        "offset": offset,

        "total": message.get(
            "total-results",
            0
        ),

        "count": len(
            articles
        ),

        "articles": articles
    }


# ============================================================
# IMPORT
# ============================================================

@router_crossref.post(
    "/import",
    status_code=201
)
async def import_crossref_articles(

    # Termo da pesquisa.
    query: str = Query(
        ...,
        min_length=2
    ),

    # Quantidade.
    rows: int = Query(
        10,
        ge=1,
        le=100
    ),

    # Offset.
    offset: int = Query(
        0,
        ge=0
    )
):
    """
    Pesquisa e importa artigos da Crossref.

    Fluxo:

        Crossref
            ↓
        S3 / LocalStack
            ↓
        Bronze
            ↓
        Airflow
            ↓
        Silver
            ↓
        PostgreSQL
    """


    # --------------------------------------------------------
    # 1. BUSCAR DADOS BRUTOS
    # --------------------------------------------------------

    raw_data = await fetch_works_raw(

        query=query,

        rows=rows,

        offset=offset
    )


    # --------------------------------------------------------
    # 2. EXTRAIR RESULTADOS
    # --------------------------------------------------------

    message = raw_data.get(
        "message",
        {}
    )


    results = message.get(
        "items",
        []
    )


    # --------------------------------------------------------
    # 3. SALVAR BRONZE
    # --------------------------------------------------------

    bronze_objects = []


    for item in results:

        object_name = save_bronze(

            source="crossref",

            resource="works",

            data=item
        )


        bronze_objects.append(
            object_name
        )


    # --------------------------------------------------------
    # 4. NORMALIZAR
    # --------------------------------------------------------

    articles = []


    for item in results:

        article = normalize_crossref_article(
            item
        )


        articles.append(
            article
        )


    # --------------------------------------------------------
    # 5. RETORNO
    # --------------------------------------------------------

    return {

        "message": (
            "Artigos da Crossref "
            "importados com sucesso."
        ),

        "source": "Crossref",

        "query": query,

        "rows": rows,

        "offset": offset,

        "found": message.get(
            "total-results",
            0
        ),

        "processed": len(
            articles
        ),

        "bronze_objects": len(
            bronze_objects
        ),

        "bronze": bronze_objects
    }
