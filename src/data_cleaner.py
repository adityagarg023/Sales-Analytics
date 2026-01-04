import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple


class DataCleaner:
    def __init__(self):
        self.cleaning_log = []

    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
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
        before_count = len(df)
        df = df.drop_duplicates(subset=['Order_ID'], keep='first')
        removed = before_count - len(df)

        if removed > 0:
            self._log(f"  → Removed {removed} duplicate orders")
            self._log(f"     Reason: Prevents revenue double-counting in reports")

        return df

    def _fix_revenue_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
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
        self.cleaning_log.append(message)
        print(f"[DataCleaner] {message}")
