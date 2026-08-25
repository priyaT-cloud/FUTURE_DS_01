"""
Task 1 - Business Sales Performance Analytics
Cleaning + analysis pipeline.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

pd.set_option("display.width", 140)

RAW = "/home/claude/FUTURE_DS_01/data/raw_sales_data.csv"
df = pd.read_csv(RAW)

log = []
def note(msg):
    log.append(msg)
    print(msg)

note(f"Raw rows loaded: {len(df)}")

# --- 1. Remove exact duplicate rows ---
before = len(df)
df = df.drop_duplicates()
note(f"Removed {before - len(df)} exact duplicate rows")

# --- 2. Standardize text columns (strip whitespace, fix casing) ---
for col in ["Region", "Category", "Product Name", "Segment", "Ship Mode", "Customer ID", "Order ID"]:
    df[col] = df[col].astype(str).str.strip()
df["Category"] = df["Category"].str.title()

# --- 3. Parse mixed date formats ---
def parse_date(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["Order Date"] = df["Order Date"].apply(parse_date)
bad_dates = df["Order Date"].isna().sum()
note(f"Unparseable dates: {bad_dates}")

# --- 4. Handle missing values ---
missing_qty = df["Quantity"].isna().sum()
df["Quantity"] = df["Quantity"].fillna(1)  # most common single-item order
missing_profit = df["Profit"].isna().sum()
# impute missing profit using the category's average profit margin on Sales
df["_margin_tmp"] = df["Profit"] / df["Sales"]
cat_margin = df.groupby("Category")["_margin_tmp"].transform("mean")
df["Profit"] = df["Profit"].fillna(df["Sales"] * cat_margin)
df.drop(columns="_margin_tmp", inplace=True)
note(f"Filled {int(missing_qty)} missing Quantity values (default=1), "
     f"{int(missing_profit)} missing Profit values (category-average margin)")

# --- 5. Type fixes & derived columns ---
df["Quantity"] = df["Quantity"].astype(int)
df["Sales"] = df["Sales"].round(2)
df["Profit"] = df["Profit"].round(2)
df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)
df["Order Month"] = df["Order Date"].dt.to_period("M").astype(str)
df["Order Year"] = df["Order Date"].dt.year

# --- 6. Drop rows with no usable date (can't be trend-analyzed) ---
before = len(df)
df = df.dropna(subset=["Order Date"])
note(f"Dropped {before - len(df)} rows with unparseable dates")

note(f"Final cleaned rows: {len(df)}")

df.to_csv("/home/claude/FUTURE_DS_01/data/cleaned_sales_data.csv", index=False)

# ============ ANALYSIS ============

total_revenue = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["Order ID"].nunique()
avg_order_value = df.groupby("Order ID")["Sales"].sum().mean()
overall_margin = total_profit / total_revenue * 100

note("\n--- KPIs ---")
note(f"Total Revenue: {total_revenue:,.2f}")
note(f"Total Profit: {total_profit:,.2f}")
note(f"Overall Profit Margin: {overall_margin:.2f}%")
note(f"Total Orders: {total_orders:,}")
note(f"Average Order Value: {avg_order_value:,.2f}")

# Monthly revenue trend
monthly = df.groupby("Order Month").agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
monthly.to_csv("/home/claude/FUTURE_DS_01/data/monthly_trend.csv", index=False)

# Top products by revenue
top_products = df.groupby("Product Name").agg(
    Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Units=("Quantity", "sum")
).sort_values("Revenue", ascending=False).reset_index()
top_products.to_csv("/home/claude/FUTURE_DS_01/data/top_products.csv", index=False)

# Category performance
cat_perf = df.groupby("Category").agg(
    Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
).assign(**{"Margin %": lambda x: (x["Profit"] / x["Revenue"] * 100).round(2)}).sort_values("Revenue", ascending=False)
cat_perf.to_csv("/home/claude/FUTURE_DS_01/data/category_performance.csv")

# Region performance
region_perf = df.groupby("Region").agg(
    Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")
).assign(**{"Margin %": lambda x: (x["Profit"] / x["Revenue"] * 100).round(2)}).sort_values("Revenue", ascending=False)
region_perf.to_csv("/home/claude/FUTURE_DS_01/data/region_performance.csv")

# Region x Category matrix
matrix = df.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="sum").round(0)
matrix.to_csv("/home/claude/FUTURE_DS_01/data/region_category_matrix.csv")

note("\n--- Top 5 Products by Revenue ---")
note(top_products.head(5).to_string(index=False))
note("\n--- Category Performance ---")
note(cat_perf.to_string())
note("\n--- Region Performance ---")
note(region_perf.to_string())

# ============ CHARTS ============
plt.style.use("seaborn-v0_8-whitegrid")
COLOR = "#2E5EAA"

# 1. Monthly revenue trend
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly["Order Month"], monthly["Revenue"], marker="o", color=COLOR, linewidth=2)
ax.set_title("Monthly Revenue Trend (2024-2025)", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue (Rs )")
ax.set_xlabel("Month")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e5:.1f}L"))
plt.xticks(rotation=60, fontsize=8)
plt.tight_layout()
plt.savefig("/home/claude/FUTURE_DS_01/charts/01_monthly_revenue_trend.png", dpi=150)
plt.close()

# 2. Top 10 products by revenue
top10 = top_products.head(10).sort_values("Revenue")
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(top10["Product Name"], top10["Revenue"], color=COLOR)
ax.set_title("Top 10 Products by Revenue", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue (Rs )")
plt.tight_layout()
plt.savefig("/home/claude/FUTURE_DS_01/charts/02_top_products.png", dpi=150)
plt.close()

# 3. Category revenue share (pie)
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(cat_perf["Revenue"], labels=cat_perf.index, autopct="%1.1f%%", startangle=90,
       colors=["#2E5EAA", "#5B9BD5", "#8EB4E3", "#C6DBF0"])
ax.set_title("Revenue Share by Category", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("/home/claude/FUTURE_DS_01/charts/03_category_share.png", dpi=150)
plt.close()

# 4. Region performance (revenue vs margin)
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.bar(region_perf.index, region_perf["Revenue"], color=COLOR, label="Revenue")
ax1.set_ylabel("Revenue (Rs )")
ax2 = ax1.twinx()
ax2.plot(region_perf.index, region_perf["Margin %"], color="#D9534F", marker="o", linewidth=2, label="Margin %")
ax2.set_ylabel("Profit Margin (%)")
ax1.set_title("Revenue & Profit Margin by Region", fontsize=13, fontweight="bold")
fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.88))
plt.tight_layout()
plt.savefig("/home/claude/FUTURE_DS_01/charts/04_region_performance.png", dpi=150)
plt.close()

with open("/home/claude/FUTURE_DS_01/data/analysis_log.txt", "w") as f:
    f.write("\n".join(log))

print("\nDone. Charts saved to charts/, tables saved to data/.")
