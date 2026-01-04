import pandas as pd
import numpy as np
import warnings
from typing import Dict, Tuple
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')


class SalesForecaster:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.monthly_revenue = None
        self.forecast_results = None

    def prepare_time_series(self) -> pd.Series:
        self.df['Order_Date'] = pd.to_datetime(self.df['Order_Date'])
        self.df['Year_Month'] = self.df['Order_Date'].dt.to_period('M')

        self.monthly_revenue = self.df.groupby('Year_Month')['Revenue'].sum().sort_index()

        return self.monthly_revenue

    def moving_average_forecast(self, window: int = 3, periods: int = 6) -> Dict:
        if self.monthly_revenue is None:
            self.prepare_time_series()

        historical_values = self.monthly_revenue.values
        predictions = []

        for i in range(periods):
            if i == 0:
                last_n = historical_values[-window:]
            else:
                last_n = list(historical_values[-window:]) + predictions[-min(i, window):]
                last_n = last_n[-window:]

            pred = np.mean(last_n)
            predictions.append(pred)

        last_date = self.monthly_revenue.index[-1].to_timestamp()
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=periods,
            freq='MS'
        )

        forecast_series = pd.Series(predictions, index=future_dates)

        std_dev = np.std(historical_values[-window:])
        lower_bound = forecast_series - (1.96 * std_dev)
        upper_bound = forecast_series + (1.96 * std_dev)

        return {
            'method': 'Moving Average',
            'forecast': forecast_series,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'explanation': f"Forecast based on average of last {window} months. "
                          f"Assumes stable sales pattern without strong trends.",
            'confidence': 'Medium - Best for stable markets',
            'parameters': {'window': window}
        }

    def exponential_smoothing_forecast(self, periods: int = 6) -> Dict:
        if self.monthly_revenue is None:
            self.prepare_time_series()

        if len(self.monthly_revenue) < 6:
            return {
                'error': 'Insufficient data',
                'message': 'Need at least 6 months of historical data for reliable exponential smoothing'
            }

        try:
            model = ExponentialSmoothing(
                self.monthly_revenue.values,
                trend='add',
                seasonal=None,
                initialization_method="estimated"
            )
            fitted_model = model.fit()

            forecast_values = fitted_model.forecast(steps=periods)

            last_date = self.monthly_revenue.index[-1].to_timestamp()
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(months=1),
                periods=periods,
                freq='MS'
            )

            forecast_series = pd.Series(forecast_values, index=future_dates)

            residuals = fitted_model.fittedvalues - self.monthly_revenue.values
            std_dev = np.std(residuals)

            lower_bound = forecast_series - (1.96 * std_dev)
            upper_bound = forecast_series + (1.96 * std_dev)

            return {
                'method': 'Exponential Smoothing',
                'forecast': forecast_series,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'explanation': "Forecast using weighted average with more importance on recent months. "
                              "Captures trend direction (growth/decline). "
                              "Confidence intervals show 95% prediction range.",
                'confidence': 'High - Recommended for trending data',
                'parameters': {
                    'trend': 'additive',
                    'seasonal': None
                }
            }

        except Exception as e:
            return {
                'error': str(e),
                'message': 'Exponential smoothing failed - data may be too irregular'
            }

    def arima_forecast(self, order: Tuple[int, int, int] = (1, 1, 1), periods: int = 6) -> Dict:
        if self.monthly_revenue is None:
            self.prepare_time_series()

        if len(self.monthly_revenue) < 12:
            return {
                'error': 'Insufficient data',
                'message': 'ARIMA requires at least 12 months of historical data'
            }

        try:
            model = ARIMA(self.monthly_revenue.values, order=order)
            fitted_model = model.fit()

            forecast_result = fitted_model.forecast(steps=periods)
            forecast_values = forecast_result

            last_date = self.monthly_revenue.index[-1].to_timestamp()
            future_dates = pd.date_range(
                start=last_date + pd.DateOffset(months=1),
                periods=periods,
                freq='MS'
            )

            forecast_series = pd.Series(forecast_values, index=future_dates)

            residuals = fitted_model.resid
            std_dev = np.std(residuals)

            lower_bound = forecast_series - (1.96 * std_dev)
            upper_bound = forecast_series + (1.96 * std_dev)

            return {
                'method': 'ARIMA',
                'forecast': forecast_series,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'explanation': f"Statistical forecast using ARIMA{order}. "
                              f"Model analyzes historical patterns, trends, and cycles. "
                              f"95% confidence interval provided.",
                'confidence': 'Very High - Best for long-term planning',
                'parameters': {
                    'order': order,
                    'p': f"{order[0]} (past values used)",
                    'd': f"{order[1]} (trend removal)",
                    'q': f"{order[2]} (error correction)"
                }
            }

        except Exception as e:
            return {
                'error': str(e),
                'message': 'ARIMA forecast failed - trying simpler model recommended'
            }

    def generate_forecast(self, method: str = 'exponential_smoothing', periods: int = 6) -> Dict:
        self.prepare_time_series()

        if method == 'moving_average':
            result = self.moving_average_forecast(periods=periods)
        elif method == 'exponential_smoothing':
            result = self.exponential_smoothing_forecast(periods=periods)
        elif method == 'arima':
            result = self.arima_forecast(periods=periods)
        else:
            return {
                'error': 'Invalid method',
                'message': 'Choose: moving_average, exponential_smoothing, or arima'
            }

        if 'error' not in result:
            result['historical_data'] = self.monthly_revenue
            result['forecast_period_months'] = periods

        self.forecast_results = result
        return result

    def get_forecast_summary(self) -> Dict:
        if self.forecast_results is None or 'error' in self.forecast_results:
            return {'error': 'No valid forecast available'}

        forecast = self.forecast_results['forecast']
        historical = self.forecast_results['historical_data']

        total_forecast_revenue = forecast.sum()
        avg_monthly_forecast = forecast.mean()
        avg_historical = historical[-6:].mean()

        if avg_historical > 0:
            pct_change = ((avg_monthly_forecast - avg_historical) / avg_historical) * 100
        else:
            pct_change = 0

        trend = 'GROWTH' if pct_change > 5 else 'DECLINE' if pct_change < -5 else 'STABLE'

        return {
            'total_forecast_revenue': total_forecast_revenue,
            'avg_monthly_forecast': avg_monthly_forecast,
            'avg_historical_last_6m': avg_historical,
            'change_from_historical_%': pct_change,
            'trend': trend,
            'interpretation': self._interpret_forecast(pct_change, trend)
        }

    @staticmethod
    def _interpret_forecast(pct_change: float, trend: str) -> str:
        if trend == 'GROWTH':
            return (
                f"Sales forecast shows {abs(pct_change):.1f}% growth. "
                f"RECOMMENDATIONS: Increase inventory, expand capacity, invest in marketing. "
                f"Monitor fulfillment capabilities to handle increased demand."
            )
        elif trend == 'DECLINE':
            return (
                f"Sales forecast shows {abs(pct_change):.1f}% decline. "
                f"RECOMMENDATIONS: Review pricing strategy, investigate competition, "
                f"enhance marketing efforts. Consider cost reduction measures."
            )
        else:
            return (
                f"Sales forecast shows stable pattern ({abs(pct_change):.1f}% change). "
                f"RECOMMENDATIONS: Maintain current operations, focus on efficiency, "
                f"explore new growth opportunities."
            )
