"""Analytical functions on Nestlé's reported figures (CHF millions)."""
import pandas as pd

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]


def group_trend(d) -> pd.DataFrame:
    f = d["financials"].copy().sort_values("Year")
    f["Sales_YoY_pct"] = f["Sales"].pct_change() * 100
    g = d["growth"].query("Level == 'Group'").set_index("Year")
    for c in ("Organic_Growth_pct", "RIG_pct", "Pricing_pct"):
        f[c] = f["Year"].map(g[c])
    f["FX_and_Portfolio_pp"] = f["Sales_YoY_pct"] - f["Organic_Growth_pct"]   # reported minus organic
    f["Net_Profit_YoY_pct"] = f["Net_Profit"].pct_change() * 100
    return f.reset_index(drop=True)


def product_summary(d) -> pd.DataFrame:
    a = d["product_annual"].pivot(index="Product_Category", columns="Year", values="Sales_CHF_m")
    a.columns = [f"Sales_{c}" for c in a.columns]
    a["Share_2025_pct"] = a["Sales_2025"] / a["Sales_2025"].sum() * 100
    a["Change_2023_25_pct"] = (a["Sales_2025"] / a["Sales_2023"] - 1) * 100
    a["Reported_YoY_2025_pct"] = (a["Sales_2025"] / a["Sales_2024"] - 1) * 100
    g = d["growth"].query("Level == 'Product'")
    for y in (2024, 2025):
        a[f"OG_{y}_pct"] = g[g["Year"] == y].set_index("Name")["Organic_Growth_pct"]
    a["RIG_2025_pct"] = g[g["Year"] == 2025].set_index("Name")["RIG_pct"]
    a["Price_Mix_2025_pct"] = a["OG_2025_pct"] - a["RIG_2025_pct"]
    return a.sort_values("Sales_2025", ascending=False).reset_index()


def segment_summary(d) -> pd.DataFrame:
    a = d["segment_annual"].pivot(index="Segment", columns="Year", values="Sales_CHF_m")
    a.columns = [f"Sales_{c}" for c in a.columns]
    a["Share_2025_pct"] = a["Sales_2025"] / a["Sales_2025"].sum() * 100
    a["Reported_YoY_2025_pct"] = (a["Sales_2025"] / a["Sales_2024"] - 1) * 100
    g = d["growth"].query("Level == 'Segment'")
    for y in (2024, 2025):
        gy = g[g["Year"] == y].set_index("Name")
        a[f"OG_{y}_pct"] = gy["Organic_Growth_pct"]
    g25 = g[g["Year"] == 2025].set_index("Name")
    a["RIG_2025_pct"], a["Pricing_2025_pct"] = g25["RIG_pct"], g25["Pricing_pct"]
    a["FX_and_Portfolio_2025_pp"] = a["Reported_YoY_2025_pct"] - a["OG_2025_pct"]
    return a.sort_values("Sales_2025", ascending=False).reset_index()


def quarterly_total(d) -> pd.DataFrame:
    q = d["product_quarterly"].groupby(["Year", "Quarter"], as_index=False)["Sales_CHF_m"].sum()
    q["Share_of_Year_pct"] = q["Sales_CHF_m"] / q.groupby("Year")["Sales_CHF_m"].transform("sum") * 100
    q["YoY_pct"] = q.groupby("Quarter")["Sales_CHF_m"].pct_change() * 100
    q["Quarter"] = pd.Categorical(q["Quarter"], QUARTERS, ordered=True)
    return q.sort_values(["Year", "Quarter"]).reset_index(drop=True)


def product_quarterly_share(d) -> pd.DataFrame:
    """Share of each product's annual sales falling in each quarter (shows seasonality by category)."""
    q = d["product_quarterly"].copy()
    q["Share_of_Year_pct"] = q["Sales_CHF_m"] / q.groupby(["Year", "Product_Category"])["Sales_CHF_m"].transform("sum") * 100
    return q.groupby(["Product_Category", "Quarter"], as_index=False)["Share_of_Year_pct"].mean()


def fy2026_sensitivity(d, og=(2.2, 2.85, 3.5), drag=(0.0, -2.5, -4.75)) -> pd.DataFrame:
    """Mechanical sensitivity (NOT a forecast): FY2026 reported sales for combinations of organic growth and
    currency/portfolio drag. Defaults: OG range and mean observed in 2024-25; drag = 0, half, and the 2024-25 average gap."""
    base = float(d["financials"].set_index("Year").loc[2025, "Sales"])
    grid = pd.DataFrame({f"Drag {x:+.2f} pp": [base * (1 + (o + x) / 100) for o in og] for x in drag},
                        index=[f"OG {o:.2f}%" for o in og])
    return grid.round(0)


MS = lambda v: f"CHF {v/1000:,.1f}B"   # noqa: E731


