"""
Data Loader Module
==================
Handles loading sales data from CSV/Excel files with error handling and validation.

Business Purpose:
- Ensures data can be loaded reliably from various file formats
- Provides clear error messages when data loading fails
- Validates that required columns exist in the dataset

Author: Data Analytics Team
"""

import pandas as pd
import streamlit as st
from typing import Optional


class DataLoader:
    """
    Responsible for loading and initial validation of sales data.

    This class handles the technical aspects of reading files while
    ensuring business-critical columns are present.
    """

    REQUIRED_COLUMNS = [
        'Order_ID', 'Order_Date', 'Product', 'Category',
        'Quantity', 'Price', 'Revenue', 'Region', 'Customer_Type'
    ]

    @staticmethod
    def load_data(file_path: str = None, uploaded_file=None) -> Optional[pd.DataFrame]:
        """
        Load sales data from a file path or uploaded file object.

        Parameters:
        -----------
        file_path : str, optional
            Path to the CSV/Excel file on disk
        uploaded_file : UploadedFile, optional
            Streamlit uploaded file object

        Returns:
        --------
        pd.DataFrame or None
            Loaded dataframe if successful, None otherwise

        Business Impact:
        ---------------
        Failed data loading means no analysis can be performed.
        This function provides clear feedback about what went wrong.
        """
        try:
            if uploaded_file is not None:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                else:
                    st.error("Unsupported file format. Please upload CSV or Excel files.")
                    return None
            elif file_path:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                else:
                    st.error("Unsupported file format. Please use CSV or Excel files.")
                    return None
            else:
                st.error("No file provided for loading.")
                return None

            DataLoader._validate_columns(df)

            return df

        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
            return None
        except pd.errors.EmptyDataError:
            st.error("The file is empty. Please provide a file with data.")
            return None
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None

    @staticmethod
    def _validate_columns(df: pd.DataFrame) -> None:
        """
        Validate that all required business columns exist in the dataset.

        Parameters:
        -----------
        df : pd.DataFrame
            The loaded dataframe to validate

        Raises:
        -------
        ValueError
            If required columns are missing

        Business Impact:
        ---------------
        Missing columns prevent business analysis. This validation
        ensures we catch structural issues early before processing.
        """
        missing_cols = set(DataLoader.REQUIRED_COLUMNS) - set(df.columns)

        if missing_cols:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_cols)}. "
                f"Expected columns: {', '.join(DataLoader.REQUIRED_COLUMNS)}"
            )

    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> dict:
        """
        Generate a quick summary of the loaded dataset.

        Parameters:
        -----------
        df : pd.DataFrame
            The dataset to summarize

        Returns:
        --------
        dict
            Summary statistics including row count, date range, etc.

        Business Impact:
        ---------------
        Provides immediate visibility into data scope and coverage,
        helping analysts understand what time period and volume they're working with.
        """
        summary = {
            'total_records': len(df),
            'columns': list(df.columns),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
        }

        if 'Order_Date' in df.columns:
            try:
                dates = pd.to_datetime(df['Order_Date'], errors='coerce')
                summary['date_range'] = f"{dates.min()} to {dates.max()}"
                summary['date_span_days'] = (dates.max() - dates.min()).days
            except:
                summary['date_range'] = "Unable to parse dates"

        return summary
