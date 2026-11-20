"""Load the tidy CSVs from data/ (build them with `python -m src.build_dataset`)."""
import pandas as pd

from . import config

TABLES = ["product_quarterly", "product_annual", "segment_quarterly", "segment_annual",
          "zone_legacy_annual", "growth", "financials", "sources"]


def load_all() -> dict[str, pd.DataFrame]:
    missing = [t for t in TABLES if not (config.DATA_DIR / f"{t}.csv").exists()]
    if missing:
        raise FileNotFoundError(f"Missing {missing}. Run `python -m src.build_dataset` first.")
    return {t: pd.read_csv(config.DATA_DIR / f"{t}.csv") for t in TABLES}


def check_reconciliation(d: dict[str, pd.DataFrame]) -> dict:
    """Products and segments must add up to published group sales for every year."""
    fin = d["financials"].set_index("Year")["Sales"]
    out = {}
    for name in ("product_annual", "segment_annual", "zone_legacy_annual"):
        tot = d[name].groupby("Year")["Sales_CHF_m"].sum()
        out[name] = {int(y): int(v - fin[y]) for y, v in tot.items()}   # differences should all be 0
    for name in ("product_quarterly", "segment_quarterly"):
        tot = d[name].groupby("Year")["Sales_CHF_m"].sum()
        out[name] = {int(y): int(v - fin[y]) for y, v in tot.items()}
    return out
