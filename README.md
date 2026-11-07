<div align="center">

# ◈ ENTERPRISE · ANALYTICS

### Business Intelligence • Data Engineering • Assistente de IA

**Dashboard futurista e responsivo para transformar dados em indicadores, análises e decisões.**

[**🚀 Acessar demonstração online**](https://enterprise-analytics-dashboard-ivory.vercel.app/) · [**📖 Guia da aplicação web**](vercel-app/README.md) · [**🔐 Segurança**](vercel-app/SECURITY.md)

[![Vercel Demo Quality](https://github.com/jmrzd/Enterprise-Analytics-Dashboard/actions/workflows/vercel-demo.yml/badge.svg)](https://github.com/jmrzd/Enterprise-Analytics-Dashboard/actions/workflows/vercel-demo.yml)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Portf%C3%B3lio%20%2F%20MVP-8B5CF6)

</div>

---

## 📌 Sobre o projeto

O **Enterprise Analytics Dashboard** é um projeto de portfólio de **Business Intelligence, desenvolvimento web e análise de dados**. Ele reúne indicadores de **Vendas, Financeiro e Recursos Humanos** em uma interface escura, com cores neon, gráficos interativos, simulador de cenários, assistente com IA e ferramentas para exportação ao Power BI.

O repositório contém **duas aplicações complementares**:

| Aplicação | Tecnologia | Objetivo |
| --- | --- | --- |
| **Dashboard web — Vercel** | Python, FastAPI, HTML, CSS, JavaScript e SVG | Apresentação pública, UX futurista, IA, simulação, Power BI Studio e assistente de Integrações |
| **Dashboard local — Streamlit** | Python, PostgreSQL, SQL, Pandas, Streamlit e Plotly | Explorar consultas reais a um banco PostgreSQL de desenvolvimento e praticar BI ponta a ponta |

> [!IMPORTANT]
> A **demonstração pública utiliza dados sintéticos** por padrão. A aba Integrações oferece apenas um **piloto autorizado de leitura de bancos externos**; essas consultas não substituem automaticamente os indicadores fictícios dos demais painéis. O projeto **não é ainda um SaaS pronto para armazenar dados confidenciais de empresas**.

## ✨ Principais funcionalidades

| Recurso | O que você pode fazer | Estado |
| --- | --- | --- |
| **Visão geral** | Consultar faturamento, lucro bruto, saldo, equipe, tendências e indicadores executivos | ✅ Demo funcional |
| **Vendas e faturamento** | Explorar produtos, clientes, pedidos, receita, margens e performance | ✅ Demo funcional |
| **Financeiro** | Acompanhar fluxo de caixa, despesas, pendências e evolução financeira | ✅ Demo funcional |
| **Recursos Humanos** | Analisar equipe, departamentos, movimentações e custos de pessoal | ✅ Demo funcional |
| **Gráficos interativos** | Alternar **Linha / Área / Barras**, consultar valores, filtrar períodos, ligar/desligar séries e ampliar gráficos | ✅ Funcional |
| **Insights e alertas** | Ler indicadores calculados, alertas demonstrativos e comparações entre períodos | ✅ Funcional |
| **Simulador de cenários** | Experimentar variações de preço, volume, custos, contratações e despesas, sem alterar a base | ✅ Funcional |
| **Assistente IA** | Fazer perguntas sobre o dashboard com OpenAI ou Gemini usando uma chave própria; realizar alguns cálculos locais sem chave | ✅ Funcional / BYOK |
| **Integrações** | Testar uma base fictícia, visualizar CSV/Excel e mapear colunas; testar PostgreSQL/MySQL com autorização | 🧪 Piloto protegido |
| **Sincronização sob demanda** | Consultar agregados de uma tabela autorizada, visualizar resumo e exportar CSV | 🧪 Piloto protegido |
| **Power BI Studio** | Exportar 6 CSVs, medidas DAX e um kit ZIP para o Power BI Desktop | ✅ Kit funcional |
| **Layout multiplataforma** | Navegar em celulares, iPhones, Android, tablets, iPads, notebooks e desktops | ✅ Responsivo |

### 🎛️ Uma experiência de BI interativa

- **Interface futurista:** cartões neon, sparklines, gráficos SVG, menus e subabas com estado ativo.
- **Gráficos exploráveis:** modos **Linha**, **Área** e **Barras**, zoom/ampliação, tooltips e legendas interativas.
- **Filtros:** períodos de 30, 90, 180 e 365 dias na aplicação web, além de detalhamento automático, semanal ou mensal quando aplicável.
- **Comparação de períodos:** comparação com o intervalo anterior equivalente para 30, 90 e 180 dias; para 365 dias, o histórico demonstrativo não é suficiente para uma comparação equivalente.
- **Busca rápida:** pressione **Ctrl + K** no computador para localizar módulos e ferramentas.
- **Central de alertas:** indicações calculadas a partir dos dados fictícios, com atalhos de navegação.
- **UX mobile:** menu lateral com botão de fechar, navegação inferior, controles maiores para toque, gráficos deslizáveis e ajustes para o teclado do Safari.

### 🧠 Assistente IA — OpenAI e Gemini

O botão **✦ IA** abre um assistente que ajuda a interpretar métricas, explicar gráficos, realizar cálculos e encontrar funcionalidades do site.

**Como funciona:**

1. Abra **Configurações IA**.
2. Escolha **OpenAI** ou **Google Gemini**.
3. Informe **sua própria chave de API** para usar o modelo disponível na sua conta.
4. Faça perguntas no assistente. Para perguntas simples e cálculos predefinidos, há respostas locais que **não exigem chave**.

| Modo | Comportamento |
| --- | --- |
| **Cálculos locais** | Respostas baseadas nos indicadores de demonstração, sem chamar um serviço LLM |
| **OpenAI** | Integração via Responses API usando o modelo configurado no backend (`gpt-5.4-mini`) |
| **Gemini** | Integração via API Google usando o modelo configurado no backend (`gemini-3.5-flash-lite`) |

**Modelo de chave própria (BYOK):** a chave permanece na memória da aba do navegador; não é salva em `localStorage`, cookies ou banco de dados pelo código da aplicação. Para perguntas via LLM, a chave é enviada por **HTTPS ao backend da Vercel** e encaminhada ao provedor escolhido. **O operador do servidor pode tecnicamente acessar requisições**; use apenas um ambiente confiável e uma chave restrita, com limite de gastos. Chamadas ao provedor podem gerar cobrança e dependem do acesso ao modelo.

**Escopo atual:** a IA recebe os **indicadores sintéticos**, a pergunta e um histórico limitado da conversa. **Ela não consulta automaticamente o banco que uma empresa conectar na aba Integrações.** Os modelos e a disponibilidade podem mudar; consulte `vercel-app/assistant_api.py`.

### 🔌 Central de Integrações

A aba **Integrações** tem um assistente visual em três etapas: **escolher fonte → testar → mapear colunas**. A proposta é explorar conexões sem alterar o código Python para cada empresa.

| Origem | O que está disponível |
| --- | --- |
| **Demonstração** | Fluxo completo com dados fictícios, sem configuração |
| **CSV / Excel (.xlsx)** | Prévia limitada em memória e associação de colunas de data, valor e categoria |
| **PostgreSQL / MySQL** | Teste remoto autorizado com TLS, verificação da estrutura de tabelas e colunas |
| **Sincronização SQL** | Consulta **somente leitura** de valores agregados, contagem e categorias, em uma área separada |

Os arquivos CSV/Excel podem ter até **1,5 MB**; são exibidas **até 12 linhas de amostra** e o arquivo **não é persistido**. Totais calculados nessa tela representam somente a amostra, não a planilha inteira.

#### Habilitação opcional do piloto SQL

Para testar uma conexão real, o **administrador do projeto** precisa configurar duas variáveis protegidas em **Vercel → Settings → Environment Variables**:

| Variável | Finalidade |
| --- | --- |
| `INTEGRATION_ADMIN_TOKEN` | Segredo administrativo aleatório com pelo menos 24 caracteres |
| `INTEGRATION_ALLOWED_HOSTS` | Lista de **hostnames exatos** previamente autorizados, separados por vírgula |

Depois de salvar as variáveis para **Production**, é necessário fazer **Redeploy**. A conexão também exige um usuário SQL **somente leitura**, certificado TLS válido e acesso de rede autorizado. Endereços internos/privados são bloqueados pelo piloto público; **não exponha um banco corporativo interno apenas para usar esta demonstração**.

O botão **Sincronizar totais agora** executa uma consulta agregada da tabela mapeada. Há atualização opcional **a cada 5 minutos enquanto a aba estiver aberta**, e a interface descarta as credenciais temporárias após **10 minutos** ou ao sair da aba. Isso **não equivale a uma sincronização permanente no servidor**.

**Ainda não implementado:** cadastro de contas empresariais, autenticação por organização, armazenamento criptografado e persistente de conexões, sincronização em segundo plano, isolamento multiempresa e substituição automática dos gráficos demo por dados de cada cliente.

[**Ler configuração, limitações e segurança da integração →**](vercel-app/README.md#integrações-self-service-etapa-de-testes-sem-armazenar-credenciais)

### 📊 Power BI Studio

A versão web oferece:

- Exportação de **6 datasets CSV**: vendas, financeiro, RH, produtos, clientes e categorias.
- Kit **ZIP** com CSVs, medidas **DAX** e orientações de importação.
- Prévia tabular, exemplos de medidas e guia para uso no **Power BI Desktop**.
- Na aplicação Streamlit local, exportações CSV e possibilidade de conectar o Power BI diretamente ao PostgreSQL.

**Limite importante:** o repositório **ainda não possui um relatório `.pbix` pronto nem um painel publicado no Power BI Service**. O Power BI Studio entrega os dados e o ponto de partida para construir o relatório.

## 📱 Responsividade e compatibilidade

A interface web adapta cartões, gráficos, menus, tabelas, assistente IA e Integrações a diferentes formatos de tela.

- **iPhone / Safari:** áreas seguras (notch e barra inferior), unidades de viewport dinâmicas, campos com fonte adequada para reduzir zoom automático ao digitar e janelas ajustáveis ao teclado.
- **Android:** navegação por toque, barra inferior e gráficos com rolagem horizontal dentro do próprio painel.
- **iPad / tablets:** rearranjo de colunas e menus para telas intermediárias.
- **Notebook / desktop:** barra lateral, gráficos amplos, atalhos de teclado e múltiplas colunas.

Os testes automatizados do workflow web executam **11 larguras/alturas em Chromium e WebKit** (22 verificações de navegador). Os dois motores passaram na atualização responsiva. **Emulação não substitui testes físicos em todos os aparelhos e versões de sistema.**

## 🛠️ Tecnologias

| Camada | Ferramentas |
| --- | --- |
| **Backend web** | Python, FastAPI, Pydantic, Uvicorn |
| **Interface web** | HTML, CSS, JavaScript vanilla, SVG |
| **Assistente IA** | APIs OpenAI e Google Gemini (BYOK) |
| **Dados de demonstração** | Gerador Python de dados sintéticos |
| **Análise local** | PostgreSQL 16, SQL, Pandas, SQLAlchemy |
| **Aplicação local** | Streamlit, Plotly |
| **Integrações** | Psycopg, PyMySQL, CSV, OpenPyXL |
| **Relatórios** | Power BI, CSV e DAX |
| **Entrega e qualidade** | Vercel, Docker Compose, GitHub Actions, Pytest, Unittest e Playwright |

## 🏗️ Arquitetura

~~~text
                    ENTERPRISE ANALYTICS DASHBOARD
                               │
              ┌────────────────┴────────────────┐
              │                                 │
        WEB / VERCEL                    LOCAL / STREAMLIT
              │                                 │
      FastAPI + HTML/CSS/JS             Streamlit + Plotly
              │                                 │
       Dados sintéticos                  Pandas / SQLAlchemy
              │                                 │
     ┌────────┼──────────┐                      PostgreSQL 16
     │        │          │                     (Docker local)
  Gráficos  Assistente  Power BI Studio             │
    SVG       IA BYOK      CSV/DAX/ZIP              CSV
     │      OpenAI/Gemini    │                      │
     │                       └──────────────┬───────┘
  Integrações (piloto)                     Power BI Desktop
  CSV / XLSX / SQL
     │
  Consulta SQL autorizada,
  agregada e temporária
  (não altera os painéis demo)
~~~

## 🚀 Como executar

### Opção 1 — aplicação web (FastAPI)

**Pré-requisitos:** Python 3.10+ e Git.

~~~bash
git clone https://github.com/jmrzd/Enterprise-Analytics-Dashboard.git
cd Enterprise-Analytics-Dashboard/vercel-app

python -m venv .venv
source .venv/bin/activate
# No Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
~~~

Abra **http://127.0.0.1:8000**. O dashboard demo funciona **sem PostgreSQL, chave de IA ou variáveis de ambiente**.

Para hospedar na Vercel: conecte o repositório, configure **Root Directory = `vercel-app`**, **Framework Preset = FastAPI** e **Production Branch = `main`**. A aplicação web é publicada automaticamente quando o branch principal é atualizado.

### Opção 2 — aplicação local com Streamlit e PostgreSQL

**Pré-requisitos:** Python 3.10+, Docker + Compose e Git.

~~~bash
git clone https://github.com/jmrzd/Enterprise-Analytics-Dashboard.git
cd Enterprise-Analytics-Dashboard

docker compose up -d
python -m venv .venv
source .venv/bin/activate
# No Fish: source .venv/bin/activate.fish
# No Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
cp .env.example .env
# No PowerShell: Copy-Item .env.example .env
python -m streamlit run app.py
~~~

Abra **http://localhost:8501**.

O `docker-compose.yml` cria o PostgreSQL local e carrega os dados sintéticos na primeira inicialização do volume. Para usar **Streamlit sem Docker**, execute em modo demo:

~~~bash
DEMO_MODE=true python -m streamlit run app.py
~~~

**Não execute `docker compose down -v` para atualizar o projeto**, pois isso apaga o volume local. Consulte [docs/DEPLOY.md](docs/DEPLOY.md) e [powerbi/README.md](powerbi/README.md).

## 📁 Estrutura do repositório

~~~text
Enterprise-Analytics-Dashboard/
├── vercel-app/
│   ├── app.py                  # API e servidor FastAPI
│   ├── analytics.py            # Dados sintéticos e indicadores
│   ├── assistant_api.py        # Integração OpenAI / Gemini
│   ├── features.py             # Insights, cenários, Power BI
│   ├── integrations.py         # Testes e importação CSV/Excel
│   ├── sync_service.py         # Consultas agregadas, autorizadas
│   ├── templates/              # Dashboard, UX futurista e mobile
│   ├── scripts/                # Testes de viewport no navegador
│   ├── tests/                  # Testes da aplicação web
│   ├── README.md
│   └── SECURITY.md
├── app.py                      # Dashboard Streamlit
├── assets/                     # Estilos Streamlit
├── database/                   # Schema e sementes SQL
├── src/                        # Consultas, métricas, dados demo
├── scripts/                    # Exportações Power BI
├── powerbi/                    # Guia de integração Power BI
├── tests/                      # Testes da aplicação Streamlit
├── docs/                       # Arquitetura e publicação
├── docker-compose.yml
└── README.md
~~~

## 🔗 API da aplicação web

A documentação interativa fica disponível em **[/api/docs](https://enterprise-analytics-dashboard-ivory.vercel.app/api/docs)**.

| Método | Endpoint | Função |
| --- | --- | --- |
| GET | `/api/health` | Saúde da aplicação |
| GET | `/api/dashboard?period=90d` | KPIs e dados sintéticos |
| GET | `/api/insights?period=90d` | Insights e alertas |
| POST | `/api/scenario` | Cálculo de cenários |
| POST | `/api/chat` | IA com chave temporária informada pelo usuário |
| GET | `/api/powerbi/kit?period=90d` | Kit ZIP de Power BI |
| GET | `/api/powerbi/dax` | Medidas DAX |
| GET | `/api/powerbi/{dataset}?period=90d` | CSV por dataset |
| GET | `/api/integrations/status` | Disponibilidade das integrações |
| POST | `/api/integrations/file-preview` | Prévia temporária de CSV/Excel |
| POST | `/api/integrations/test` | Verificação SQL com autorização administrativa |
| POST | `/api/integrations/sync` | Agregados SQL de leitura, temporários e autorizados |

Os endpoints de integração SQL são **desativados por padrão** e não aceitam SQL arbitrário enviado pelo visitante. Veja o [guia de segurança](vercel-app/SECURITY.md).

## 🧪 Qualidade e testes

### Aplicação web

~~~bash
cd vercel-app
python -m unittest discover -s tests -v
node --check templates/app.js
node --check templates/upgrade.js
node --check templates/studio.js
node --check templates/integrations.js
node --check templates/responsive.js
~~~

O GitHub Actions também executa testes visuais e de navegação com **Playwright (Chromium e WebKit)** em celulares, tablets e desktops, além de testes de API e segurança.

### Aplicação Streamlit

~~~bash
python -m pytest -q
~~~

Os testes SQL da integração local utilizam um PostgreSQL de desenvolvimento. Nenhuma chave real de API é necessária para os testes automatizados.

## 🔐 Segurança e privacidade

- **Sem credenciais no repositório:** nunca suba `.env`, tokens, senhas empresariais nem arquivos com dados confidenciais.
- **IA BYOK:** chaves temporárias na memória da aba e encaminhamento por HTTPS. Uma chave restrita continua indispensável.
- **Conexões SQL:** autorização do administrador, allowlist de servidores, TLS verificado, conta somente leitura, consultas agregadas e sem persistência no piloto.
- **Aplicação web:** Content Security Policy com nonce por resposta, cabeçalhos de segurança, limites de tamanho de requisição e bloqueio de chamadas de origem cruzada.
- **Limitações atuais:** **sem login empresarial, controle de acesso por empresa, rate limiting distribuído, cofre persistente de credenciais ou auditoria corporativa completa**.

> [!WARNING]
> **Não conecte dados pessoais, financeiros confidenciais ou bases de clientes reais a esta demonstração pública.** Antes de utilizar em produção empresarial, implemente autenticação, isolamento multiempresa, autorização granular, gestão de segredos, auditoria e infraestrutura privada apropriada.

[**Detalhes técnicos e recomendações de segurança →**](vercel-app/SECURITY.md)

## 🗺️ Próximas evoluções

- [ ] Autenticação empresarial (SSO/OIDC, MFA e papéis de acesso).
- [ ] Isolamento por organização e armazenamento criptografado de conectores.
- [ ] Sincronização periódica persistente no servidor, com filas e auditoria.
- [ ] Conexão de datasets reais aos painéis e IA com autorização apropriada.
- [ ] Relatório Power BI `.pbix` versionado e integração Power BI Service.
- [ ] Revisão de segurança e testes em dispositivos físicos adicionais.

## 👨‍💻 Autor

**[jmrzd](https://github.com/jmrzd) — projeto de desenvolvimento e BI**

Projeto criado para demonstrar conhecimentos de **Python, SQL, bancos de dados, APIs, desenvolvimento web, BI, experiência do usuário e integração de IA**.

**[🌐 Ver o dashboard](https://enterprise-analytics-dashboard-ivory.vercel.app/)** · **[💻 Explorar o código](https://github.com/jmrzd/Enterprise-Analytics-Dashboard)**

---

<div align="center">
  <sub>◈ ENTERPRISE · ANALYTICS • Projeto de portfólio em evolução • Dados demonstrativos sintéticos</sub>
</div>
