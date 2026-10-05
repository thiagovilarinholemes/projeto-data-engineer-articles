"""
ETL Bronze -> Silver.

Fluxo:

LocalStack S3
     |
     v
Bronze
     |
     v
bronze_etl_control
     |
     v
Normalização
     |
     v
silver_articles
"""

from typing import Any

from app.services.service_bronze import (
    list_bronze_objects,
    read_bronze_object,
)

from app.services.service_silver import (
    create_silver_table,
    save_silver_article,
    is_bronze_processed,
    start_bronze_processing,
    mark_bronze_processed,
    mark_bronze_error,
)


# ============================================================
# ABSTRACT OPENALEX
# ============================================================

def extract_openalex_abstract(
    inverted_index: dict | None
) -> str | None:
    """
    Reconstrói o abstract da OpenAlex.

    Exemplo:

        {
            "This": [0],
            "paper": [1],
            "is": [2]
        }

    Resultado:

        This paper is
    """

    if not inverted_index:
        return None

    words = []

    for word, positions in inverted_index.items():

        for position in positions:

            words.append(
                (
                    position,
                    word
                )
            )

    words.sort(
        key=lambda item: item[0]
    )

    return " ".join(
        word
        for _, word in words
    )


# ============================================================
# OPENALEX
# ============================================================

def normalize_openalex(
    item: dict
) -> dict:
    """
    Normaliza um artigo da OpenAlex
    para o modelo Silver.
    """

    authors = []

    for authorship in item.get(
        "authorships",
        []
    ):

        author = authorship.get(
            "author"
        ) or {}

        name = author.get(
            "display_name"
        )

        if name:
            authors.append(name)

    primary_location = (
        item.get(
            "primary_location"
        )
        or {}
    )

    source = (
        primary_location.get(
            "source"
        )
        or {}
    )

    best_oa_location = (
        item.get(
            "best_oa_location"
        )
        or {}
    )

    open_access = (
        item.get(
            "open_access"
        )
        or {}
    )

    return {

        "source_api": "openalex",

        "external_id": item.get(
            "id"
        ),

        "doi": item.get(
            "doi"
        ),

        "title": item.get(
            "title"
        ),

        "authors": authors,

        "abstract": extract_openalex_abstract(
            item.get(
                "abstract_inverted_index"
            )
        ),

        "publication_year": item.get(
            "publication_year"
        ),

        "container_title": source.get(
            "display_name"
        ),

        "publisher": None,

        "language": None,

        "field_of_study": None,

        "document_type": item.get(
            "type"
        ),

        "url": item.get(
            "id"
        ),

        "fulltext_urls": [],

        "pdf_url": best_oa_location.get(
            "pdf_url"
        ),

        "open_access": open_access.get(
            "is_oa"
        ),

        "reference_count": item.get(
            "referenced_works_count"
        ),

        "is_referenced_by_count": item.get(
            "cited_by_count"
        ),
    }


# ============================================================
# CORE
# ============================================================

def normalize_core(
    item: dict
) -> dict:
    """
    Normaliza um artigo da CORE.
    """

    authors = []

    for author in item.get(
        "authors",
        []
    ):

        name = author.get(
            "name"
        )

        if name:
            authors.append(name)

    language_data = (
        item.get(
            "language"
        )
        or {}
    )

    fulltext_urls = list(
        item.get(
            "sourceFulltextUrls"
        )
        or []
    )

    download_url = item.get(
        "downloadUrl"
    )

    if download_url:
        fulltext_urls.append(
            download_url
        )

    return {

        "source_api": "core",

        "external_id": str(
            item.get("id")
        ),

        "doi": item.get(
            "doi"
        ),

        "title": item.get(
            "title"
        ),

        "authors": authors,

        "abstract": item.get(
            "abstract"
        ),

        "publication_year": item.get(
            "yearPublished"
        ),

        "container_title": None,

        "publisher": item.get(
            "publisher"
        ),

        "language": language_data.get(
            "code"
        ),

        "field_of_study": item.get(
            "fieldOfStudy"
        ),

        "document_type": item.get(
            "documentType"
        ),

        "url": None,

        "fulltext_urls": fulltext_urls,

        "pdf_url": download_url,

        "open_access": None,

        "reference_count": item.get(
            "citationCount"
        ),

        "is_referenced_by_count": None,
    }


# ============================================================
# CROSSREF
# ============================================================

def normalize_crossref(
    item: dict
) -> dict:
    """
    Normaliza um artigo da Crossref.
    """

    authors = []

    for author in item.get(
        "author",
        []
    ):

        given = author.get(
            "given"
        ) or ""

        family = author.get(
            "family"
        ) or ""

        name = (
            f"{given} {family}"
        ).strip()

        if name:
            authors.append(name)

    title_list = (
        item.get(
            "title"
        )
        or []
    )

    container_list = (
        item.get(
            "container-title"
        )
        or []
    )

    publication_year = None

    for date_field in [
        "published-print",
        "published-online",
        "published",
    ]:

        date_data = (
            item.get(
                date_field
            )
            or {}
        )

        date_parts = (
            date_data.get(
                "date-parts"
            )
            or []
        )

        if date_parts:

            first_date = (
                date_parts[0]
            )

            if first_date:

                publication_year = (
                    first_date[0]
                )

                break

    fulltext_urls = []

    for link in (
        item.get(
            "link"
        )
        or []
    ):

        url = link.get(
            "URL"
        )

        if url:
            fulltext_urls.append(
                url
            )

    doi = item.get(
        "DOI"
    )

    url = item.get(
        "URL"
    )

    return {

        "source_api": "crossref",

        "external_id": (
            doi
            or url
        ),

        "doi": doi,

        "title": (
            title_list[0]
            if title_list
            else None
        ),

        "authors": authors,

        "abstract": item.get(
            "abstract"
        ),

        "publication_year": publication_year,

        "container_title": (
            container_list[0]
            if container_list
            else None
        ),

        "publisher": item.get(
            "publisher"
        ),

        "language": None,

        "field_of_study": None,

        "document_type": item.get(
            "type"
        ),

        "url": url,

        "fulltext_urls": fulltext_urls,

        "pdf_url": (
            fulltext_urls[0]
            if fulltext_urls
            else None
        ),

        "open_access": None,

        "reference_count": item.get(
            "reference-count"
        ),

        "is_referenced_by_count": item.get(
            "is-referenced-by-count"
        ),
    }


