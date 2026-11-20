import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src import build_dataset, insights
from src.data_loader import check_reconciliation


@pytest.fixture(scope="module")
def d():
    return build_dataset.build()


def test_all_tables_reconcile_to_group_sales(d):
    rec = check_reconciliation(d)
    assert all(v == 0 for t in rec.values() for v in t.values())


def test_group_sales_match_published_totals(d):
    f = d["financials"].set_index("Year")["Sales"]
    assert f.to_dict() == {2023: 92998, 2024: 91354, 2025: 89490}


def test_quarters_sum_to_fy_and_are_positive(d):
    q = d["product_quarterly"]
    assert (q["Sales_CHF_m"] > 0).all()
    fy = q.groupby(["Year", "Product_Category"])["Sales_CHF_m"].sum().reset_index()
    a = d["product_annual"].query("Year >= 2024")
    m = fy.merge(a, on=["Year", "Product_Category"])
    assert (m["Sales_CHF_m_x"] == m["Sales_CHF_m_y"]).all()


def test_pricing_plus_rig_close_to_organic_growth(d):
    g = d["growth"].dropna(subset=["RIG_pct", "Pricing_pct"])
    assert ((g["RIG_pct"] + g["Pricing_pct"] - g["Organic_Growth_pct"]).abs() <= 0.15).all()


def test_insights(d):
    t = insights.group_trend(d).set_index("Year")
    assert t.loc[2025, "Sales_YoY_pct"] == pytest.approx((89490 / 91354 - 1) * 100)
    assert t.loc[2025, "FX_and_Portfolio_pp"] < 0
    p = insights.product_summary(d)
    assert p.iloc[0]["Product_Category"] == "Powdered and Liquid Beverages"
    assert p["Share_2025_pct"].sum() == pytest.approx(100)
    assert len(insights.generate_insights_text(d)) >= 10
    g = insights.fy2026_sensitivity(d)
    assert g.shape == (3, 3) and g.iloc[1, 0] > g.iloc[1, 2]
