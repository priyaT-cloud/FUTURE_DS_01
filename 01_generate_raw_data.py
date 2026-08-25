"""
Task 1 - Business Sales Performance Analytics
Generates a realistic, messy raw sales transactions dataset for a mid-size
multi-category retail business (2 years of orders), styled like a real
export from an order-management / POS system - including the kinds of
issues real analysts have to clean: inconsistent casing, stray whitespace,
duplicate rows, missing values, and mixed date formats.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)

regions = ["North", "South", "East", "West"]
categories = {
    "Electronics": ["Wireless Mouse", "Bluetooth Speaker", "USB-C Charger", "Laptop Stand",
                     "Noise Cancelling Headphones", "Smartwatch", "Webcam HD", "Power Bank 10000mAh"],
    "Furniture": ["Office Chair", "Study Table", "Bookshelf", "Bean Bag", "Filing Cabinet",
                  "Wall Shelf", "Recliner Sofa", "Bed Side Table"],
    "Office Supplies": ["A4 Paper Ream", "Stapler", "Sticky Notes Pack", "Ballpoint Pen Box",
                         "Whiteboard Marker Set", "File Folder Pack", "Desk Organizer", "Printer Ink Cartridge"],
    "Clothing": ["Cotton T-Shirt", "Denim Jeans", "Running Shoes", "Formal Shirt",
                 "Hoodie", "Rain Jacket", "Sports Cap", "Woolen Sweater"],
}
# per-product base price range and margin profile (used to make revenue/profit realistic)
price_map = {}
for cat, prods in categories.items():
    for p in prods:
        base = {
            "Electronics": rng.uniform(600, 6000),
            "Furniture": rng.uniform(1200, 15000),
            "Office Supplies": rng.uniform(40, 500),
            "Clothing": rng.uniform(300, 2500),
        }[cat]
        margin = rng.uniform(0.08, 0.35)
        price_map[p] = (round(base, 2), margin, cat)

customer_segments = ["Consumer", "Corporate", "Home Office"]
ship_modes = ["Standard", "Express", "Same Day"]

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
n_days = (end_date - start_date).days

n_orders = 5200
rows = []
order_id_seq = 1000

for i in range(n_orders):
    # seasonality: more orders around Oct-Dec (festive/holiday) and July (mid-year sale)
    day_offset = rng.integers(0, n_days)
    order_date = start_date + timedelta(days=int(day_offset))
    month = order_date.month
    seasonal_boost = 1.0
    if month in (10, 11, 12):
        seasonal_boost = 1.6
    elif month == 7:
        seasonal_boost = 1.3
    if rng.random() > (0.55 * seasonal_boost / 1.6):
        continue

    order_id_seq += 1
    order_id = f"ORD-{order_id_seq:05d}"
    region = rng.choice(regions, p=[0.28, 0.24, 0.26, 0.22])
    n_items = rng.integers(1, 4)
    segment = rng.choice(customer_segments, p=[0.55, 0.30, 0.15])
    ship_mode = rng.choice(ship_modes, p=[0.65, 0.25, 0.10])
    customer_id = f"CUST-{rng.integers(1, 1400):04d}"

    for _ in range(n_items):
        cat = rng.choice(list(categories.keys()), p=[0.32, 0.18, 0.28, 0.22])
        product = rng.choice(categories[cat])
        base_price, margin, _ = price_map[product]
        qty = int(rng.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.15, 0.08, 0.04, 0.03]))
        discount = rng.choice([0, 0, 0, 0.05, 0.1, 0.15, 0.2], p=[0.45, 0.15, 0.1, 0.1, 0.1, 0.06, 0.04])
        unit_price = base_price * (1 - discount)
        sales = round(unit_price * qty, 2)
        profit = round(sales * margin - (sales * discount * 0.3), 2)

        # inject messiness
        date_str = order_date.strftime("%Y-%m-%d") if rng.random() > 0.15 else order_date.strftime("%d/%m/%Y")
        cat_messy = cat
        if rng.random() < 0.08:
            cat_messy = cat.upper()
        elif rng.random() < 0.08:
            cat_messy = cat.lower() + "  "
        region_messy = region if rng.random() > 0.05 else f" {region}"

        rows.append({
            "Order ID": order_id,
            "Order Date": date_str,
            "Customer ID": customer_id,
            "Segment": segment,
            "Region": region_messy,
            "Category": cat_messy,
            "Product Name": product if rng.random() > 0.03 else product + "  ",
            "Quantity": qty if rng.random() > 0.01 else None,
            "Discount": discount,
            "Sales": sales,
            "Profit": profit,
            "Ship Mode": ship_mode,
        })

df = pd.DataFrame(rows)

# duplicate ~1.5% of rows (common real-world export issue)
dupes = df.sample(frac=0.015, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# null out a few Sales/Profit values
null_idx = df.sample(frac=0.01, random_state=2).index
df.loc[null_idx, "Profit"] = None

# shuffle
df = df.sample(frac=1, random_state=3).reset_index(drop=True)

df.to_csv("/home/claude/FUTURE_DS_01/data/raw_sales_data.csv", index=False)
print("Rows generated:", len(df))
print(df.head(8).to_string())
