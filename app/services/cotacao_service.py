# ============================================================
#  app/services/cotacao_service.py
#
#  Responsabilidade: buscar cotacoes de criptomoedas e
#  moedas fiat em tempo real via CoinGecko e ExchangeRate API.
#
#  Padroes aplicados:
#    - Cache em memoria para respeitar rate limits
#    - Fallback para ultimo valor conhecido (HTTP 429)
#    - Separacao entre crypto e fiat
#    - Funcoes pequenas com responsabilidade unica
# ============================================================

import httpx
import time
import random
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.schemas.cotacao import (
    Cotacao,
    PrecoCotacao,
    HistoricoCotacao,
    PontoHistorico,
    RespostaCotacoes,
)

settings = get_settings()

# ── Moedas monitoradas ────────────────────────────────────
MOEDAS_CRYPTO = [
    "bitcoin", "ethereum", "binancecoin", "solana",
    "cardano", "ripple", "dogecoin", "polygon-ecosystem-token",
]

MOEDAS_FIAT = {
    "usd": {"nome": "Dolar Americano", "simbolo": "USD"},
    "eur": {"nome": "Euro",            "simbolo": "EUR"},
    "gbp": {"nome": "Libra Esterlina", "simbolo": "GBP"},
    "jpy": {"nome": "Iene Japones",    "simbolo": "JPY"},
}

PERIODO_DIAS = {"1d": 1, "7d": 7, "30d": 30}

# ── Cache local simples (independente do cache global) ────
_cache: dict = {}


def _cache_get(chave: str):
    """Retorna valor do cache se ainda valido, senao None."""
    item = _cache.get(chave)
    if item and time.time() < item["expira"]:
        return item["valor"]
    return None


def _cache_set(chave: str, valor, ttl: int) -> None:
    """Armazena valor no cache com tempo de expiracao."""
    _cache[chave] = {"valor": valor, "expira": time.time() + ttl}


# ── Taxa de cambio BRL ────────────────────────────────────
async def _buscar_taxa_brl() -> float:
    """
    Busca a taxa de cambio USD para BRL.
    Retorna 5.0 como fallback em caso de erro.
    """
    taxa_em_cache = _cache_get("taxa_brl")
    if taxa_em_cache:
        return taxa_em_cache

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://api.exchangerate-api.com/v4/latest/USD")
            taxa = float(response.json()["rates"]["BRL"])
            _cache_set("taxa_brl", taxa, ttl=300)
            return taxa
    except Exception:
        return 5.0


# ── Cotacoes de criptomoedas ──────────────────────────────
async def buscar_cotacoes_crypto() -> list[Cotacao]:
    """
    Busca cotacoes de criptomoedas via CoinGecko.
    Cache de 30 segundos. Fallback em caso de rate limit (HTTP 429).
    """
    em_cache = _cache_get("crypto")
    if em_cache:
        return em_cache

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{settings.COINGECKO_URL}/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ",".join(MOEDAS_CRYPTO),
                "order": "market_cap_desc",
                "price_change_percentage": "24h,7d",
                "sparkline": False,
            },
        )

        if response.status_code == 429:
            fallback = _cache_get("crypto_fallback")
            return fallback if fallback else []

        response.raise_for_status()
        moedas = response.json()

    taxa_brl = await _buscar_taxa_brl()

    cotacoes = [
        Cotacao(
            id=moeda["id"],
            simbolo=moeda["symbol"].upper(),
            nome=moeda["name"],
            tipo="crypto",
            imagem=moeda.get("image"),
            preco=PrecoCotacao(
                usd=float(moeda["current_price"] or 0),
                brl=round(float(moeda["current_price"] or 0) * taxa_brl, 2),
                eur=round(float(moeda["current_price"] or 0) * 0.92, 2),
                variacao_24h=moeda.get("price_change_percentage_24h"),
                variacao_7d=moeda.get("price_change_percentage_7d_in_currency"),
                volume_24h=moeda.get("total_volume"),
                market_cap=moeda.get("market_cap"),
            ),
        )
        for moeda in moedas
    ]

    _cache_set("crypto", cotacoes, ttl=30)
    _cache_set("crypto_fallback", cotacoes, ttl=3600)
    return cotacoes


