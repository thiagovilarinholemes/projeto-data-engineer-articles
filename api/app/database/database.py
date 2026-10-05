"""
Configuração da conexão com PostgreSQL.

O PostgreSQL será utilizado principalmente
para as camadas:

    SILVER
    GOLD

Os dados brutos ficam no MinIO.
"""


# ============================================================
# IMPORTS
# ============================================================
# Permite acessar variáveis de ambiente.
import os

# Driver PostgreSQL.
import psycopg2


# ============================================================
# CONEXÃO
# ============================================================
def get_connection():
    """
    Cria e retorna uma conexão com PostgreSQL.

    As configurações são obtidas através
    das variáveis de ambiente.
    """

    return psycopg2.connect(

        # Host do PostgreSQL.
        #
        # Dentro do Docker:
        #
        #     postgres
        host=os.getenv(
            "POSTGRES_HOST",
        ),

        # Porta.
        port=os.getenv(
            "POSTGRES_PORT",
        ),

        # Banco.
        database=os.getenv(
            "POSTGRES_DB",
        ),

        # Usuário.
        user=os.getenv(
            "POSTGRES_USER",
        ),

        # Senha.
        password=os.getenv(
            "POSTGRES_PASSWORD",
        )
    )
