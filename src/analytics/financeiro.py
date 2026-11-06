from src.db import query

def fluxo_caixa():
    return query("""
        SELECT date_trunc('month',data_pagamento)::date AS mes,
               SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END) AS entradas,
               SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END) AS saidas,
               SUM(CASE WHEN tipo='receita' THEN valor ELSE -valor END) AS saldo
        FROM lancamentos_financeiros
        WHERE data_pagamento IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """)

def contas_pendentes():
    return query("""
        SELECT descricao,categoria,tipo,valor,data_vencimento
        FROM lancamentos_financeiros
        WHERE data_pagamento IS NULL ORDER BY data_vencimento
    """)
