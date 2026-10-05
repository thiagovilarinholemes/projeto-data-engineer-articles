"""
Modelos Pydantic utilizados pela integração com a OpenAlex.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class OpenAlexArticle(BaseModel):
    """
    Representa um artigo científico normalizado
    a partir dos dados da OpenAlex.
    """

    id: str

    title: Optional[str] = None

    authors: List[str] = Field(
        default_factory=list
    )

    abstract: Optional[str] = None

    publication_year: Optional[int] = None

    doi: Optional[str] = None

    language: Optional[str] = None

    source: Optional[str] = None

    pdf_url: Optional[str] = None

    open_access: bool = False


class OpenAlexSearchResponse(BaseModel):
    """
    Resposta paginada da API de artigos.
    """

    total: int

    page: int

    per_page: int

    pages: int

    results: List[OpenAlexArticle] = Field(
        default_factory=list
    )