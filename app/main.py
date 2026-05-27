# ============================================================
#  app/main.py
#
#  Ponto de entrada da aplicação TechBoard.
#  Configura o FastAPI, middlewares, routers e serve
#  o dashboard frontend como arquivo estático.
# ============================================================

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import cotacoes, noticias
from app.core.config import get_settings

settings = get_settings()

# ── Instância do FastAPI ──────────────────────────────────
app = FastAPI(
    title=f"⚡ {settings.APP_NAME} — Crypto, Câmbio e Tech News",
    description="""
**TechBoard** — Painel completo para desenvolvedores.

## Módulos disponíveis:
- 📈 **Cotações** — Crypto e moedas fiat em tempo real
- 📰 **Notícias** — Tech news das melhores fontes do mundo

Desenvolvido por **Janderson Maciel**
    """,
    version=settings.APP_VERSION,
)

# ── CORS ──────────────────────────────────────────────────
# Permite que o frontend acesse a API em qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────
app.include_router(
    cotacoes.router,
    prefix="/api/cotacoes",
    tags=["📈 Cotações"],
)
app.include_router(
    noticias.router,
    prefix="/api/noticias",
    tags=["📰 Notícias"],
)

# ── Frontend estático ─────────────────────────────────────
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    @app.get("/", include_in_schema=False)
    async def dashboard():
        """Serve o dashboard principal."""
        return FileResponse("frontend/index.html")


# ── Health check ──────────────────────────────────────────
@app.get("/api/health", tags=["Sistema"])
async def health_check():
    """Verifica se a API está no ar e retorna informações básicas."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "versao": settings.APP_VERSION,
        "desenvolvido_por": "Janderson Maciel",
    }
