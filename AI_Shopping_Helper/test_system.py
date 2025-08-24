#!/usr/bin/env python3
"""
Test script to check database content and test recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.db_connection import DatabaseConnection
from backend.ai.recommendations import recommendation_engine

def test_database():
    """Test database content"""
    print("=== Testing Database Content ===")
    
    db = DatabaseConnection()
    db.connect()
    
    # Check products
    db.cursor.execute("SELECT COUNT(*) FROM products")
    count = db.cursor.fetchone()[0]
    print(f"Total products in database: {count}")
    
    if count > 0:
        db.cursor.execute("SELECT id, name, price FROM products LIMIT 5")
        products = db.cursor.fetchall()
        print("\nFirst 5 products:")
        for product in products:
            print(f"ID: {product[0]}, Name: {product[1]}, Price: ${product[2]}")
    
    db.disconnect()

def test_recommendations():
    """Test recommendation system"""
    print("\n=== Testing Recommendation Engine ===")
    
    try:
        # Test recommendations for product ID 1
        recommendations = recommendation_engine.get_recommendations(product_id=1, num_recommendations=3)
        print(f"Recommendations for Product ID 1:")
        for rec in recommendations:
            print(f"- {rec['name']} (Score: {rec['similarity_score']:.4f})")
    except Exception as e:
        print(f"Error getting recommendations: {e}")

if __name__ == "__main__":
    test_database()
    test_recommendations()
