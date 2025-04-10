"""
Price Prediction API Endpoints
----------------------------
API endpoints for price prediction.

Author: Haseeb
Version: 1.0
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List

# Import services
from services.price_prediction_service import get_price_prediction

# Import models
from models.price_prediction_model import PricePredictionResponse

router = APIRouter()


@router.get("/price-prediction", response_model=PricePredictionResponse)
async def get_product_price_prediction(product: str = Query(..., description="Product name")):
    """
    Get price prediction for a specific product.

    Args:
        product: Name of the product

    Returns:
        Price prediction response
    """
    try:
        prediction = get_price_prediction(product)
        if not prediction:
            raise HTTPException(status_code=404, detail=f"Price prediction for '{product}' not found")
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))