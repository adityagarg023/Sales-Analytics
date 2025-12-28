"""
Sales Analytics & Forecasting Dashboard - Source Package
========================================================

This package contains all core modules for sales data analysis and forecasting.

Modules:
- data_loader: Data loading and validation
- data_cleaner: Data quality and cleaning operations
- feature_engineer: Feature creation and transformation
- analytics: Business intelligence and analysis
- forecasting: Time-series forecasting methods
"""

__version__ = "1.0.0"
__author__ = "Data Analytics Team"

from .data_loader import DataLoader
from .data_cleaner import DataCleaner
from .feature_engineer import FeatureEngineer
from .analytics import SalesAnalytics
from .forecasting import SalesForecaster

__all__ = [
    'DataLoader',
    'DataCleaner',
    'FeatureEngineer',
    'SalesAnalytics',
    'SalesForecaster'
]
