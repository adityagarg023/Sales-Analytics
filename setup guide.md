# Quick Setup Guide

## Getting Started in 5 Minutes

### Step 1: Install Python
Ensure you have Python 3.8 or higher installed:
```bash
python --version
```

If not installed, download from: https://www.python.org/downloads/

---

### Step 2: Install Dependencies

Open terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

**Note:** If you encounter permission issues, use:
```bash
pip install --user -r requirements.txt
```

Or create a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## Troubleshooting

### Problem: "streamlit: command not found"

**Solution:**
```bash
pip install streamlit
```

### Problem: "No module named 'pandas'"

**Solution:**
```bash
pip install pandas numpy matplotlib seaborn statsmodels openpyxl
```

### Problem: Port 8501 already in use

**Solution:** Use a different port:
```bash
streamlit run app.py --server.port 8502
```

### Problem: Import errors

**Solution:** Make sure you're running from the project root directory:
```bash
cd path/to/sales-analytics-dashboard
streamlit run app.py
```

---

## Using the Dashboard

1. **Data Source Selection:**
   - Click "Use Sample Data" to try with pre-loaded data
   - Or click "Upload Your Data" to analyze your own files

2. **Navigation:**
   - Use tabs at the top to switch between analyses
   - Use sidebar filters to slice data

3. **Generating Forecasts:**
   - Go to "Forecasting" tab
   - Select forecasting method
   - Choose forecast horizon
   - Click "Generate Forecast"

---

## Testing with Your Own Data

Your CSV/Excel file must have these columns:
- Order_ID
- Order_Date
- Product
- Category
- Quantity
- Price
- Revenue
- Region
- Customer_Type

Upload via the sidebar, and the dashboard will automatically process it.

---

## Next Steps

1. Explore the sample data to understand features
2. Try different forecasting methods
3. Upload your own data
4. Review the code in `src/` to understand the implementation
5. Check `README.md` for detailed project documentation

---

## Need Help?

- Review the `README.md` for comprehensive documentation
- Check function docstrings in the source code
- Each module has detailed comments explaining business logic

---

## Project Structure Quick Reference

```
app.py                  → Main dashboard (start here)
src/data_loader.py      → Loads and validates data
src/data_cleaner.py     → Cleans messy data
src/feature_engineer.py → Creates analytical features
src/analytics.py        → Business analysis
src/forecasting.py      → Sales predictions
data/                   → Sample datasets
```

---

Happy analyzing!
