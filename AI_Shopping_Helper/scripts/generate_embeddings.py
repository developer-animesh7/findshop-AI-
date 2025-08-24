#!/usr/bin/env python3
"""
Script to generate embeddings for all products in the database.
This should be run once initially and then whenever new products are added.

Usage:
    python scripts/generate_embeddings.py
"""

import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai.recommendations import recommendation_engine
from backend.database.db_connection import DatabaseConnection

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def add_sample_products():
    """Add some sample products with descriptions if the database is empty"""
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # Check if we have products with descriptions
        result = db.execute_query("""
            SELECT COUNT(*) as count 
            FROM products 
            WHERE description IS NOT NULL AND description != ''
        """)
        
        count = result[0]['count'] if result else 0
        
        if count == 0:
            logger.info("No products with descriptions found. Adding sample products...")
            
            sample_products = [
                {
                    'name': 'iPhone 15 Pro',
                    'category': 'Electronics',
                    'price': 999.99,
                    'rating': 4.8,
                    'platform': 'Apple Store',
                    'url': 'https://apple.com/iphone-15-pro',
                    'description': 'The most advanced iPhone with titanium design, A17 Pro chip, and professional camera system. Features 5G connectivity, Face ID, and all-day battery life.',
                    'image_url': 'https://example.com/iphone15pro.jpg'
                },
                {
                    'name': 'Samsung Galaxy S24 Ultra',
                    'category': 'Electronics',
                    'price': 1199.99,
                    'rating': 4.7,
                    'platform': 'Samsung Store',
                    'url': 'https://samsung.com/galaxy-s24-ultra',
                    'description': 'Premium Android smartphone with S Pen, 200MP camera, and AI-powered features. Large 6.8-inch display with 120Hz refresh rate.',
                    'image_url': 'https://example.com/galaxys24ultra.jpg'
                },
                {
                    'name': 'MacBook Air M3',
                    'category': 'Electronics',
                    'price': 1099.99,
                    'rating': 4.9,
                    'platform': 'Apple Store',
                    'url': 'https://apple.com/macbook-air',
                    'description': 'Ultra-thin laptop with M3 chip for incredible performance and all-day battery life. Perfect for students and professionals.',
                    'image_url': 'https://example.com/macbookair.jpg'
                },
                {
                    'name': 'Dell XPS 13',
                    'category': 'Electronics',
                    'price': 899.99,
                    'rating': 4.6,
                    'platform': 'Dell Store',
                    'url': 'https://dell.com/xps-13',
                    'description': 'Compact Windows laptop with Intel processor, premium build quality, and excellent display. Great for business and productivity.',
                    'image_url': 'https://example.com/dellxps13.jpg'
                },
                {
                    'name': 'Sony WH-1000XM5',
                    'category': 'Electronics',
                    'price': 399.99,
                    'rating': 4.8,
                    'platform': 'Sony Store',
                    'url': 'https://sony.com/wh-1000xm5',
                    'description': 'Premium noise-canceling headphones with industry-leading sound quality, 30-hour battery life, and multipoint connectivity.',
                    'image_url': 'https://example.com/sonyheadphones.jpg'
                },
                {
                    'name': 'AirPods Pro 2',
                    'category': 'Electronics',
                    'price': 249.99,
                    'rating': 4.7,
                    'platform': 'Apple Store',
                    'url': 'https://apple.com/airpods-pro',
                    'description': 'True wireless earbuds with active noise cancellation, spatial audio, and seamless Apple device integration.',
                    'image_url': 'https://example.com/airpodspro2.jpg'
                },
                {
                    'name': 'Nike Air Max 270',
                    'category': 'Shoes',
                    'price': 150.00,
                    'rating': 4.5,
                    'platform': 'Nike Store',
                    'url': 'https://nike.com/air-max-270',
                    'description': 'Comfortable athletic sneakers with Max Air cushioning, breathable mesh upper, and modern style. Perfect for everyday wear.',
                    'image_url': 'https://example.com/nikeairmax270.jpg'
                },
                {
                    'name': 'Adidas Ultraboost 22',
                    'category': 'Shoes',
                    'price': 180.00,
                    'rating': 4.6,
                    'platform': 'Adidas Store',
                    'url': 'https://adidas.com/ultraboost-22',
                    'description': 'High-performance running shoes with responsive Boost midsole, Primeknit upper, and Continental rubber outsole for superior grip.',
                    'image_url': 'https://example.com/ultraboost22.jpg'
                },
                {
                    'name': 'Levi\'s 501 Original Jeans',
                    'category': 'Clothing',
                    'price': 89.99,
                    'rating': 4.4,
                    'platform': 'Levi\'s Store',
                    'url': 'https://levis.com/501-original',
                    'description': 'Classic straight-leg jeans made from premium denim. Timeless style that never goes out of fashion with button fly closure.',
                    'image_url': 'https://example.com/levis501.jpg'
                },
                {
                    'name': 'Patagonia Better Sweater',
                    'category': 'Clothing',
                    'price': 99.99,
                    'rating': 4.7,
                    'platform': 'Patagonia Store',
                    'url': 'https://patagonia.com/better-sweater',
                    'description': 'Cozy fleece jacket made from recycled polyester. Perfect for outdoor activities and casual wear with zippered pockets.',
                    'image_url': 'https://example.com/patagoniasweater.jpg'
                }
            ]
            
            # Insert sample products
            for product in sample_products:
                query = """
                INSERT INTO products (name, category, price, rating, platform, url, description, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    product['name'], product['category'], product['price'], 
                    product['rating'], product['platform'], product['url'],
                    product['description'], product['image_url']
                )
                db.execute_update(query, params)
            
            logger.info(f"Added {len(sample_products)} sample products to database")
        else:
            logger.info(f"Found {count} products with descriptions in database")
            
    except Exception as e:
        logger.error(f"Error adding sample products: {e}")
        raise e
    finally:
        db.disconnect()

def main():
    """Main function to generate embeddings"""
    try:
        logger.info("Starting embedding generation process...")
        
        # Add sample products if database is empty
        add_sample_products()
        
        # Generate embeddings for all products
        logger.info("Generating embeddings for all products...")
        recommendation_engine.generate_embeddings_for_all_products()
        
        logger.info("Embedding generation completed successfully!")
        
        # Test the recommendation system
        logger.info("Testing recommendation system...")
        recommendations = recommendation_engine.get_recommendations(product_id=1, num_recommendations=3)
        
        if recommendations:
            logger.info("Test successful! Sample recommendations:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec['name']} (similarity: {rec['similarity_score']})")
        else:
            logger.warning("No recommendations generated in test")
            
    except Exception as e:
        logger.error(f"Error in embedding generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
