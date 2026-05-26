# ============================================================
#  app/core/cache.py
#  Sistema de cache em memória.
#  Evita chamar APIs externas a cada requisição,
#  reduzindo latência e respeitando rate limits.
# ============================================================

import time
from typing import Any, Optional


class CacheItem:
    """Representa um item armazenado no cache com TTL."""

    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl

    def is_expired(self) -> bool:
        """Verifica se o item já expirou."""
        return time.time() > self.expires_at


class MemoryCache:
    """
    Cache simples em memória com suporte a TTL por chave.
    Padrão usado em aplicações de alta performance.
    """

    def __init__(self):
        self._store: dict[str, CacheItem] = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Retorna o valor do cache se existir e não tiver expirado.
        Retorna None caso contrário.
        """
        item = self._store.get(key)
        if item is None or item.is_expired():
            if key in self._store:
                del self._store[key]
            return None
        return item.value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Armazena um valor no cache com tempo de expiração."""
        self._store[key] = CacheItem(value=value, ttl=ttl)

    def delete(self, key: str) -> None:
        """Remove um item do cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Limpa todo o cache."""
        self._store.clear()

    def size(self) -> int:
        """Retorna o número de itens no cache."""
        return len(self._store)


# Instância global do cache — compartilhada por toda a aplicação
cache = MemoryCache()
