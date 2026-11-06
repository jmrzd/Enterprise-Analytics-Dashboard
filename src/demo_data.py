"""Dados 100% sintéticos para a demonstração pública sem servidor PostgreSQL.

A versão local continua usando consultas SQL reais. Os datasets gerados aqui
são determinísticos e internamente coerentes entre vendas, produtos e clientes.
Não representam empresas, funcionários ou transações reais.
"""
from collections import defaultdict
from datetime import date, timedelta
from random import Random

import pandas as pd


START = date(2025, 11, 1)
PRODUCTS = (
    ("Notebook Pro", "Tecnologia", 3990, 2630),
    ("Monitor 27", "Tecnologia", 1150, 715),
    ("Mouse sem fio", "Acessórios", 129, 54),
    ("Teclado mecânico", "Acessórios", 329, 148),
    ("Headset Office", "Acessórios", 279, 135),
    ("Mesa escritório", "Móveis", 940, 520),
    ("Cadeira ergonômica", "Móveis", 1250, 710),
    ("Webcam Full HD", "Tecnologia", 385, 192),
    ("Hub USB-C", "Acessórios", 189, 82),
    ("Impressora Wi-Fi", "Tecnologia", 1099, 680),
)
CITIES = ("Rio de Janeiro", "Niterói", "Duque de Caxias", "Nova Iguaçu")
DEPARTMENTS = (
    ("Comercial", 9, 4500),
    ("Financeiro", 5, 5300),
    ("Recursos Humanos", 4, 4900),
    ("Tecnologia", 7, 7100),
    ("Logística", 6, 3900),
)


def _summary(rows, groups, values):
    frame = pd.DataFrame(rows)
    return (
        frame.groupby(groups, as_index=False)[values]
        .sum()
        .sort_values(groups)
        .reset_index(drop=True)
    )


def load_demo_data():
    """Retorna os oito DataFrames usados pela aplicação, sem acesso à rede."""
    rng = Random(20261106)
    sales_rows, product_rows, client_rows, order_rows = [], [], [], []
    cash_rows = []

    for offset in range(365):
        day = START + timedelta(days=offset)
        # Pedidos: uma linha por pedido para contar corretamente os concluídos.
        for _ in range(rng.randint(1, 4)):
            status = rng.choices(
                ["concluido", "pendente", "cancelado"], weights=[82, 11, 7]
            )[0]
            order_rows.append({"data": day, "status": status, "total": 1})
            if status != "concluido":
                continue

            customer_id = rng.randint(1, 16)
            customer = f"Empresa Demonstração {customer_id:02d}"
            city = CITIES[(customer_id - 1) % len(CITIES)]
            total_revenue = 0
            total_profit = 0

            for name, category, price, cost in rng.sample(PRODUCTS, rng.randint(1, 3)):
                quantity = rng.randint(1, 4)
                revenue = quantity * price
                gross = quantity * (price - cost)
                total_revenue += revenue
                total_profit += gross
                product_rows.append({
                    "data": day, "produto": name, "categoria": category,
                    "unidades": quantity, "receita": revenue, "lucro_bruto": gross,
                })

            sales_rows.append({
                "data": day, "pedidos": 1, "receita": total_revenue,
                "lucro_bruto": total_profit,
            })
            client_rows.append({
                "data": day, "cliente": customer, "cidade": city,
                "receita": total_revenue,
            })

        # O financeiro é independente dos pedidos, como no banco do MVP.
        for _ in range(rng.randint(1, 3)):
            income = rng.random() < 0.46
            category = (
                rng.choice(["Serviços", "Aportes", "Outras receitas"])
                if income else rng.choice(
                    ["Infraestrutura", "Marketing", "Operacional", "Fornecedores"]
                )
            )
            cash_rows.append({
                "data": day,
                "tipo": "receita" if income else "despesa",
                "categoria": category,
                "descricao": f"Lançamento fictício — {category}",
                "valor": round(
                    rng.uniform(2800, 13500) if income else rng.uniform(350, 6800),
                    2,
                ),
            })

    # Pedidos/produtos/clientes derivam dos MESMOS eventos de venda.
    sales = _summary(sales_rows, ["data"], ["pedidos", "receita", "lucro_bruto"])
    products = _summary(
        product_rows, ["data", "produto", "categoria"],
        ["unidades", "receita", "lucro_bruto"],
    )
    clients = _summary(
        client_rows, ["data", "cliente", "cidade"], ["receita"]
    )
    orders = _summary(order_rows, ["data", "status"], ["total"])

    pending = pd.DataFrame([
        {
            "descricao": f"Compromisso fictício {i + 1:02d}",
            "categoria": ("Infraestrutura", "Fornecedores", "Operacional")[i % 3],
            "tipo": "despesa",
            "valor": 560 + i * 177,
            "data_vencimento": START + timedelta(days=350 + 7 * i),
        }
        for i in range(9)
    ])

    hr = pd.DataFrame([
        {"departamento": dept, "ativos": count, "folha_mensal": count * salary}
        for dept, count, salary in DEPARTMENTS
    ])
    movements = pd.DataFrame([
        {"mes": date(2025 + (10 + i) // 12, (10 + i) % 12 + 1, 1),
         "movimento": movement, "quantidade": quantity}
        for i in range(12)
        for movement, quantity in (
            ("admissao", 2 + i % 4),
            ("desligamento", i % 3),
        )
    ])

    return {
        "sales": sales,
        "products": products,
        "clients": clients,
        "orders": orders,
        "cash": pd.DataFrame(cash_rows),
        "pending": pending,
        "hr": hr,
        "movements": movements,
    }
