"""
Product Data Models
-----------------
Pydantic models for product data.

Author: Haseeb
Version: 1.0
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ProductBase(BaseModel):
    """Base product information."""
    product_name: str = Field(..., description="Name of the product")


class ProductDB(ProductBase):
    """Product information as stored in the database."""
    product_id: str = Field(..., description="Unique product identifier")
    price: float = Field(..., description="Current product price")
    rating: float = Field(..., ge=0, le=5, description="Product rating (0-5)")
    num_reviews: int = Field(..., ge=0, description="Number of product reviews")
    reviews: List[str] = Field(default=[], description="List of product reviews")


class ProductResponse(ProductDB):
    """Product information returned in API responses."""
    pass


class Review(BaseModel):
    """Customer review information."""
    text: str = Field(..., description="Review text")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Review rating (0-5)")


class ScrapingRequest(BaseModel):
    """Request to start a scraping job."""
    search_term: str = Field(..., description="Product to search for")
    max_products: int = Field(10, ge=1, le=100, description="Maximum number of products to scrape per site")


class ScrapingJobResponse(BaseModel):
    """Response with scraping job information."""
    job_id: str = Field(..., description="Unique job identifier")
    search_term: str = Field(..., description="Product search term")
    status: str = Field(..., description="Job status (pending, running, completed, failed)")
    progress: Optional[float] = Field(None, description="Job progress percentage")
    message: Optional[str] = Field(None, description="Additional job information")