"""Teste end-to-end: requer Docker PostgreSQL inicializado e DATABASE_URL."""
import pandas as pd

from src.analytics.insights import (
    clientes_diarios, lancamentos_pagos, lancamentos_pendentes,
    produtos_diarios, status_pedidos, vendas_diarias,
)
from src.analytics.rh import quadro_funcionarios
from src.metrics import cash_summary, filter_period, group_sum, monthly, pct


def test_sql_demo_dataset():
    sales=vendas_diarias()
    products=produtos_diarios()
    customers=clientes_diarios()
    status=status_pedidos()
    paid=lancamentos_pagos()
    people=quadro_funcionarios()
    assert len(sales) >= 100
    assert len(products) >= 100
    assert len(customers) >= 100
    assert set(status["status"]) >= {"concluido","cancelado","pendente"}
    assert len(paid) >= 100
    assert int(people["ativos"].sum()) >= 10
    assert not lancamentos_pendentes().empty


def test_metrics_and_filters_on_postgres():
    sales=vendas_diarias()
    start=pd.Timestamp(sales["data"].min()).date()
    end=pd.Timestamp(sales["data"].max()).date()
    filtered=filter_period(sales,start,end)
    monthly_sales=monthly(filtered,["receita","lucro_bruto","pedidos"])
    assert len(monthly_sales) >= 6
    assert float(monthly_sales["receita"].sum()) > 0
    assert pct(10,0)==0
    categories=group_sum(produtos_diarios(),"categoria",["receita"])
    assert len(categories) >= 3
    cash=cash_summary(lancamentos_pagos())
    assert cash["entradas"] >= 0 and cash["saidas"] >= 0
    assert abs(cash["saldo"]-(cash["entradas"]-cash["saidas"]))<0.001


def test_streamlit_pages_render():
    """Verifica todos os módulos, além dos testes sintáticos e de dados."""
    from streamlit.testing.v1 import AppTest

    app=AppTest.from_file("app.py",default_timeout=60).run()
    assert not app.exception, str(app.exception)
    for page in ["↗  Vendas","▤  Financeiro","♧  Recursos Humanos","▦  Power BI","◈  Visão geral"]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, f"{page}: {app.exception}"
