# ============================================================
#  tests/test_cotacoes.py
#  Testes automatizados para os endpoints de cotacoes.
#
#  Padrao aplicado: mock das APIs externas para os testes
#  nao dependerem de rede externa nem de rate limit no CI.
# ============================================================

import time
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.cache import cache

client = TestClient(app)

# ── Dados falsos que simulam respostas das APIs ───────────
CRYPTO_MOCK = [
    {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "image": "https://example.com/btc.png",
        "current_price": 75000,
        "price_change_percentage_24h": -1.0,
        "price_change_percentage_7d_in_currency": 2.5,
        "total_volume": 30000000000,
        "market_cap": 1500000000000,
    },
]

FIAT_MOCK = {
    "rates": {"BRL": 5.03, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "USD": 1.0}
}

HISTORICO_MOCK = {
    "prices": [[1620000000000, 75000], [1620086400000, 76000]]
}


def setup_function():
    """Limpa o cache antes de cada teste."""
    cache.clear()
    # Limpa tambem o cache interno do cotacao_service
    from app.services import cotacao_service
    cotacao_service._cache.clear()


def test_health_check():
    """Testa se a API esta online."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app"] == "BitNews"


def test_listar_cotacoes_retorna_200():
    """Testa se o endpoint de cotacoes responde sem chamar APIs reais."""
    from app.services import cotacao_service
    from app.schemas.cotacao import Cotacao, PrecoCotacao

    cotacao_fake = Cotacao(
        id="bitcoin", simbolo="BTC", nome="Bitcoin", tipo="crypto",
        preco=PrecoCotacao(usd=75000, brl=377250, eur=69000)
    )

    with patch.object(cotacao_service, "buscar_cotacoes_crypto", new=AsyncMock(return_value=[cotacao_fake])):
        with patch.object(cotacao_service, "buscar_cotacoes_fiat", new=AsyncMock(return_value=[])):
            response = client.get("/api/cotacoes/")
    assert response.status_code == 200


def test_listar_cotacoes_estrutura():
    """Testa se a resposta tem a estrutura correta."""
    from app.services import cotacao_service
    from app.schemas.cotacao import Cotacao, PrecoCotacao

    cotacao_fake = Cotacao(
        id="bitcoin", simbolo="BTC", nome="Bitcoin", tipo="crypto",
        preco=PrecoCotacao(usd=75000, brl=377250, eur=69000)
    )

    with patch.object(cotacao_service, "buscar_cotacoes_crypto", new=AsyncMock(return_value=[cotacao_fake])):
        with patch.object(cotacao_service, "buscar_cotacoes_fiat", new=AsyncMock(return_value=[])):
            response = client.get("/api/cotacoes/")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "cotacoes" in data
    assert "atualizado_em" in data
    assert isinstance(data["cotacoes"], list)


def test_historico_periodo_invalido():
    """Testa se periodos invalidos retornam erro 400."""
    response = client.get("/api/cotacoes/historico/bitcoin?periodo=invalido")
    assert response.status_code == 400


def test_historico_periodo_valido():
    """Testa se periodos validos sao aceitos."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.raise_for_status = lambda: None
        mock_get.return_value.json = lambda: HISTORICO_MOCK
        for periodo in ["1d", "7d", "30d"]:
            response = client.get(f"/api/cotacoes/historico/bitcoin?periodo={periodo}")
            assert response.status_code == 200


def test_cache_funciona():
    """Testa se o cache esta funcionando."""
    cache.set("teste", {"valor": 42}, ttl=60)
    resultado = cache.get("teste")
    assert resultado == {"valor": 42}


def test_cache_expira():
    """Testa se o cache expira corretamente."""
    cache.set("expira", "valor", ttl=1)
    time.sleep(2)
    resultado = cache.get("expira")
    assert resultado is None
