"""
Sentiment Analysis API Endpoints
-------------------------------
API endpoints for sentiment analysis.

Author: Haseeb
Version: 1.0
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List

# Import services
from services.sentiment_service import get_sentiment_by_product_name, get_top_issues

# Import models
from models.sentiment_model import SentimentResponse, TopIssuesResponse

from services.sentiment_service import generate_combined_analysis

router = APIRouter()


@router.post("/generate-analysis")
async def generate_analysis():
    """
    Generate combined sentiment and price prediction analysis CSV.
    """
    try:
        result = generate_combined_analysis()
        if result:
            return {"message": "Analysis completed successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to generate analysis")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment", response_model=SentimentResponse)
async def get_sentiment(product_name: str = Query(..., description="Product name")):
    """
    Get sentiment analysis for a specific product.

    Args:
        product_name: Name of the product

    Returns:
        Sentiment analysis response
    """
    try:
        sentiment = get_sentiment_by_product_name(product_name)
        if not sentiment:
            raise HTTPException(status_code=404, detail=f"Sentiment analysis for '{product_name}' not found")
        return sentiment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-issues", response_model=TopIssuesResponse)
async def get_product_top_issues(product: str = Query(..., description="Product name")):
    """
    Get top issues/complaints for a specific product.

    Args:
        product: Name of the product

    Returns:
        Top issues response
    """
    try:
        issues = get_top_issues(product)
        if not issues:
            raise HTTPException(status_code=404, detail=f"No issues found for '{product}'")
        return issues
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))