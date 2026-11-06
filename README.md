# ◈ Enterprise Analytics Dashboard

**Business Intelligence com PostgreSQL, Python, Pandas, Streamlit, Plotly e Power BI.**

Plataforma demonstrativa de indicadores de **Vendas, Financeiro e Recursos Humanos**. Interface futurista em roxo/ciano, inspirada em painel analítico fornecido pelo autor. O **modo local** consulta PostgreSQL via SQL/Pandas; para exibir a aplicação publicamente sem credenciais, há um **modo demo** separado, com dados sintéticos determinísticos.

> **Projeto de portfólio / MVP:** todas as informações de exemplo são fictícias. Sem autenticação e sem controle de acesso por departamento; **não hospede com dados empresariais ou pessoais reais** antes de implementar segurança.

## Destaques

| Módulo | O que mostra |
|---|---|
| ◈ Visão geral | Receita, lucro bruto, saldo do caixa, equipe, série temporal, composição, radar de headcount, volume semanal e clientes |
| ↗ Vendas | Receita, margem bruta, pedidos, produtos e clientes líderes, categorias, status de pedidos e CSV |
| ▤ Financeiro | Entradas, saídas, saldo, fluxo mensal, composição de despesas, saldo acumulado, pendências e CSV |
| ♧ Recursos Humanos | Headcount, folha mensal, distribuição, admissões/desligamentos e exportação **agregada** |
| ▦ Power BI | Exportação CSV, explicação de conexão com PostgreSQL e fluxo para criação de relatórios |

Os filtros permitem **30, 90, 180, 365 dias, histórico completo e intervalo personalizado**. As janelas relativas usam a **data mais recente disponível no banco**, para a demonstração continuar útil mesmo sem atualizações diárias.

## Publicar uma demonstração para recrutadores

A aplicação pode ser publicada no **Streamlit Community Cloud** sem PostgreSQL de produção. Nesse caso, o código gera dados **100% sintéticos, reproduzíveis e explicitamente rotulados**.

1. Entre em [Streamlit Community Cloud](https://share.streamlit.io/) com GitHub e escolha o repositório `jmrzd/Enterprise-Analytics-Dashboard`, branch `main`, arquivo `app.py`.
2. Em **Advanced settings → Secrets**, insira `DEMO_MODE = "true"`.
3. Clique em **Deploy**, abra a URL gerada e compartilhe com recrutadores.

**O link público ainda depende do deploy na sua conta Streamlit.** Veja o guia completo [docs/DEPLOY.md](docs/DEPLOY.md).

Para rodar a demonstração no seu computador, sem Docker:

```bash
DEMO_MODE=true python -m streamlit run app.py
```

> O modo demo não consulta PostgreSQL. Ele serve para apresentação visual. O código SQL do projeto continua funcionando no modo local.

## Executar no computador

**Pré-requisitos:** Git, Docker + Compose, Python 3.10+.

```bash
git clone https://github.com/jmrzd/Enterprise-Analytics-Dashboard.git
cd Enterprise-Analytics-Dashboard
docker compose up -d
python -m venv .venv
# CachyOS / Fish:
source .venv/bin/activate.fish
# Linux Bash/Zsh: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env
python -m streamlit run app.py
```

No Windows PowerShell, use `Copy-Item .env.example .env` no lugar de `cp`.

Abra **http://localhost:8501**.

### Já usa o projeto? Atualize sem apagar seus dados

```bash
git pull origin main
# Para inserir dados fictícios novos em seu banco existente (sem resetar o volume):
docker compose exec -T postgres psql -U dashboard -d enterprise_analytics < database/seed_extended.sql
python -m streamlit run app.py
```

**Importante:** `docker compose up -d` só executa scripts em `docker-entrypoint-initdb.d` quando o volume PostgreSQL está vazio. A carga estendida usa IDs fixos e `ON CONFLICT DO NOTHING`, podendo ser repetida sem duplicar dados. Não execute `docker compose down -v` se quiser preservar dados.

## Usar o Power BI

Na aplicação, abra a área **Power BI** e baixe os CSVs agregados, ou execute:

```bash
python -m scripts.export_powerbi
```

No Power BI Desktop, importe os arquivos em `outputs/` ou conecte ao PostgreSQL (localhost:5432, banco `enterprise_analytics`). Veja [powerbi/README.md](powerbi/README.md). O arquivo `.pbix` ainda precisa ser criado.

## Como funciona

```text
PostgreSQL 16 (Docker)
     │ consultas SQL
     ▼
src/analytics/insights.py ──────► src/metrics.py (Pandas, KPIs, filtros)
                                           │
                                           ▼
                                     Streamlit + Plotly
                                           │
                                           └──► CSV → Power BI Desktop
```

### Pastas
- `database/`: esquema e dados fictícios, incluindo `seed_extended.sql`
- `src/analytics/`: consultas SQL por domínio
- `src/metrics.py`: KPIs, filtro por período e agrupamentos testáveis
- `src/charts.py`: gráficos Plotly reutilizáveis
- `assets/dashboard.css`: tema futurista responsivo
- `app.py`: interface com cinco seções
- `scripts/` e `powerbi/`: exportação e instruções de BI
- `src/demo_data.py`: gerador determinístico de dados fictícios para a vitrine pública
- `docs/DEPLOY.md`: publicação do modo demo com segurança
- `tests/`: testes unitários, integração e modo demo + GitHub Actions

## Verificações

```bash
python -m compileall -q app.py src scripts tests
python -m pytest -q
```

O GitHub Actions executa testes em pushes e pull requests. É necessária uma instância PostgreSQL para testar o dashboard integrado; os testes unitários não dependem de banco.

## Interpretação e segurança

- Receita de vendas: apenas pedidos **concluídos**, sem cancelados ou pendentes.
- Lucro bruto estimado: receita menos custo de mercadorias vendidas; **não é lucro líquido**.
- Caixa: soma de lançamentos **efetivamente pagos**; não é conciliado automaticamente com vendas ou folha.
- RH e contas pendentes mostram o **estado atual/total**, rotulados separadamente dos filtros históricos.
- A senha de `docker-compose.yml` é apenas para **desenvolvimento local**. Nunca a reutilize em produção.
- Não comite `.env`, exportações contendo dados reais ou credenciais; ainda faltam login, controle de acesso, TLS e auditoria.

**Próximas entregas:** dashboard Power BI `.pbix`, autenticação empresarial e publicação da demonstração sintética no Streamlit Community Cloud. Os testes SQL/Streamlit e de demonstração são automatizados.
