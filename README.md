# FUTURE_DS_01 — Business Sales Performance Analytics

**Future Interns — Data Science & Analytics Internship, Task 1**

![Dashboard](charts/Task1_Dashboard.png)

## Objective
Analyze business sales data to identify revenue trends, top-selling products, high-value
categories, and regional performance — and turn that into a client-ready set of insights
and recommendations.

## Dataset
A simulated 2-year (2024–2025) multi-category retail sales dataset (4,119 cleaned transaction-line
records after cleaning), generated to reflect realistic patterns and realistic messiness found in
real order-management exports: mixed date formats, inconsistent text casing, duplicate rows, and
missing values. Categories: Electronics, Furniture, Office Supplies, Clothing across 4 regions
(North/South/East/West).

*(Per the task's dataset guidance, any dataset reflecting a real sales scenario is acceptable —
including self-created/simulated data. This can be swapped for a Kaggle dataset such as the
[Superstore Sales Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
with the same pipeline.)*

## Tools Used
- **Python (pandas, matplotlib)** — data cleaning, aggregation, and charting
- **Excel (openpyxl)** — final KPI dashboard workbook with live formulas

## Data Cleaning Steps
1. Removed 67 exact duplicate rows
2. Standardized text fields (trimmed whitespace, fixed inconsistent casing on Region/Category)
3. Parsed two mixed date formats (`YYYY-MM-DD` and `DD/MM/YYYY`) into a single date type
4. Filled 43 missing `Quantity` values with the dataset mode (1 item — the most common order size)
5. Filled 42 missing `Profit` values using each category's average profit margin applied to Sales
6. Derived `Profit Margin %`, `Order Month`, and `Order Year` for trend analysis

## Key Insights
- **Total Revenue: Rs 1.49 Cr | Total Profit: Rs 28.8L | Overall Margin: 19.4%**
- Furniture (Rs 68.7L) and Electronics (Rs 60.1L) drive ~87% of total revenue combined
- Electronics has the strongest margin (19.99%); Clothing lags at 15.79%
- Top 3 products by revenue: Office Chair, Wireless Mouse, Bluetooth Speaker
- North region leads on both revenue (Rs 44.5L) and margin (19.7%); South is lowest on revenue
  but has a comparable margin — a demand gap, not a profitability problem
- Clear seasonality: Oct–Dec festive season revenue runs well above baseline

Full insights and 4 actionable recommendations are in the **Insights & Recommendations** tab of
the Excel workbook.

## Files
```
FUTURE_DS_01/
├── data/
│   └── cleaned_sales_data.csv                        # cleaned, analysis-ready dataset
├── charts/
│   ├── Task1_Dashboard.png                            # one-page dashboard overview
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_top_products.png
│   ├── 03_category_share.png
│   └── 04_region_performance.png
├── 01_generate_raw_data.py
├── 02_clean_and_analyze.py
├── 03_build_workbook.py
├── Task1_Business_Sales_Performance_Analytics.xlsx    # final deliverable
└── README.md
```

## How to Reproduce
```bash
python3 01_generate_raw_data.py      # regenerates the raw (uncleaned) dataset
python3 02_clean_and_analyze.py      # cleans data, runs analysis, saves charts
python3 03_build_workbook.py         # builds the final Excel dashboard workbook
```
Note: the raw dataset isn't included in this repo (only the cleaned output is) — running
`01_generate_raw_data.py` first recreates it before the cleaning step.
