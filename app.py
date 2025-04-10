"""
AI E-commerce Analysis Platform
-------------------------------
Main application entry point.

Author: Haseeb
Version: 1.0
"""

import os
import yaml
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import API routers
from api.product_api import router as product_router
from api.price_prediction_api import router as price_prediction_router
from api.sentiment_api import router as sentiment_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
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

# Create FastAPI app
app = FastAPI(
    title="AI E-commerce Analysis API",
    description="API for e-commerce product analysis including web scraping, sentiment analysis, and price prediction",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": str(e)}
        )


# Include routers
app.include_router(product_router, prefix="/api/v1", tags=["Products"])
app.include_router(price_prediction_router, prefix="/api/v1", tags=["Price Predictions"])
app.include_router(sentiment_router, prefix="/api/v1", tags=["Sentiment Analysis"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to AI E-commerce Analysis API", "version": "1.0.0"}


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8000)
    debug = server_config.get("debug", False)
    reload = server_config.get("reload", False)

    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=reload)