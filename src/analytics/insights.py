"""Consultas analíticas detalhadas: somente leitura, valores de pedidos concluídos."""
from src.db import query


def vendas_diarias():
    return query("""
        SELECT p.data_pedido AS data,
               COUNT(DISTINCT p.id)::integer AS pedidos,
               SUM(i.quantidade * i.preco_venda) AS receita,
               SUM(i.quantidade * (i.preco_venda - i.custo_unitario)) AS lucro_bruto
        FROM pedidos p JOIN itens_pedido i ON i.pedido_id = p.id
        WHERE p.status = 'concluido'
        GROUP BY p.data_pedido ORDER BY p.data_pedido
    """)


def produtos_diarios():
    return query("""
        SELECT p.data_pedido AS data, pr.nome AS produto, pr.categoria,
               SUM(i.quantidade)::integer AS unidades,
               SUM(i.quantidade * i.preco_venda) AS receita,
               SUM(i.quantidade * (i.preco_venda - i.custo_unitario)) AS lucro_bruto
        FROM itens_pedido i
        JOIN pedidos p ON p.id = i.pedido_id
        JOIN produtos pr ON pr.id = i.produto_id
        WHERE p.status = 'concluido'
        GROUP BY p.data_pedido, pr.id, pr.nome, pr.categoria
        ORDER BY p.data_pedido
    """)


def clientes_diarios():
    return query("""
        SELECT p.data_pedido AS data, c.nome AS cliente, c.cidade,
               SUM(i.quantidade * i.preco_venda) AS receita
        FROM pedidos p
        JOIN clientes c ON c.id = p.cliente_id
        JOIN itens_pedido i ON i.pedido_id = p.id
        WHERE p.status = 'concluido'
        GROUP BY p.data_pedido, c.id, c.nome, c.cidade
        ORDER BY p.data_pedido
    """)


def status_pedidos():
    return query("""
        SELECT data_pedido AS data, status, COUNT(*)::integer AS total
        FROM pedidos GROUP BY data_pedido, status ORDER BY data_pedido
    """)


def lancamentos_pagos():
    return query("""
        SELECT data_pagamento AS data, tipo, categoria, descricao, valor
        FROM lancamentos_financeiros
        WHERE data_pagamento IS NOT NULL
        ORDER BY data_pagamento
    """)


def lancamentos_pendentes():
    return query("""
        SELECT descricao, categoria, tipo, valor, data_vencimento
        FROM lancamentos_financeiros
        WHERE data_pagamento IS NULL ORDER BY data_vencimento
    """)
