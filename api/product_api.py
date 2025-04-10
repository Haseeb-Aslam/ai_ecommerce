"""
Product API Endpoints
--------------------
API endpoints for product data.

Author: Haseeb
Version: 1.0
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional

# Import services
from services.scraper_service import start_scraping_job, get_scraping_job_status
from services.data_service import get_product_by_name, get_all_products, get_product_by_id

# Import models
from models.product_model import ProductResponse, ScrapingJobResponse, ScrapingRequest

router = APIRouter()


@router.get("/products", response_model=List[ProductResponse])
async def get_products(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        search: Optional[str] = None
):
    """
    Get a list of products.

    Args:
        limit: Maximum number of products to return
        offset: Number of products to skip
        search: Search term to filter products

    Returns:
        List of product responses
    """
    try:
        products = get_all_products(limit, offset, search)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product", response_model=ProductResponse)
async def get_product(name: str = Query(..., description="Product name")):
    """
    Get details for a specific product by name.

    Args:
        name: Name of the product

    Returns:
        Product response
    """
    try:
        product = get_product_by_name(name)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{name}' not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product_by_id_endpoint(product_id: str):
    """
    Get details for a specific product by ID.

    Args:
        product_id: ID of the product

    Returns:
        Product response
    """
    try:
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape", response_model=ScrapingJobResponse)
async def start_scrape(request: ScrapingRequest):
    """
    Start a scraping job.

    Args:
        request: Scraping request containing search term and max products

    Returns:
        Scraping job response with job ID
    """
    try:
        job_response = start_scraping_job(request.search_term, request.max_products)
        return job_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scrape/{job_id}", response_model=ScrapingJobResponse)
async def get_scraping_status(job_id: str):
    """
    Get the status of a scraping job.

    Args:
        job_id: ID of the scraping job

    Returns:
        Scraping job response with status
    """
    try:
        job_response = get_scraping_job_status(job_id)
        if not job_response:
            raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found")
        return job_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))