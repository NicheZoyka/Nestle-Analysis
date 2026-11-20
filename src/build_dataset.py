"""Builds the tidy CSVs in data/ from figures published by Nestlé (CHF millions).

Every number below is transcribed from the documents listed in SOURCES. Q1 is reported; Q2-Q4 are DERIVED by
differencing the cumulative H1 / 9M / FY figures (flagged in the `Basis` column). All sums are validated
against the published group totals before anything is written.

Structure notes (important when comparing years)
- Product categories (7) are identical for 2023, 2024 and 2025 as originally published.
- Segments in the "2025 structure" (Zone AMS, AOA, EUR, Nestlé Health Science, Nespresso, NW&PB, Other) are
  available for 2024 (restated) and 2025. 2023 is only available in the older zone structure
  (Zone NA, EUR, AOA, LATAM, GC, ...), so it is stored separately in zone_legacy_annual.csv.
- Nestlé later re-cut 2025 again (Health Science folded into the Zones; products regrouped into Coffee,
  Petcare, Nutrition, Food & Snacks, Waters & Premium Beverages). That re-cut has no 2023/2024 comparatives in
  the files used, so it is NOT used here.
"""
import pandas as pd

from . import config

SOURCES = [
    ("S1", "Nestlé Annual Review 2024", "https://www.nestle.com/sites/default/files/2025-02/annual-review-2024-en.pdf",
     "FY2023 and FY2024: group sales, profit, EPS, sales by zone and product category, 2024 organic growth by product"),
    ("S2", "2024 operating segments restated (Vevey, 24 March 2025)",
     "https://www.nestle.com/sites/default/files/2025-03/nestle-group-restatements-2024.pdf",
     "2024 Q1/H1/9M/FY sales by product and by segment (2025 structure); 2024 RIG, pricing, organic growth by segment"),
    ("S3", "2025 operating segments and information by products restated",
     "https://www.nestle.com/sites/default/files/2026-03/nestle-group-restatements-2025.pdf",
     "2025 Q1/H1/9M/FY sales as originally published, by segment and by product category"),
    ("S4", "Nestlé Annual Review 2025", "https://www.nestle.com/sites/default/files/2026-02/annual-review-2025-en.pdf",
     "FY2025 group results, segment and product growth (RIG, OG, pricing)"),
]

# ---- cumulative sales: name -> [Q1, H1, 9M, FY] ---------------------------------------------------------
PRODUCT_CUM = {
    2024: {  # S2
        "Powdered and Liquid Beverages": [5847, 12041, 17952, 24598],
        "Water": [701, 1621, 2474, 3180],
        "Milk products and Ice cream": [2605, 5189, 7648, 10397],
        "Nutrition and Health Science": [3680, 7637, 11313, 15137],
        "Prepared dishes and cooking aids": [2626, 5260, 7826, 10711],
        "Confectionery": [2043, 3845, 5920, 8449],
        "PetCare": [4590, 9452, 14015, 18882],
    },
    2025: {  # S3 (as originally published)
        "Powdered and Liquid Beverages": [6124, 12308, 18443, 25144],
        "Water": [722, 1611, 2431, 3128],
        "Milk products and Ice cream": [2542, 4830, 7175, 9698],
        "Nutrition and Health Science": [3657, 7237, 10718, 14304],
        "Prepared dishes and cooking aids": [2660, 5051, 7445, 10114],
        "Confectionery": [2192, 3962, 6074, 8696],
        "PetCare": [4704, 9229, 13583, 18406],
    },
}
PRODUCT_FY_2023 = {  # S1
    "Powdered and Liquid Beverages": 24786, "Water": 3320, "Milk products and Ice cream": 10981,
    "Nutrition and Health Science": 15278, "Prepared dishes and cooking aids": 11666,
    "Confectionery": 8107, "PetCare": 18860,
}
SEGMENT_CUM = {
    2024: {  # S2, restated to the 2025 segment structure
        "Zone AMS": [8639, 17821, 26567, 36135],
        "Zone AOA": [5344, 10591, 15641, 21177],
        "Zone EUR": [4248, 8342, 12456, 17082],
        "Nestlé Health Science": [1511, 3239, 4915, 6739],
        "Nespresso": [1503, 3096, 4586, 6378],
        "Nestlé Waters & Premium Beverages": [779, 1810, 2765, 3551],
        "Other businesses": [68, 146, 218, 292],
    },
    2025: {  # S3, as originally published
        "Zone AMS": [8639, 16954, 25294, 34482],
        "Zone AOA": [5539, 10442, 15263, 20553],
        "Zone EUR": [4353, 8467, 12785, 17581],
        "Nestlé Health Science": [1593, 3225, 4849, 6551],
        "Nespresso": [1595, 3172, 4706, 6481],
        "Nestlé Waters & Premium Beverages": [809, 1821, 2753, 3548],
        "Other businesses": [73, 147, 219, 294],
    },
}
GROUP_CUM = {2024: [22092, 45045, 67148, 91354], 2025: [22601, 44228, 65869, 89490]}
GROUP_FY = {2023: 92998, 2024: 91354, 2025: 89490}

