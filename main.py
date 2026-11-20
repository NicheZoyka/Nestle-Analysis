"""Run the analysis: data check -> insights -> figures -> Power BI tables.

    python -m src.build_dataset   # (re)build data/*.csv from the transcribed report figures
    python main.py
"""
import matplotlib.pyplot as plt

from src import build_dataset, config, insights, plots
from src.data_loader import check_reconciliation, load_all
from src.powerbi_export import export_powerbi


def main() -> None:
    if not (config.DATA_DIR / "financials.csv").exists():
        build_dataset.main()
    d = load_all()
    rec = check_reconciliation(d)
    assert all(v == 0 for t in rec.values() for v in t.values()), f"Reconciliation failed: {rec}"
    print("Reconciliation OK (all tables sum to published group sales)")

    config.FIG_DIR.mkdir(parents=True, exist_ok=True)
    figs = {
        "01_group_sales_growth": plots.group_sales_fig(d),
        "02_profitability": plots.profit_fig(d),
        "03_product_sales": plots.product_sales_fig(d),
        "04_product_growth": plots.product_growth_fig(d),
        "05_segment_sales": plots.segment_sales_fig(d),
        "06_segment_growth_volume_vs_price": plots.segment_growth_fig(d),
        "07_quarterly_sales": plots.quarterly_fig(d),
        "08_seasonality_by_category": plots.seasonality_fig(d),
        "09_fy2026_sensitivity": plots.sensitivity_fig(d),
    }
    for name, fig in figs.items():
        fig.savefig(config.FIG_DIR / f"{name}.png", bbox_inches="tight")
        plt.close(fig)

    for name, df in {"product_summary": insights.product_summary(d), "segment_summary": insights.segment_summary(d),
                     "group_trend": insights.group_trend(d), "quarterly_total": insights.quarterly_total(d)}.items():
        df.round(2).to_csv(config.REPORT_DIR / f"{name}.csv", index=False)

    lines = ["# Key insights (auto-generated from reported figures)\n"] + [f"- {t}" for t in insights.generate_insights_text(d)]
    (config.REPORT_DIR / "insights.md").write_text("\n".join(lines), encoding="utf-8")
    export_powerbi(d)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
