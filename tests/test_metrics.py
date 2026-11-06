from datetime import date

import pandas as pd

from src.metrics import amount, brl, cash_summary, compact_brl, filter_period, group_sum, monthly, pct, period_bounds


def test_currency_and_zero_division():
    assert brl(1234.5) == "R$ 1.234,50"
    assert compact_brl(20000) == "R$ 20,0 mil"
    assert pct(10, 0) == 0
    assert pct(50, 200) == 25


def test_rolling_date_inclusive():
    first, last = period_bounds(date(2026, 6, 30), "30 dias", date(2026, 1, 1))
    assert (first, last) == (date(2026, 6, 1), date(2026, 6, 30))


def test_filter_and_group_month():
    f = pd.DataFrame({"data": ["2026-01-01", "2026-01-28", "2026-02-01"], "receita": [2, 3, 9]})
    filtered = filter_period(f, date(2026, 1, 1), date(2026, 1, 31))
    assert amount(filtered, "receita") == 5
    grouped = monthly(filtered, ["receita"])
    assert len(grouped) == 1 and grouped.loc[0, "receita"] == 5


def test_cash_summary_is_not_sales_revenue():
    f = pd.DataFrame({"tipo": ["receita", "despesa", "despesa"], "valor": [150, 60, 20]})
    assert cash_summary(f) == {"entradas": 150, "saidas": 80, "saldo": 70}


def test_empty_group():
    result = group_sum(pd.DataFrame(columns=["categoria", "valor"]), "categoria", ["valor"])
    assert result.empty
