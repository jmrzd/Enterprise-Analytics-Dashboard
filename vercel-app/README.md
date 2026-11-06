# Enterprise Analytics — versão Vercel

Interface web futurista para portfólio, com **FastAPI (Python)**, HTML/CSS/JavaScript e visualizações SVG sem bibliotecas externas de gráficos.

> **Atenção:** este deploy usa **dados 100% sintéticos**. Não há conexão com dados reais, nem login. A aplicação original Streamlit + PostgreSQL + Pandas e os scripts Power BI continuam na raiz do repositório.

## Executar localmente

```bash
cd vercel-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Acesse http://127.0.0.1:8000.

## Endpoints

- `GET /` — interface responsiva.
- `GET /api/dashboard?period=30d|90d|180d|365d` — indicadores gerados em Python, em JSON.
- `GET /api/health` — status do serviço.
- `GET /api/docs` — documentação OpenAPI do FastAPI.

O endpoint gera dados sintéticos determinísticos por dia, com consistência entre vendas, produtos e clientes. Financeiro e RH são conjuntos separados e não devem ser interpretados como lucro líquido contábil.

## Publicação na Vercel

Configure o projeto da Vercel com:

- **Git Repository:** `jmrzd/Enterprise-Analytics-Dashboard`
- **Root Directory:** `vercel-app`
- **Framework Preset:** `FastAPI`
- **Production Branch:** `main`
- **Environment variables:** nenhuma para o modo demo.

A Vercel instala `vercel-app/requirements.txt` e expõe a aplicação FastAPI em `app.py`. Não aponte a Vercel para o Streamlit da raiz. Os arquivos HTML/CSS/JS ficam em `templates/` (NÃO em `public/`) para evitar que a CDN sirva `index.html` sem passar pelo FastAPI. A resposta `/` inclui CSS, JavaScript e dados iniciais inline. Cabeçalho de diagnóstico: `X-Dashboard-Render: fastapi-inline-v3`.

## Testes

```bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/app.js
```

## Próximos passos

- Implementar API autenticada e conexão segura com PostgreSQL para dados reais.
- Adicionar controle de acesso por função antes de disponibilizar RH.
- Construir o arquivo Power BI `.pbix` e publicar relatórios.
- Adicionar testes de ponta a ponta no navegador.