def generate_insights_text(d) -> list[str]:
    out = []
    t = group_trend(d).set_index("Year")
    out.append(f"**Reported sales fell in CHF while organic growth was positive.** Sales: {MS(t.loc[2023,'Sales'])} (2023) → "
               f"{MS(t.loc[2024,'Sales'])} ({t.loc[2024,'Sales_YoY_pct']:+.1f}%) → {MS(t.loc[2025,'Sales'])} ({t.loc[2025,'Sales_YoY_pct']:+.1f}%), "
               f"yet organic growth was {t.loc[2024,'Organic_Growth_pct']:+.1f}% and {t.loc[2025,'Organic_Growth_pct']:+.1f}%. "
               f"The gap ({t.loc[2024,'FX_and_Portfolio_pp']:+.1f} pp, {t.loc[2025,'FX_and_Portfolio_pp']:+.1f} pp) is currency translation and portfolio changes, which these sources do not split.")
    out.append(f"**Growth is price-led.** Pricing contributed {t.loc[2025,'Pricing_pct']:.1f} of the {t.loc[2025,'Organic_Growth_pct']:.1f} pp organic growth in 2025 "
               f"({t.loc[2024,'Pricing_pct']:.1f} of {t.loc[2024,'Organic_Growth_pct']:.1f} pp in 2024); real internal growth (volume/mix) was only "
               f"{t.loc[2025,'RIG_pct']:.1f}% in both years.")
    out.append(f"**Profitability weakened.** Underlying trading operating margin: {t.loc[2023,'UTOP_Margin_pct']:.1f}% → {t.loc[2024,'UTOP_Margin_pct']:.1f}% → "
               f"{t.loc[2025,'UTOP_Margin_pct']:.1f}%. Net profit {MS(t.loc[2023,'Net_Profit'])} → {MS(t.loc[2025,'Net_Profit'])} "
               f"({(t.loc[2025,'Net_Profit']/t.loc[2023,'Net_Profit']-1)*100:+.0f}% vs 2023); basic EPS CHF {t.loc[2023,'Basic_EPS']:.2f} → {t.loc[2025,'Basic_EPS']:.2f}.")

    p = product_summary(d)
    top = p.iloc[0]
    out.append(f"**Largest product category:** {top.Product_Category} ({MS(top.Sales_2025)}, {top.Share_2025_pct:.1f}% of 2025 sales); next: "
               f"{p.iloc[1].Product_Category} ({p.iloc[1].Share_2025_pct:.1f}%) and {p.iloc[2].Product_Category} ({p.iloc[2].Share_2025_pct:.1f}%).")
    fast = p.sort_values("OG_2025_pct", ascending=False).head(2)
    out.append("**Fastest organic growth in 2025:** " + " and ".join(f"{r.Product_Category} ({r.OG_2025_pct:+.1f}%)" for r in fast.itertuples()) + ".")
    slow = p.sort_values("Change_2023_25_pct").head(2)
    out.append("**Biggest CHF declines 2023→2025:** " + ", ".join(
        f"{r.Product_Category} ({r.Change_2023_25_pct:+.1f}%)" for r in slow.itertuples()) +
        f". That is far more than their organic growth ({slow.iloc[0].OG_2024_pct:+.1f}% / {slow.iloc[0].OG_2025_pct:+.1f}% and "
        f"{slow.iloc[1].OG_2024_pct:+.1f}% / {slow.iloc[1].OG_2025_pct:+.1f}% in 2024 / 2025) implies, so currency translation and portfolio changes explain much of it.")
    pc = p.set_index("Product_Category").loc["PetCare"]
    out.append(f"**PetCare is the volume-driven category:** 2025 RIG {pc.RIG_2025_pct:+.1f}% against organic growth of {pc.OG_2025_pct:+.1f}%, "
               f"i.e. price/mix was negative.")

    s = segment_summary(d)
    best_og = s.sort_values("OG_2025_pct", ascending=False).iloc[0]
    big = s.iloc[0]
    out.append(f"**Largest segment:** {big.Segment} ({MS(big.Sales_2025)}, {big.Share_2025_pct:.1f}% of 2025 sales). "
               f"**Fastest organic growth in 2025:** {best_og.Segment} ({best_og.OG_2025_pct:+.1f}%).")
    z = s.set_index("Segment")
    out.append(f"**Europe vs Americas:** Zone EUR organic growth {z.loc['Zone EUR','OG_2025_pct']:+.1f}% (pricing {z.loc['Zone EUR','Pricing_2025_pct']:+.1f}%) "
               f"vs Zone AMS {z.loc['Zone AMS','OG_2025_pct']:+.1f}%, but Zone AMS is {z.loc['Zone AMS','Share_2025_pct']:.0f}% of sales.")

    q = quarterly_total(d)
    qs = product_quarterly_share(d).pivot(index="Product_Category", columns="Quarter", values="Share_of_Year_pct")
    q25 = q[q["Year"] == 2025].set_index("Quarter")
    hi, lo = q25["Share_of_Year_pct"].idxmax(), q25["Share_of_Year_pct"].idxmin()
    out.append("**Seasonality (2025):** quarterly shares of annual sales are "
               + ", ".join(f"{k} {q25.loc[k,'Share_of_Year_pct']:.1f}%" for k in QUARTERS) +
               f". Group sales are evenly spread ({hi} highest, {lo} lowest), but categories differ: "
               f"Confectionery is {qs.loc['Confectionery','Q4']:.0f}% in Q4, Water {qs.loc['Water','Q2']:.0f}% in Q2.")
    return out
