# Quick Reference Guide

## Common Commands

### Installation
```bash
pip install -r requirements.txt
```

### Run Dashboard
```bash
streamlit run app.py
```

### Generate Extended Data
```bash
python data/generate_extended_data.py
```

---

## Project Components at a Glance

### Data Pipeline
```
Load → Clean → Engineer → Analyze → Forecast → Visualize
```

### Key Files
- `app.py` - Main dashboard
- `src/data_loader.py` - Load data
- `src/data_cleaner.py` - Clean data
- `src/feature_engineer.py` - Create features
- `src/analytics.py` - Analyze data
- `src/forecasting.py` - Predict sales

---

## Forecasting Methods Quick Reference

### Moving Average
- **Formula:** Average(Last N months)
- **Best For:** Stable sales
- **Pros:** Simple, quick
- **Cons:** Misses trends

### Exponential Smoothing
- **Formula:** Weighted average (recent = more weight)
- **Best For:** Growing/declining sales
- **Pros:** Captures trends
- **Cons:** Needs decent history

### ARIMA
- **Formula:** AR + I + MA statistical model
- **Best For:** Complex patterns
- **Pros:** Most accurate
- **Cons:** Needs 12+ months data

---

## Data Cleaning Decision Matrix

| Issue | Action | Reason |
|-------|--------|--------|
| Missing Revenue | Recalculate | Qty × Price |
| Missing Quantity | Remove | Can't determine value |
| Missing Price | Remove | Can't determine value |
| Duplicates | Keep first | Prevent double-count |
| Wrong dates | Standardize | Enable time analysis |
| Wrong revenue | Recalculate | Ensure accuracy |

---

## Business Insights Framework

### For Each Analysis, Ask:
1. **What's the pattern?** (Describe what you see)
2. **Why does it matter?** (Business impact)
3. **What should we do?** (Action/recommendation)

### Example:
- **Pattern:** Top 20% products = 80% revenue
- **Impact:** Product concentration risk
- **Action:** Diversify product mix, focus marketing on top products

---

## Interview Soundbites

### Project Summary (30 seconds)
"Sales analytics dashboard with data cleaning, business analysis, and forecasting. Handles messy real-world data, generates actionable insights across products/regions/time, and predicts future sales using three statistical methods."

### Technical Skills (15 seconds)
"Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, Statsmodels. End-to-end pipeline from raw data to interactive dashboard."

### Business Value (15 seconds)
"Transforms data into decisions: inventory planning from forecasts, product strategy from sales analysis, resource allocation from regional performance."

---

## Dashboard Navigation

### Tabs:
1. **Overview** - Executive KPIs
2. **Sales Performance** - Revenue metrics
3. **Products** - Product rankings
4. **Regions** - Geographic analysis
5. **Time Trends** - Temporal patterns
6. **Forecasting** - Future predictions

### Filters:
- Date range
- Region
- Category

---

## Code Snippets for Quick Reference

### Load Data
```python
from src.data_loader import DataLoader
df = DataLoader.load_data('data/sales_data_sample.csv')
```

### Clean Data
```python
from src.data_cleaner import DataCleaner
cleaner = DataCleaner()
df_clean, log = cleaner.clean_data(df)
```

### Engineer Features
```python
from src.feature_engineer import FeatureEngineer
df_enhanced = FeatureEngineer.create_features(df_clean)
```

### Analyze
```python
from src.analytics import SalesAnalytics
analytics = SalesAnalytics(df_enhanced)
performance = analytics.analyze_sales_performance()
```

### Forecast
```python
from src.forecasting import SalesForecaster
forecaster = SalesForecaster(df_enhanced)
result = forecaster.generate_forecast(method='exponential_smoothing', periods=6)
```

---

## Troubleshooting Quick Fixes

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Streamlit command not found"
```bash
pip install streamlit
```

### Dashboard won't start
```bash
cd /path/to/project
streamlit run app.py
```

### Import errors
Make sure you're in project root directory

---

## Resume Bullet Point

**Sales Analytics & Forecasting Dashboard**
- Developed end-to-end Python-based analytics platform processing 5000+ orders with automated data cleaning pipeline handling missing values, duplicates, and calculation errors
- Implemented 3 time-series forecasting methods (Moving Average, Exponential Smoothing, ARIMA) with 95% confidence intervals for revenue prediction
- Built interactive Streamlit dashboard delivering insights across sales performance, product rankings, regional analysis, and customer segmentation
- Achieved actionable insights for inventory planning, product strategy, and resource allocation through multi-dimensional business analysis

---

## Key Metrics to Memorize

- **Modules:** 5 core modules
- **Pipeline Stages:** 6 (Load, Clean, Engineer, Analyze, Forecast, Visualize)
- **Forecasting Methods:** 3
- **Analysis Dimensions:** 6 (Sales, Products, Categories, Regions, Time, Customers)
- **Dashboard Tabs:** 6
- **Technologies:** Python + 6 libraries

---

## One-Liners for Common Questions

**"What's your project?"**
→ "Sales analytics dashboard with forecasting - Python, Pandas, Streamlit."

**"What makes it unique?"**
→ "Real-world data quality handling + explainable forecasting + business-focused insights."

**"What was challenging?"**
→ "Balancing technical complexity with business explainability in forecasting methods."

**"What did you learn?"**
→ "Every data decision needs business justification, not just technical correctness."

**"What's next?"**
→ "Database integration, automated testing, customer churn prediction."

---

Print this for quick reference during interviews!
