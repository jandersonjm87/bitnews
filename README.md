# TechBoard — Painel do Desenvolvedor

Painel web completo em tempo real com cotacoes financeiras e noticias tech.
Desenvolvido com FastAPI, Python e Docker.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-containerizado-blue?logo=docker)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-black?logo=github-actions)
![Status](https://img.shields.io/badge/Status-Concluido-brightgreen)

## Sobre o projeto

O TechBoard e um painel profissional para desenvolvedores que reune em um unico
lugar informacoes essenciais do mercado e do mundo tech.

- Cotacoes de criptomoedas e moedas fiat em tempo real
- Graficos historicos interativos com periodos de 1D, 7D e 30D
- Noticias das maiores fontes tech do mundo
- Atualizacao automatica a cada 10 segundos

## Funcionalidades

### Cotacoes em Tempo Real
- Criptomoedas: Bitcoin, Ethereum, BNB, Solana, Cardano, XRP, Dogecoin, Polygon
- Moedas Fiat: Dolar Americano, Euro, Libra Esterlina, Iene Japones
- Precos em BRL e USD com variacao percentual 24h
- Grafico de linha interativo com Chart.js
- Cache inteligente com fallback para rate limit

### Noticias Tech
- Fontes: TechCrunch, The Verge, Wired, Ars Technica
- Categorizacao automatica: Python, DevOps, IA, Seguranca, Web
- Paginacao e filtro por categoria
- Atualizacao a cada 30 minutos

## Arquitetura

    techboard/
    app/
        api/routes/         Endpoints REST
            cotacoes.py
            noticias.py
        core/
            cache.py        Cache em memoria com TTL
            config.py       Configuracoes centralizadas
        schemas/            Modelos de dados Pydantic
            cotacao.py
            noticia.py
        services/           Logica de negocio
            cotacao_service.py
            noticia_service.py
        main.py
    frontend/
        css/style.css
        js/cotacoes.js
        js/noticias.js
        index.html
    tests/
    Dockerfile
    docker-compose.yml
    requirements.txt

## Tecnologias

- FastAPI: Framework da API REST
- httpx: Requisicoes HTTP assincronas
- Pydantic: Validacao de dados com type hints
- CoinGecko API: Cotacoes de criptomoedas gratuita
- ExchangeRate API: Cotacoes de moedas fiat gratuita
- NewsAPI: Noticias tech em tempo real
- Chart.js: Graficos interativos
- Docker: Containerizacao
- GitHub Actions: Pipeline CI/CD

## Como rodar

### Com Docker
    git clone https://github.com/jandersonjm87/techboard.git
    cd techboard
    cp .env.example .env
    docker-compose up --build

### Sem Docker
    git clone https://github.com/jandersonjm87/techboard.git
    cd techboard
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload

Acesse: http://localhost:8000

## Variaveis de ambiente

Copie .env.example para .env e preencha:

    NEWS_API_KEY=sua_chave_aqui
    DEBUG=false

Chave gratuita em: https://newsapi.org/register

## Testes

    pip install pytest pytest-asyncio
    pytest tests/ -v

## Endpoints da API

- GET /api/health             Status da aplicacao
- GET /api/cotacoes/          Todas as cotacoes
- GET /api/cotacoes/crypto    Apenas criptomoedas
- GET /api/cotacoes/fiat      Apenas moedas fiat
- GET /api/cotacoes/historico/{id}  Historico para graficos
- GET /api/noticias/          Noticias tech
- GET /api/noticias/categorias     Categorias disponiveis

## Autor

Janderson Maciel Alves da Silva

LinkedIn: https://linkedin.com/in/janderson-maciel-1791872b1
GitHub: https://github.com/jandersonjm87

## Licenca

Este projeto esta sob a licenca MIT.
