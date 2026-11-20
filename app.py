"""Interactive Streamlit dashboard.   Run:  streamlit run app.py"""
import streamlit as st

from src import insights, plots
from src.data_loader import load_all

st.set_page_config(page_title="Nestlé reported sales 2023–2025", layout="wide")


@st.cache_data
def get_data():
    return load_all()


d = get_data()
st.title("Nestlé reported sales and growth, 2023–2025")
st.caption("Source: Nestlé annual reviews and restatement documents (CHF millions). See data/sources.csv.")

t = insights.group_trend(d).set_index("Year")
year = st.sidebar.selectbox("Year", [2025, 2024, 2023])
c = st.columns(4)
c[0].metric("Group sales", f"CHF {t.loc[year,'Sales']/1000:,.1f}B",
            None if year == 2023 else f"{t.loc[year,'Sales_YoY_pct']:+.1f}% reported")
c[1].metric("Organic growth", "n/a" if year == 2023 else f"{t.loc[year,'Organic_Growth_pct']:+.1f}%")
c[2].metric("Underlying trading margin", f"{t.loc[year,'UTOP_Margin_pct']:.1f}%")
c[3].metric("Net profit", f"CHF {t.loc[year,'Net_Profit']/1000:,.1f}B")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Group", "Products", "Segments", "Seasonality", "Insights & scenario"])
with tab1:
    st.pyplot(plots.group_sales_fig(d))
    st.pyplot(plots.profit_fig(d))
with tab2:
    st.pyplot(plots.product_sales_fig(d))
    st.pyplot(plots.product_growth_fig(d))
    st.dataframe(insights.product_summary(d).round(1), hide_index=True)
with tab3:
    st.caption("Segments use Nestlé's 2025 structure and are available for 2024–2025 only.")
    st.pyplot(plots.segment_sales_fig(d))
    st.pyplot(plots.segment_growth_fig(d))
    st.dataframe(insights.segment_summary(d).round(1), hide_index=True)
with tab4:
    st.caption("Q2–Q4 are derived from cumulative H1 / 9M / FY reports.")
    st.pyplot(plots.quarterly_fig(d))
    st.pyplot(plots.seasonality_fig(d))
with tab5:
    for line in insights.generate_insights_text(d):
        st.markdown(f"- {line}")
    st.subheader("FY2026 sensitivity (illustrative, not a forecast)")
    st.pyplot(plots.sensitivity_fig(d))
    st.download_button("Download sources", d["sources"].to_csv(index=False), "sources.csv", "text/csv")
