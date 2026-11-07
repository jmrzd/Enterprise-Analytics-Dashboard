"""Dashboard 2.0 capabilities shared by the API and Power BI starter kit.

All datasets are synthetic. Revenue/profit come from order items; cash entries
and payroll come from independent demo sources. Scenarios are mathematical
what-ifs, not forecasts or an accounting reconciliation.
"""
from __future__ import annotations

import csv
import io
import math
import zipfile
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from analytics import MONTHS, dashboard

Period = Literal["30d", "90d", "180d", "365d"]
Dataset = Literal["vendas", "financeiro", "rh", "produtos", "clientes", "categorias"]


class ScenarioInput(BaseModel):
    period: Period = "90d"
    price_pct: float = Field(default=0, ge=-25, le=40)
    volume_pct: float = Field(default=0, ge=-35, le=50)
    cost_pct: float = Field(default=0, ge=-25, le=40)
    hires: int = Field(default=0, ge=0, le=15)
    expense_reduction_pct: float = Field(default=0, ge=0, le=40)


def _money(value):
    return round(float(value), 2)


def calculate_scenario(settings: ScenarioInput, data=None):
    """Use explicit, transparent assumptions on synthetic aggregate KPIs."""
    d = data or dashboard(settings.period)
    k = d["kpis"]
    price_factor = 1 + settings.price_pct / 100
    volume_factor = 1 + settings.volume_pct / 100
    cost_factor = 1 + settings.cost_pct / 100
    new_revenue = k["revenue"] * price_factor * volume_factor
    original_cogs = k["revenue"] - k["grossProfit"]
    new_cogs = original_cogs * volume_factor * cost_factor
    new_gross_profit = new_revenue - new_cogs
    # Independent finance ledger: an expenses reduction is not a forecast of
    # customer payments. Show its effect only on the expense ledger.
    expense_savings = k["expenses"] * settings.expense_reduction_pct / 100
    current_avg_pay = k["payroll"] / k["headcount"] if k["headcount"] else 0
    extra_monthly_payroll = settings.hires * current_avg_pay
    new_payroll = k["payroll"] + extra_monthly_payroll
    return {
        "period": settings.period,
        "baseline": {
            "revenue": _money(k["revenue"]),
            "grossProfit": _money(k["grossProfit"]),
            "margin": k["margin"],
            "expenses": _money(k["expenses"]),
            "payrollMonthly": _money(k["payroll"]),
            "headcount": k["headcount"],
        },
        "scenario": {
            "revenue": _money(new_revenue),
            "grossProfit": _money(new_gross_profit),
            "margin": round(new_gross_profit / new_revenue * 100, 1) if new_revenue else 0,
            "expenses": _money(k["expenses"] - expense_savings),
            "expenseSavings": _money(expense_savings),
            "payrollMonthly": _money(new_payroll),
            "extraMonthlyPayroll": _money(extra_monthly_payroll),
            "headcount": k["headcount"] + settings.hires,
        },
        "delta": {
            "revenue": _money(new_revenue - k["revenue"]),
            "grossProfit": _money(new_gross_profit - k["grossProfit"]),
            "marginPoints": round(
                (100 * new_gross_profit / new_revenue if new_revenue else 0) - k["margin"], 1
            ),
        },
        "disclaimer": (
            "Simulação matemática hipotética sobre dados fictícios. Pressupõe "
            "quantidade/preço/custo constantes por grupo, com ajustes uniformes. "
            "A economia de despesas e a folha são independentes das vendas; "
            "não representa previsão, lucro líquido ou saldo futuro de caixa."
        ),
    }


