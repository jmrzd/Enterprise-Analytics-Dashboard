# Integração com Microsoft Power BI

O projeto entrega **dados analíticos agregados**, além de uma conexão direta possível com PostgreSQL. **Ainda não existe um arquivo .pbix publicado no repositório**.

## Opção A — importar CSVs (início mais simples)
1. Inicie o PostgreSQL e configure a variável `DATABASE_URL` em `.env`.
2. Execute `python -m scripts.export_powerbi` na raiz do projeto.
3. No Power BI Desktop, escolha **Obter dados → Texto/CSV** e selecione os CSVs em `outputs/`.
4. Configure o tipo **Data** para a coluna `mes` e **Número decimal** para valores financeiros.
5. Monte páginas de Vendas, Financeiro e RH; documente cada medida.

O app Streamlit também oferece uma aba **Power BI**, onde exporta indicadores filtrados (CSV UTF-8 com BOM).

## Opção B — conexão PostgreSQL
1. No Power BI Desktop, **Obter dados → PostgreSQL**.
2. Servidor local: `localhost:5432`. Banco: `enterprise_analytics`.
3. Use as credenciais de seu ambiente local. Não salve credenciais no GitHub.
4. Crie consultas ou views que considerem apenas pedidos concluídos para receita; use lançamentos com `data_pagamento IS NOT NULL` para caixa.

## Cuidados semânticos
- Receita de vendas é calculada em `itens_pedido` x `pedidos` concluídos.
- Lucro bruto = receita de vendas menos custo do item vendido; não é lucro líquido.
- Saldo de caixa = receitas pagas menos despesas pagas; não é resultado contábil.
- Folha salarial do RH não é debitada automaticamente do caixa neste MVP.
- O cadastro de RH contém dados fictícios, mas dados reais exigem acesso restrito.

## Compartilhamento
Relatórios privados no Power BI Service podem exigir licença, gateway para dados locais e controle de acesso. Não publique dados confidenciais.
