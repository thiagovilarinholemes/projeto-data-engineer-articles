"""
Modelos Pydantic utilizados pela integração
com a API Crossref.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CrossrefArticle(BaseModel):

    # ==========================================================
    # IDENTIFICAÇÃO
    # ==========================================================

    # DOI do trabalho.
    doi: Optional[str] = None

    # ==========================================================
    # INFORMAÇÕES BIBLIOGRÁFICAS
    # ==========================================================

    # Título.
    title: Optional[str] = None

    # Lista de autores.
    authors: List[str] = Field(
        default_factory=list
    )

    # Abstract.
    abstract: Optional[str] = None

    # ==========================================================
    # PUBLICAÇÃO
    # ==========================================================

    # Ano de publicação.
    publication_year: Optional[int] = None

    # Nome da revista, periódico ou publicação.
    container_title: Optional[str] = None

    # Editora.
    publisher: Optional[str] = None

    # Tipo do documento.
    document_type: Optional[str] = None

    # ==========================================================
    # IDENTIFICADORES
    # ==========================================================

    # ISSN.
    issn: List[str] = Field(
        default_factory=list
    )

    # URL do DOI.
    url: Optional[str] = None

    # ==========================================================
    # TEXTO COMPLETO
    # ==========================================================

    # URLs de texto completo.
    fulltext_urls: List[str] = Field(
        default_factory=list
    )

    # ==========================================================
    # METADADOS
    # ==========================================================

    # Número de referências.
    reference_count: Optional[int] = None

    # Número de citações.
    is_referenced_by_count: Optional[int] = None
