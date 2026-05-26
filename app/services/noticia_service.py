# ============================================================
#  app/services/noticia_service.py
#
#  Responsabilidade: buscar, processar e categorizar
#  notícias tech via NewsAPI.
#
#  Padrões aplicados:
#    - Categorização automática por palavras-chave
#    - Cache de 30 minutos para respeitar limites da API
#    - Paginação server-side
#    - Funções pequenas com responsabilidade única
# ============================================================

import httpx
from datetime import datetime
from typing import Optional

from app.core.cache import cache
from app.core.config import get_settings
from app.schemas.noticia import Noticia, Fonte, RespostaNoticias

settings = get_settings()

# ── Fontes monitoradas ────────────────────────────────────
FONTES_TECH = "techcrunch,the-verge,wired,ars-technica"

# ── Categorias e palavras-chave ───────────────────────────
CATEGORIAS = {
    "Python":    ["python", "django", "fastapi", "flask", "pandas", "pytorch"],
    "DevOps":    ["docker", "kubernetes", "devops", "ci/cd", "jenkins", "terraform", "aws", "cloud"],
    "IA":        ["artificial intelligence", "machine learning", "gpt", "llm", "openai", "deep learning", "neural"],
    "Segurança": ["cybersecurity", "hack", "vulnerability", "breach", "security", "malware"],
    "Web":       ["javascript", "react", "typescript", "node", "frontend", "backend", "api"],
}


# ── Utilitários ───────────────────────────────────────────
def _categorizar(titulo: str, descricao: str) -> str:
    """
    Categoriza uma notícia automaticamente por palavras-chave.
    Retorna 'Geral' se nenhuma categoria for identificada.
    """
    texto = f"{titulo} {descricao or ''}".lower()
    for categoria, palavras in CATEGORIAS.items():
        if any(palavra in texto for palavra in palavras):
            return categoria
    return "Geral"


def _formatar_data(data_str: str) -> str:
    """Converte data ISO para formato brasileiro (dd/mm/yyyy HH:MM)."""
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return data_str


# ── Serviço principal ─────────────────────────────────────
async def buscar_noticias(
    categoria: Optional[str] = None,
    pagina: int = 1,
    por_pagina: int = 12,
) -> RespostaNoticias:
    """
    Busca notícias tech das principais fontes via NewsAPI.
    Cache de 30 minutos. Suporta filtro por categoria e paginação.

    Categorias disponíveis: Python, DevOps, IA, Segurança, Web, Geral
    """
    cache_key = f"noticias_{categoria or 'todas'}_{pagina}"
    dados_cache = cache.get(cache_key)
    cache_hit = dados_cache is not None

    if not dados_cache:
        dados_cache = await _buscar_da_api()
        cache.set(cache_key, dados_cache, ttl=settings.CACHE_NOTICIAS_TTL)

    # Filtra por categoria se informado
    noticias_filtradas = (
        dados_cache
        if not categoria or categoria == "Todas"
        else [n for n in dados_cache if n.categoria == categoria]
    )

    # Paginação
    inicio = (pagina - 1) * por_pagina
    noticias_paginadas = noticias_filtradas[inicio:inicio + por_pagina]

    return RespostaNoticias(
        total=len(noticias_filtradas),
        noticias=noticias_paginadas,
        cache_hit=cache_hit,
        atualizado_em=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


async def _buscar_da_api() -> list[Noticia]:
    """Faz a requisição à NewsAPI e retorna lista de notícias processadas."""
    url = f"{settings.NEWS_API_URL}/top-headlines"
    params = {
        "apiKey": settings.NEWS_API_KEY,
        "sources": FONTES_TECH,
        "pageSize": 50,
        "page": 1,
        "language": "en",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        artigos = response.json().get("articles", [])

    noticias = []
    for artigo in artigos:
        # Ignora artigos removidos ou sem título
        if not artigo.get("title") or artigo["title"] == "[Removed]":
            continue

        categoria = _categorizar(
            artigo.get("title", ""),
            artigo.get("description", ""),
        )

        noticias.append(Noticia(
            titulo=artigo["title"],
            descricao=artigo.get("description"),
            url=artigo["url"],
            imagem=artigo.get("urlToImage"),
            fonte=Fonte(
                id=artigo["source"].get("id"),
                nome=artigo["source"].get("name", "Desconhecida"),
            ),
            autor=artigo.get("author"),
            publicado_em=_formatar_data(artigo.get("publishedAt", "")),
            categoria=categoria,
        ))

    return noticias


async def buscar_categorias_disponiveis() -> list[str]:
    """Retorna todas as categorias disponíveis para filtro."""
    return ["Todas"] + list(CATEGORIAS.keys()) + ["Geral"]
