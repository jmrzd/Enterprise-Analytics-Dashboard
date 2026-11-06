from src.db import query

def quadro_funcionarios():
    return query("""
        SELECT d.nome AS departamento,
               COUNT(f.id) FILTER (WHERE f.desligamento IS NULL) AS ativos,
               COALESCE(SUM(f.salario) FILTER (WHERE f.desligamento IS NULL),0) AS folha_mensal
        FROM departamentos d LEFT JOIN funcionarios f ON f.departamento_id=d.id
        GROUP BY d.id,d.nome ORDER BY d.nome
    """)

def movimentacoes():
    return query("""
        SELECT date_trunc('month',admissao)::date AS mes,
               'admissao' AS movimento, COUNT(*) AS quantidade
        FROM funcionarios GROUP BY 1
        UNION ALL
        SELECT date_trunc('month',desligamento)::date AS mes,
               'desligamento' AS movimento, COUNT(*) AS quantidade
        FROM funcionarios WHERE desligamento IS NOT NULL GROUP BY 1
        ORDER BY mes,movimento
    """)
