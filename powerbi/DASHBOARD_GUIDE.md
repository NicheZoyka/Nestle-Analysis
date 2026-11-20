# Power BI dashboard: build guide

This folder contains everything needed to build `.pbix` file quickly. Save the result as `powerbi/Nestle_Reporting_Dashboard.pbix` and put screenshots in `powerbi/screenshots/`.

## 1. Load
1. **Get Data → Text/CSV**: load every file from `powerbi/data/` (`product_annual`, `product_quarterly`, `segment_annual`, `segment_quarterly`, `zone_legacy_annual`, `growth`, `financials`, `sources`, `dim_product`, `dim_segment`, `dim_quarter`).
2. Set `Year` to Whole number; sales, growth and profit columns to Decimal number.
3. **Model view**: create the relationships listed at the top of `measures.dax`.
4. **View → Themes → Browse for themes** → `nestle_theme.json`. Add the measures from `measures.dax`.

## 2. Pages
| Page | Visuals |
|---|---|
| **1. Group overview** | Cards: Group Sales, Reported YoY %, UTOP Margin %, Net Profit; column chart of sales by year; clustered column reported vs organic growth (use `financials` + `growth` table filtered to Level = Group) |
| **2. Products** | Bar chart of sales by category with `Product Share %`; clustered bars 2023 / 2024 / 2025; bar chart of organic growth by category (`growth`, Level = Product) |
| **3. Segments (2024–2025)** | Bar chart of segment sales and share; stacked bar of RIG + Pricing per segment (`growth`, Level = Segment, Year = 2025); note on the page that 2023 is not available in this structure |
| **4. Seasonality** | Clustered column of quarterly sales by year; matrix category × quarter with `Quarter Share of Year %` as a colour scale. Add a note: Q2–Q4 are derived from cumulative reports |
| **5. Legacy zones 2023–2024** | Bar chart from `zone_legacy_annual` (old zone structure, the only one with 2023) |
| **6. Data & sources** | Table from `sources` with the document links |

## 3. Design rules
- Blue `#2a6f97` for the main measure, orange `#d9822b` for the comparison (reported vs organic; volume vs pricing).
- Keep one Year slicer in the same place on every page and sync it.
- Titles should state the takeaway, for example *"Growth is price-led: pricing is 2.8 of 3.5 pp in 2025"*.
- Segment and product structures differ between documents: label which structure each page uses.
