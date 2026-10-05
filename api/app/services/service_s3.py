"""
Serviço responsável pelo armazenamento dos dados
brutos na camada Bronze utilizando S3 / LocalStack.

Arquitetura:

    API
     |
     v
    service_s3.py
     |
     v
    S3 / LocalStack
     |
     v
    Bronze

Estrutura dos objetos:

    bronze/
        openalex/
            works/
                YYYY/
                    MM/
                        DD/
                            <identificador>.json

        core/
            works/
                YYYY/
                    MM/
                        DD/
                            <identificador>.json

        crossref/
            works/
                YYYY/
                    MM/
                        DD/
                            <doi>.json

Regras de identificação:

    OpenAlex
        -> id

    CORE
        -> id

    Crossref
        -> DOI
        -> URL
        -> SHA-256 do JSON

    Outras APIs
        -> id
        -> DOI
        -> URL
        -> SHA-256 do JSON
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from typing import Any


import boto3
from botocore.exceptions import (
    ClientError,
)


# ==============================================================
# CONFIGURAÇÕES
# ==============================================================

S3_ENDPOINT = os.getenv(
    "S3_ENDPOINT",
    "http://localstack:4566",
)


S3_ACCESS_KEY = os.getenv(
    "AWS_ACCESS_KEY_ID",
    "test",
)


S3_SECRET_KEY = os.getenv(
    "AWS_SECRET_ACCESS_KEY",
    "test",
)


S3_REGION = os.getenv(
    "AWS_DEFAULT_REGION",
    "us-east-1",
)


S3_BUCKET = os.getenv(
    "S3_BUCKET",
    "scientific-articles",
)


# ==============================================================
# CLIENTE S3
# ==============================================================

s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

# ============================================================ 
# GET S3 CLIENT 
# ============================================================ 
def get_s3_client(): 
    """ 
    Retorna o cliente boto3 utilizado pela aplicação. 
    Essa função é utilizada principalmente pelos 
    serviços de Bronze e pelo ETL do Airflow. """ 
    return s3_client

# ==============================================================
# GARANTIR BUCKET
# ==============================================================

def ensure_bucket() -> None:
    """
    Garante que o bucket configurado exista.

    Se o bucket já existir, nenhuma alteração é realizada.
    """

    try:

        s3_client.head_bucket(
            Bucket=S3_BUCKET
        )

        return

    except ClientError:
        pass


    try:

        if S3_REGION == "us-east-1":

            s3_client.create_bucket(
                Bucket=S3_BUCKET
            )

        else:

            s3_client.create_bucket(
                Bucket=S3_BUCKET,
                CreateBucketConfiguration={
                    "LocationConstraint": S3_REGION
                }
            )

    except ClientError as error:

        error_code = error.response.get(
            "Error",
            {}
        ).get(
            "Code"
        )

        # Bucket já existe.
        if error_code not in (
            "BucketAlreadyExists",
            "BucketAlreadyOwnedByYou",
        ):

            raise


# ==============================================================
# NORMALIZAR IDENTIFICADOR
# ==============================================================

def sanitize_identifier(
    identifier: str
) -> str:
    """
    Converte um identificador em um nome seguro
    para utilização como objeto S3.

    Exemplos:

        10.1000/xyz123
        ->
        10.1000-xyz123

        https://doi.org/10.1000/xyz123
        ->
        https-doi.org-10.1000-xyz123
    """

    identifier = str(
        identifier
    ).strip()


    # Remove espaços.
    identifier = re.sub(
        r"\s+",
        "-",
        identifier
    )


    # Remove caracteres problemáticos
    # para nomes de objetos.
    identifier = re.sub(
        r"[^a-zA-Z0-9._-]+",
        "-",
        identifier
    )


    # Evita vários "-" consecutivos.
    identifier = re.sub(
        r"-+",
        "-",
        identifier
    )


    # Remove "-" das extremidades.
    identifier = identifier.strip(
        "-"
    )


    return identifier


# ==============================================================
# HASH DO JSON
# ==============================================================

def generate_data_hash(
    data: dict
) -> str:
    """
    Gera um SHA-256 determinístico
    baseado no conteúdo do JSON.

    É utilizado como último fallback
    quando o artigo não possui um
    identificador conhecido.
    """

    serialized_data = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":"
        )
    )


    hash_object = hashlib.sha256(
        serialized_data.encode(
            "utf-8"
        )
    )


    return hash_object.hexdigest()


# ==============================================================
# OBTER IDENTIFICADOR
# ==============================================================

def get_identifier(
    source: str,
    data: dict
) -> str:
    """
    Obtém o identificador único do registro.

    Regras específicas:

    OpenAlex
        -> id

    CORE
        -> id

    Crossref
        -> DOI
        -> URL
        -> SHA-256

    Outras fontes
        -> id
        -> DOI
        -> URL
        -> SHA-256
    """

    source_normalized = (
        source
        .strip()
        .lower()
    )


    # ==========================================================
    # CROSSREF
    # ==========================================================

    if source_normalized == "crossref":

        doi = data.get(
            "DOI"
        )

        if doi:

            return sanitize_identifier(
                doi
            )


        url = data.get(
            "URL"
        )

        if url:

            return sanitize_identifier(
                url
            )


        return generate_data_hash(
            data
        )


    # ==========================================================
    # OPENALEX
    # ==========================================================

    if source_normalized == "openalex":

        article_id = data.get(
            "id"
        )

        if article_id:

            return sanitize_identifier(
                article_id
            )


    # ==========================================================
    # CORE
    # ==========================================================

    if source_normalized == "core":

        article_id = data.get(
            "id"
        )

        if article_id:

            return sanitize_identifier(
                article_id
            )


    # ==========================================================
    # FALLBACK GENÉRICO
    # ==========================================================

    article_id = data.get(
        "id"
    )

    if article_id:

        return sanitize_identifier(
            article_id
        )


    doi = data.get(
        "DOI"
    )

    if doi:

        return sanitize_identifier(
            doi
        )


    url = data.get(
        "URL"
    )

    if url:

        return sanitize_identifier(
            url
        )


    # ==========================================================
    # ÚLTIMO FALLBACK
    # ==========================================================

    return generate_data_hash(
        data
    )


# ==============================================================
# SALVAR BRONZE
# ==============================================================

def save_bronze(
    source: str,
    resource: str,
    data: dict,
    identifier: str | None = None,
) -> str:
    """
    Salva um registro bruto na camada Bronze.

    Parâmetros:

        source:
            Nome da API.

            Exemplos:
                openalex
                core
                crossref

        resource:
            Tipo do recurso.

            Exemplo:
                works

        data:
            JSON bruto retornado pela API.

        identifier:
            Identificador opcional informado
            explicitamente pelo router.

            Para Crossref normalmente será:

                item.get("DOI")

    Retorna:

        Caminho do objeto criado no S3.

    Exemplo:

        bronze/crossref/works/2026/10/04/
        10.1000-xyz123.json
    """

    # ==========================================================
    # GARANTE BUCKET
    # ==========================================================

    ensure_bucket()


    # ==========================================================
    # DATA ATUAL
    # ==========================================================

    now = datetime.now(
        timezone.utc
    )


    year = now.strftime(
        "%Y"
    )

    month = now.strftime(
        "%m"
    )

    day = now.strftime(
        "%d"
    )


    # ==========================================================
    # IDENTIFICADOR
    # ==========================================================

    if identifier:

        object_identifier = (
            sanitize_identifier(
                identifier
            )
        )

    else:

        object_identifier = (
            get_identifier(
                source=source,
                data=data
            )
        )


    # ==========================================================
    # PROTEÇÃO CONTRA IDENTIFICADOR VAZIO
    # ==========================================================

    if not object_identifier:

        object_identifier = (
            generate_data_hash(
                data
            )
        )


    # ==========================================================
    # NOME DO OBJETO
    # ==========================================================

    object_key = (
        f"bronze/"
        f"{source}/"
        f"{resource}/"
        f"{year}/"
        f"{month}/"
        f"{day}/"
        f"{object_identifier}.json"
    )


    # ==========================================================
    # SERIALIZA JSON
    # ==========================================================

    json_data = json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
        default=str,
    )


    # ==========================================================
    # SALVA NO S3
    # ==========================================================

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=object_key,
        Body=json_data.encode(
            "utf-8"
        ),
        ContentType=(
            "application/json"
        ),
    )


    # ==========================================================
    # LOG
    # ==========================================================

    print(
        "Bronze salvo:"
    )

    print(
        f"  Bucket : {S3_BUCKET}"
    )

    print(
        f"  Key    : {object_key}"
    )


    return object_key


# ==============================================================
# LER OBJETO
# ==============================================================

def read_bronze_object(
    object_key: str
) -> dict:
    """
    Lê um objeto JSON da Bronze
    e retorna seu conteúdo como dict.
    """

    response = s3_client.get_object(
        Bucket=S3_BUCKET,
        Key=object_key
    )


    content = response[
        "Body"
    ].read().decode(
        "utf-8"
    )


    return json.loads(
        content
    )


# ==============================================================
# LISTAR BRONZE
# ==============================================================

def list_bronze_objects(
    prefix: str = "bronze/"
) -> list[str]:
    """
    Lista os objetos existentes na Bronze.

    Retorna somente as chaves dos objetos.
    """

    objects = []


    response = s3_client.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=prefix
    )


    for item in response.get(
        "Contents",
        []
    ):

        key = item.get(
            "Key"
        )

        if key:

            objects.append(
                key
            )


    return objects


# ==============================================================
# DELETAR OBJETO
# ==============================================================

def delete_bronze_object(
    object_key: str
) -> None:
    """
    Remove um objeto da camada Bronze.
    """

    s3_client.delete_object(
        Bucket=S3_BUCKET,
        Key=object_key
    )


# ==============================================================
# VERIFICAR EXISTÊNCIA
# ==============================================================

def bronze_object_exists(
    object_key: str
) -> bool:
    """
    Verifica se um objeto existe no S3.
    """

    try:

        s3_client.head_object(
            Bucket=S3_BUCKET,
            Key=object_key
        )

        return True

    except ClientError:

        return False
