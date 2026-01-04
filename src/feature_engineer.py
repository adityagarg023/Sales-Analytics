import pandas as pd
import numpy as np
from datetime import datetime


class FeatureEngineer:

    @staticmethod
    def create_features(df: pd.DataFrame) -> pd.DataFrame:
        df_enhanced = df.copy()

        df_enhanced = FeatureEngineer._add_time_features(df_enhanced)
        df_enhanced = FeatureEngineer._add_revenue_features(df_enhanced)
        df_enhanced = FeatureEngineer._add_product_features(df_enhanced)

        return df_enhanced

    @staticmethod
    def _add_time_features(df: pd.DataFrame) -> pd.DataFrame:
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])

        df['Year'] = df['Order_Date'].dt.year
        df['Quarter'] = df['Order_Date'].dt.quarter
        df['Month'] = df['Order_Date'].dt.month
        df['Month_Name'] = df['Order_Date'].dt.strftime('%B')
        df['Day'] = df['Order_Date'].dt.day
        df['Day_Name'] = df['Order_Date'].dt.strftime('%A')
        df['Week_of_Year'] = df['Order_Date'].dt.isocalendar().week
        df['Year_Month'] = df['Order_Date'].dt.to_period('M')

        first_order_date = df['Order_Date'].min()
        df['Days_Since_First_Order'] = (df['Order_Date'] - first_order_date).dt.days

        return df

    @staticmethod
    def _add_revenue_features(df: pd.DataFrame) -> pd.DataFrame:
        avg_revenue = df['Revenue'].mean()
        df['AOV'] = avg_revenue

        df['Order_Value_Tier'] = pd.cut(
            df['Revenue'],
            bins=[0, avg_revenue * 0.5, avg_revenue, avg_revenue * 2, float('inf')],
            labels=['Low', 'Medium', 'High', 'Premium']
        )

        df['Unit_Revenue'] = df['Revenue'] / df['Quantity']

        return df

    @staticmethod
    def _add_product_features(df: pd.DataFrame) -> pd.DataFrame:
        product_revenue = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
        product_rank = {product: rank + 1 for rank, product in enumerate(product_revenue.index)}
        df['Product_Revenue_Rank'] = df['Product'].map(product_rank)

        category_revenue = df.groupby('Category')['Revenue'].sum()
        total_revenue = df['Revenue'].sum()
        category_share = (category_revenue / total_revenue * 100).to_dict()
        df['Category_Revenue_Share'] = df['Category'].map(category_share)

        return df

    @staticmethod
    def create_aggregated_metrics(df: pd.DataFrame) -> dict:
        metrics = {
            'total_revenue': df['Revenue'].sum(),
            'total_orders': len(df),
            'average_order_value': df['Revenue'].mean(),
            'total_units_sold': df['Quantity'].sum(),
            'unique_products': df['Product'].nunique(),
            'unique_categories': df['Category'].nunique(),
            'unique_customers': df['Customer_Type'].nunique(),
            'date_range': {
                'start': df['Order_Date'].min(),
                'end': df['Order_Date'].max(),
                'days': (df['Order_Date'].max() - df['Order_Date'].min()).days
            }
        }

        monthly_revenue = df.groupby('Year_Month')['Revenue'].sum().sort_index()

        if len(monthly_revenue) > 1:
            first_month = monthly_revenue.iloc[0]
            last_month = monthly_revenue.iloc[-1]

            if first_month > 0:
                total_growth = ((last_month - first_month) / first_month) * 100
                metrics['total_growth_pct'] = total_growth
            else:
                metrics['total_growth_pct'] = 0

            monthly_changes = monthly_revenue.pct_change().dropna() * 100
            metrics['avg_monthly_growth'] = monthly_changes.mean()
        else:
            metrics['total_growth_pct'] = 0
            metrics['avg_monthly_growth'] = 0

        return metrics
