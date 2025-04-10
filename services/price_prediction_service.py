"""
Price Prediction Service
----------------------
Service for predicting future product prices.

Author: Haseeb
Version: 1.0
"""

import os
import logging
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from prophet import Prophet
import matplotlib.pyplot as plt

# Configure logging
logger = logging.getLogger(__name__)


# Load configuration
def load_config():
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


config = load_config()
price_config = config.get("price_prediction", {})
database_config = config.get("database", {})


def analyze_competitive_pricing(product_data: List[Dict]) -> Dict[str, List[str]]:
    """
    Analyze which products are competitively priced and which are overpriced.

    Args:
        product_data: List of product dictionaries with price information

    Returns:
        Dictionary with competitive and overpriced product lists
    """
    try:
        # Group products by similar characteristics (like model year)
        product_groups = {}

        for product in product_data:
            # Extract key characteristics to group similar products
            if "MacBook Air" in product["product_name"]:
                if "M2" in product["product_name"]:
                    group = "MacBook Air M2"
                elif "M3" in product["product_name"]:
                    group = "MacBook Air M3"
                else:
                    group = "MacBook Air Other"
            else:
                group = "Other"

            if group not in product_groups:
                product_groups[group] = []

            product_groups[group].append(product)

        # Analyze each group to find competitive and overpriced products
        competitive_products = []
        overpriced_products = []

        for group, products in product_groups.items():
            if len(products) <= 1:
                continue

            # Calculate average price for the group
            prices = [p["price"] for p in products]
            avg_price = sum(prices) / len(prices)

            # Identify competitive and overpriced products
            for product in products:
                name = product["product_name"]
                price = product["price"]

                # If price is more than 15% above average, consider it overpriced
                if price > avg_price * 1.15:
                    overpriced_products.append(name)
                # If price is below or at average, consider it competitive
                elif price <= avg_price:
                    competitive_products.append(name)

        return {
            "competitive": competitive_products,
            "overpriced": overpriced_products
        }
    except Exception as e:
        logger.error(f"Error analyzing competitive pricing: {e}")
        return {"competitive": [], "overpriced": []}


def generate_dummy_price_history(current_price: float, num_days: int = 90) -> pd.DataFrame:
    """
    Generate dummy price history data for a product.
    In a real implementation, this would be replaced with actual historical data.

    Args:
        current_price: Current price of the product
        num_days: Number of days of history to generate

    Returns:
        DataFrame with price history
    """
    # Generate dates from past to present
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Generate random prices with a trend
    base_price = current_price * 0.8  # Start at 80% of current price
    prices = []

    for i in range(len(dates)):
        # Add trend (gradual increase)
        trend = (current_price - base_price) * (i / len(dates))

        # Add seasonality (weekly pattern)
        day_of_week = dates[i].dayofweek
        if day_of_week in [0, 6]:  # Weekend discount
            seasonality = -0.03 * base_price
        else:
            seasonality = 0.01 * base_price * (day_of_week / 5)

        # Add noise
        noise = np.random.normal(0, 0.01 * base_price)

        # Combine components
        price = base_price + trend + seasonality + noise
        prices.append(max(price, base_price * 0.7))  # Ensure price doesn't drop too low

    # Create DataFrame
    df = pd.DataFrame({
        'ds': dates,
        'y': prices
    })

    return df


def train_prophet_model(price_history: pd.DataFrame) -> Prophet:
    """
    Train a Prophet model on price history data.

    Args:
        price_history: DataFrame with price history (columns: ds, y)

    Returns:
        Trained Prophet model
    """
    try:
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )

        # Fit model
        model.fit(price_history)
        logger.info("Prophet model trained successfully")
        return model

    except Exception as e:
        logger.error(f"Error training Prophet model: {e}")
        return None


def predict_prices(model: Prophet, periods: int = 30) -> pd.DataFrame:
    """
    Predict future prices using a trained Prophet model.

    Args:
        model: Trained Prophet model
        periods: Number of days to forecast

    Returns:
        DataFrame with price predictions
    """
    try:
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods)

        # Make predictions
        forecast = model.predict(future)

        return forecast

    except Exception as e:
        logger.error(f"Error predicting prices: {e}")
        return None


def get_price_prediction(product_name: str) -> Optional[Dict]:
    """
    Get price prediction for a specific product.

    Args:
        product_name: Name of the product

    Returns:
        Price prediction response
    """
    try:
        # In a real implementation, this would query a database for the product
        # For this example, we'll search CSV files in the data directory
        csv_path = database_config.get("csv_path", "./data/")

        current_price = 0.0
        product_found = False

        # List all CSV files in the data directory
        for filename in os.listdir(csv_path):
            if not filename.endswith('.csv'):
                continue

            file_path = os.path.join(csv_path, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Find products matching the name
                product_rows = df[df['product_name'].str.contains(product_name, case=False, na=False)]

                if len(product_rows) > 0:
                    # Use the first matching product
                    current_price = float(product_rows.iloc[0]['price'])
                    product_found = True
                    break

            except Exception as e:
                logger.error(f"Error reading CSV file {filename}: {e}")

        if not product_found:
            logger.warning(f"Product not found: {product_name}")
            return None

        # Generate dummy price history
        # In a real implementation, this would be replaced with actual historical data
        forecast_periods = price_config.get("forecast_periods", 30)
        price_history = generate_dummy_price_history(current_price)

        # Train model
        model = train_prophet_model(price_history)
        if model is None:
            return None

        # Predict future prices
        forecast = predict_prices(model, periods=forecast_periods)
        if forecast is None:
            return None

        # Extract prediction for next month
        last_date = forecast['ds'].max()
        next_month = last_date - timedelta(days=last_date.day - 1)
        predicted_price = forecast[forecast['ds'] >= next_month]['yhat'].mean()

        # Determine trend
        if predicted_price > current_price * 1.02:
            trend = "up"
        elif predicted_price < current_price * 0.98:
            trend = "down"
        else:
            trend = "stable"

        # Generate plot for debugging/visualization
        if not os.path.exists('plots'):
            os.makedirs('plots')

        fig = model.plot(forecast)
        plt.title(f'Price Forecast for {product_name}')
        plt.savefig(f'plots/{product_name.replace(" ", "_")}_forecast.png')
        plt.close(fig)

        return {
            "product_name": product_name,
            "current_price": current_price,
            "predicted_price_next_month": round(predicted_price, 2),
            "trend": trend
        }

    except Exception as e:
        logger.error(f"Error getting price prediction for product {product_name}: {e}")
        return None