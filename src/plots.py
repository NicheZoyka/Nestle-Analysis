"""Matplotlib figures for the README and the Streamlit app."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np

from . import insights

BLUE, ORANGE, GREY, DARK, GREEN = "#2a6f97", "#d9822b", "#b8c0c8", "#2b2f33", "#5b9a68"
YEAR_C = {2023: "#b8c0c8", 2024: "#7aa6c2", 2025: "#2a6f97"}
SHORT = {"Powdered and Liquid Beverages": "Powdered & liquid bev.", "Prepared dishes and cooking aids": "Prepared dishes & cooking aids",
         "Nestlé Waters & Premium Beverages": "Waters & Premium Bev."}

plt.rcParams.update({
    "figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#9aa3ab",
    "axes.labelcolor": DARK, "xtick.color": DARK, "ytick.color": DARK, "axes.grid": True, "grid.color": "#e6e9ec",
    "grid.linewidth": 0.8, "axes.axisbelow": True, "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left",
})
_s = lambda n: SHORT.get(n, n)                            # noqa: E731
_B = mt.FuncFormatter(lambda x, _: f"{x/1000:,.0f}B")     # CHF millions -> billions


def group_sales_fig(d):
    t = insights.group_trend(d)
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [1, 1.1]})
    a.bar(t["Year"].astype(str), t["Sales"], color=[YEAR_C[y] for y in t["Year"]], width=0.6)
    for x, v in zip(t["Year"].astype(str), t["Sales"]):
        a.text(x, v, f"{v/1000:,.1f}B", ha="center", va="bottom", fontsize=9)
    a.set_ylim(0, t["Sales"].max() * 1.12)
    a.yaxis.set_major_formatter(_B)
    a.set_title("Reported group sales, CHF")
    a.grid(axis="x", visible=False)
    g = t.dropna(subset=["Organic_Growth_pct"])
    x = np.arange(len(g))
    b.bar(x - 0.2, g["Sales_YoY_pct"], 0.38, color=ORANGE, label="Reported (CHF)")
    b.bar(x + 0.2, g["Organic_Growth_pct"], 0.38, color=BLUE, label="Organic")
    for xi, r, o in zip(x, g["Sales_YoY_pct"], g["Organic_Growth_pct"]):
        b.text(xi - 0.2, r, f"{r:+.1f}", ha="center", va="top" if r < 0 else "bottom", fontsize=9)
        b.text(xi + 0.2, o, f"{o:+.1f}", ha="center", va="bottom", fontsize=9)
    b.axhline(0, color=DARK, lw=0.8)
    b.set_xticks(x, g["Year"].astype(str))
    b.set_title("Growth, %: reported vs organic")
    b.legend(frameon=False, loc="upper left")
    b.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def profit_fig(d):
    t = insights.group_trend(d)
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8))
    a.bar(t["Year"].astype(str), t["Net_Profit"], color=[YEAR_C[y] for y in t["Year"]], width=0.6)
    for x, v in zip(t["Year"].astype(str), t["Net_Profit"]):
        a.text(x, v, f"{v/1000:,.1f}B", ha="center", va="bottom", fontsize=9)
    a.set_ylim(0, t["Net_Profit"].max() * 1.15)
    a.yaxis.set_major_formatter(_B)
    a.set_title("Net profit, CHF")
    a.grid(axis="x", visible=False)
    b.plot(t["Year"].astype(str), t["UTOP_Margin_pct"], marker="o", lw=2, color=BLUE, label="Underlying trading op. margin")
    b.plot(t["Year"].astype(str), t["TOP_Margin_pct"], marker="o", lw=2, color=ORANGE, label="Trading operating margin")
    for col, c in (("UTOP_Margin_pct", BLUE), ("TOP_Margin_pct", ORANGE)):
        for x, v in zip(t["Year"].astype(str), t[col]):
            b.text(x, v + 0.25, f"{v:.1f}%", ha="center", fontsize=9, color=DARK)
    b.set_ylim(12, 19)
    b.yaxis.set_major_formatter(mt.PercentFormatter(decimals=0))
    b.set_title("Margins")
    b.legend(frameon=False, loc="lower left", fontsize=9)
    fig.tight_layout()
    return fig


def product_sales_fig(d):
    p = insights.product_summary(d).iloc[::-1]
    y = np.arange(len(p))
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, yr in enumerate((2023, 2024, 2025)):
        ax.barh(y + (i - 1) * 0.27, p[f"Sales_{yr}"], 0.26, color=YEAR_C[yr], label=str(yr))
    ax.set_yticks(y, [_s(n) for n in p["Product_Category"]])
    ax.xaxis.set_major_formatter(_B)
    ax.set_title("Sales by product category, CHF")
    ax.legend(frameon=False, ncol=3, loc="lower right")
    ax.grid(axis="y", visible=False)
    return fig


def product_growth_fig(d):
    p = insights.product_summary(d).sort_values("OG_2025_pct")
    y = np.arange(len(p))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(y + 0.2, p["OG_2024_pct"], 0.38, color=GREY, label="Organic growth 2024")
    ax.barh(y - 0.2, p["OG_2025_pct"], 0.38, color=BLUE, label="Organic growth 2025")
    for yi, v in zip(y, p["OG_2025_pct"]):
        ax.text(v, yi - 0.2, f" {v:+.1f}", va="center", ha="left" if v >= 0 else "right", fontsize=9)
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_yticks(y, [_s(n) for n in p["Product_Category"]])
    ax.xaxis.set_major_formatter(mt.PercentFormatter(decimals=0))
    ax.set_title("Organic growth by product category")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    return fig


def segment_sales_fig(d):
    s = insights.segment_summary(d).iloc[::-1]
    y = np.arange(len(s))
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.barh(y + 0.2, s["Sales_2024"], 0.38, color=GREY, label="2024")
    ax.barh(y - 0.2, s["Sales_2025"], 0.38, color=BLUE, label="2025")
    for yi, v, sh in zip(y, s["Sales_2025"], s["Share_2025_pct"]):
        ax.text(v, yi - 0.2, f"  {sh:.1f}%", va="center", fontsize=9)
    ax.set_yticks(y, [_s(n) for n in s["Segment"]])
    ax.xaxis.set_major_formatter(_B)
    ax.set_xlim(0, s["Sales_2024"].max() * 1.15)
    ax.set_title("Sales by segment, CHF (label = share of 2025)")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="y", visible=False)
    return fig


def segment_growth_fig(d):
    s = insights.segment_summary(d).dropna(subset=["OG_2025_pct"]).sort_values("OG_2025_pct")
    y = np.arange(len(s))
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.barh(y, s["RIG_2025_pct"], 0.55, color=BLUE, label="Real internal growth (volume / mix)")
    ax.barh(y, s["Pricing_2025_pct"], 0.55, left=s["RIG_2025_pct"].clip(lower=0), color=ORANGE, label="Pricing")
    for yi, v, r, p in zip(y, s["OG_2025_pct"], s["RIG_2025_pct"], s["Pricing_2025_pct"]):
        ax.text(max(r, 0) + max(p, 0) + 0.1, yi, f"OG {v:+.1f}%", va="center", fontsize=9)
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_yticks(y, [_s(n) for n in s["Segment"]])
    ax.set_xlim(None, s["OG_2025_pct"].max() + 1.6)
    ax.xaxis.set_major_formatter(mt.PercentFormatter(decimals=0))
    ax.set_title("2025 organic growth by segment: volume vs pricing")
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    ax.grid(axis="y", visible=False)
    return fig


def quarterly_fig(d):
    q = insights.quarterly_total(d)
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(4)
    for i, yr in enumerate((2024, 2025)):
        v = q[q["Year"] == yr]["Sales_CHF_m"].to_numpy()
        ax.bar(x + (i - 0.5) * 0.38, v, 0.36, color=YEAR_C[yr], label=str(yr))
    ax.set_xticks(x, insights.QUARTERS)
    ax.set_ylim(18000, None)
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1000:,.0f}B"))
    ax.set_title("Quarterly sales, CHF (Q2–Q4 derived from cumulative reports; axis starts at 18B)")
    ax.title.set_fontsize(10)
    ax.legend(frameon=False)
    ax.grid(axis="x", visible=False)
    return fig


def seasonality_fig(d):
    s = insights.product_quarterly_share(d).pivot(index="Product_Category", columns="Quarter", values="Share_of_Year_pct")
    s = s.loc[s.std(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    im = ax.imshow(s.values, cmap="Blues", aspect="auto", vmin=20, vmax=31)
    ax.set_xticks(range(4), insights.QUARTERS)
    ax.set_yticks(range(len(s)), [_s(n) for n in s.index])
    ax.grid(False)
    for i in range(s.shape[0]):
        for j in range(4):
            v = s.values[i, j]
            ax.text(j, i, f"{v:.1f}%", ha="center", va="center", fontsize=9, color="white" if v > 27 else DARK)
    ax.set_title("Share of annual sales by quarter (avg 2024–25)")
    return fig


def sensitivity_fig(d):
    g = insights.fy2026_sensitivity(d)
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.imshow(g.values, cmap="Blues_r", aspect="auto")
    ax.set_xticks(range(g.shape[1]), g.columns)
    ax.set_yticks(range(g.shape[0]), g.index)
    ax.grid(False)
    for i in range(g.shape[0]):
        for j in range(g.shape[1]):
            ax.text(j, i, f"{g.values[i, j]/1000:,.1f}B", ha="center", va="center", fontsize=10, color=DARK)
    ax.set_title("FY2026 sales sensitivity, CHF (illustrative, not a forecast)")
    fig.tight_layout()
    return fig
