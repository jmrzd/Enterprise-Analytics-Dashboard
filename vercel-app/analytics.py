"""Deterministic synthetic BI dataset for the public Vercel portfolio demo.

No credentials, customer records, external services or production database access.
The original PostgreSQL + Pandas Streamlit project remains in the repository root.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from functools import lru_cache
from random import Random

PRODUCTS = (
    ("Notebook Pro 14", "Tecnologia", 4390, 2780),
    ("Monitor UltraWide", "Tecnologia", 1790, 1040),
    ("Cadeira Ergo", "Escritório", 1350, 720),
    ("Teclado Mecânico", "Acessórios", 390, 180),
    ("Mouse Wireless", "Acessórios", 179, 69),
    ("Headset Studio", "Acessórios", 490, 235),
    ("Mesa Flex", "Escritório", 990, 510),
    ("Webcam 4K", "Tecnologia", 890, 480),
    ("Hub USB-C", "Acessórios", 250, 110),
    ("Impressora Office", "Tecnologia", 1490, 890),
)
CLIENTS = (
    ("Grupo Horizonte", "Rio de Janeiro"), ("Nova Tech", "Niterói"),
    ("Mercado Solaris", "Duque de Caxias"), ("Alfa Comércio", "Rio de Janeiro"),
    ("Prime Logística", "Nova Iguaçu"), ("Casa Atlântica", "Niterói"),
    ("Vértice Digital", "Rio de Janeiro"), ("Oficina Central", "Petrópolis"),
    ("Loja Órbita", "Duque de Caxias"), ("Empresa Nexus", "Rio de Janeiro"),
    ("Orion Serviços", "São Gonçalo"), ("Aurora Comércio", "Niterói"),
)
DEPARTMENTS = (
    ("Comercial", 12, 4650), ("Tecnologia", 9, 7200),
    ("Financeiro", 6, 5400), ("Recursos Humanos", 5, 4900),
    ("Operações", 14, 3950),
)
MONTHS = ("jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez")
PERIOD_DAYS = {"30d": 30, "90d": 90, "180d": 180, "365d": 365, "all": 365}


def _month_key(day):
    return day.year, day.month


def _month_label(key):
    return f"{MONTHS[key[1]-1]}/{str(key[0])[-2:]}"


def _pct_change(values):
    if len(values) < 2 or not values[-2]:
        return 0.0
    return round((values[-1] / values[-2] - 1) * 100, 1)


@lru_cache(maxsize=3)
def _events(today: date):
    rng = Random(20261106)
    sales, orders, cash = [], [], []
    first = today - timedelta(days=364)
    for index in range(365):
        day = first + timedelta(days=index)
        for _ in range(rng.randint(2, 6)):
            status = rng.choices(("concluido", "pendente", "cancelado"), weights=(84, 10, 6))[0]
            orders.append({"date": day, "status": status})
            if status != "concluido":
                continue
            client, city = rng.choice(CLIENTS)
            revenue = cost = quantity = 0
            items = []
            for product, category, price, unit_cost in rng.sample(PRODUCTS, rng.randint(1, 3)):
                units = rng.randint(1, 3)
                amount = price * units
                revenue += amount
                cost += unit_cost * units
                quantity += units
                items.append({"name": product, "category": category, "units": units, "revenue": amount})
            sales.append({
                "date": day, "client": client, "city": city, "revenue": revenue,
                "profit": revenue - cost, "quantity": quantity, "items": items,
            })
        for _ in range(rng.randint(1, 4)):
            kind = "receita" if rng.random() < .51 else "despesa"
            category = rng.choice(
                ("Serviços", "Consultoria", "Outras receitas")
                if kind == "receita" else
                ("Fornecedores", "Infraestrutura", "Marketing", "Operacional")
            )
            cash.append({
                "date": day, "kind": kind, "category": category,
                "amount": round(rng.uniform(2300, 12500) if kind == "receita" else rng.uniform(600, 6900), 2),
            })
    return sales, orders, cash


def dashboard(period="90d", today=None):
    """Return internally consistent, synthetic dashboard indicators."""
    if period not in PERIOD_DAYS:
        raise ValueError("Período inválido")
    today = today or date.today()
    start = today - timedelta(days=PERIOD_DAYS[period] - 1)
    sales_all, orders_all, cash_all = _events(today)
    previous = None
    if PERIOD_DAYS[period] <= 180:
        n_days = PERIOD_DAYS[period]
        previous_start = start - timedelta(days=n_days)
        prev_sales = [s for s in sales_all if previous_start <= s["date"] < start]
        prev_cash = [c for c in cash_all if previous_start <= c["date"] < start]
        previous_revenue = sum(s["revenue"] for s in prev_sales)
        previous_profit = sum(s["profit"] for s in prev_sales)
        previous_income = sum(c["amount"] for c in prev_cash if c["kind"] == "receita")
        previous_expenses = sum(c["amount"] for c in prev_cash if c["kind"] == "despesa")
        previous = {
            "from": previous_start.isoformat(),
            "to": (start - timedelta(days=1)).isoformat(),
            "revenue": previous_revenue,
            "grossProfit": previous_profit,
            "orders": len(prev_sales),
            "cashBalance": round(previous_income - previous_expenses, 2),
        }
    sales = [s for s in sales_all if s["date"] >= start]
    orders = [o for o in orders_all if o["date"] >= start]
    cash = [c for c in cash_all if c["date"] >= start]

    revenue = sum(s["revenue"] for s in sales)
    profit = sum(s["profit"] for s in sales)
    income = sum(c["amount"] for c in cash if c["kind"] == "receita")
    expenses = sum(c["amount"] for c in cash if c["kind"] == "despesa")
    completed = len(sales)
    status = Counter(o["status"] for o in orders)
    by_product = defaultdict(lambda: {"units": 0, "revenue": 0})
    by_category = Counter()
    by_client = Counter()
    by_city = Counter()
    monthly = defaultdict(lambda: {"revenue": 0, "profit": 0, "orders": 0, "income": 0, "expense": 0})
    weekly = defaultdict(lambda: {"revenue": 0, "profit": 0, "orders": 0, "income": 0, "expense": 0})
    for sale in sales:
        month = monthly[_month_key(sale["date"])]
        month["revenue"] += sale["revenue"]
        month["profit"] += sale["profit"]
        month["orders"] += 1
        monday = sale["date"] - timedelta(days=sale["date"].weekday())
        week = weekly[monday]
        week["revenue"] += sale["revenue"]
        week["profit"] += sale["profit"]
        week["orders"] += 1
        by_client[sale["client"]] += sale["revenue"]
        by_city[sale["city"]] += sale["revenue"]
        for item in sale["items"]:
            entry = by_product[item["name"]]
            entry["units"] += item["units"]
            entry["revenue"] += item["revenue"]
            by_category[item["category"]] += item["revenue"]
    expense_categories = Counter()
    for entry in cash:
        month = monthly[_month_key(entry["date"])]
        month["income" if entry["kind"] == "receita" else "expense"] += entry["amount"]
        monday = entry["date"] - timedelta(days=entry["date"].weekday())
        week = weekly[monday]
        week["income" if entry["kind"] == "receita" else "expense"] += entry["amount"]
        if entry["kind"] == "despesa":
            expense_categories[entry["category"]] += entry["amount"]

    months = [
        {"label": _month_label(key), "revenue": round(v["revenue"], 2),
         "profit": round(v["profit"], 2), "orders": v["orders"],
         "income": round(v["income"], 2), "expense": round(v["expense"], 2)}
        for key, v in sorted(monthly.items())
    ]
    weeks = [
        {"label": key.strftime("%d/%m"), "revenue": round(v["revenue"], 2),
         "profit": round(v["profit"], 2), "orders": v["orders"],
         "income": round(v["income"], 2), "expense": round(v["expense"], 2)}
        for key, v in sorted(weekly.items())
    ]
    product_rows = sorted(
        [{"name": k, "units": v["units"], "revenue": v["revenue"]} for k, v in by_product.items()],
        key=lambda row: row["revenue"], reverse=True,
    )
    category_rows = [
        {"name": k, "value": v} for k, v in by_category.most_common()
    ]
    dept_rows = [
        {"name": name, "headcount": count, "payroll": count * salary}
        for name, count, salary in DEPARTMENTS
    ]
    # Synthetic monthly HR movements; not personal employment data.
    hr_movements = [
        {"label": item["label"], "hired": 2 + (i * 3) % 5, "left": i % 3}
        for i, item in enumerate(months)
    ]
    recent = sorted(sales, key=lambda s: s["date"], reverse=True)[:6]
    revenue_trend = _pct_change([m["revenue"] for m in months])
    return {
        "meta": {
            "mode": "demo", "source": "Dados fictícios gerados em Python",
            "period": period, "from": start.isoformat(), "to": today.isoformat(),
            "updatedAt": today.isoformat(),
            "disclaimer": "Indicadores sintéticos para portfólio. Vendas, caixa e folha são bases independentes.",
        },
        "kpis": {
            "revenue": revenue, "grossProfit": profit, "margin": round(100 * profit / revenue, 1) if revenue else 0,
            "orders": completed, "avgTicket": round(revenue / completed, 2) if completed else 0,
            "income": round(income, 2), "expenses": round(expenses, 2),
            "cashBalance": round(income - expenses, 2),
            "headcount": sum(d["headcount"] for d in dept_rows),
            "payroll": sum(d["payroll"] for d in dept_rows),
            "departments": len(dept_rows), "revenueTrend": revenue_trend,
        },
        "comparison": previous,
        "months": months,
        "weekly": weeks,
        "products": [{**product, "category": next((p[1] for p in PRODUCTS if p[0] == product["name"]), "Outros")} for product in product_rows],
        "categories": category_rows,
        "clients": [{"name": name, "value": amount} for name, amount in by_client.most_common(6)],
        "cities": [{"name": name, "value": amount} for name, amount in by_city.most_common(5)],
        "statuses": [
            {"name": "Concluídos", "value": status["concluido"]},
            {"name": "Pendentes", "value": status["pendente"]},
            {"name": "Cancelados", "value": status["cancelado"]},
        ],
        "expenseCategories": [
            {"name": name, "value": round(value, 2)} for name, value in expense_categories.most_common()
        ],
        "departments": dept_rows,
        "hrMovements": hr_movements,
        "pending": [
            {"name": f"Compromisso fictício {i+1:02d}", "category": ("Infraestrutura", "Fornecedores", "Operacional")[i % 3],
             "amount": 750 + 180 * i, "due": (today + timedelta(days=i * 4 + 2)).isoformat()}
            for i in range(7)
        ],
        "recent": [
            {"client": row["client"], "city": row["city"], "date": row["date"].isoformat(),
             "amount": row["revenue"], "status": "Concluído"}
            for row in recent
        ],
        "insights": [
            {"title": "Tendência de receita", "value": f"{revenue_trend:+.1f}%", "description": "Variação entre os dois últimos meses do período"},
            {"title": "Ticket médio", "value": round(revenue / completed, 2) if completed else 0,
             "description": "Receita por pedido concluído", "format": "currency"},
            {"title": "Margem bruta", "value": round(100 * profit / revenue, 1) if revenue else 0,
             "description": "Receita menos custo dos itens", "format": "percent"},
        ],
    }
