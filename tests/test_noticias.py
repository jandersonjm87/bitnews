# ============================================================
#  tests/test_noticias.py
#  Testes automatizados para os endpoints de notícias.
# ============================================================

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.cache import cache

client = TestClient(app)


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
    """Testa se o endpoint de notícias responde."""
    response = client.get("/api/noticias/")
    assert response.status_code == 200


def test_listar_noticias_estrutura():
    """Testa se a resposta tem a estrutura correta."""
    response = client.get("/api/noticias/")
    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "noticias" in data
        assert "atualizado_em" in data
        assert isinstance(data["noticias"], list)


def test_paginacao_valida():
    """Testa se a paginação funciona."""
    response = client.get("/api/noticias/?pagina=1&por_pagina=5")
    assert response.status_code == 200


def test_filtro_por_categoria():
    """Testa se o filtro por categoria funciona."""
    response = client.get("/api/noticias/?categoria=Python")
    assert response.status_code == 200


def test_categorizacao_automatica():
    """Testa a função de categorização de notícias."""
    from app.services.noticia_service import _categorizar_noticia

    assert _categorizar_noticia("New Python 3.12 features", "") == "Python"
    assert _categorizar_noticia("Docker containers explained", "") == "DevOps"
    assert _categorizar_noticia("OpenAI releases new GPT model", "") == "IA"
    assert _categorizar_noticia("Major cybersecurity breach", "") == "Segurança"
    assert _categorizar_noticia("Random news story", "") == "Geral"
