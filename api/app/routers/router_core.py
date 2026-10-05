"""
Rotas FastAPI responsáveis pela integração
com a API CORE.
"""

from fastapi import APIRouter, Query

from app.services.service_core import (
    fetch_works_raw,
    normalize_core_article
)

from app.services.service_s3  import (
    save_bronze
)


router_core = APIRouter(
    prefix="/api/v1/core",
    tags=["CORE"]
)


# ==============================================================
# PESQUISAR ARTIGOS
# ==============================================================

@router_core.get(
    "/search"
)
async def search_core_articles(
    q: str = Query(
        ...,
        description="Termo utilizado na pesquisa."
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Quantidade de resultados."
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Deslocamento dos resultados."
    )
):
    """
    Pesquisa artigos na API CORE.

    Exemplo:

        GET /api/v1/core/search?q=mining

    A rota consulta a CORE, extrai os registros
    encontrados e normaliza cada artigo.
    """

    # ==========================================================
    # CONSULTA CORE
    # ==========================================================

    data = await fetch_works_raw(
        query=q,
        limit=limit,
        offset=offset
    )

    # ==========================================================
    # OBTÉM OS RESULTADOS
    # ==========================================================

    results = data.get(
        "results",
        []
    )

    # ==========================================================
    # NORMALIZA OS ARTIGOS
    # ==========================================================

    articles = []

    for item in results:

        article = normalize_core_article(
            item
        )

        articles.append(
            article
        )

    # ==========================================================
    # RETORNO
    # ==========================================================

    return {
        "source": "CORE",
        "query": q,
        "limit": limit,
        "offset": offset,
        "total": data.get(
            "totalHits",
            len(articles)
        ),
        "count": len(articles),
        "articles": articles
    }


# ============================================================
# IMPORT
# ============================================================
@router_core.post(
    "/import",
    status_code=201
)
async def works(
    q: str = Query(
        ...,
        min_length=1,
        description="Termo da pesquisa"
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Quantidade de resultados"
    ),

    offset: int = Query(
        0,
        ge=0,
        description="Deslocamento da paginação"
    )
):

    # return await fetch_works_raw(
    #     query=q,
    #     limit=limit,
    #     offset=offset
    # )

    

    # --------------------------------------------------------
    # 1. BUSCAR DADOS BRUTOS
    # --------------------------------------------------------
    # Obtém o JSON original da Core.
    raw_data = await fetch_works_raw(

        query=q,

        limit=limit,

        offset=offset
    )


    # --------------------------------------------------------
    # 2. SALVAR BRONZE
    # --------------------------------------------------------
    # Guarda o JSON original no MinIO.

    # Cada resultado da Core é salvo
    # individualmente.
    bronze_objects = []

    # # Percorre os artigos retornados.
    for item in raw_data.get(
        "results",
        []
    ):

        # Salva o registro original.
        object_name = save_bronze(

            # Fonte.
            source="core",

            # Tipo do recurso.
            resource="works",

            # JSON original.
            data=item
        )

        # Guarda o caminho do objeto.
        bronze_objects.append(
            object_name
        )


    # --------------------------------------------------------
    # 3. NORMALIZAR
    # --------------------------------------------------------
    # Lista dos artigos normalizados.
    articles = []

    # Percorre novamente os registros.
    for item in raw_data.get(
        "results",
        []
    ):

        # Converte para o modelo da aplicação.
        article = normalize_core_article(
            item
        )

        # Adiciona à lista.
        articles.append(
            article
        )


    # --------------------------------------------------------
    # 4. SALVAR SILVER
    # --------------------------------------------------------
    # Persiste os dados normalizados
    # no PostgreSQL.
    # saved = save_articles( -> COMENTADO PARA NÃO SALVAR NO POSTGRESQL AINDA.
    #     articles
    # )


    # --------------------------------------------------------
    # 5. RETORNO
    # --------------------------------------------------------
    # Metadados da Core.
    meta = raw_data.get(
        "meta",
        {}
    )

    # Retorna informações sobre o processamento.
    return {

        # Mensagem.
        "message": (
            "Artigos importados "
            "com sucesso."
        ),

        # Fonte.
        "source": "Core",

        # Consulta realizada.
        "query": q,

        # Página.
        "limit": limit,

        # Quantidade solicitada.
        "offset": offset,

        # Quantidade encontrada pela Core.
        "found": meta.get(
            "count",
            0
        ),

        # Quantidade de registros enviados
        # para o PostgreSQL.
        # "processed": saved, -> COMENTADO PARA NÃO SALVAR NO POSTGRESQL AINDA.

        # Quantidade de objetos salvos
        # no MinIO.
        "bronze_objects": len(
            bronze_objects
        ),

        # Localização dos objetos Bronze.
        "bronze": bronze_objects
    }
