# ============================================================
#  app/schemas/noticia.py
#  Modelos de dados para notícias tech.
# ============================================================

from pydantic import BaseModel
from typing import Optional


class Fonte(BaseModel):
    """Fonte de uma notícia."""
    id: Optional[str] = None
    nome: str


class Noticia(BaseModel):
    """Dados de uma notícia tech."""
    titulo: str
    descricao: Optional[str] = None
    url: str
    imagem: Optional[str] = None
    fonte: Fonte
    autor: Optional[str] = None
    publicado_em: str
    categoria: str = "Geral"


class RespostaNoticias(BaseModel):
    """Resposta da API com lista de notícias."""
    total: int
    noticias: list[Noticia]
    cache_hit: bool = False
    atualizado_em: str
