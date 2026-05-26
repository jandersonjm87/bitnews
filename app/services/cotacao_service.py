import httpx, time, random
from datetime import datetime, timedelta
from app.core.config import get_settings
from app.schemas.cotacao import Cotacao, PrecoCotacao, HistoricoCotacao, PontoHistorico, RespostaCotacoes

settings = get_settings()
MOEDAS_CRYPTO = ['bitcoin','ethereum','binancecoin','solana','cardano','ripple','dogecoin','polygon-ecosystem-token']
MOEDAS_FIAT = {'usd':{'nome':'Dólar Americano','simbolo':'USD'},'eur':{'nome':'Euro','simbolo':'EUR'},'gbp':{'nome':'Libra Esterlina','simbolo':'GBP'},'jpy':{'nome':'Iene Japonês','simbolo':'JPY'}}
PERIODO_DIAS = {'1d':1,'7d':7,'30d':30}
_cache = {}

def _cget(k):
    i=_cache.get(k)
    return i['v'] if i and time.time()<i['e'] else None

def _cset(k,v,t):
    _cache[k]={'v':v,'e':time.time()+t}

async def _taxa_brl():
    c=_cget('brl')
    if c: return c
    try:
        async with httpx.AsyncClient(timeout=5.0) as cl:
            r=await cl.get('https://api.exchangerate-api.com/v4/latest/USD')
            t=float(r.json()['rates']['BRL'])
            _cset('brl',t,300)
            return t
    except: return 5.0

async def buscar_cotacoes_crypto():
    c=_cget('crypto')
    if c: return c
    async with httpx.AsyncClient(timeout=15.0) as cl:
        r=await cl.get(f'{settings.COINGECKO_URL}/coins/markets',params={'vs_currency':'usd','ids':','.join(MOEDAS_CRYPTO),'order':'market_cap_desc','price_change_percentage':'24h,7d','sparkline':False})
        if r.status_code==429:
            fb=_cget('crypto_fb')
            return fb if fb else []
        r.raise_for_status()
        dados=r.json()
    t=await _taxa_brl()
    result=[Cotacao(id=m['id'],simbolo=m['symbol'].upper(),nome=m['name'],tipo='crypto',imagem=m.get('image'),preco=PrecoCotacao(usd=float(m["current_price"] or 0),brl=round(float(m["current_price"] or 0)*float(t),2),eur=round(float(m["current_price"] or 0)*0.92,2),variacao_24h=m.get('price_change_percentage_24h'),variacao_7d=m.get('price_change_percentage_7d_in_currency'),volume_24h=m.get('total_volume'),market_cap=m.get('market_cap'))) for m in dados]
    _cset('crypto',result,30)
    _cset('crypto_fb',result,3600)
    return result

async def buscar_cotacoes_fiat():
    c=_cget('fiat')
    if c: return c
    async with httpx.AsyncClient(timeout=10.0) as cl:
        r=await cl.get('https://api.exchangerate-api.com/v4/latest/USD')
        r.raise_for_status()
        taxas=r.json()['rates']
    brl=taxas.get('BRL',5.0)
    result=[Cotacao(id=k,simbolo=v['simbolo'],nome=v['nome'],tipo='fiat',preco=PrecoCotacao(usd=round(1.0/taxas.get(k.upper(),1.0),4),brl=round(brl/taxas.get(k.upper(),1.0),2),eur=round(taxas.get('EUR',0.92)/taxas.get(k.upper(),1.0),4),variacao_24h=None)) for k,v in MOEDAS_FIAT.items()]
    _cset('fiat',result,60)
    return result

async def buscar_historico(moeda_id,periodo,tipo='crypto'):
    ck=f'h_{moeda_id}_{periodo}_{tipo}'
    c=_cget(ck)
    if c: return c
    dias=PERIODO_DIAS.get(periodo,7)
    if tipo=='crypto':
        async with httpx.AsyncClient(timeout=15.0) as cl:
            r=await cl.get(f'{settings.COINGECKO_URL}/coins/{moeda_id}/market_chart',params={'vs_currency':'usd','days':dias})
            r.raise_for_status()
            dados=r.json()
        pontos=[PontoHistorico(timestamp=int(p[0]),preco=p[1]) for p in dados.get('prices',[])]
    else:
        async with httpx.AsyncClient(timeout=10.0) as cl:
            r=await cl.get('https://api.exchangerate-api.com/v4/latest/USD')
            taxas=r.json()['rates']
        brl=taxas.get('BRL',5.0)
        taxa=taxas.get(moeda_id.upper(),1.0)
        pa=brl/taxa if taxa>0 else brl
        pontos=[]
        agora=datetime.now()
        p=pa*(1+random.uniform(-0.02,0.02))
        for i in range(100):
            ts=int((agora-timedelta(days=dias)+timedelta(seconds=i*dias*864)).timestamp()*1000)
            p=p*(1+random.uniform(-0.003,0.003))
            pontos.append(PontoHistorico(timestamp=ts,preco=round(p,4)))
        pontos[-1].preco=pa
    h=HistoricoCotacao(moeda_id=moeda_id,periodo=periodo,dados=pontos)
    _cset(ck,h,300)
    return h

async def buscar_todas_cotacoes():
    c=_cget('todas')
    if c: return RespostaCotacoes(total=len(c),cotacoes=c,cache_hit=True,atualizado_em=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    crypto=await buscar_cotacoes_crypto()
    fiat=await buscar_cotacoes_fiat()
    todas=fiat+crypto
    _cset('todas',todas,30)
    return RespostaCotacoes(total=len(todas),cotacoes=todas,cache_hit=False,atualizado_em=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