def insights_for(data):
    """Deterministic explainable insight and alert cards, no LLM involved."""
    k = data["kpis"]
    total_revenue = k["revenue"]
    categories = data["categories"]
    products = data["products"]
    clients = data["clients"]
    pending = data["pending"]
    count_pending = sum(1 for item in pending if item.get("amount", 0) > 0)
    category = max(categories, key=lambda r: r["value"]) if categories else None
    top_product = max(products, key=lambda r: r["revenue"]) if products else None
    top_client = max(clients, key=lambda r: r["value"]) if clients else None
    top_share = 100 * category["value"] / total_revenue if category and total_revenue else 0
    customer_share = 100 * top_client["value"] / total_revenue if top_client and total_revenue else 0
    expense_ratio = k["expenses"] / k["income"] * 100 if k["income"] else 0

    cards = [
        {"id": "margin", "kind": "success" if k["margin"] >= 40 else "warning",
         "title": "Margem bruta", "value": f'{k["margin"]:.1f}%',
         "detail": "Lucro bruto dividido pelo faturamento do período",
         "formula": "lucro_bruto / receita × 100", "view": "sales"},
        {"id": "category", "kind": "warning" if top_share >= 65 else "info",
         "title": "Concentração por categoria", "value": f"{top_share:.1f}%",
         "detail": f'Categoria líder: {category["name"]}' if category else "Sem categoria no período",
         "formula": "receita_categoria / receita_total × 100", "view": "sales"},
        {"id": "client", "kind": "info", "title": "Cliente com maior receita",
         "value": f"{customer_share:.1f}%",
         "detail": top_client["name"] if top_client else "Sem cliente no período",
         "formula": "receita_cliente / receita_total × 100", "view": "sales"},
        {"id": "product", "kind": "info", "title": "Produto líder",
         "value": top_product["name"] if top_product else "Sem produtos",
         "detail": f'{top_product["units"]} unidades • R$ {top_product["revenue"]:,.2f}' if top_product else "Sem vendas",
         "formula": "ranking por faturamento", "view": "sales"},
    ]

    alerts = []
    if k["margin"] < 40:
        alerts.append({"level": "attention", "title": "Margem abaixo do parâmetro de 40%",
                       "detail": "A meta de 40% é ilustrativa e não representa um orçamento aprovado.",
                       "view": "sales"})
    if top_share >= 65 and category:
        alerts.append({"level": "attention", "title": "Receita concentrada em uma categoria",
                       "detail": f'{category["name"]} representa {top_share:.1f}% do faturamento.',
                       "view": "sales"})
    if expense_ratio >= 85:
        alerts.append({"level": "attention", "title": "Despesas elevadas frente às entradas",
                       "detail": f'Despesas pagas equivalem a {expense_ratio:.1f}% das entradas pagas.',
                       "view": "finance"})
    if count_pending:
        alerts.append({"level": "info", "title": f"{count_pending} contas de demonstração pendentes",
                       "detail": "Confira as datas fictícias na seção Financeiro. Não são cobranças reais.",
                       "view": "finance"})
    if not alerts:
        alerts.append({"level": "success", "title": "Nenhum alerta definido foi acionado",
                       "detail": "As regras monitoradas são ilustrativas e não substituem metas de negócio.",
                       "view": "overview"})
    return {
        "insights": cards,
        "alerts": alerts,
        "summary": {
            "categoryShare": round(top_share, 1),
            "clientShare": round(customer_share, 1),
            "expensesToIncome": round(expense_ratio, 1),
            "pendingCount": count_pending,
        },
        "note": "Insights por regras transparentes sobre dados sintéticos, não gerados por IA.",
    }


def get_insights(period: Period = "90d"):
    return insights_for(dashboard(period))