# ── Cotacoes de moedas fiat ───────────────────────────────
async def buscar_cotacoes_fiat() -> list[Cotacao]:
    """
    Busca cotacoes de moedas fiat via ExchangeRate API.
    Cache de 60 segundos.
    """
    em_cache = _cache_get("fiat")
    if em_cache:
        return em_cache

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://api.exchangerate-api.com/v4/latest/USD")
        response.raise_for_status()
        taxas = response.json()["rates"]

    taxa_brl = taxas.get("BRL", 5.0)

    cotacoes = [
        Cotacao(
            id=moeda_id,
            simbolo=info["simbolo"],
            nome=info["nome"],
            tipo="fiat",
            preco=PrecoCotacao(
                usd=round(1.0 / taxas.get(moeda_id.upper(), 1.0), 4),
                brl=round(taxa_brl / taxas.get(moeda_id.upper(), 1.0), 2),
                eur=round(taxas.get("EUR", 0.92) / taxas.get(moeda_id.upper(), 1.0), 4),
                variacao_24h=None,
            ),
        )
        for moeda_id, info in MOEDAS_FIAT.items()
    ]

    _cache_set("fiat", cotacoes, ttl=60)
    return cotacoes


# ── Historico para graficos ───────────────────────────────
async def buscar_historico(moeda_id: str, periodo: str, tipo: str = "crypto") -> HistoricoCotacao:
    """
    Busca historico de precos para renderizar graficos.
    Crypto: dados reais via CoinGecko.
    Fiat: simulacao baseada na taxa atual com variacao realista.
    """
    chave_cache = f"historico_{moeda_id}_{periodo}_{tipo}"
    em_cache = _cache_get(chave_cache)
    if em_cache:
        return em_cache

    dias = PERIODO_DIAS.get(periodo, 7)

    if tipo == "crypto":
        pontos = await _buscar_historico_crypto(moeda_id, dias)
    else:
        pontos = await _gerar_historico_fiat(moeda_id, dias)

    historico = HistoricoCotacao(moeda_id=moeda_id, periodo=periodo, dados=pontos)
    _cache_set(chave_cache, historico, ttl=300)
    return historico


async def _buscar_historico_crypto(moeda_id: str, dias: int) -> list[PontoHistorico]:
    """Busca historico real de criptomoeda via CoinGecko."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{settings.COINGECKO_URL}/coins/{moeda_id}/market_chart",
            params={"vs_currency": "usd", "days": dias},
        )
        response.raise_for_status()
        dados = response.json()

    return [
        PontoHistorico(timestamp=int(ponto[0]), preco=ponto[1])
        for ponto in dados.get("prices", [])
    ]


async def _gerar_historico_fiat(moeda_id: str, dias: int) -> list[PontoHistorico]:
    """
    Gera historico simulado para moedas fiat.
    Usa a taxa atual como ancora e aplica variacao aleatoria realista.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("https://api.exchangerate-api.com/v4/latest/USD")
        taxas = response.json()["rates"]

    taxa_brl = taxas.get("BRL", 5.0)
    taxa_moeda = taxas.get(moeda_id.upper(), 1.0)
    preco_atual = taxa_brl / taxa_moeda if taxa_moeda > 0 else taxa_brl

    pontos = []
    agora = datetime.now()
    preco = preco_atual * (1 + random.uniform(-0.02, 0.02))

    for i in range(100):
        timestamp = int(
            (agora - timedelta(days=dias) + timedelta(seconds=i * dias * 864)).timestamp() * 1000
        )
        preco = preco * (1 + random.uniform(-0.003, 0.003))
        pontos.append(PontoHistorico(timestamp=timestamp, preco=round(preco, 4)))

    pontos[-1].preco = preco_atual
    return pontos


# ── Todas as cotacoes juntas ──────────────────────────────
async def buscar_todas_cotacoes() -> RespostaCotacoes:
    """
    Agrega crypto e fiat em uma unica resposta.
    Cache de 30 segundos.
    """
    em_cache = _cache_get("todas")
    if em_cache:
        return RespostaCotacoes(
            total=len(em_cache),
            cotacoes=em_cache,
            cache_hit=True,
            atualizado_em=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    crypto = await buscar_cotacoes_crypto()
    fiat = await buscar_cotacoes_fiat()
    todas = fiat + crypto

    _cache_set("todas", todas, ttl=30)

    return RespostaCotacoes(
        total=len(todas),
        cotacoes=todas,
        cache_hit=False,
        atualizado_em=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
