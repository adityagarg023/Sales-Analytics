import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.feature_engineer import FeatureEngineer
from src.analytics import SalesAnalytics
from src.forecasting import SalesForecaster

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def load_and_process_data(file_source):
    """Load and process sales data through complete pipeline."""
    with st.spinner("Loading data..."):
        if isinstance(file_source, str):
            df = DataLoader.load_data(file_path=file_source)
        else:
            df = DataLoader.load_data(uploaded_file=file_source)

        if df is None:
            return None, None, None

    with st.spinner("Cleaning data..."):
        cleaner = DataCleaner()
        df_clean, cleaning_log = cleaner.clean_data(df)

        with st.expander("📋 Data Cleaning Log"):
            for log in cleaning_log:
                st.text(log)

    with st.spinner("Engineering features..."):
        df_enhanced = FeatureEngineer.create_features(df_clean)

    return df_enhanced, df, cleaning_log


def display_overview_metrics(df):
    """Display key performance indicators."""
    st.header("📈 Executive Summary")

    metrics = FeatureEngineer.create_aggregated_metrics(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Revenue",
            f"${metrics['total_revenue']:,.0f}",
            delta=f"{metrics.get('total_growth_pct', 0):.1f}% overall"
        )

    with col2:
        st.metric(
            "Total Orders",
            f"{metrics['total_orders']:,}",
            delta=f"{metrics.get('avg_monthly_growth', 0):.1f}% avg monthly"
        )

    with col3:
        st.metric(
            "Average Order Value",
            f"${metrics['average_order_value']:,.2f}"
        )

    with col4:
        st.metric(
            "Total Units Sold",
            f"{metrics['total_units_sold']:,}"
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Unique Products", metrics['unique_products'])
    with col2:
        st.metric("Categories", metrics['unique_categories'])
    with col3:
        st.metric("Data Period", f"{metrics['date_range']['days']} days")
    with col4:
        st.metric("Date Range", f"{metrics['date_range']['start']} to {metrics['date_range']['end']}")


def display_sales_performance(analytics):
    """Display sales performance analysis."""
    st.header("💰 Sales Performance Analysis")

    performance = analytics.analyze_sales_performance()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Metrics")
        perf_df = pd.DataFrame({
            'Metric': ['Total Revenue', 'Total Orders', 'Avg Order Value', 'Median Order Value', 'Total Units Sold'],
            'Value': [
                f"${performance['total_revenue']:,.2f}",
                f"{performance['total_orders']:,}",
                f"${performance['avg_order_value']:,.2f}",
                f"${performance['median_order_value']:,.2f}",
                f"{performance['total_units_sold']:,}"
            ]
        })
        st.dataframe(perf_df, use_container_width=True, hide_index=True)

    with col2:
        if 'month_over_month_growth' in performance:
            st.subheader("Growth Indicators")
            mom_growth = performance['month_over_month_growth']
            st.metric("Month-over-Month Growth", f"{mom_growth:.2f}%")

            if mom_growth > 5:
                st.success("🚀 Strong growth momentum!")
            elif mom_growth < -5:
                st.warning("⚠️ Declining trend - action needed")
            else:
                st.info("📊 Stable performance")


def display_product_analysis(analytics):
    """Display product performance analysis."""
    st.header("🏷️ Product Performance")

    product_data = analytics.analyze_products()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 5 Products by Revenue")
        top_products = pd.DataFrame(product_data['top_5_products']).T
        top_products = top_products[['Revenue', 'Order_Count', 'Revenue_Share_%']].round(2)
        st.dataframe(top_products, use_container_width=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        top_products['Revenue'].plot(kind='barh', ax=ax, color='#2E86AB')
        ax.set_xlabel('Revenue ($)')
        ax.set_title('Top 5 Products by Revenue')
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Bottom 5 Products by Revenue")
        bottom_products = pd.DataFrame(product_data['bottom_5_products']).T
        bottom_products = bottom_products[['Revenue', 'Order_Count', 'Revenue_Share_%']].round(2)
        st.dataframe(bottom_products, use_container_width=True)

        st.info(f"**Product Concentration:** {product_data['concentration_ratio']:.1f}% of products "
                f"generate 80% of revenue")

    st.subheader("Category Performance")
    category_data = analytics.analyze_categories()
    category_df = pd.DataFrame(category_data['category_performance']).T
    category_df = category_df.round(2)
    st.dataframe(category_df, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(
        category_df['Total_Revenue'],
        labels=category_df.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=sns.color_palette('Set2')
    )
    ax.set_title('Revenue Distribution by Category')
    st.pyplot(fig)


def display_regional_analysis(analytics):
    """Display regional performance analysis."""
    st.header("🗺️ Regional Performance")

    regional_data = analytics.analyze_regions()
    regional_df = pd.DataFrame(regional_data['regional_performance']).T
    regional_df = regional_df.round(2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Regional Metrics")
        st.dataframe(regional_df, use_container_width=True)

    with col2:
        st.subheader("Revenue by Region")
        fig, ax = plt.subplots(figsize=(10, 6))
        regional_df['Total_Revenue'].plot(kind='bar', ax=ax, color='#A23B72')
        ax.set_xlabel('Region')
        ax.set_ylabel('Revenue ($)')
        ax.set_title('Total Revenue by Region')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)


def display_time_trends(analytics, df):
    """Display time-based trend analysis."""
    st.header("📅 Time-Based Trends")

    trends = analytics.analyze_time_trends()

    st.subheader("Monthly Revenue Trend")
    monthly_df = pd.DataFrame(trends['monthly_trends']).T

    fig, ax = plt.subplots(figsize=(14, 6))
    monthly_df.index = monthly_df.index.astype(str)
    ax.plot(monthly_df.index, monthly_df['Revenue'], marker='o', linewidth=2, markersize=8, color='#F18F01')
    ax.set_xlabel('Month')
    ax.set_ylabel('Revenue ($)')
    ax.set_title('Monthly Revenue Trend')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Metrics")
        display_df = monthly_df[['Revenue', 'Orders', 'Units']].round(2)
        st.dataframe(display_df, use_container_width=True)

    with col2:
        st.subheader("Revenue Growth by Month")
        growth_df = monthly_df[['Revenue_Growth_%']].dropna().round(2)
        st.dataframe(growth_df, use_container_width=True)

    if trends['yearly_trends']:
        st.subheader("Yearly Comparison")
        yearly_df = pd.DataFrame(trends['yearly_trends']).T
        st.dataframe(yearly_df, use_container_width=True)


def display_forecasting(df):
    """Display sales forecasting section."""
    st.header("🔮 Sales Forecasting")

    st.markdown("""
    ### About Forecasting Methods

    This dashboard offers three forecasting approaches:

    **1. Moving Average** - Simple average of recent months
    - Best for: Stable sales patterns
    - Pros: Easy to understand, quick calculation
    - Cons: Doesn't capture trends

    **2. Exponential Smoothing** - Weighted average favoring recent data
    - Best for: Growing or declining sales
    - Pros: Captures trends, responsive to changes
    - Cons: Requires decent history

    **3. ARIMA** - Statistical model analyzing patterns
    - Best for: Complex patterns, high accuracy needs
    - Pros: Most sophisticated, handles complexity
    - Cons: Needs more data (12+ months)
    """)

    col1, col2 = st.columns(2)

    with col1:
        forecast_method = st.selectbox(
            "Select Forecasting Method",
            ["Exponential Smoothing", "Moving Average", "ARIMA"],
            help="Choose based on your data pattern and forecasting needs"
        )

    with col2:
        forecast_periods = st.slider(
            "Forecast Horizon (months)",
            min_value=3,
            max_value=12,
            value=6,
            help="Number of months to forecast"
        )

    if st.button("Generate Forecast", type="primary"):
        method_map = {
            "Moving Average": "moving_average",
            "Exponential Smoothing": "exponential_smoothing",
            "ARIMA": "arima"
        }

        forecaster = SalesForecaster(df)

        with st.spinner(f"Generating {forecast_method} forecast..."):
            result = forecaster.generate_forecast(
                method=method_map[forecast_method],
                periods=forecast_periods
            )

        if 'error' in result:
            st.error(f"❌ {result['error']}: {result['message']}")
        else:
            st.success(f"✅ Forecast generated using {result['method']}")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("Forecast Visualization")

                fig, ax = plt.subplots(figsize=(14, 7))

                historical = result['historical_data']
                forecast = result['forecast']
                lower = result['lower_bound']
                upper = result['upper_bound']

                ax.plot(
                    range(len(historical)),
                    historical.values,
                    label='Historical Sales',
                    marker='o',
                    linewidth=2,
                    markersize=6,
                    color='#2E86AB'
                )

                forecast_x = range(len(historical), len(historical) + len(forecast))
                ax.plot(
                    forecast_x,
                    forecast.values,
                    label='Forecast',
                    marker='s',
                    linewidth=2,
                    markersize=6,
                    color='#F18F01',
                    linestyle='--'
                )

                ax.fill_between(
                    forecast_x,
                    lower.values,
                    upper.values,
                    alpha=0.3,
                    color='#F18F01',
                    label='95% Confidence Interval'
                )

                ax.axvline(x=len(historical)-0.5, color='red', linestyle=':', linewidth=2, label='Forecast Start')

                ax.set_xlabel('Time Period (Months)')
                ax.set_ylabel('Revenue ($)')
                ax.set_title(f'Sales Forecast - {result["method"]}')
                ax.legend()
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.subheader("Forecast Details")

                st.info(result['explanation'])

                st.markdown(f"**Confidence Level:** {result['confidence']}")

                summary = forecaster.get_forecast_summary()
                if 'error' not in summary:
                    st.metric("Total Forecast Revenue", f"${summary['total_forecast_revenue']:,.0f}")
                    st.metric("Avg Monthly Forecast", f"${summary['avg_monthly_forecast']:,.0f}")
                    st.metric(
                        "Change from Historical",
                        f"{summary['change_from_historical_%']:.1f}%",
                        delta=f"{summary['trend']}"
                    )

                    if summary['trend'] == 'GROWTH':
                        st.success(summary['interpretation'])
                    elif summary['trend'] == 'DECLINE':
                        st.warning(summary['interpretation'])
                    else:
                        st.info(summary['interpretation'])

            st.subheader("Forecast Data")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Historical Data (Last 6 Months)**")
                hist_df = pd.DataFrame({
                    'Month': historical.index[-6:].astype(str),
                    'Revenue': historical.values[-6:].round(2)
                })
                st.dataframe(hist_df, use_container_width=True, hide_index=True)

            with col2:
                st.markdown("**Forecast Data**")
                forecast_df = pd.DataFrame({
                    'Month': forecast.index.strftime('%Y-%m'),
                    'Forecast': forecast.values.round(2),
                    'Lower Bound': lower.values.round(2),
                    'Upper Bound': upper.values.round(2)
                })
                st.dataframe(forecast_df, use_container_width=True, hide_index=True)


def main():
    """Main dashboard application."""

    st.title("📊 Sales Analytics & Forecasting Dashboard")
    st.markdown("### Real-time Business Intelligence for Data-Driven Decisions")

    st.sidebar.title("⚙️ Dashboard Controls")
    st.sidebar.markdown("---")

    data_source = st.sidebar.radio(
        "Data Source",
        ["Use Sample Data", "Upload Your Data"],
        help="Choose to use provided sample data or upload your own CSV/Excel file"
    )

    if data_source == "Upload Your Data":
        uploaded_file = st.sidebar.file_uploader(
            "Upload Sales Data",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV or Excel file with sales data"
        )

        if uploaded_file is None:
            st.info("👈 Please upload a sales data file to begin analysis")
            st.markdown("""
            ### Required Columns:
            - Order_ID
            - Order_Date
            - Product
            - Category
            - Quantity
            - Price
            - Revenue
            - Region
            - Customer_Type
            """)
            return

        file_source = uploaded_file
    else:
        file_source = "data/sales_data_sample.csv"

    df_processed, df_raw, cleaning_log = load_and_process_data(file_source)

    if df_processed is None:
        st.error("Failed to load data. Please check the file format and try again.")
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Summary")
    st.sidebar.metric("Total Records", len(df_processed))
    st.sidebar.metric("Date Range", f"{df_processed['Order_Date'].min()} to {df_processed['Order_Date'].max()}")

    st.sidebar.markdown("---")
    date_filter = st.sidebar.checkbox("Enable Date Filtering")

    df_filtered = df_processed.copy()

    if date_filter:
        min_date = pd.to_datetime(df_processed['Order_Date']).min()
        max_date = pd.to_datetime(df_processed['Order_Date']).max()

        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:
            df_filtered = df_filtered[
                (pd.to_datetime(df_filtered['Order_Date']) >= pd.to_datetime(date_range[0])) &
                (pd.to_datetime(df_filtered['Order_Date']) <= pd.to_datetime(date_range[1]))
            ]

    region_filter = st.sidebar.multiselect(
        "Filter by Region",
        options=df_processed['Region'].unique(),
        default=df_processed['Region'].unique()
    )

    if region_filter:
        df_filtered = df_filtered[df_filtered['Region'].isin(region_filter)]

    category_filter = st.sidebar.multiselect(
        "Filter by Category",
        options=df_processed['Category'].unique(),
        default=df_processed['Category'].unique()
    )

    if category_filter:
        df_filtered = df_filtered[df_filtered['Category'].isin(category_filter)]

    st.sidebar.markdown("---")
    st.sidebar.info(f"**Filtered Records:** {len(df_filtered):,}")

    analytics = SalesAnalytics(df_filtered)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Overview",
        "💰 Sales Performance",
        "🏷️ Products",
        "🗺️ Regions",
        "📅 Time Trends",
        "🔮 Forecasting"
    ])

    with tab1:
        display_overview_metrics(df_filtered)

    with tab2:
        display_sales_performance(analytics)

    with tab3:
        display_product_analysis(analytics)

    with tab4:
        display_regional_analysis(analytics)

    with tab5:
        display_time_trends(analytics, df_filtered)

    with tab6:
        display_forecasting(df_filtered)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    **Sales Analytics Dashboard**

    Built with:
    - Python
    - Streamlit
    - Pandas & NumPy
    - Matplotlib & Seaborn
    - Statsmodels

    Features:
    - Real-time data analysis
    - Interactive filtering
    - Sales forecasting
    - Business insights
    """)


if __name__ == "__main__":
    main()