def _csv_value(value):
    """Neutralize spreadsheet formula injection even for future input datasets."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _csv_bytes(header, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow([_csv_value(v) for v in row])
    return ("\ufeff" + output.getvalue()).encode("utf-8")


def _month_iso(label: str):
    abbrev, year = label.split("/")
    month = MONTHS.index(abbrev) + 1
    return f"20{year}-{month:02d}-01"


def export_data(dataset: Dataset, data):
    """Export explicit aggregate CSVs, not invented transaction-level records."""
    if dataset == "vendas":
        header = ["mes_inicio", "mes", "receita", "lucro_bruto", "pedidos_concluidos"]
        rows = [[_month_iso(m["label"]), m["label"], m["revenue"], m["profit"], m["orders"]]
                for m in data["months"]]
    elif dataset == "financeiro":
        header = ["mes_inicio", "mes", "entradas", "saidas", "saldo"]
        rows = [[_month_iso(m["label"]), m["label"], m["income"], m["expense"],
                 _money(m["income"] - m["expense"])] for m in data["months"]]
    elif dataset == "rh":
        header = ["departamento", "colaboradores_ativos", "folha_mensal"]
        rows = [[x["name"], x["headcount"], x["payroll"]] for x in data["departments"]]
    elif dataset == "produtos":
        header = ["produto", "unidades", "receita"]
        rows = [[x["name"], x["units"], x["revenue"]] for x in data["products"]]
    elif dataset == "clientes":
        header = ["cliente", "receita"]
        rows = [[x["name"], x["value"]] for x in data["clients"]]
    elif dataset == "categorias":
        header = ["categoria", "receita"]
        rows = [[x["name"], x["value"]] for x in data["categories"]]
    else:
        raise ValueError("Dataset não suportado")
    return _csv_bytes(header, rows)


DAX_EXAMPLES = """-- Importe os arquivos CSV e renomeie as tabelas no Power BI:
-- vendas.csv -> FatoVendas; financeiro.csv -> FatoFinanceiro
-- rh.csv -> DimDepartamento; produtos.csv -> DimProduto
-- Estas medidas são exemplos DAX; o arquivo .pbix ainda precisa ser criado.

Receita Total = SUM(FatoVendas[receita])
Lucro Bruto = SUM(FatoVendas[lucro_bruto])
Pedidos Concluidos = SUM(FatoVendas[pedidos_concluidos])
Margem Bruta % = DIVIDE([Lucro Bruto], [Receita Total], 0)
Ticket Medio = DIVIDE([Receita Total], [Pedidos Concluidos], 0)

Entradas = SUM(FatoFinanceiro[entradas])
Saidas = SUM(FatoFinanceiro[saidas])
Saldo Caixa = [Entradas] - [Saidas]

Colaboradores = SUM(DimDepartamento[colaboradores_ativos])
Folha Mensal = SUM(DimDepartamento[folha_mensal])
"""


KIT_README = """Enterprise Analytics — Power BI Starter Kit
=============================================

Todos os dados são sintéticos, gerados para demonstração de portfólio.

1. No Power BI Desktop, clique em Obter Dados > Texto/CSV.
2. Selecione cada CSV. Delimitador: ponto e vírgula; codificação: UTF-8.
3. Renomeie tabelas: vendas -> FatoVendas, financeiro -> FatoFinanceiro,
   rh -> DimDepartamento, produtos -> DimProduto.
4. Tipifique mes_inicio como Data, valores monetários como Número decimal
   e quantidades como Número inteiro.
5. Crie medidas DAX usando exemplos em medidas.dax.
6. Use gráficos de linha, barras, cartões e tabelas com filtros.
7. Uma tabela de calendário pode relacionar FatoVendas e FatoFinanceiro
   por mes_inicio. Não relacione RH diretamente a vendas.

IMPORTANTE: os CSVs são agregados. Não há transações individuais nem
relatório .pbix pronto. Financeiro é um livro-razão sintético independente
das vendas; não some as duas fontes como se fossem o mesmo negócio.

Gerado automaticamente pelo Enterprise Analytics Dashboard.
"""


def create_powerbi_kit(data):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for dataset in ("vendas", "financeiro", "rh", "produtos", "clientes", "categorias"):
            archive.writestr(f"{dataset}.csv", export_data(dataset, data))
        archive.writestr("medidas.dax", DAX_EXAMPLES)
        archive.writestr("LEIA-ME.txt", KIT_README)
    return buffer.getvalue()
