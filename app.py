"""
KPI Dashboard — Sales Analytics
---------------------------------
Interactive dashboard built with Streamlit + pandas.
Visualises monthly KPIs, revenue trends, and regional performance.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Sales KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SAMPLE DATA ───────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load from DB if available, else generate synthetic data."""
    db_path = "output/sales.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT * FROM sales_clean", conn)
        conn.close()
        df["order_date"] = pd.to_datetime(df["order_date"])
        return df

    # Generate synthetic fallback
    np.random.seed(42)
    n = 3000
    categories = ["Electronics", "Clothing", "Food", "Books", "Sports"]
    regions = ["North", "South", "East", "West", "Central"]

    df = pd.DataFrame({
        "order_id": [f"ORD-{i:05d}" for i in range(n)],
        "order_date": pd.date_range("2023-01-01", periods=n, freq="3h"),
        "customer_id": [f"CUST-{np.random.randint(1, 300):04d}" for _ in range(n)],
        "category": np.random.choice(categories, n),
        "region": np.random.choice(regions, n),
        "quantity": np.random.randint(1, 15, n),
        "unit_price": np.round(np.random.uniform(10.0, 300.0, n), 2),
    })
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    df["year"] = df["order_date"].dt.year
    return df


df = load_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────
st.sidebar.title("🔍 Filters")

years = sorted(df["year"].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Year", years)

categories = ["All"] + sorted(df["category"].unique().tolist())
selected_cat = st.sidebar.selectbox("Category", categories)

regions = ["All"] + sorted(df["region"].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

# Apply filters
filtered = df[df["year"] == selected_year]
if selected_cat != "All":
    filtered = filtered[filtered["category"] == selected_cat]
if selected_region != "All":
    filtered = filtered[filtered["region"] == selected_region]

# ── HEADER ────────────────────────────────────────────────────
st.title("📊 Sales KPI Dashboard")
st.caption(f"Showing data for {selected_year} · {len(filtered):,} orders")

# ── KPI CARDS ─────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = filtered["revenue"].sum()
total_orders = len(filtered)
avg_order_value = filtered["revenue"].mean()
unique_customers = filtered["customer_id"].nunique()
avg_quantity = filtered["quantity"].mean()

# Compare to previous year
prev_year = df[df["year"] == selected_year - 1]
if selected_cat != "All":
    prev_year = prev_year[prev_year["category"] == selected_cat]
if selected_region != "All":
    prev_year = prev_year[prev_year["region"] == selected_region]

def delta(current, previous):
    if previous == 0:
        return None
    return f"{((current - previous) / previous * 100):+.1f}%"

col1.metric("💰 Total Revenue",
            f"€{total_revenue:,.0f}",
            delta(total_revenue, prev_year["revenue"].sum()))

col2.metric("📦 Total Orders",
            f"{total_orders:,}",
            delta(total_orders, len(prev_year)))

col3.metric("🎯 Avg Order Value",
            f"€{avg_order_value:.2f}",
            delta(avg_order_value, prev_year["revenue"].mean()))

col4.metric("👥 Unique Customers",
            f"{unique_customers:,}",
            delta(unique_customers, prev_year["customer_id"].nunique()))

col5.metric("📊 Avg Quantity",
            f"{avg_quantity:.1f}",
            delta(avg_quantity, prev_year["quantity"].mean()))

st.divider()

# ── CHARTS ────────────────────────────────────────────────────
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📈 Monthly Revenue")
    monthly = (
        filtered.groupby("month")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"month": "Month", "revenue": "Revenue (€)"})
    )
    st.line_chart(monthly.set_index("Month"))

with row1_col2:
    st.subheader("🗂️ Revenue by Category")
    by_cat = (
        filtered.groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"category": "Category", "revenue": "Revenue (€)"})
    )
    st.bar_chart(by_cat.set_index("Category"))

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("🌍 Revenue by Region")
    by_region = (
        filtered.groupby("region")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"region": "Region", "revenue": "Revenue (€)"})
    )
    st.bar_chart(by_region.set_index("Region"))

with row2_col2:
    st.subheader("📋 Top 10 Monthly KPIs")
    kpi_table = (
        filtered.groupby("month").agg(
            Revenue=("revenue", "sum"),
            Orders=("order_id", "count"),
            AOV=("revenue", "mean"),
            Customers=("customer_id", "nunique")
        ).round(2)
        .sort_values("Revenue", ascending=False)
        .head(10)
    )
    kpi_table["Revenue"] = kpi_table["Revenue"].map("€{:,.0f}".format)
    kpi_table["AOV"] = kpi_table["AOV"].map("€{:.2f}".format)
    st.dataframe(kpi_table, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────
st.divider()
st.caption("Built with Streamlit · Data Engineering portfolio project · Hajar Toubali")
