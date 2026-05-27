# ============================================================
#  tests/test_noticias.py
#  Testes automatizados para os endpoints de notícias.
#
#  Padrão aplicado: mock da NewsAPI para os testes não
#  dependerem de rede externa nem de chave válida no CI.
# ============================================================
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.cache import cache

client = TestClient(app)

# ── Dados falsos que simulam a resposta da NewsAPI ────────
NOTICIAS_MOCK = [
    {
        "title": "New Python 3.12 features released",
        "description": "Python brings new features to developers",
        "url": "https://example.com/python",
        "urlToImage": None,
        "source": {"id": "techcrunch", "name": "TechCrunch"},
        "author": "Author",
        "publishedAt": "2024-01-01T10:00:00Z",
    },
    {
        "title": "Docker containers explained",
        "description": "DevOps guide to containers",
        "url": "https://example.com/docker",
        "urlToImage": None,
        "source": {"id": "the-verge", "name": "The Verge"},
        "author": "Author",
        "publishedAt": "2024-01-01T11:00:00Z",
    },
    {
        "title": "OpenAI releases new GPT model",
        "description": "AI news from OpenAI",
        "url": "https://example.com/gpt",
        "urlToImage": None,
        "source": {"id": "wired", "name": "Wired"},
        "author": "Author",
        "publishedAt": "2024-01-01T12:00:00Z",
    },
]

RESPOSTA_API_MOCK = {"articles": NOTICIAS_MOCK}


def setup_function():
    """Limpa o cache antes de cada teste."""
    cache.clear()


def test_listar_categorias():
    """Testa se o endpoint de categorias funciona."""
    response = client.get("/api/noticias/categorias")
    assert response.status_code == 200
    data = response.json()
    assert "categorias" in data
    assert isinstance(data["categorias"], list)
    assert "Todas" in data["categorias"]


def test_categorias_esperadas():
    """Testa se as categorias esperadas estão presentes."""
    response = client.get("/api/noticias/categorias")
    data = response.json()
    categorias = data["categorias"]
    for cat in ["Python", "DevOps", "IA", "Segurança"]:
        assert cat in categorias


def test_listar_noticias_retorna_200():
    """Testa se o endpoint de notícias responde — sem chamar a API real."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: RESPOSTA_API_MOCK
        response = client.get("/api/noticias/")
    assert response.status_code == 200


def test_listar_noticias_estrutura():
    """Testa se a resposta tem a estrutura correta."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: RESPOSTA_API_MOCK
        response = client.get("/api/noticias/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "noticias" in data
    assert "atualizado_em" in data
    assert isinstance(data["noticias"], list)


def test_paginacao_valida():
    """Testa se a paginação funciona."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: RESPOSTA_API_MOCK
        response = client.get("/api/noticias/?pagina=1&por_pagina=5")
    assert response.status_code == 200


def test_filtro_por_categoria():
    """Testa se o filtro por categoria funciona."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: RESPOSTA_API_MOCK
        response = client.get("/api/noticias/?categoria=Python")
    assert response.status_code == 200


def test_categorizacao_automatica():
    """Testa a função de categorização — nome correto da função."""
    from app.services.noticia_service import _categorizar
    assert _categorizar("New Python 3.12 features", "") == "Python"
    assert _categorizar("Docker containers explained", "") == "DevOps"
    assert _categorizar("OpenAI releases new GPT model", "") == "IA"
    assert _categorizar("Major cybersecurity breach", "") == "Segurança"
    assert _categorizar("Random news story", "") == "Geral"
