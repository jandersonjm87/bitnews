# ============================================================
#  app/api/routes/noticias.py
#  Endpoints de notícias tech.
# ============================================================

from fastapi import APIRouter, Query
from typing import Optional

from app.services import noticia_service
from app.schemas.noticia import RespostaNoticias

router = APIRouter()


@router.get("/", response_model=RespostaNoticias)
async def listar_noticias(
    categoria: Optional[str] = Query(None, description="Filtra por categoria"),
    pagina: int = Query(1, ge=1, description="Número da página"),
    por_pagina: int = Query(12, ge=1, le=50, description="Itens por página"),
):
    """
    Retorna notícias tech das principais fontes.
    Fontes: TechCrunch, The Verge, Wired, Ars Technica, Hacker News.
    Notícias são categorizadas automaticamente.
    """
    return await noticia_service.buscar_noticias(
        categoria=categoria,
        pagina=pagina,
        por_pagina=por_pagina,
    )


@router.get("/categorias")
async def listar_categorias():
    """Retorna as categorias disponíveis para filtro."""
    categorias = await noticia_service.buscar_categorias_disponiveis()
    return {"categorias": categorias}
