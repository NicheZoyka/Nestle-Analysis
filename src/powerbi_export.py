"""Copy the tidy tables to powerbi/data and add small dimension tables."""
import pandas as pd

from . import config


def export_powerbi(d: dict[str, pd.DataFrame], out_dir=config.PBI_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("product_quarterly", "product_annual", "segment_quarterly", "segment_annual",
                 "zone_legacy_annual", "growth", "financials", "sources"):
        d[name].to_csv(out_dir / f"{name}.csv", index=False)
    pd.DataFrame({"Product_Category": sorted(d["product_annual"]["Product_Category"].unique())}).to_csv(
        out_dir / "dim_product.csv", index=False)
    pd.DataFrame({"Segment": sorted(d["segment_annual"]["Segment"].unique())}).to_csv(out_dir / "dim_segment.csv", index=False)
    pd.DataFrame({"Quarter": ["Q1", "Q2", "Q3", "Q4"], "QuarterNum": [1, 2, 3, 4]}).to_csv(out_dir / "dim_quarter.csv", index=False)
    print(f"Power BI tables -> {out_dir}")
