# Neon Observatory — design do dashboard

Direção visual baseada no HTML de referência **Painel Analítico Futurista** fornecido pelo autor:
- Tema roxo escuro com acentos ciano, rosa e dourado
- KPI cards com luz sutil e forte hierarquia visual
- Gráficos de área, rosca, radar e barras
- Sidebar com navegação e filtros
- Interatividade com Plotly / Streamlit

O HTML de referência trazia *candlestick e preços fictícios de mercado*. Neste projeto esses indicadores foram substituídos por métricas de verdade da operação empresarial; não simulamos cotações nem inventamos participação de canais sem dados correspondentes.

## Páginas
- **Visão geral**: receita, lucro bruto, caixa, headcount, tendências, categorias, radar e ranking.
- **Vendas**: KPIs de pedidos concluídos, status, produtos, categorias, clientes e CSV.
- **Financeiro**: caixa pago, categorias de despesas, saldo acumulado, pendências e CSV.
- **RH**: quadro atual e folha por departamento, histórico de admissões/desligamentos e exportação agregada.
- **Power BI**: exportação CSV e instruções de conexão direta ao PostgreSQL.

## Regras de dados
- Filtros relativos aos registros do dataset, não ao relógio do servidor.
- Filtros de Vendas e Financeiro por data efetiva (pedido ou pagamento).
- RH atual e pendências gerais são intencionalmente não filtrados por data.
- Cache expira em até cinco minutos e há botão para recarregar.
- Dados fictícios; aplicação sem login — não usar dados reais de pessoas.

## Próxima versão
Autenticação, isolamento de empresas, filtros consistentes de comparativos anuais, testes integrados com banco, DAX e arquivos Power BI reais.
