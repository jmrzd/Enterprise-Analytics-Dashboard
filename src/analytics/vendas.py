from src.db import query

def resumo_vendas():
    return query("""
        SELECT date_trunc('month',p.data_pedido)::date AS mes,
               COUNT(DISTINCT p.id) AS pedidos,
               SUM(i.quantidade * i.preco_venda) AS receita,
               SUM(i.quantidade * (i.preco_venda - i.custo_unitario)) AS lucro_bruto
        FROM pedidos p JOIN itens_pedido i ON i.pedido_id=p.id
        WHERE p.status='concluido'
        GROUP BY 1 ORDER BY 1
    """)

def produtos_mais_vendidos():
    return query("""
        SELECT pr.nome AS produto, SUM(i.quantidade) AS unidades,
               SUM(i.quantidade*i.preco_venda) AS receita
        FROM itens_pedido i
        JOIN pedidos p ON p.id=i.pedido_id
        JOIN produtos pr ON pr.id=i.produto_id
        WHERE p.status='concluido'
        GROUP BY pr.id,pr.nome ORDER BY unidades DESC
    """)
