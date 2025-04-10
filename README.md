# AI E-commerce Analysis Platform

A comprehensive e-commerce data analysis platform with web scraping, AI-powered sentiment analysis, and price prediction capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Testing](#testing)

## Overview

This project implements an end-to-end solution for e-commerce product analysis with three main components:

1. **Web Scraping**: Collects product data from Amazon and eBay including names, prices, ratings, and reviews
2. **AI Analysis**: Performs sentiment analysis on customer reviews and predicts future product prices
3. **REST API**: Provides interfaces to access collected data, sentiment insights, and price predictions

## Features

### Part 1: Web Scraping
- Scrapes multiple e-commerce platforms (Amazon, eBay)
- Extracts comprehensive product details
- Implements rotating user agents and proxy handling
- Respects robots.txt and website terms of service
- Saves data in CSV format

### Part 2: AI Analysis
- **Sentiment Analysis**:
  - Classifies reviews as Positive, Neutral, or Negative
  - Extracts common complaints/praises from reviews
  - Identifies key product issues
- **Price Prediction**:
  - Time series forecasting of product prices
  - Price trend identification
  - Competitive pricing analysis

### Part 3: REST API
- Fast and responsive FastAPI-based endpoints
- Easy-to-use query interface
- Background processing for long-running tasks
- Comprehensive error handling

## Project Structure

```
ai_ecommerce/
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── product_api.py     # Product data endpoints
│   ├── price_prediction_api.py # Price prediction endpoints
│   └── sentiment_api.py   # Sentiment analysis endpoints
├── models/                # Data models/schemas
│   ├── __init__.py
│   ├── product_model.py
│   ├── sentiment_model.py
│   └── price_prediction_model.py
├── services/              # Business logic implementation
│   ├── __init__.py
│   ├── scraper_service.py # Web scraping implementation
│   ├── sentiment_service.py # Sentiment analysis implementation
│   ├── price_prediction_service.py # Price prediction implementation
│   └── data_service.py    # Data access layer
├── app.py                 # Main application entry point
├── config.yaml            # Configuration settings
└── requirements.txt       # Project dependencies
```

## Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/ai-ecommerce.git
   cd ai_ecommerce
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```


## Usage

1. Start the server
   ```
   python app.py
   ```

2. Access the API at `http://localhost:8001/docs`

3. Use API endpoints:
   - Start a scraping job: `POST /api/v1/scrape`
   - Get product details: `GET /api/v1/product?name=ProductName`
   - Get sentiment analysis: `GET /api/v1/sentiment?product_name=ProductName`
   - Get price prediction: `GET /api/v1/price-prediction?product=ProductName`

## API Documentation

Once the server is running, you can access the auto-generated API documentation at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Key Endpoints

#### Product Endpoints
- `GET /api/v1/products` - List all products
- `GET /api/v1/product?name={name}` - Get product by name
- `GET /api/v1/product/{product_id}` - Get product by ID
- `POST /api/v1/scrape` - Start a scraping job
- `GET /api/v1/scrape/{job_id}` - Check scraping job status

#### Sentiment Analysis Endpoints
- `GET /api/v1/generate-analysis` - Get analysis in csv file
- `GET /api/v1/sentiment?product_name={name}` - Get sentiment analysis
- `GET /api/v1/top-issues?product={name}` - Get top issues/complaints

#### Price Prediction Endpoints
- `GET /api/v1/price-prediction?product={name}` - Get price prediction

## Configuration

All configuration settings are in the `config.yaml` file:

- **Server**: Configure host, port, and debug mode
- **Database**: Set up storage options (CSV path or database connections)
- **Scraper**: Configure scraping behavior, platforms, and request limits
- **AI Models**: Set model parameters for sentiment analysis and price prediction

## Testing

Run tests with pytest:

```
pytest
```

This will execute all unit tests and validate the core functionality of the application.

---