ZONE_LEGACY = {  # S1 (2023 'Other businesses' derived = group - reported segments)
    2023: {"Zone North America": 25995, "Zone Europe": 19098, "Zone Asia, Oceania and Africa": 17519,
           "Zone Latin America": 12196, "Zone Greater China": 5037, "Nestlé Health Science": 6498,
           "Nespresso": 6372},
    2024: {"Zone North America": 25336, "Zone Europe": 18910, "Zone Asia, Oceania and Africa": 16793,
           "Zone Latin America": 11933, "Zone Greater China": 4973, "Nestlé Health Science": 6739,
           "Nespresso": 6378, "Other businesses": 292},
}

# ---- growth: (Year, Level, Name, OG %, RIG %, Pricing %, source) -----------------------------------------
GROWTH = [
    (2024, "Group", "Total Group", 2.2, 0.8, 1.5, "S1"),
    (2025, "Group", "Total Group", 3.5, 0.8, 2.8, "S4"),
    # segments 2024 (S2, restated structure; FY)
    (2024, "Segment", "Zone AMS", 0.4, -0.7, 1.2, "S2"),
    (2024, "Segment", "Zone AOA", 3.1, 1.5, 1.6, "S2"),
    (2024, "Segment", "Zone EUR", 3.3, 1.0, 2.3, "S2"),
    (2024, "Segment", "Nestlé Health Science", 6.2, 5.5, 0.7, "S2"),
    (2024, "Segment", "Nespresso", 2.2, 1.6, 0.6, "S2"),
    (2024, "Segment", "Nestlé Waters & Premium Beverages", 2.8, -0.2, 3.0, "S2"),
    (2024, "Segment", "Other businesses", 6.6, 5.3, 1.3, "S2"),
    # segments 2025 (S4)
    (2025, "Segment", "Zone AMS", 2.8, 0.1, 2.8, "S4"),
    (2025, "Segment", "Zone AOA", 3.2, 0.8, 2.5, "S4"),
    (2025, "Segment", "Zone EUR", 4.3, 0.4, 3.9, "S4"),
    (2025, "Segment", "Nestlé Health Science", 3.2, 3.5, -0.3, "S4"),
    (2025, "Segment", "Nespresso", 6.0, 1.6, 4.4, "S4"),
    (2025, "Segment", "Nestlé Waters & Premium Beverages", 5.3, 2.6, 2.7, "S4"),
    # product categories: 2024 organic growth only (S1); 2025 RIG and OG (S4)
    (2024, "Product", "Powdered and Liquid Beverages", 3.3, None, None, "S1"),
    (2024, "Product", "Water", 2.3, None, None, "S1"),
    (2024, "Product", "Milk products and Ice cream", -0.6, None, None, "S1"),
    (2024, "Product", "Nutrition and Health Science", 2.8, None, None, "S1"),
    (2024, "Product", "Prepared dishes and cooking aids", -1.7, None, None, "S1"),
    (2024, "Product", "Confectionery", 6.2, None, None, "S1"),
    (2024, "Product", "PetCare", 2.7, None, None, "S1"),
    (2025, "Product", "Powdered and Liquid Beverages", 7.3, 0.7, None, "S4"),
    (2025, "Product", "Water", 3.9, 1.0, None, "S4"),
    (2025, "Product", "Milk products and Ice cream", 1.3, 0.8, None, "S4"),
    (2025, "Product", "Nutrition and Health Science", 0.6, 0.1, None, "S4"),
    (2025, "Product", "Prepared dishes and cooking aids", -0.4, -0.2, None, "S4"),
    (2025, "Product", "Confectionery", 8.2, -0.7, None, "S4"),
    (2025, "Product", "PetCare", 2.2, 2.6, None, "S4"),
]