# ============================================================
# NORMALIZAÇÃO CENTRAL
# ============================================================

def normalize_article(
    source: str,
    item: dict
) -> dict:
    """
    Escolhe a normalização de acordo
    com a API de origem.
    """

    if source == "openalex":

        return normalize_openalex(
            item
        )

    if source == "core":

        return normalize_core(
            item
        )

    if source == "crossref":

        return normalize_crossref(
            item
        )

    raise ValueError(
        f"Fonte não suportada: {source}"
    )


# ============================================================
# PROCESSAMENTO BRONZE
# ============================================================

def process_bronze(
    source: str,
    resource: str = "works"
) -> dict:
    """
    Processa todos os objetos Bronze
    de uma determinada fonte.
    """

    print()
    print("=" * 70)
    print(
        f"BRONZE -> SILVER: {source.upper()}"
    )
    print("=" * 70)

    prefix = (
        f"bronze/"
        f"{source}/"
        f"{resource}/"
    )

    print(
        f"Prefixo: {prefix}"
    )

    objects = list_bronze_objects(
        prefix=prefix
    )

    print(
        f"Objetos encontrados: "
        f"{len(objects)}"
    )

    processed = 0
    errors = 0
    skipped = 0

    for object_name in objects:

        print()
        print(
            f"Processando: {object_name}"
        )

        # ----------------------------------------------------
        # CONTROLE
        # ----------------------------------------------------

        if is_bronze_processed(
            source,
            object_name
        ):

            print(
                "SKIP: objeto já processado."
            )

            skipped += 1

            continue

        try:

            # ------------------------------------------------
            # MARCA COMO PROCESSING
            # ------------------------------------------------

            start_bronze_processing(
                source_api=source,
                s3_object_key=object_name
            )

            # ------------------------------------------------
            # LEITURA DO BRONZE
            # ------------------------------------------------

            item = read_bronze_object(
                object_name
            )

            print(
                f"Objeto Bronze lido: "
                f"{object_name}"
            )

            # ------------------------------------------------
            # NORMALIZAÇÃO
            # ------------------------------------------------

            article = normalize_article(
                source,
                item
            )

            # ------------------------------------------------
            # VALIDAÇÃO DO ID
            # ------------------------------------------------

            if not article.get(
                "external_id"
            ):

                raise ValueError(
                    "external_id não encontrado."
                )

            # ------------------------------------------------
            # SILVER
            # ------------------------------------------------

            save_silver_article(
                article
            )

            # ------------------------------------------------
            # CONTROLE
            # ------------------------------------------------

            mark_bronze_processed(
                source_api=source,
                s3_object_key=object_name
            )

            processed += 1

            print(
                "OK: artigo salvo na Silver."
            )

        except Exception as exc:

            errors += 1

            error_message = (
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            )

            print()
            print(
                "=" * 70
            )

            print(
                f"ERRO: {object_name}"
            )

            print(
                f"Mensagem: {error_message}"
            )

            print(
                "=" * 70
            )

            # -----------------------------------------------
            # REGISTRA ERRO
            # -----------------------------------------------

            try:

                mark_bronze_error(
                    source_api=source,
                    s3_object_key=object_name,
                    error_message=error_message
                )

            except Exception as control_error:

                print(
                    "ERRO AO REGISTRAR "
                    "bronze_etl_control:"
                )

                print(
                    control_error
                )

    print()
    print("=" * 70)
    print("RESULTADO")
    print("=" * 70)

    print(
        f"Encontrados : {len(objects)}"
    )

    print(
        f"Processados : {processed}"
    )

    print(
        f"Ignorados   : {skipped}"
    )

    print(
        f"Erros       : {errors}"
    )

    print("=" * 70)

    return {

        "source": source,

        "objects_found": len(
            objects
        ),

        "processed": processed,

        "skipped": skipped,

        "errors": errors,
    }


# ============================================================
# OPENALEX
# ============================================================

def process_openalex_bronze():
    """
    Processa Bronze da OpenAlex.
    """

    create_silver_table()

    return process_bronze(
        source="openalex",
        resource="works"
    )


# ============================================================
# CORE
# ============================================================

def process_core_bronze():
    """
    Processa Bronze da CORE.
    """

    create_silver_table()

    return process_bronze(
        source="core",
        resource="works"
    )


# ============================================================
# CROSSREF
# ============================================================

def process_crossref_bronze():
    """
    Processa Bronze da Crossref.
    """

    create_silver_table()

    return process_bronze(
        source="crossref",
        resource="works"
    )


# ============================================================
# TODAS AS FONTES
# ============================================================

def process_all_bronze():
    """
    Processa todas as fontes Bronze.
    """

    create_silver_table()

    results = []

    results.append(
        process_bronze(
            source="openalex",
            resource="works"
        )
    )

    results.append(
        process_bronze(
            source="core",
            resource="works"
        )
    )

    results.append(
        process_bronze(
            source="crossref",
            resource="works"
        )
    )

    return results
