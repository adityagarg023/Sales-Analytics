"""
Data Cleaner Module
===================
Handles data quality issues in real-world sales data.

Business Purpose:
- Ensures data accuracy for reliable business decisions
- Prevents incorrect revenue reporting due to data quality issues
- Documents every cleaning decision for audit and transparency

Key Principle:
Data quality directly impacts business decisions. Bad data = bad decisions.
Every cleaning step must have a clear business justification.

Author: Data Analytics Team
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple


class DataCleaner:
    """
    Handles all data cleaning operations with business-focused reasoning.

    Philosophy:
    - Only clean when there's a clear business reason
    - Document what was changed and why
    - Preserve as much data as possible
    """

    def __init__(self):
        self.cleaning_log = []

    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """
        Execute the complete data cleaning pipeline.

        Parameters:
        -----------
        df : pd.DataFrame
            Raw sales data with potential quality issues

        Returns:
        --------
        Tuple[pd.DataFrame, list]
            Cleaned dataframe and log of all changes made

        Business Impact:
        ---------------
        Clean data ensures accurate revenue reporting, reliable forecasting,
        and trustworthy business insights for decision-making.
        """
        df_clean = df.copy()
        original_count = len(df_clean)

        self._log(f"Starting data cleaning with {original_count} records")

        df_clean = self._standardize_dates(df_clean)
        df_clean = self._handle_missing_values(df_clean)
        df_clean = self._remove_duplicates(df_clean)
        df_clean = self._fix_revenue_calculations(df_clean)
        df_clean = self._validate_data_types(df_clean)
        df_clean = self._handle_outliers(df_clean)

        final_count = len(df_clean)
        removed_count = original_count - final_count

        self._log(f"Cleaning complete: {final_count} records retained, {removed_count} removed")

        return df_clean, self.cleaning_log

    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert all date formats to a consistent standard format.

        Business Reason:
        ---------------
        Inconsistent date formats break time-series analysis and forecasting.
        Business reports must show accurate monthly/quarterly trends.

        Common Issues:
        - Excel date formats vs string formats
        - Various date separators (/, -, .)
        - Different date orderings (MM/DD/YYYY vs DD/MM/YYYY)
        """
        self._log("Standardizing date formats...")

        try:
            df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')

            invalid_dates = df['Order_Date'].isna().sum()
            if invalid_dates > 0:
                self._log(f"⚠️  Found {invalid_dates} invalid dates - these orders will be removed")
                df = df.dropna(subset=['Order_Date'])

            df['Order_Date'] = df['Order_Date'].dt.date

        except Exception as e:
            self._log(f"❌ Error in date standardization: {str(e)}")

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values based on business logic.

        Business Reasoning:
        ------------------
        1. Missing Quantity: Cannot determine order value → Remove
           Impact: Prevents understating sales volume

        2. Missing Price: Cannot calculate revenue → Remove
           Impact: Prevents revenue calculation errors

        3. Missing Revenue: Can be recalculated from Quantity × Price
           Impact: Recovers potentially valid orders

        4. Missing Region/Customer_Type: Use 'Unknown' category
           Impact: Preserves order data while acknowledging uncertainty
        """
        self._log("Handling missing values...")

        critical_cols = ['Order_ID', 'Product', 'Category']
        before_count = len(df)
        df = df.dropna(subset=critical_cols)
        removed = before_count - len(df)
        if removed > 0:
            self._log(f"  → Removed {removed} orders with missing critical fields (ID/Product/Category)")

        missing_qty = df['Quantity'].isna().sum()
        missing_price = df['Price'].isna().sum()

        if missing_qty > 0:
            self._log(f"  → Removing {missing_qty} orders with missing quantity")
            df = df.dropna(subset=['Quantity'])

        if missing_price > 0:
            self._log(f"  → Removing {missing_price} orders with missing price")
            df = df.dropna(subset=['Price'])

        missing_revenue = df['Revenue'].isna().sum()
        if missing_revenue > 0:
            self._log(f"  → Recalculating {missing_revenue} missing revenue values from Quantity × Price")
            df.loc[df['Revenue'].isna(), 'Revenue'] = df['Quantity'] * df['Price']

        if df['Region'].isna().any():
            df['Region'].fillna('Unknown', inplace=True)
            self._log(f"  → Filled missing regions with 'Unknown'")

        if df['Customer_Type'].isna().any():
            df['Customer_Type'].fillna('Unknown', inplace=True)
            self._log(f"  → Filled missing customer types with 'Unknown'")

        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate orders to prevent double-counting.

        Business Reason:
        ---------------
        Duplicate orders artificially inflate revenue and volume metrics.
        This leads to:
        - Overstated performance
        - Incorrect forecasts
        - Misallocated resources

        Strategy:
        - Keep the first occurrence of each order
        - Duplicates are identified by Order_ID
        """
        before_count = len(df)
        df = df.drop_duplicates(subset=['Order_ID'], keep='first')
        removed = before_count - len(df)

        if removed > 0:
            self._log(f"  → Removed {removed} duplicate orders")
            self._log(f"     Reason: Prevents revenue double-counting in reports")

        return df

    def _fix_revenue_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Verify and correct revenue calculations.

        Business Reason:
        ---------------
        Incorrect revenue figures can result from:
        - System bugs
        - Manual data entry errors
        - Currency conversion issues
        - Discount application errors

        Impact: Revenue is the most critical metric. Any error here
        directly affects financial reporting and business decisions.

        Method:
        - Calculate expected revenue: Quantity × Price
        - Compare with recorded revenue
        - Flag discrepancies > 1% (allows for rounding)
        - Recalculate when discrepancies found
        """
        self._log("Validating revenue calculations...")

        df['Expected_Revenue'] = df['Quantity'] * df['Price']

        df['Revenue_Diff'] = abs(df['Revenue'] - df['Expected_Revenue'])
        df['Revenue_Diff_Pct'] = (df['Revenue_Diff'] / df['Expected_Revenue']) * 100

        incorrect_revenue = (df['Revenue_Diff_Pct'] > 1.0).sum()

        if incorrect_revenue > 0:
            self._log(f"  → Found {incorrect_revenue} orders with incorrect revenue calculations")
            self._log(f"     Recalculating revenue as Quantity × Price")

            df.loc[df['Revenue_Diff_Pct'] > 1.0, 'Revenue'] = df['Expected_Revenue']

        df = df.drop(columns=['Expected_Revenue', 'Revenue_Diff', 'Revenue_Diff_Pct'])

        return df

    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure all columns have correct data types for analysis.

        Business Reason:
        ---------------
        Wrong data types break mathematical operations and aggregations.
        For example:
        - Can't sum revenue if it's stored as text
        - Can't calculate average order value
        - Can't perform time-series analysis
        """
        self._log("Validating data types...")

        numeric_cols = ['Quantity', 'Price', 'Revenue']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['Order_ID'] = df['Order_ID'].astype(str)
        df['Product'] = df['Product'].astype(str)
        df['Category'] = df['Category'].astype(str)
        df['Region'] = df['Region'].astype(str)
        df['Customer_Type'] = df['Customer_Type'].astype(str)

        return df

    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify and handle extreme outliers in business metrics.

        Business Reason:
        ---------------
        Extreme outliers can indicate:
        1. Data entry errors (e.g., extra zero added to quantity)
        2. Fraudulent transactions
        3. System glitches

        However, some outliers are legitimate (bulk orders, enterprise deals).

        Strategy:
        - Flag values beyond 3 standard deviations
        - Review but don't automatically remove
        - Log for manual review by business team
        """
        self._log("Checking for outliers...")

        for col in ['Quantity', 'Price', 'Revenue']:
            mean = df[col].mean()
            std = df[col].std()
            outliers = ((df[col] - mean).abs() > 3 * std).sum()

            if outliers > 0:
                self._log(f"  ⚠️  Found {outliers} potential outliers in {col}")
                self._log(f"     These may be legitimate bulk orders - review manually")

        return df

    def _log(self, message: str):
        """
        Add a message to the cleaning log.

        Business Purpose:
        ----------------
        Maintains an audit trail of all data transformations.
        Critical for:
        - Data governance
        - Troubleshooting analysis discrepancies
        - Compliance and reporting standards
        """
        self.cleaning_log.append(message)
        print(f"[DataCleaner] {message}")
