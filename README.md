# ⚡ BitNews — Crypto, Câmbio e Tech News

![CI](https://github.com/jandersonjm87/bitnews/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple?logo=railway)

Acompanhe cotações de crypto e moedas fiat em tempo real, junto com as principais notícias tech do mundo.

Demo ao vivo: https://bitnews-production.up.railway.app
Documentação da API: https://bitnews-production.up.railway.app/docs

## 🚀 Sobre o projeto

O BitNews é um painel profissional para desenvolvedores que reúne em um único lugar o que importa: mercado financeiro e mundo tech.

- 📈 Cotações de criptomoedas e moedas fiat em tempo real
- 📊 Gráficos históricos interativos com períodos de 1D, 7D e 30D
- 📰 Notícias das maiores fontes tech do mundo
- 🔄 Atualização automática a cada 10 segundos
- ⚙️ Pipeline CI/CD completo com GitHub Actions + Railway

## ✨ Funcionalidades

### 📈 Cotações em Tempo Real
- Criptomoedas: Bitcoin, Ethereum, BNB, Solana, Cardano, XRP, Dogecoin, Polygon
- Moedas Fiat: Dólar Americano, Euro, Libra Esterlina, Iene Japonês
- Preços em BRL e USD com variação percentual 24h
- Gráfico de linha interativo com Chart.js
- Cache inteligente com fallback para rate limit HTTP 429

### 📰 Notícias Tech
- Fontes: TechCrunch, The Verge, Wired, Ars Technica
- Categorização automática: Python, DevOps, IA, Segurança, Web
- Paginação e filtro por categoria
- Atualização a cada 30 minutos

## 🛠️ Tecnologias

- ⚡ FastAPI — Framework da API REST
- 🐍 Python 3.11 — Linguagem principal
- 🔄 httpx — Requisições HTTP assíncronas
- ✅ Pydantic — Validação de dados com type hints
- 📊 CoinGecko API — Cotações de criptomoedas
- 💱 ExchangeRate API — Cotações de moedas fiat
- 📰 NewsAPI — Notícias tech em tempo real
- 📈 Chart.js — Gráficos interativos
- 🐳 Docker — Containerização
- ⚙️ GitHub Actions — Pipeline CI/CD
- 🚂 Railway — Deploy em produção

## 🚀 Como rodar

### 🐳 Com Docker

    git clone https://github.com/jandersonjm87/bitnews.git
    cd bitnews
    cp .env.example .env
    docker-compose up --build

### 🐍 Sem Docker

    git clone https://github.com/jandersonjm87/bitnews.git
    cd bitnews
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload

Acesse: http://localhost:8000

## ⚙️ Variáveis de ambiente

Copie .env.example para .env e preencha:

    NEWS_API_KEY=sua_chave_aqui
    DEBUG=false

Chave gratuita em: https://newsapi.org/register

## 🧪 Testes

    pytest tests/ -v

14 testes cobrindo endpoints, cache, categorização e paginação.

## 📡 Endpoints da API

- GET /api/health — Status da API
- GET /api/cotacoes/ — Todas as cotações
- GET /api/cotacoes/crypto — Apenas criptomoedas
- GET /api/cotacoes/fiat — Apenas moedas fiat
- GET /api/cotacoes/historico/{id} — Histórico para gráficos
- GET /api/noticias/ — Lista de notícias
- GET /api/noticias/categorias — Categorias disponíveis

## 👨‍💻 Autor

Janderson Maciel Alves da Silva
LinkedIn: https://linkedin.com/in/janderson-maciel-1791872b1
GitHub: https://github.com/jandersonjm87

## 📄 Licença

Este projeto está sob a licença MIT.
