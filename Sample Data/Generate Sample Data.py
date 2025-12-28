import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

products = [
    'Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones',
    'Webcam', 'USB Cable', 'Hard Drive', 'SSD', 'RAM',
    'Graphics Card', 'Motherboard', 'Power Supply', 'Case', 'CPU Cooler'
]

categories = {
    'Laptop': 'Computers',
    'Mouse': 'Accessories',
    'Keyboard': 'Accessories',
    'Monitor': 'Display',
    'Headphones': 'Audio',
    'Webcam': 'Accessories',
    'USB Cable': 'Accessories',
    'Hard Drive': 'Storage',
    'SSD': 'Storage',
    'RAM': 'Components',
    'Graphics Card': 'Components',
    'Motherboard': 'Components',
    'Power Supply': 'Components',
    'Case': 'Components',
    'CPU Cooler': 'Components'
}

regions = ['North', 'South', 'East', 'West', 'Central']
customer_types = ['Regular', 'Premium', 'New', 'VIP']

start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

records = []
order_id = 1000

for i in range(5000):
    order_date = start_date + timedelta(days=random.randint(0, date_range))
    product = random.choice(products)
    category = categories[product]
    quantity = random.randint(1, 10)

    base_prices = {
        'Laptop': 800, 'Mouse': 25, 'Keyboard': 50, 'Monitor': 300,
        'Headphones': 80, 'Webcam': 60, 'USB Cable': 10, 'Hard Drive': 100,
        'SSD': 150, 'RAM': 80, 'Graphics Card': 500, 'Motherboard': 200,
        'Power Supply': 90, 'Case': 70, 'CPU Cooler': 40
    }

    price = base_prices[product] * (1 + random.uniform(-0.2, 0.3))
    revenue = quantity * price

    region = random.choice(regions)
    customer_type = random.choice(customer_types)

    records.append({
        'Order_ID': order_id,
        'Order_Date': order_date.strftime('%Y-%m-%d'),
        'Product': product,
        'Category': category,
        'Quantity': quantity,
        'Price': round(price, 2),
        'Revenue': round(revenue, 2),
        'Region': region,
        'Customer_Type': customer_type
    })

    order_id += 1

df = pd.DataFrame(records)

missing_indices = np.random.choice(df.index, size=150, replace=False)
df.loc[missing_indices[:50], 'Revenue'] = np.nan
df.loc[missing_indices[50:100], 'Price'] = np.nan
df.loc[missing_indices[100:150], 'Quantity'] = np.nan

duplicate_indices = np.random.choice(df.index, size=100, replace=False)
duplicates = df.loc[duplicate_indices].copy()
df = pd.concat([df, duplicates], ignore_index=True)

wrong_date_indices = np.random.choice(df.index, size=50, replace=False)
df.loc[wrong_date_indices, 'Order_Date'] = df.loc[wrong_date_indices, 'Order_Date'].astype(str).str.replace('-', '/')

wrong_revenue_indices = np.random.choice(df.index, size=80, replace=False)
df.loc[wrong_revenue_indices, 'Revenue'] = df.loc[wrong_revenue_indices, 'Revenue'] * 1.5

df = df.sample(frac=1).reset_index(drop=True)

df.to_csv('data/sales_data.csv', index=False)

print(f"Generated {len(df)} records with intentional data quality issues:")
print(f"- Missing values in Revenue, Price, Quantity")
print(f"- Duplicate orders")
print(f"- Inconsistent date formats")
print(f"- Incorrect revenue calculations")
print("\nSample data:")
print(df.head(10))
print("\nData info:")
print(df.info())
