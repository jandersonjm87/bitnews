# ============================================================
#  app/core/config.py
#  Configurações centralizadas da aplicação.
#  Todas as variáveis sensíveis vêm do arquivo .env —
#  nunca hardcoded no código. Padrão de mercado.
# ============================================================

from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Informações da aplicação
    APP_NAME: str = "BitNews"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # NewsAPI
    NEWS_API_KEY: str
    NEWS_API_URL: str = "https://newsapi.org/v2"

    # CoinGecko (sem chave — API pública)
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3"

    # Cache em memória (segundos)
    CACHE_COTACOES_TTL: int = 10    # cotações: 10 segundos
    CACHE_NOTICIAS_TTL: int = 1800  # notícias: 30 minutos

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação usando cache.
    lru_cache garante que o arquivo .env é lido apenas uma vez.
    """
    return Settings()