FINANCIALS = pd.DataFrame([  # S1 (2023, 2024), S4 (2025). CHF millions except margins % and EPS CHF.
    dict(Year=2023, Sales=92998, UTOP=16053, UTOP_Margin_pct=17.3, TOP=14520, TOP_Margin_pct=15.6,
         Net_Profit=11209, Basic_EPS=4.24, Underlying_EPS=4.80),
    dict(Year=2024, Sales=91354, UTOP=15704, UTOP_Margin_pct=17.2, TOP=14633, TOP_Margin_pct=16.0,
         Net_Profit=10884, Basic_EPS=4.19, Underlying_EPS=4.77),
    dict(Year=2025, Sales=89490, UTOP=14389, UTOP_Margin_pct=16.1, TOP=12675, TOP_Margin_pct=14.2,
         Net_Profit=9033, Basic_EPS=3.51, Underlying_EPS=4.42),
])


def _quarterly(cum: dict, entity_col: str) -> pd.DataFrame:
    rows = []
    for year, ents in cum.items():
        for name, (q1, h1, m9, fy) in ents.items():
            vals = [q1, h1 - q1, m9 - h1, fy - m9]
            for q, v in zip(["Q1", "Q2", "Q3", "Q4"], vals):
                rows.append({"Year": year, "Quarter": q, entity_col: name, "Sales_CHF_m": v,
                             "Basis": "Reported" if q == "Q1" else "Derived (cumulative difference)"})
    return pd.DataFrame(rows)


def _validate() -> None:
    for year in (2024, 2025):
        for label, cum in (("product", PRODUCT_CUM), ("segment", SEGMENT_CUM)):
            for i, p in enumerate(["Q1", "H1", "9M", "FY"]):
                total = sum(v[i] for v in cum[year].values())
                assert total == GROUP_CUM[year][i], f"{label} {year} {p}: {total} != {GROUP_CUM[year][i]}"
    assert sum(PRODUCT_FY_2023.values()) == GROUP_FY[2023]
    assert sum(ZONE_LEGACY[2024].values()) == GROUP_FY[2024]


def build() -> dict:
    _validate()
    prod_q = _quarterly(PRODUCT_CUM, "Product_Category")
    seg_q = _quarterly(SEGMENT_CUM, "Segment")
    assert (prod_q["Sales_CHF_m"] > 0).all() and (seg_q["Sales_CHF_m"] > 0).all()

    prod_a = pd.DataFrame(
        [{"Year": 2023, "Product_Category": k, "Sales_CHF_m": v} for k, v in PRODUCT_FY_2023.items()] +
        [{"Year": y, "Product_Category": k, "Sales_CHF_m": v[3]} for y, d in PRODUCT_CUM.items() for k, v in d.items()])
    seg_a = pd.DataFrame([{"Year": y, "Segment": k, "Sales_CHF_m": v[3], "Structure": "2025 structure"}
                          for y, d in SEGMENT_CUM.items() for k, v in d.items()])

    legacy = dict(ZONE_LEGACY[2023])
    legacy["Other businesses"] = GROUP_FY[2023] - sum(legacy.values())
    z = {2023: legacy, 2024: ZONE_LEGACY[2024]}
    zone_a = pd.DataFrame([{"Year": y, "Segment": k, "Sales_CHF_m": v,
                            "Basis": "Derived (group total minus reported segments)" if (y == 2023 and k == "Other businesses") else "Reported"}
                           for y, d in z.items() for k, v in d.items()])
    growth = pd.DataFrame(GROWTH, columns=["Year", "Level", "Name", "Organic_Growth_pct", "RIG_pct", "Pricing_pct", "Source"])
    sources = pd.DataFrame(SOURCES, columns=["Source", "Document", "URL", "Used_for"])
    return {"product_quarterly": prod_q, "product_annual": prod_a, "segment_quarterly": seg_q,
            "segment_annual": seg_a, "zone_legacy_annual": zone_a, "growth": growth,
            "financials": FINANCIALS, "sources": sources}


def main() -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in build().items():
        df.to_csv(config.DATA_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: {len(df)} rows")


if __name__ == "__main__":
    main()
