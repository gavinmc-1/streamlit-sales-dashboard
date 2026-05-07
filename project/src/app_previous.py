from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Sales and Profit Dashboard",
    layout="wide"
)

st.title("Sales and Profit Performance Dashboard")

st.markdown(
    """
    This dashboard supports business decision-making by analysing sales, profit,
    product performance, customer segments, countries, and discounting patterns.
    """
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #4b5563;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }

    section[data-testid="stSidebar"] {
        background-color: #eef2f7;
    }

    h1, h2, h3 {
        color: #111827;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DATA_PATH = Path("project/data/Financial_Sample.xlsx")


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)

    # Remove accidental spaces in column names, e.g. " Sales"
    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(df["Date"])
    df["Profit Margin"] = df["Profit"] / df["Sales"]
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    return df


df = load_data(DATA_PATH)

# ----------------
# Sidebar filters
# ----------------

st.sidebar.header("Filters")

selected_years = st.sidebar.multiselect(
    "Year",
    sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)

selected_countries = st.sidebar.multiselect(
    "Country",
    sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

selected_products = st.sidebar.multiselect(
    "Product",
    sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

selected_segments = st.sidebar.multiselect(
    "Segment",
    sorted(df["Segment"].unique()),
    default=sorted(df["Segment"].unique())
)

filtered_df = df[
    (df["Year"].isin(selected_years))
    & (df["Country"].isin(selected_countries))
    & (df["Product"].isin(selected_products))
    & (df["Segment"].isin(selected_segments))
]

# ----------------
# KPI calculations
# ----------------

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_units = filtered_df["Units Sold"].sum()
total_discount = filtered_df["Discounts"].sum()
profit_margin = total_profit / total_sales if total_sales else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Total Sales", f"£{total_sales:,.0f}")
kpi2.metric("Total Profit", f"£{total_profit:,.0f}")
kpi3.metric("Units Sold", f"{total_units:,.0f}")
kpi4.metric("Total Discount", f"£{total_discount:,.0f}")
kpi5.metric("Profit Margin", f"{profit_margin:.2%}")

st.divider()

# ----------------
# Sales and profit over time
# ----------------

monthly_performance = (
    filtered_df
    .groupby("Month", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Month")
)

time_chart = px.line(
    monthly_performance,
    x="Month",
    y=["Sales", "Profit"],
    markers=True,
    title="Sales and Profit Over Time"
)

fig.update_layout(
    template="plotly_white",
    title_font_size=20,
    font=dict(size=13),
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(time_chart, use_container_width=True)


# ----------------
# Product and segment performance
# ----------------

left_col, right_col = st.columns(2)

product_performance = (
    filtered_df
    .groupby("Product", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Profit", ascending=False)
)

product_performance["Profit Margin"] = (
    product_performance["Profit"] / product_performance["Sales"]
)

product_margin_chart = px.bar(
    product_performance.sort_values("Profit Margin", ascending=False),
    x="Product",
    y="Profit Margin",
    title="Profit Margin by Product",
    text_auto=".2%"
)

st.plotly_chart(product_margin_chart, use_container_width=True)

product_chart = px.bar(
    product_performance,
    x="Product",
    y="Profit",
    title="Profit by Product",
    text_auto=".2s"
)

left_col.plotly_chart(product_chart, use_container_width=True)

segment_performance = (
    filtered_df
    .groupby("Segment", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Profit", ascending=False)
)

segment_chart = px.bar(
    segment_performance,
    x="Segment",
    y="Profit",
    title="Profit by Segment",
    text_auto=".2s"
)

right_col.plotly_chart(segment_chart, use_container_width=True)

# ----------------
# Country and discount analysis
# ----------------

left_col, right_col = st.columns(2)

country_performance = (
    filtered_df
    .groupby("Country", as_index=False)[["Sales", "Profit"]]
    .sum()
    .sort_values("Profit", ascending=False)
)

country_chart = px.bar(
    country_performance,
    x="Country",
    y="Profit",
    title="Profit by Country",
    text_auto=".2s"
)

left_col.plotly_chart(country_chart, use_container_width=True)

discount_chart = px.scatter(
    filtered_df,
    x="Discounts",
    y="Profit",
    size="Sales",
    color="Segment",
    hover_data=["Country", "Product", "Discount Band"],
    title="Discounts vs Profit"
)

right_col.plotly_chart(discount_chart, use_container_width=True)

st.subheader("Discount Band Analysis")

discount_band_summary = (
    filtered_df
    .groupby("Discount Band", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Discounts=("Discounts", "sum"),
        Units_Sold=("Units Sold", "sum")
    )
)

discount_band_summary["Profit Margin"] = (
    discount_band_summary["Profit"] / discount_band_summary["Sales"]
)

discount_band_chart = px.bar(
    discount_band_summary,
    x="Discount Band",
    y="Profit Margin",
    title="Profit Margin by Discount Band",
    text_auto=".2%"
)

st.plotly_chart(discount_band_chart, use_container_width=True)

st.dataframe(
    discount_band_summary.style.format(
        {
            "Sales": "£{:,.0f}",
            "Profit": "£{:,.0f}",
            "Discounts": "£{:,.0f}",
            "Units_Sold": "{:,.0f}",
            "Profit Margin": "{:.2%}",
        }
    ),
    use_container_width=True
)

# ----------------
# Summary table
# ----------------

st.subheader("Summary by Product and Segment")

summary_table = (
    filtered_df
    .groupby(["Product", "Segment"], as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Units_Sold=("Units Sold", "sum"),
        Discounts=("Discounts", "sum")
    )
)

summary_table["Profit Margin"] = summary_table["Profit"] / summary_table["Sales"]

st.dataframe(
    summary_table.style.format(
        {
            "Sales": "£{:,.0f}",
            "Profit": "£{:,.0f}",
            "Units_Sold": "{:,.0f}",
            "Discounts": "£{:,.0f}",
            "Profit Margin": "{:.2%}",
        }
    ),
    use_container_width=True
)

# ----------------
# Business insight prompts
# ----------------

st.subheader("Key Business Insights")

top_profit_product = product_performance.sort_values("Profit", ascending=False).iloc[0]
low_margin_high_sales = product_performance.sort_values(
    ["Sales", "Profit Margin"],
    ascending=[False, True]
).iloc[0]

top_segment = segment_performance.sort_values("Profit", ascending=False).iloc[0]
top_country = country_performance.sort_values("Profit", ascending=False).iloc[0]
weak_country = country_performance.sort_values("Profit", ascending=True).iloc[0]

best_discount_band = discount_band_summary.sort_values("Profit Margin", ascending=False).iloc[0]
worst_discount_band = discount_band_summary.sort_values("Profit Margin", ascending=True).iloc[0]

insight1, insight2 = st.columns(2)

with insight1:
    st.success(
        f"Most profitable product: **{top_profit_product['Product']}** "
        f"with profit of £{top_profit_product['Profit']:,.0f}."
    )

    st.warning(
        f"High-sales but lower-margin product to review: **{low_margin_high_sales['Product']}** "
        f"with sales of £{low_margin_high_sales['Sales']:,.0f} "
        f"and margin of {low_margin_high_sales['Profit Margin']:.2%}."
    )

    st.info(
        f"Most profitable segment: **{top_segment['Segment']}** "
        f"with profit of £{top_segment['Profit']:,.0f}."
    )

with insight2:
    st.success(
        f"Strongest country by profit: **{top_country['Country']}** "
        f"with profit of £{top_country['Profit']:,.0f}."
    )

    st.warning(
        f"Weakest country by profit: **{weak_country['Country']}** "
        f"with profit of £{weak_country['Profit']:,.0f}."
    )

    st.info(
        f"Best discount band by margin: **{best_discount_band['Discount Band']}** "
        f"with margin of {best_discount_band['Profit Margin']:.2%}. "
        f"Worst discount band: **{worst_discount_band['Discount Band']}** "
        f"with margin of {worst_discount_band['Profit Margin']:.2%}."
    )