import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_extended_sample_data(output_file='sales_data_extended.csv'):

    np.random.seed(42)
    random.seed(42)

    products = [
        'Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones',
        'Webcam', 'USB Cable', 'Hard Drive', 'SSD', 'RAM',
        'Graphics Card', 'Motherboard', 'Power Supply', 'Case', 'CPU Cooler'
    ]

    categories = {
        'Laptop': 'Computers', 'Mouse': 'Accessories', 'Keyboard': 'Accessories',
        'Monitor': 'Display', 'Headphones': 'Audio', 'Webcam': 'Accessories',
        'USB Cable': 'Accessories', 'Hard Drive': 'Storage', 'SSD': 'Storage',
        'RAM': 'Components', 'Graphics Card': 'Components',
        'Motherboard': 'Components', 'Power Supply': 'Components',
        'Case': 'Components', 'CPU Cooler': 'Components'
    }

    regions = ['North', 'South', 'East', 'West', 'Central']
    customer_types = ['Regular', 'Premium', 'New', 'VIP']

    base_prices = {
        'Laptop': 850, 'Mouse': 25, 'Keyboard': 50, 'Monitor': 300,
        'Headphones': 80, 'Webcam': 60, 'USB Cable': 10, 'Hard Drive': 100,
        'SSD': 150, 'RAM': 80, 'Graphics Card': 500, 'Motherboard': 200,
        'Power Supply': 90, 'Case': 70, 'CPU Cooler': 40
    }

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)

    records = []
    order_id = 10000

    current_date = start_date
    month_counter = 0

    while current_date <= end_date:
        month_counter += 1

        growth_factor = 1 + (month_counter * 0.02)

        if current_date.month in [11, 12]:
            seasonal_factor = 1.4
        elif current_date.month in [1, 2]:
            seasonal_factor = 0.8
        else:
            seasonal_factor = 1.0

        orders_this_month = int(200 * growth_factor * seasonal_factor * random.uniform(0.9, 1.1))

        for _ in range(orders_this_month):
            day_offset = random.randint(0, 27)
            order_date = current_date + timedelta(days=day_offset)

            if order_date > end_date:
                break

            product = random.choice(products)
            category = categories[product]
            quantity = random.randint(1, 8)

            price = base_prices[product] * random.uniform(0.85, 1.15)
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

        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)

    df = pd.DataFrame(records)

    total_records = len(df)
    missing_revenue_count = int(total_records * 0.02)
    missing_price_count = int(total_records * 0.01)
    missing_quantity_count = int(total_records * 0.01)

    missing_revenue_indices = np.random.choice(df.index, size=missing_revenue_count, replace=False)
    df.loc[missing_revenue_indices, 'Revenue'] = np.nan

    missing_price_indices = np.random.choice(df.index, size=missing_price_count, replace=False)
    df.loc[missing_price_indices, 'Price'] = np.nan

    missing_quantity_indices = np.random.choice(df.index, size=missing_quantity_count, replace=False)
    df.loc[missing_quantity_indices, 'Quantity'] = np.nan

    duplicate_count = int(total_records * 0.015)
    duplicate_indices = np.random.choice(df.index, size=duplicate_count, replace=False)
    duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    wrong_date_count = int(len(df) * 0.01)
    wrong_date_indices = np.random.choice(df.index, size=wrong_date_count, replace=False)
    df.loc[wrong_date_indices, 'Order_Date'] = df.loc[wrong_date_indices, 'Order_Date'].astype(str).str.replace('-', '/')

    wrong_revenue_count = int(len(df) * 0.02)
    wrong_revenue_indices = np.random.choice(df.index, size=wrong_revenue_count, replace=False)
    df.loc[wrong_revenue_indices, 'Revenue'] = df.loc[wrong_revenue_indices, 'Revenue'] * random.uniform(1.3, 1.7)

    df = df.sample(frac=1).reset_index(drop=True)

    df.to_csv(output_file, index=False)

    print(f"✅ Generated {len(df)} records")
    print(f"📅 Date range: {df['Order_Date'].min()} to {df['Order_Date'].max()}")
    print(f"\n📊 Data Quality Issues Introduced:")
    print(f"   - {missing_revenue_count} missing revenue values")
    print(f"   - {missing_price_count} missing price values")
    print(f"   - {missing_quantity_count} missing quantity values")
    print(f"   - {duplicate_count} duplicate orders")
    print(f"   - {wrong_date_count} inconsistent date formats")
    print(f"   - {wrong_revenue_count} incorrect revenue calculations")
    print(f"\n💾 Saved to: {output_file}")

if __name__ == "__main__":
    generate_extended_sample_data('sales_data_extended.csv')
    print("\n✨ Extended sample data generated successfully!")
    print("Use this file for more robust time-series analysis and forecasting.")
