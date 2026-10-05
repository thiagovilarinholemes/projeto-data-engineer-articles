"""
====================================================================
SERVICE BRONZE
====================================================================

Serviço responsável pela leitura dos dados Bronze
armazenados no LocalStack S3.

Responsabilidades:

    - Garantir que o bucket exista
    - Criar bucket automaticamente quando necessário
    - Listar todos os objetos da camada Bronze
    - Suportar paginação do S3
    - Ler objetos JSON da camada Bronze

Arquitetura:

    LocalStack S3
         ↓
       BRONZE
         ↓
    service_bronze
         ↓
     service_etl
         ↓
      SILVER
====================================================================
"""

import json


from app.services.service_s3 import (
    get_s3_client,
    ensure_bucket,
    S3_BUCKET
)


# ==================================================================
# GARANTIR BUCKET
# ==================================================================

def ensure_bronze_bucket():
    """
    Garante que o bucket utilizado pelo Bronze exista.
    """

    ensure_bucket()


# ==================================================================
# LISTAR OBJETOS BRONZE
# ==================================================================

def list_bronze_objects(
    prefix: str
) -> list[str]:
    """
    Lista todos os objetos armazenados na camada Bronze.

    Utiliza o paginator do boto3 para garantir que
    todos os objetos sejam encontrados mesmo quando
    o bucket possuir muitos arquivos.

    Parâmetros
    ----------
    prefix:
        Prefixo utilizado para localizar os objetos.

    Exemplo:

        bronze/openalex/works/

    Retorno
    -------
    list[str]
        Lista contendo as chaves dos objetos encontrados.
    """

    # --------------------------------------------------------------
    # Garantir bucket
    # --------------------------------------------------------------

    ensure_bronze_bucket()


    # --------------------------------------------------------------
    # Criar cliente S3
    # --------------------------------------------------------------

    s3 = get_s3_client()


    # --------------------------------------------------------------
    # Criar paginator
    # --------------------------------------------------------------

    paginator = s3.get_paginator(
        "list_objects_v2"
    )


    # --------------------------------------------------------------
    # Lista final
    # --------------------------------------------------------------

    objects = []


    # --------------------------------------------------------------
    # Percorrer todas as páginas
    # --------------------------------------------------------------

    pages = paginator.paginate(

        Bucket=S3_BUCKET,

        Prefix=prefix
    )


    for page in pages:

        contents = page.get(
            "Contents",
            []
        )


        for item in contents:

            key = item.get(
                "Key"
            )


            if key:

                objects.append(
                    key
                )


    # --------------------------------------------------------------
    # Log
    # --------------------------------------------------------------

    print(
        "=================================================="
    )

    print(
        "BRONZE - LISTAGEM S3"
    )

    print(
        f"Bucket: {S3_BUCKET}"
    )

    print(
        f"Prefix: {prefix}"
    )

    print(
        f"Objetos encontrados: {len(objects)}"
    )

    print(
        "=================================================="
    )


    return objects


# ==================================================================
# LER OBJETO BRONZE
# ==================================================================

def read_bronze_object(
    object_name: str
) -> dict:
    """
    Lê um objeto JSON armazenado no Bronze.

    Parâmetros
    ----------
    object_name:
        Nome/chave do objeto no S3.

    Exemplo:

        bronze/openalex/works/2026/10/02/W123.json

    Retorno
    -------
    dict
        Conteúdo JSON convertido para dicionário Python.
    """

    # --------------------------------------------------------------
    # Garantir bucket
    # --------------------------------------------------------------

    ensure_bronze_bucket()


    # --------------------------------------------------------------
    # Criar cliente S3
    # --------------------------------------------------------------

    s3 = get_s3_client()


    # --------------------------------------------------------------
    # Ler objeto
    # --------------------------------------------------------------

    response = s3.get_object(

        Bucket=S3_BUCKET,

        Key=object_name
    )


    # --------------------------------------------------------------
    # Ler conteúdo
    # --------------------------------------------------------------

    body = response["Body"].read()


    # --------------------------------------------------------------
    # Converter JSON
    # --------------------------------------------------------------

    article = json.loads(

        body.decode(
            "utf-8"
        )
    )


    # --------------------------------------------------------------
    # Log
    # --------------------------------------------------------------

    print(
        "Objeto Bronze lido:",
        object_name
    )


    return article
