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

## Assistente de IA (OpenAI e Gemini)

O dashboard inclui um assistente flutuante **✦ Assistente IA** e uma tela **Configurações IA**. O visitante escolhe um provedor e usa sua própria chave de API para perguntas livres. Estão disponíveis também respostas locais e exatas sem chave (faturamento, lucro bruto, margem, ticket médio, ranking de produtos, caixa, RH e suporte à navegação).

- O navegador guarda a chave **somente na memória desta aba** até fechar/recarregar. Não usa cookies, \`localStorage\`, \`sessionStorage\` ou banco de dados.
- Para perguntas livres, o navegador envia a chave por **HTTPS** à rota \`POST /api/chat\`. O FastAPI encaminha-a somente ao endereço fixo do provedor escolhido; a chave não aparece na URL nem é salva, retornada ou escrita em logs pelo código da aplicação.
- **Importante:** o operador do site controla o backend e pode tecnicamente interceptar requisições. Não peça que visitantes usem chaves de alto privilégio. Recomende criar chave com gastos limitados e uso restrito, usando apenas sites confiáveis.
- O OpenAI Responses API usa \`gpt-5.4-mini\` com \`store: false\`. O Gemini API usa \`gemini-3.5-flash-lite\` com \`x-goog-api-key\`. O acesso depende da conta do visitante, disponibilidade de modelos e possíveis cobranças.
- Os provedores externos recebem apenas a pergunta, um trecho recente da conversa e os **indicadores sintéticos do dashboard**; não recebem dados pessoais reais nem acesso ao PostgreSQL.
- O endpoint aceita perguntas de até 900 caracteres, histórico de no máximo seis mensagens, tempo limite de requisição, e não permite URLs de destino fornecidas pelo visitante. Erros do provedor são filtrados para não vazar credenciais.
- Ainda não há autenticação, rate limiting distribuído ou suporte a dados empresariais reais. **Não utilize chaves de produção ou dados privados.**

## Gráficos ampliados e interativos

A página ganhou opção de detalhamento **automático / semanal / mensal**, visões maiores, valores exatos sob o cursor ou via teclado, e botão **⛶** para ampliar gráficos. O cálculo das séries semanais é feito no Python a partir das mesmas vendas e lançamentos que alimentam os KPIs. Todos os resultados permanecem fictícios.

## Testes da integração

\`\`\`bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/app.js
\`\`\`

Os testes de IA são simulados, **sem usar chaves de terceiros nem realizar cobranças reais**. É necessário fazer uma pergunta com uma chave válida para validar ao vivo o acesso do provedor escolhido.
