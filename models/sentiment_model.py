"""
Sentiment Analysis Data Models
----------------------------
Pydantic models for sentiment analysis.

Author: Haseeb
Version: 1.0
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SentimentCategory(str, Enum):
    """Sentiment categories."""
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class SentimentBase(BaseModel):
    """Base sentiment information."""
    product_name: str = Field(..., description="Name of the product")


class SentimentDB(SentimentBase):
    """Sentiment information as stored in the database."""
    product_id: str = Field(..., description="Unique product identifier")
    sentiment: SentimentCategory = Field(..., description="Overall sentiment category")
    positive_score: float = Field(..., ge=0, le=1, description="Positive sentiment score (0-1)")
    neutral_score: float = Field(..., ge=0, le=1, description="Neutral sentiment score (0-1)")
    negative_score: float = Field(..., ge=0, le=1, description="Negative sentiment score (0-1)")
    top_issues: List[str] = Field(default=[], description="List of top issues/complaints")


class SentimentResponse(SentimentBase):
    """Sentiment information returned in API responses."""
    sentiment: SentimentCategory = Field(..., description="Overall sentiment category")
    top_issues: List[str] = Field(default=[], description="List of top issues/complaints")


class TopIssuesResponse(BaseModel):
    """Top issues response model."""
    product_name: str = Field(..., description="Name of the product")
    top_issues: List[str] = Field(..., description="List of top issues/complaints")