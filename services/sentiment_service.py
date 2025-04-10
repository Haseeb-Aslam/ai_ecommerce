"""
Sentiment Analysis Service
------------------------
Service for analyzing customer review sentiment.

Author: Haseeb
Version: 1.0
"""

import os
import csv
import logging
import yaml
from typing import Dict, List, Optional, Any
from collections import Counter
import pandas as pd
# Get price prediction
from services.price_prediction_service import get_price_prediction
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.feature_extraction.text import CountVectorizer

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
sentiment_config = config.get("sentiment_analysis", {})
database_config = config.get("database", {})

# Sentiment analysis model
sentiment_analyzer = None
tokenizer = None
model = None


def load_sentiment_model():
    """Load the sentiment analysis model."""
    global sentiment_analyzer, tokenizer, model

    try:
        model_name = sentiment_config.get("model_name", "distilbert-base-uncased-finetuned-sst-2-english")

        # Load tokenizer and model for classification
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)

        # Initialize sentiment pipeline
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

        logger.info(f"Loaded sentiment model: {model_name}")
        return True
    except Exception as e:
        logger.error(f"Error loading sentiment model: {e}")
        return False


def generate_combined_analysis(output_filename="combined_analysis.csv"):
    """
    Generate a combined CSV with product data, price prediction, and sentiment analysis.

    Args:
        output_filename: Name of the output CSV file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get all product data from CSV files
        products_data = []
        csv_path = database_config.get("csv_path", "./data/")

        # List all CSV files in the data directory
        for filename in os.listdir(csv_path):
            if not filename.endswith('.csv'):
                continue

            file_path = os.path.join(csv_path, filename)
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Process each product
                for _, row in df.iterrows():
                    product_name = row['product_name']

                    # Get sentiment analysis
                    sentiment_result = get_sentiment_by_product_name(product_name)


                    price_prediction = get_price_prediction(product_name)

                    # If both analyses were successful, add to the results
                    if sentiment_result and price_prediction:
                        products_data.append({
                            'product_id': row['product_id'],
                            'product_name': product_name,
                            'price': row['price'],
                            'rating': row['rating'],
                            'sentiment': sentiment_result['sentiment'],
                            'top_issues': ';'.join(sentiment_result['top_issues']),
                            'predicted_price': price_prediction['predicted_price_next_month'],
                            'price_trend': price_prediction['trend']
                        })
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")

        # Write the combined data to a CSV file
        if products_data:
            output_path = os.path.join(csv_path, output_filename)
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['product_id', 'product_name', 'price', 'rating',
                              'sentiment', 'top_issues', 'predicted_price', 'price_trend']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for product in products_data:
                    writer.writerow(product)

            logger.info(f"Combined analysis saved to {output_path}")
            return True
        else:
            logger.warning("No product data to save")
            return False

    except Exception as e:
        logger.error(f"Error generating combined analysis: {e}")
        return False


def extract_key_features(reviews: List[str]) -> Dict[str, int]:
    """
    Extract key product features mentioned in reviews.

    Args:
        reviews: List of review texts

    Returns:
        Dictionary mapping features to their occurrence count
    """
    try:
        # Define key features to look for
        features = {
            "battery life": ["battery", "charge", "power", "battery life"],
            "performance": ["fast", "speed", "performance", "slow", "lag"],
            "display": ["screen", "display", "resolution", "color"],
            "keyboard": ["keyboard", "typing", "keys"],
            "price": ["price", "expensive", "cheap", "cost", "worth"],
            "design": ["design", "sleek", "thin", "light", "weight"],
            "heat": ["hot", "heat", "thermal", "warm", "temperature"],
            "noise": ["noise", "fan", "silent", "quiet", "loud"],
            "quality": ["quality", "build", "premium", "solid"],
            "connectivity": ["ports", "usb", "thunderbolt", "dongle"]
        }

        # Count occurrences of each feature
        feature_counts = {feature: 0 for feature in features}

        for review in reviews:
            review_lower = review.lower()
            for feature, keywords in features.items():
                if any(keyword in review_lower for keyword in keywords):
                    feature_counts[feature] += 1

        # Return non-zero features sorted by count
        return {k: v for k, v in sorted(feature_counts.items(),
                                        key=lambda item: item[1],
                                        reverse=True) if v > 0}
    except Exception as e:
        logger.error(f"Error extracting key features: {e}")
        return {}


def analyze_sentiment(review_text: str) -> Dict:
    """
    Analyze the sentiment of a review text.

    Args:
        review_text: Text of the review

    Returns:
        Dictionary with sentiment analysis results
    """
    global sentiment_analyzer

    if not sentiment_analyzer:
        success = load_sentiment_model()
        if not success:
            return {"label": "NEUTRAL", "score": 0.5}

    try:
        # Simple preprocessing to handle very long reviews
        review_text = review_text[:512]  # Limit to prevent token overflow

        # Get sentiment prediction
        result = sentiment_analyzer(review_text)[0]

        # Map labels to our categories
        label_map = {
            "POSITIVE": "Positive",
            "NEGATIVE": "Negative",
            "NEUTRAL": "Neutral"
        }

        # Map common labels to our format
        label = result["label"]
        if "POSITIVE" in label:
            category = "Positive"
        elif "NEGATIVE" in label:
            category = "Negative"
        else:
            category = "Neutral"

        return {
            "label": category,
            "score": result["score"]
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"label": "Neutral", "score": 0.5}


def extract_issues(reviews: List[str]) -> List[str]:
    """
    Extract common issues/complaints from reviews.

    Args:
        reviews: List of review texts

    Returns:
        List of common issues/complaints
    """
    if not reviews:
        return []

    try:
        # Initialize a count vectorizer to extract common phrases
        vectorizer = CountVectorizer(
            ngram_range=(2, 3),  # Use bigrams and trigrams
            stop_words='english',
            min_df=2,  # Only phrases that appear at least twice
            max_features=20  # Limit to top 20 features
        )

        # Fit the vectorizer on the reviews
        X = vectorizer.fit_transform(reviews)

        # Get feature names (phrases)
        feature_names = vectorizer.get_feature_names_out()

        # Count the occurrences of each phrase
        feature_counts = X.sum(axis=0).A1

        # Create a dictionary of phrases and their counts
        phrase_counts = {feature_names[i]: feature_counts[i] for i in range(len(feature_names))}

        # Sort phrases by count in descending order
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)

        # Return the top 5 phrases
        return [phrase for phrase, count in sorted_phrases[:5]]

    except Exception as e:
        logger.error(f"Error extracting issues: {e}")
        return []


def load_product_reviews(product_name: str) -> List[Dict]:
    """
    Load reviews for a specific product.

    Args:
        product_name: Name of the product

    Returns:
        List of reviews
    """
    reviews = []

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
                product_rows = df[df['product_name'].str.contains(product_name, case=False, na=False)]

                if len(product_rows) > 0:
                    # Extract reviews
                    for _, row in product_rows.iterrows():
                        review_texts = row['reviews'].split(';') if isinstance(row['reviews'], str) else []
                        reviews.extend(review_texts)
            except Exception as e:
                logger.error(f"Error reading CSV file {filename}: {e}")

        return reviews

    except Exception as e:
        logger.error(f"Error loading product reviews: {e}")
        return []



def get_sentiment_by_product_name(product_name: str) -> Optional[Dict]:
    """
    Get sentiment analysis for a specific product.

    Args:
        product_name: Name of the product

    Returns:
        Sentiment analysis response
    """
    try:
        # Load reviews for the product
        reviews = load_product_reviews(product_name)

        if not reviews:
            logger.warning(f"No reviews found for product: {product_name}")
            return None

        # Analyze sentiment for each review
        sentiments = [analyze_sentiment(review) for review in reviews]

        # Count sentiment categories
        categories = [s["label"] for s in sentiments]
        category_counts = Counter(categories)

        # Determine overall sentiment
        if category_counts.get("Positive", 0) > category_counts.get("Negative", 0):
            overall_sentiment = "Positive"
        elif category_counts.get("Negative", 0) > category_counts.get("Positive", 0):
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"

        # Extract key features from reviews
        feature_counts = extract_key_features(reviews)

        # Extract top issues using both methods
        top_issues_ngrams = extract_issues(reviews)

        # Combine the results
        top_issues = list(feature_counts.keys())[:3]  # Top 3 features
        if top_issues_ngrams:
            # Add any unique ngrams not already in top_issues
            for issue in top_issues_ngrams:
                if not any(issue in key for key in top_issues):
                    top_issues.append(issue)
                    if len(top_issues) >= 5:  # Limit to top 5
                        break

        return {
            "product_name": product_name,
            "sentiment": overall_sentiment,
            "top_issues": top_issues
        }

    except Exception as e:
        logger.error(f"Error getting sentiment for product {product_name}: {e}")
        return None


def get_top_issues(product_name: str) -> Optional[Dict]:
    """
    Get top issues/complaints for a specific product.

    Args:
        product_name: Name of the product

    Returns:
        Top issues response
    """
    try:
        # Load reviews for the product
        reviews = load_product_reviews(product_name)

        if not reviews:
            logger.warning(f"No reviews found for product: {product_name}")
            return None

        # First, identify negative reviews
        negative_reviews = []
        for review in reviews:
            sentiment = analyze_sentiment(review)
            if sentiment["label"] == "Negative":
                negative_reviews.append(review)

        # If no negative reviews found, try using key feature extraction
        if not negative_reviews:
            # Extract key features from all reviews
            feature_counts = extract_key_features(reviews)

            # Get issue-related features
            issue_features = ["battery life", "heat", "price", "performance", "keyboard"]
            top_issues = [feature for feature in issue_features if feature in feature_counts]

            if not top_issues:
                top_issues = ["No significant issues identified"]
        else:
            # Extract issues from negative reviews
            top_issues = extract_issues(negative_reviews)

            # If no phrases extracted, use keyword approach
            if not top_issues:
                # Define issue keywords
                issue_keywords = {
                    "battery issues": ["battery", "charge", "power", "drain"],
                    "overheating": ["hot", "heat", "thermal", "temperature"],
                    "price concerns": ["expensive", "overpriced", "costly"],
                    "performance problems": ["slow", "lag", "freeze", "crash"],
                    "keyboard issues": ["keyboard", "keys", "typing"]
                }

                # Check for issues in negative reviews
                issue_counts = {issue: 0 for issue in issue_keywords}
                for review in negative_reviews:
                    review_lower = review.lower()
                    for issue, keywords in issue_keywords.items():
                        if any(keyword in review_lower for keyword in keywords):
                            issue_counts[issue] += 1

                # Get top issues by count
                top_issues = [issue for issue, count in
                              sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
                              if count > 0][:5]

                if not top_issues:
                    top_issues = ["No specific issues identified"]

        return {
            "product_name": product_name,
            "top_issues": top_issues
        }

    except Exception as e:
        logger.error(f"Error getting top issues for product {product_name}: {e}")
        return None