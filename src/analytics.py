"""
Analytics Module
================
Performs core business analysis on sales data.

Business Purpose:
- Extract actionable insights from sales data
- Identify trends, patterns, and anomalies
- Support data-driven decision making

Analysis Categories:
1. Sales Performance → Overall business health
2. Product Analysis → Product strategy & inventory
3. Regional Analysis → Market expansion & resource allocation
4. Time-Series Analysis → Forecasting & seasonality
5. Customer Analysis → Segmentation & retention

Author: Data Analytics Team
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class SalesAnalytics:
    """
    Comprehensive sales analysis engine for business intelligence.

    Each analysis method answers specific business questions and
    provides insights that directly inform decisions.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize analytics engine with processed sales data.

        Parameters:
        -----------
        df : pd.DataFrame
            Cleaned and feature-engineered sales data
        """
        self.df = df

    def analyze_sales_performance(self) -> Dict:
        """
        Analyze overall sales performance metrics.

        Business Questions:
        ------------------
        1. How much revenue are we generating?
        2. What's our order volume trend?
        3. What's the average transaction value?
        4. Are we growing or declining?

        Returns:
        --------
        Dict containing:
        - Total revenue
        - Total orders
        - Average order value
        - Growth trends
        """
        performance = {
            'total_revenue': self.df['Revenue'].sum(),
            'total_orders': len(self.df),
            'avg_order_value': self.df['Revenue'].mean(),
            'median_order_value': self.df['Revenue'].median(),
            'total_units_sold': self.df['Quantity'].sum(),
            'avg_units_per_order': self.df['Quantity'].mean()
        }

        monthly_revenue = self.df.groupby('Year_Month')['Revenue'].sum().sort_index()
        if len(monthly_revenue) >= 2:
            recent_month = monthly_revenue.iloc[-1]
            previous_month = monthly_revenue.iloc[-2]
            mom_growth = ((recent_month - previous_month) / previous_month * 100) if previous_month != 0 else 0
            performance['month_over_month_growth'] = mom_growth

        return performance

    def analyze_products(self) -> Dict:
        """
        Analyze product performance and contribution.

        Business Questions:
        ------------------
        1. Which products generate most revenue?
        2. Which products sell most volume?
        3. Which products underperform?
        4. What's our product mix?

        Insights Drive:
        --------------
        - Inventory planning
        - Marketing budget allocation
        - Product discontinuation decisions
        - Pricing strategy

        Returns:
        --------
        Dict containing:
        - Top products by revenue
        - Top products by volume
        - Worst performers
        - Product concentration risk
        """
        product_revenue = self.df.groupby('Product').agg({
            'Revenue': 'sum',
            'Quantity': 'sum',
            'Order_ID': 'count'
        }).rename(columns={'Order_ID': 'Order_Count'})

        product_revenue = product_revenue.sort_values('Revenue', ascending=False)

        product_revenue['Revenue_Share_%'] = (product_revenue['Revenue'] / product_revenue['Revenue'].sum() * 100)
        product_revenue['Cumulative_Revenue_Share_%'] = product_revenue['Revenue_Share_%'].cumsum()

        top_5_products = product_revenue.head(5).to_dict('index')
        bottom_5_products = product_revenue.tail(5).to_dict('index')

        total_products = len(product_revenue)
        products_80_pct_revenue = (product_revenue['Cumulative_Revenue_Share_%'] <= 80).sum()
        concentration_ratio = (products_80_pct_revenue / total_products * 100) if total_products > 0 else 0

        return {
            'top_5_products': top_5_products,
            'bottom_5_products': bottom_5_products,
            'total_products': total_products,
            'concentration_ratio': concentration_ratio,
            'product_details': product_revenue.to_dict('index')
        }

    def analyze_categories(self) -> Dict:
        """
        Analyze category-level performance.

        Business Questions:
        ------------------
        1. Which categories drive revenue?
        2. Which categories have growth potential?
        3. Should we expand/contract category offerings?

        Strategic Impact:
        ----------------
        - Category expansion decisions
        - Resource allocation across categories
        - Vendor negotiations
        - Assortment planning

        Returns:
        --------
        Dict containing category metrics and rankings
        """
        category_metrics = self.df.groupby('Category').agg({
            'Revenue': ['sum', 'mean', 'count'],
            'Quantity': 'sum'
        })

        category_metrics.columns = ['Total_Revenue', 'Avg_Order_Value', 'Order_Count', 'Units_Sold']
        category_metrics = category_metrics.sort_values('Total_Revenue', ascending=False)

        category_metrics['Revenue_Share_%'] = (category_metrics['Total_Revenue'] / category_metrics['Total_Revenue'].sum() * 100)

        return {
            'category_performance': category_metrics.to_dict('index'),
            'total_categories': len(category_metrics)
        }

    def analyze_regions(self) -> Dict:
        """
        Analyze regional sales performance.

        Business Questions:
        ------------------
        1. Which regions generate most revenue?
        2. Where should we expand operations?
        3. Which regions need support?
        4. Are there regional preference patterns?

        Operational Impact:
        ------------------
        - Warehouse location decisions
        - Sales team allocation
        - Regional marketing campaigns
        - Expansion planning

        Returns:
        --------
        Dict containing regional performance metrics
        """
        regional_metrics = self.df.groupby('Region').agg({
            'Revenue': ['sum', 'mean'],
            'Order_ID': 'count',
            'Quantity': 'sum'
        })

        regional_metrics.columns = ['Total_Revenue', 'Avg_Order_Value', 'Order_Count', 'Units_Sold']
        regional_metrics = regional_metrics.sort_values('Total_Revenue', ascending=False)

        regional_metrics['Revenue_Share_%'] = (regional_metrics['Total_Revenue'] / regional_metrics['Total_Revenue'].sum() * 100)

        return {
            'regional_performance': regional_metrics.to_dict('index'),
            'total_regions': len(regional_metrics)
        }

    def analyze_time_trends(self) -> Dict:
        """
        Analyze temporal patterns and trends.

        Business Questions:
        ------------------
        1. Are sales growing or declining?
        2. Are there seasonal patterns?
        3. Which months/quarters perform best?
        4. What's our growth trajectory?

        Forecasting Impact:
        ------------------
        - Revenue forecasting
        - Inventory planning
        - Cash flow projections
        - Hiring decisions

        Returns:
        --------
        Dict containing:
        - Monthly trends
        - Yearly comparisons
        - Seasonality indicators
        - Growth rates
        """
        monthly_trends = self.df.groupby('Year_Month').agg({
            'Revenue': 'sum',
            'Order_ID': 'count',
            'Quantity': 'sum'
        }).sort_index()

        monthly_trends.columns = ['Revenue', 'Orders', 'Units']

        monthly_trends['Revenue_Growth_%'] = monthly_trends['Revenue'].pct_change() * 100
        monthly_trends['Orders_Growth_%'] = monthly_trends['Orders'].pct_change() * 100

        if len(self.df['Year'].unique()) > 1:
            yearly_trends = self.df.groupby('Year').agg({
                'Revenue': 'sum',
                'Order_ID': 'count'
            })
            yearly_trends.columns = ['Revenue', 'Orders']
        else:
            yearly_trends = None

        quarterly_trends = self.df.groupby(['Year', 'Quarter']).agg({
            'Revenue': 'sum',
            'Order_ID': 'count'
        })
        quarterly_trends.columns = ['Revenue', 'Orders']

        day_of_week_avg = self.df.groupby('Day_Name')['Revenue'].mean().sort_values(ascending=False)

        return {
            'monthly_trends': monthly_trends.to_dict('index'),
            'yearly_trends': yearly_trends.to_dict('index') if yearly_trends is not None else None,
            'quarterly_trends': quarterly_trends.to_dict('index'),
            'day_of_week_patterns': day_of_week_avg.to_dict()
        }

    def analyze_customers(self) -> Dict:
        """
        Analyze customer segments and behavior.

        Business Questions:
        ------------------
        1. Which customer segments are most valuable?
        2. What's the revenue distribution by segment?
        3. Which segments have highest AOV?

        Marketing Impact:
        ----------------
        - Customer acquisition strategy
        - Loyalty program design
        - Personalized marketing
        - Segment-specific promotions

        Returns:
        --------
        Dict containing customer segment analysis
        """
        customer_metrics = self.df.groupby('Customer_Type').agg({
            'Revenue': ['sum', 'mean'],
            'Order_ID': 'count',
            'Quantity': 'sum'
        })

        customer_metrics.columns = ['Total_Revenue', 'Avg_Order_Value', 'Order_Count', 'Units_Purchased']
        customer_metrics = customer_metrics.sort_values('Total_Revenue', ascending=False)

        customer_metrics['Revenue_Share_%'] = (customer_metrics['Total_Revenue'] / customer_metrics['Total_Revenue'].sum() * 100)

        return {
            'customer_segment_performance': customer_metrics.to_dict('index'),
            'total_segments': len(customer_metrics)
        }

    def get_full_analysis_report(self) -> Dict:
        """
        Generate comprehensive business analysis report.

        Returns:
        --------
        Dict containing all analysis results

        Business Use:
        ------------
        This report provides a complete view of business performance
        for executive dashboards, board presentations, and strategic planning.
        """
        return {
            'sales_performance': self.analyze_sales_performance(),
            'product_analysis': self.analyze_products(),
            'category_analysis': self.analyze_categories(),
            'regional_analysis': self.analyze_regions(),
            'time_trends': self.analyze_time_trends(),
            'customer_analysis': self.analyze_customers()
        }
