"""
Modelos Pydantic utilizados pela integração
com a API CORE.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CoreArticle(BaseModel):

    # ==============================================================
    # IDENTIFICAÇÃO
    # ==============================================================

    # ID da obra dentro da CORE.
    id: str

    # ==============================================================
    # INFORMAÇÕES BIBLIOGRÁFICAS
    # ==============================================================

    # Título do artigo.
    title: Optional[str] = None

    # Lista de autores.
    authors: List[str] = Field(
        default_factory=list
    )

    # Resumo.
    abstract: Optional[str] = None

    # Ano de publicação. Na API yearPublished
    publication_year: Optional[int] = None

    # DOI.
    doi: Optional[str] = None

    # ==============================================================
    # CLASSIFICAÇÃO
    # ==============================================================

    # Idioma.
    language: Optional[str] = None

    # Área de estudo. Na API fieldOfStudy
    field_of_study: Optional[str] = None

    # Tipo do documento. Na API documentType
    document_type: Optional[str] = None

    # ==============================================================
    # PUBLICAÇÃO
    # ==============================================================

    # Editora.
    publisher: Optional[str] = None

    # ==============================================================
    # ARQUIVOS / PDF
    # ==============================================================

    # URLs onde o texto completo está disponível. Na API sourceFulltextUrls
    source_fulltext_urls: List[str] = Field(
        default_factory=list
    )