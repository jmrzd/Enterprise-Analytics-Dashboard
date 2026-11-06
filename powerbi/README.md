# Power BI
O Power BI Desktop pode conectar diretamente ao PostgreSQL (host localhost, banco enterprise_analytics) ou importar os CSVs gerados por `python -m scripts.export_powerbi`.

Crie páginas: **Vendas**, **Financeiro** e **RH**. Indicadores sugeridos: receita de pedidos concluídos, lucro bruto estimado, entradas/saídas efetivamente pagas e funcionários ativos.

Os CSVs exportados são agregados e fictícios. Não publique dados pessoais de funcionários ou credenciais. Para disponibilizar relatórios privados, configure as permissões e licenças necessárias no Power BI Service. A atualização de banco local no serviço pode exigir gateway.
