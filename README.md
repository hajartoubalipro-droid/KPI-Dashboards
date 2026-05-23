# KPI Dashboard — Sales Analytics

An interactive sales analytics dashboard built with **Streamlit + pandas**, featuring real-time filtering, KPI cards with year-over-year deltas, and multi-chart visualisation.

> 💡 Works standalone or as a front-end to the [ETL Pipeline Demo](../etl-pipeline-demo) — automatically reads from the SQLite database if available.

## Problem

After running ETL pipelines, analysts need an interactive way to explore KPIs without writing SQL queries or building static reports. This dashboard turns cleaned data into actionable insights in seconds.

## Solution & Architecture

```
output/sales.db  (from ETL pipeline)
        │
        ▼
  Streamlit app  ──  pandas aggregations
        │
        ├── KPI cards  (revenue, orders, AOV, customers)
        ├── YoY delta  (vs previous year)
        ├── Monthly revenue trend
        ├── Revenue by category
        ├── Revenue by region
        └── Top 10 monthly KPI table
```

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| Dashboard | Streamlit |
| Data processing | pandas, numpy |
| Storage | SQLite / CSV fallback |

## Key Features

- **5 KPI cards** with year-over-year delta indicators
- **Sidebar filters** — Year / Category / Region
- **4 interactive charts** — line, bar, regional breakdown
- **Auto-fallback** — generates synthetic data if no DB is present
- **Cached data loading** — `@st.cache_data` for performance

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: run ETL pipeline first for real data
# cd ../etl-pipeline-demo && python pipeline.py

# Launch dashboard
streamlit run app.py
# → Open http://localhost:8501
```

## Screenshots

The dashboard displays:
- Total Revenue, Orders, Average Order Value, Unique Customers, Average Quantity
- Monthly revenue trend line chart
- Revenue breakdown by category and region
- Top 10 months ranked by revenue

---
*Part of a 3-project data engineering portfolio. See also: [ETL Pipeline Demo](../etl-pipeline-demo) and [Predictive Maintenance API](../predictive-maintenance-api).*
