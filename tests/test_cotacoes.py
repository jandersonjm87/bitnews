# ============================================================
#  tests/test_cotacoes.py
#  Testes automatizados para os endpoints de cotações.
#  Testes garantem que o código funciona como esperado.
# ============================================================

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.cache import cache

client = TestClient(app)


def setup_function():
    """Limpa o cache antes de cada teste."""
    cache.clear()


def test_health_check():
    """Testa se a API está online."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app"] == "TechBoard"


def test_listar_cotacoes_retorna_200():
    """Testa se o endpoint de cotações responde corretamente."""
    response = client.get("/api/cotacoes/")
    assert response.status_code == 200


def test_listar_cotacoes_estrutura():
    """Testa se a resposta tem a estrutura correta."""
    response = client.get("/api/cotacoes/")
    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "cotacoes" in data
        assert "atualizado_em" in data
        assert isinstance(data["cotacoes"], list)


def test_historico_periodo_invalido():
    """Testa se períodos inválidos retornam erro 400."""
    response = client.get("/api/cotacoes/historico/bitcoin?periodo=invalido")
    assert response.status_code == 400


def test_historico_periodo_valido():
    """Testa se períodos válidos são aceitos."""
    for periodo in ["1d", "7d", "30d"]:
        response = client.get(f"/api/cotacoes/historico/bitcoin?periodo={periodo}")
        assert response.status_code in [200, 503]  # 503 se API externa indisponível


def test_cache_funciona():
    """Testa se o cache está funcionando."""
    from app.core.cache import cache

    cache.set("teste", {"valor": 42}, ttl=60)
    resultado = cache.get("teste")
    assert resultado == {"valor": 42}


def test_cache_expira():
    """Testa se o cache expira corretamente."""
    import time
    from app.core.cache import cache

    cache.set("expira", "valor", ttl=1)
    time.sleep(2)
    resultado = cache.get("expira")
    assert resultado is None
