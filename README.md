# Enterprise Analytics Dashboard

Projeto demonstrativo de Business Intelligence com **PostgreSQL, SQL, Python, Pandas, Streamlit e Power BI**, integrando Vendas, Financeiro e Recursos Humanos.

> **Status:** MVP inicial. Dados fictícios, sem autenticação de usuários. **Não use com dados reais/confidenciais antes de implementar login, autorização por função e proteção de infraestrutura.**

## Módulos
- **Vendas:** pedidos concluídos, receita, lucro bruto estimado e produtos mais vendidos.
- **Financeiro:** entradas e saídas efetivamente pagas, saldo de caixa e contas pendentes.
- **RH:** funcionários ativos, folha salarial mensal e movimentações de pessoal.

**Importante:** os lançamentos financeiros são independentes dos pedidos de venda no MVP. O saldo de caixa não representa lucro líquido e a folha salarial não é debitada automaticamente do caixa.

## Executar localmente

Pré-requisitos: Python 3.10+, Docker com Compose e, opcionalmente, Power BI Desktop.

```bash
git clone https://github.com/jmrzd/Enterprise-Analytics-Dashboard.git
cd Enterprise-Analytics-Dashboard
docker compose up -d
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

No Windows, copie `.env.example` para `.env` manualmente ou use `Copy-Item .env.example .env`. Acesse **http://localhost:8501**.

O Docker inicializa `schema.sql` e `seed.sql` somente na criação do volume do banco. A senha de exemplo serve **apenas para desenvolvimento local**; altere-a antes de qualquer implantação.

## Power BI

Para exportar indicadores agregados como CSV:
```bash
python -m scripts.export_powerbi
```
Os CSVs são gerados em `outputs/` (ignorado pelo Git). Consulte [powerbi/README.md](powerbi/README.md) para conectar diretamente ao PostgreSQL ou importar os CSVs.

## Organização
```text
app.py                    Dashboard Streamlit
database/schema.sql       Estrutura do PostgreSQL
database/seed.sql         Dados fictícios
src/db.py                 Conexão SQLAlchemy/Pandas
src/analytics/            Consultas de Vendas, Financeiro e RH
scripts/export_powerbi.py Exportação de CSV
powerbi/README.md         Instruções de integração Power BI
```

## Segurança e próximos passos
- Adicionar autenticação e controle de acesso por perfil (especialmente RH).
- Migrar senhas para secret manager e usar TLS, backups e permissões mínimas.
- Criar conciliação entre vendas, contas a receber e lançamentos financeiros.
- Adicionar testes de integração, filtros por período e implantação em nuvem.

**Licença:** definir antes de reutilização comercial.
