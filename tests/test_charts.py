import pandas as pd

from src.charts import area, columns, donut, horizontal, radar


def test_figures_from_real_shape_data():
    month = pd.DataFrame({"mes": pd.to_datetime(["2026-01-01","2026-02-01"]),
                          "receita":[1200,1400], "saidas":[600,500]})
    assert len(area(month,"mes",[("Receita","receita","#a855f7")]).data) == 2
    assert len(columns(month,"mes",[("Saídas","saidas","#f472b6")]).data) == 1
    groups = pd.DataFrame({"categoria":["A","B"],"valor":[12,15]})
    assert len(donut(groups,"categoria","valor").data) == 1
    assert len(horizontal(groups,"categoria","valor").data) == 1
    assert len(radar(groups,"categoria","valor").data) == 1


def test_empty_frames_do_not_crash():
    empty = pd.DataFrame(columns=["categoria","valor"])
    assert len(donut(empty,"categoria","valor").data) == 0
    assert len(radar(empty,"categoria","valor").data) == 0
