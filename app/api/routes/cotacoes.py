from fastapi import APIRouter, HTTPException, Query
from app.services import cotacao_service
from app.schemas.cotacao import RespostaCotacoes, HistoricoCotacao

router = APIRouter()

@router.get("/", response_model=RespostaCotacoes)
async def listar_cotacoes():
    """Retorna todas as cotações — crypto e fiat em tempo real."""
    try:
        return await cotacao_service.buscar_todas_cotacoes()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/crypto")
async def listar_crypto():
    """Retorna apenas criptomoedas."""
    try:
        return await cotacao_service.buscar_cotacoes_crypto()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/fiat")
async def listar_fiat():
    """Retorna apenas moedas fiat."""
    try:
        return await cotacao_service.buscar_cotacoes_fiat()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/historico/{moeda_id}", response_model=HistoricoCotacao)
async def historico_cotacao(
    moeda_id: str,
    periodo: str = Query("7d", description="Período: 1d, 7d ou 30d"),
    tipo: str = Query("crypto", description="Tipo: crypto ou fiat"),
):
    """Histórico de preços para gráficos. Suporta crypto e fiat."""
    if periodo not in ["1d","7d","30d"]:
        raise HTTPException(status_code=400, detail="Período inválido. Use: 1d, 7d ou 30d")
    if tipo not in ["crypto","fiat"]:
        raise HTTPException(status_code=400, detail="Tipo inválido. Use: crypto ou fiat")
    try:
        return await cotacao_service.buscar_historico(moeda_id, periodo, tipo)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
