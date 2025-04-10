"""
Price Prediction Data Models
-------------------------
Pydantic models for price prediction.

Author: Haseeb
Version: 1.0
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PricePredictionBase(BaseModel):
    """Base price prediction information."""
    product_name: str = Field(..., description="Name of the product")


class PricePredictionDB(PricePredictionBase):
    """Price prediction information as stored in the database."""
    product_id: str = Field(..., description="Unique product identifier")
    current_price: float = Field(..., description="Current product price")
    prediction_date: datetime = Field(..., description="Date when prediction was made")
    predicted_prices: List[float] = Field(..., description="List of predicted prices")
    prediction_dates: List[datetime] = Field(..., description="List of dates for predictions")


class PricePredictionResponse(PricePredictionBase):
    """Price prediction information returned in API responses."""
    current_price: float = Field(..., description="Current product price")
    predicted_price_next_month: float = Field(..., description="Predicted price in one month")
    trend: str = Field(..., description="Price trend (up, down, stable)")