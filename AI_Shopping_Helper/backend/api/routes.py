"""
API routes for the AI Shopping Helper
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from backend.scraping.product_scraper import ProductScraper
from backend.ai_scoring.quality_scorer import QualityScorer
from backend.database.product_db import ProductDatabase
from backend.utils.image_processor import ImageProcessor
from backend.ai.recommendations import recommendation_engine
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components
scraper = ProductScraper()
scorer = QualityScorer()
db = ProductDatabase()
image_processor = ImageProcessor()

# Pydantic models for request/response
class ProductAnalysisRequest(BaseModel):
    url: Optional[str] = None
    image: Optional[str] = None

class ProductInfo(BaseModel):
    name: str
    price: float
    quality_score: float
    final_score: float
    rating: float
    specs: dict

class Alternative(BaseModel):
    id: int
    name: str
    category: str
    price: float
    rating: float
    platform: str
    url: str
    quality_score: float
    final_score: float
    image_url: Optional[str] = None

class AnalysisResponse(BaseModel):
    original_product: ProductInfo
    alternatives: List[Alternative]
    savings: dict
    recommendation: Optional[Alternative]

class FeedbackRequest(BaseModel):
    product_id: int
    rating: int
    helpful: bool
    comments: Optional[str] = None

class RecommendationResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    rating: float
    platform: str
    similarity_score: float
    description_preview: str

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_product(request: ProductAnalysisRequest):
    """
    Analyze a product from URL or image and find alternatives
    """
    try:
        # Handle URL input
        if request.url:
            logger.info(f"Analyzing product from URL: {request.url}")
            
            # Scrape product details
            product_data = scraper.scrape_product(request.url)
            if not product_data:
                raise HTTPException(status_code=400, detail="Could not extract product data from URL")
            
        # Handle image input
        elif request.image:
            logger.info("Analyzing product from image")
            
            # Process image to extract product info
            product_data = image_processor.extract_product_info(request.image)
            if not product_data:
                raise HTTPException(status_code=400, detail="Could not extract product data from image")
        
        else:
            raise HTTPException(status_code=400, detail="Either URL or image must be provided")
        
        # Calculate quality score
        quality_score = scorer.calculate_quality_score(
            product_data['specs'], 
            product_data['category']
        )
        
        # Calculate final score with ratings
        final_score = scorer.calculate_final_score(
            quality_score, 
            product_data.get('rating', 4.0)
        )
        
        # Find alternatives
        alternatives = db.find_alternatives(
            category=product_data['category'],
            target_score=final_score,
            max_price=product_data.get('price', 0) * 0.8  # 20% less than original
        )
        
        # Calculate potential savings
        original_price = product_data.get('price', 0)
        best_alternative = alternatives[0] if alternatives else None
        savings = original_price - best_alternative['price'] if best_alternative else 0
        savings_percentage = (savings / original_price * 100) if original_price > 0 else 0
        
        response = AnalysisResponse(
            original_product=ProductInfo(
                name=product_data.get('name'),
                price=original_price,
                quality_score=quality_score,
                final_score=final_score,
                rating=product_data.get('rating'),
                specs=product_data.get('specs', {})
            ),
            alternatives=[Alternative(**alt) for alt in alternatives],
            savings={
                "amount": savings,
                "percentage": round(savings_percentage, 2)
            },
            recommendation=Alternative(**best_alternative) if best_alternative else None
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories")
async def get_categories():
    """Get available product categories"""
    try:
        categories = db.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/products/{category}")
async def get_products_by_category(category: str, page: int = 1, limit: int = 20):
    """Get products by category"""
    try:
        products = db.get_products_by_category(category, page, limit)
        return {"products": products}
    except Exception as e:
        logger.error(f"Error fetching products for category {category}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit user feedback for improving recommendations"""
    try:
        feedback_data = {
            'product_id': feedback.product_id,
            'rating': feedback.rating,
            'helpful': feedback.helpful,
            'comments': feedback.comments
        }
        
        # Store feedback in database
        feedback_id = db.store_feedback(feedback_data)
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/products/{product_id}/recommendations", response_model=List[RecommendationResponse])
async def get_product_recommendations(product_id: int, limit: int = 5):
    """Get AI-powered product recommendations based on similarity"""
    try:
        if limit > 20:
            limit = 20  # Cap the limit for performance
        
        recommendations = recommendation_engine.get_recommendations(
            product_id=product_id, 
            num_recommendations=limit
        )
        
        if not recommendations:
            raise HTTPException(
                status_code=404, 
                detail=f"No recommendations found for product {product_id}"
            )
        
        return [RecommendationResponse(**rec) for rec in recommendations]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/embeddings/generate")
async def generate_embeddings():
    """Generate embeddings for all products (admin endpoint)"""
    try:
        recommendation_engine.generate_embeddings_for_all_products()
        return {"message": "Embeddings generated successfully"}
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/embeddings/product/{product_id}")
async def add_product_embedding(product_id: int):
    """Add embedding for a specific product"""
    try:
        recommendation_engine.add_product_embedding(product_id)
        return {"message": f"Embedding added for product {product_id}"}
    except Exception as e:
        logger.error(f"Error adding embedding for product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
