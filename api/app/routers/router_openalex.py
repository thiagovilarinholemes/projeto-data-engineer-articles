"""
Rotas relacionadas à pesquisa de artigos científicos
utilizando a OpenAlex.
"""


# ============================================================
# IMPORTS
# ============================================================
from fastapi import APIRouter, Query


# ============================================================
# MODELOS
# ============================================================
from app.models.model_openalex import (
    OpenAlexSearchResponse
)


# ============================================================
# SERVIÇOS
# ============================================================
from app.services.service_openalex import (
    fetch_articles_raw,
    normalize_article,
    search_articles
)

from app.services.service_articles import (
    save_articles
)

from app.services.service_s3  import (
    save_bronze
)


# ============================================================
# ROUTER
# ============================================================
router_openalex = APIRouter(

    # Prefixo das rotas.
    prefix="/api/v1/articles",

    # Nome exibido no Swagger.
    tags=["OpenAlex"]
)


# ============================================================
# GET
# ============================================================
@router_openalex.get(
    "/",
    response_model=OpenAlexSearchResponse
)
async def get_articles(

    # Termo obrigatório da pesquisa.
    query: str = Query(
        ...,
        min_length=2
    ),

    # Página.
    page: int = Query(
        1,
        ge=1
    ),

    # Quantidade por página.
    per_page: int = Query(
        10,
        ge=1,
        le=100
    ),

    # Filtro por ano.
    year: int | None = Query(
        None,
        ge=1900,
        le=2100
    ),

    # Filtro Open Access.
    open_access: bool | None = Query(
        None
    ),

    # Ordenação.
    sort: str | None = Query(
        None
    )
):
    """
    Pesquisa artigos na OpenAlex.

    IMPORTANTE:

    Esta rota apenas consulta a OpenAlex.

    Não salva dados no MinIO
    nem no PostgreSQL.

    Para persistir os dados utilize:

        POST /api/v1/articles/import
    """

    # Executa a pesquisa.
    return await search_articles(

        query=query,

        page=page,

        per_page=per_page,

        year=year,

        open_access=open_access,

        sort=sort
    )


# ============================================================
# IMPORT
# ============================================================
@router_openalex.post(
    "/import",
    status_code=201
)
async def import_articles(

    # Termo da pesquisa.
    query: str = Query(
        ...,
        min_length=2
    ),

    # Página.
    page: int = Query(
        1,
        ge=1
    ),

    # Quantidade.
    per_page: int = Query(
        10,
        ge=1,
        le=100
    ),

    # Ano.
    year: int | None = Query(
        None,
        ge=1900,
        le=2100
    ),

    # Open Access.
    open_access: bool | None = Query(
        None
    ),

    # Ordenação.
    sort: str | None = Query(
        None
    )
):
    """
    Pesquisa e importa artigos da OpenAlex.

    Fluxo:

        OpenAlex
            ↓
        MinIO Bronze
            ↓
        Normalização
            ↓
        PostgreSQL
    """

    # --------------------------------------------------------
    # 1. BUSCAR DADOS BRUTOS
    # --------------------------------------------------------
    # Obtém o JSON original da OpenAlex.
    raw_data = await fetch_articles_raw(

        query=query,

        page=page,

        per_page=per_page,

        year=year,

        open_access=open_access,

        sort=sort
    )


    # --------------------------------------------------------
    # 2. SALVAR BRONZE
    # --------------------------------------------------------
    # Guarda o JSON original no MinIO.

    # Cada resultado da OpenAlex é salvo
    # individualmente.
    bronze_objects = []

    # Percorre os artigos retornados.
    for item in raw_data.get(
        "results",
        []
    ):

        # Salva o registro original.
        object_name = save_bronze(

            # Fonte.
            source="openalex",

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
        article = normalize_article(
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
    # Metadados da OpenAlex.
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
        "source": "OpenAlex",

        # Consulta realizada.
        "query": query,

        # Página.
        "page": page,

        # Quantidade solicitada.
        "per_page": per_page,

        # Quantidade encontrada pela OpenAlex.
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
