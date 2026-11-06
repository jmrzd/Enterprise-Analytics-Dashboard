# Dashboard visual v0.2

Interface escura inspirada em dashboards SaaS, com quatro seções: visão geral, vendas, financeiro e RH.

## Recursos
- Cards de indicadores, gráficos Plotly, menu lateral e filtro anual.
- Exportação CSV dos indicadores de vendas e financeiro.
- Dados reais de consultas SQL ao PostgreSQL, com seed fictício.
- Sem login: somente dados demonstrativos; não publique informações confidenciais.

## Atualização local
```bash
git pull origin main
python -m streamlit run app.py
```

O filtro anual aplica-se aos indicadores de vendas e financeiro. Ranking de produtos, contas pendentes e quadro atual de RH mostram o histórico/estado atual e estão identificados na interface.

## Próximos passos
Testes automatizados, integração com Power BI Desktop, autenticação e publicação segura.
