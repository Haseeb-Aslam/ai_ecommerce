"""
Data Service
-----------
Service for accessing stored product data.

Author: Haseeb
Version: 1.0
"""

import os
import csv
import logging
import yaml
import pandas as pd
from typing import Dict, List, Optional, Any

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
database_config = config.get("database", {})


def get_all_products(limit: int = 10, offset: int = 0, search: Optional[str] = None) -> List[Dict]:
    """
    Get a list of products.

    Args:
        limit: Maximum number of products to return
        offset: Number of products to skip
        search: Search term to filter products

    Returns:
        List of products
    """
    try:
        all_products = []

        # In a real implementation, this would query a database
        # For this example, we'll read CSV files in the data directory
        csv_path = database_config.get("csv_path", "./data/")

        # List all CSV files in the data directory
        for filename in os.listdir(csv_path):
            if not filename.endswith('.csv'):
                continue

            file_path = os.path.join(csv_path, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Apply search filter if provided
                if search:
                    df = df[df['product_name'].str.contains(search, case=False, na=False)]

                # Convert DataFrame to list of dictionaries
                for _, row in df.iterrows():
                    product = {
                        "product_id": row['product_id'],
                        "product_name": row['product_name'],
                        "price": float(row['price']),
                        "rating": float(row['rating']),
                        "num_reviews": int(row['num_reviews']),
                        "reviews": row['reviews'].split(';') if isinstance(row['reviews'], str) else []
                    }
                    all_products.append(product)

            except Exception as e:
                logger.error(f"Error reading CSV file {filename}: {e}")

        # Apply pagination
        paginated_products = all_products[offset:offset + limit]

        return paginated_products

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return []


def get_product_by_name(name: str) -> Optional[Dict]:
    """
    Get details for a specific product by name.

    Args:
        name: Name of the product

    Returns:
        Product data
    """
    try:
        # In a real implementation, this would query a database
        # For this example, we'll search CSV files in the data directory
        csv_path = database_config.get("csv_path", "./data/")

        # List all CSV files in the data directory
        for filename in os.listdir(csv_path):
            if not filename.endswith('.csv'):
                continue

            file_path = os.path.join(csv_path, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Find products matching the name
                product_rows = df[df['product_name'].str.contains(name, case=False, na=False)]

                if len(product_rows) > 0:
                    # Return the first matching product
                    row = product_rows.iloc[0]
                    return {
                        "product_id": row['product_id'],
                        "product_name": row['product_name'],
                        "price": float(row['price']),
                        "rating": float(row['rating']),
                        "num_reviews": int(row['num_reviews']),
                        "reviews": row['reviews'].split(';') if isinstance(row['reviews'], str) else []
                    }

            except Exception as e:
                logger.error(f"Error reading CSV file {filename}: {e}")

        return None

    except Exception as e:
        logger.error(f"Error getting product by name {name}: {e}")
        return None


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """
    Get details for a specific product by ID.

    Args:
        product_id: ID of the product

    Returns:
        Product data
    """
    try:
        # In a real implementation, this would query a database
        # For this example, we'll search CSV files in the data directory
        csv_path = database_config.get("csv_path", "./data/")

        # List all CSV files in the data directory
        for filename in os.listdir(csv_path):
            if not filename.endswith('.csv'):
                continue

            file_path = os.path.join(csv_path, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Find product with matching ID
                product_rows = df[df['product_id'] == product_id]

                if len(product_rows) > 0:
                    # Return the matching product
                    row = product_rows.iloc[0]
                    return {
                        "product_id": row['product_id'],
                        "product_name": row['product_name'],
                        "price": float(row['price']),
                        "rating": float(row['rating']),
                        "num_reviews": int(row['num_reviews']),
                        "reviews": row['reviews'].split(';') if isinstance(row['reviews'], str) else []
                    }

            except Exception as e:
                logger.error(f"Error reading CSV file {filename}: {e}")

        return None

    except Exception as e:
        logger.error(f"Error getting product by ID {product_id}: {e}")
        return None