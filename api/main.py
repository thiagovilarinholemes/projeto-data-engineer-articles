"""
Aplicação principal da Scientific Articles API.

A aplicação integra:

    OpenAlex
    CORE

E utiliza:

    MinIO      → Bronze
    PostgreSQL → Silver

Posteriormente teremos:

    Crossref
    Europe PMC
    Gold
    Airflow
"""


# ============================================================
# IMPORTS
# ============================================================

from contextlib import asynccontextmanager


# FastAPI.
from fastapi import FastAPI


# Inicialização do PostgreSQL.
from app.database.init_db import (
    create_tables
)


# Inicialização do MinIO.
from app.services.service_s3 import ensure_bucket

# Router OpenAlex.
from app.routers.router_openalex import router_openalex

# Router CORE.
from app.routers.router_core import router_core

# Router Crossref.
from app.routers.router_crossref import router_crossref

from app.database.create_gold import create_gold_tables


# Router CORE.
# from app.routers.router_core import (
#     router as router_core
# )


# ============================================================
# LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    """
    Executa tarefas durante o ciclo de vida da aplicação.

    Na inicialização:

        1. Cria tabelas PostgreSQL.
        2. Garante a existência do bucket MinIO.

    Depois disso a API fica disponível.
    """

    # --------------------------------------------------------
    # POSTGRESQL
    # --------------------------------------------------------

    # Cria as tabelas necessárias.
    create_tables()
    create_gold_tables()

    # --------------------------------------------------------
    # MINIO
    # --------------------------------------------------------

    # Garante que o bucket Bronze exista.
    ensure_bucket()


    # --------------------------------------------------------
    # APLICAÇÃO
    # --------------------------------------------------------

    # Entrega o controle para o FastAPI.
    yield


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(

    # Título exibido no Swagger.
    title="Scientific Articles API",

    # Descrição da aplicação.
    description=(
        "API para pesquisa de artigos científicos "
        "utilizando OpenAlex e CORE. "
        "Os dados brutos são armazenados no MinIO "
        "e os dados normalizados no PostgreSQL."
    ),

    # Versão.
    version="1.0.0",

    # Ciclo de vida.
    lifespan=lifespan
)


# ============================================================
# ROUTERS
# ============================================================

# Registra as rotas OpenAlex.
app.include_router(
    router_openalex,
)

# Registra as rotas CORE.
app.include_router(
    router_core
)

# Registra as rotas Crossref.
app.include_router(
    router_crossref
)