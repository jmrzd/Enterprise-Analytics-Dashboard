"""Testes do modo demonstração que dispensa Docker e credenciais."""
from pathlib import Path

import pandas as pd

from src.demo_data import load_demo_data
from src.metrics import cash_summary, filter_period, monthly


def test_synthetic_data_is_consistent_and_deterministic():
    a = load_demo_data()
    b = load_demo_data()
    assert set(a) == {
        "sales", "products", "clients", "orders",
        "cash", "pending", "hr", "movements",
    }
    for key in a:
        pd.testing.assert_frame_equal(a[key], b[key])

    assert len(a["sales"]) > 200
    assert set(a["orders"]["status"]) == {"concluido", "pendente", "cancelado"}
    assert round(a["sales"]["receita"].sum(), 2) == round(
        a["products"]["receita"].sum(), 2
    )
    assert round(a["sales"]["receita"].sum(), 2) == round(
        a["clients"]["receita"].sum(), 2
    )
    assert int(a["sales"]["pedidos"].sum()) == int(
        a["orders"].loc[a["orders"]["status"] == "concluido", "total"].sum()
    )
    assert a["products"]["categoria"].nunique() >= 3
    assert int(a["hr"]["ativos"].sum()) > 20
    assert not a["pending"].empty
    assert len(monthly(a["sales"], ["receita", "lucro_bruto"])) >= 10
    assert cash_summary(a["cash"])["entradas"] > 0
    first = a["sales"]["data"].min()
    last = a["sales"]["data"].max()
    assert not filter_period(a["sales"], first, last).empty


def test_all_streamlit_pages_in_demo_mode(monkeypatch):
    """Valida as cinco páginas sem conectar a um banco real."""
    monkeypatch.setenv("DEMO_MODE", "true")
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py",
        default_timeout=60,
    ).run()
    assert not app.exception, str(app.exception)
    for page in (
        "↗  Vendas", "▤  Financeiro",
        "♧  Recursos Humanos", "▦  Power BI", "◈  Visão geral",
    ):
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, f"{page}: {app.exception}"
