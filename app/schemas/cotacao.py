# ============================================================
#  app/schemas/cotacao.py
#  Modelos de dados para cotações.
#  Type hints em tudo — padrão de código limpo.
# ============================================================

from pydantic import BaseModel
from typing import Optional


class PrecoCotacao(BaseModel):
    """Preço atual de uma moeda/cripto."""
    usd: float
    brl: float
    eur: float
    variacao_24h: Optional[float] = None
    variacao_7d: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None


class Cotacao(BaseModel):
    """Dados completos de uma moeda ou criptomoeda."""
    id: str
    simbolo: str
    nome: str
    tipo: str  # "fiat" ou "crypto"
    preco: PrecoCotacao
    imagem: Optional[str] = None


class PontoHistorico(BaseModel):
    """Ponto de dado em um gráfico histórico."""
    timestamp: int
    preco: float


class HistoricoCotacao(BaseModel):
    """Histórico de preços para gráficos."""
    moeda_id: str
    periodo: str  # "1d", "7d", "30d"
    dados: list[PontoHistorico]


class RespostaCotacoes(BaseModel):
    """Resposta da API com lista de cotações."""
    total: int
    cotacoes: list[Cotacao]
    cache_hit: bool = False
    atualizado_em: str
