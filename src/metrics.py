"""Funções de métricas e filtros, independentes do banco e da interface."""
from datetime import date, timedelta

import pandas as pd


def brl(value: float) -> str:
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def compact_brl(value: float) -> str:
    n = float(value)
    if abs(n) >= 1_000_000:
        return f"R$ {n / 1_000_000:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs(n) >= 10_000:
        return f"R$ {n / 1_000:,.1f} mil".replace(",", "X").replace(".", ",").replace("X", ".")
    return brl(n)


def pct(numerator: float, denominator: float) -> float:
    return (float(numerator) / float(denominator) * 100.0) if denominator else 0.0


def period_bounds(last_date: date, preset: str, first_date: date) -> tuple[date, date]:
    """Janelas relativas ao registro mais recente, não ao relógio do servidor."""
    days = {"30 dias": 30, "90 dias": 90, "180 dias": 180, "365 dias": 365}
    if preset not in days:
        return first_date, last_date
    return max(first_date, last_date - timedelta(days=days[preset] - 1)), last_date


def filter_period(frame: pd.DataFrame, start: date, end: date, column="data") -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    dates = pd.to_datetime(frame[column], errors="coerce").dt.date
    return frame.loc[dates.between(start, end)].copy()


def monthly(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["mes", *columns])
    data = frame.copy()
    data["mes"] = pd.to_datetime(data["data"]).dt.to_period("M").dt.to_timestamp()
    for col in columns:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    return data.groupby("mes", as_index=False)[columns].sum().sort_values("mes")


def amount(frame: pd.DataFrame, column: str) -> float:
    return float(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum()) if column in frame else 0.0


def cash_summary(frame: pd.DataFrame) -> dict:
    entradas = amount(frame.loc[frame["tipo"] == "receita"], "valor") if not frame.empty else 0.0
    saidas = amount(frame.loc[frame["tipo"] == "despesa"], "valor") if not frame.empty else 0.0
    return {"entradas": entradas, "saidas": saidas, "saldo": entradas - saidas}


def group_sum(frame: pd.DataFrame, group: str, values: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=[group, *values])
    data = frame.copy()
    for col in values:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    return data.groupby(group, as_index=False)[values].sum().sort_values(values[0], ascending=False)
