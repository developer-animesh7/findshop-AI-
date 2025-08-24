"""
Unit tests for the AI Shopping Helper
"""

import unittest
import json
from backend.ai_scoring.quality_scorer import QualityScorer
from backend.utils.helpers import TextProcessor, UrlValidator, DataValidator

class TestQualityScorer(unittest.TestCase):
    """Test the quality scoring system"""
    
    def setUp(self):
        self.scorer = QualityScorer()
    
    def test_headphones_scoring(self):
        """Test headphones quality scoring"""
        specs = {
            'battery_life': '24 hours',
            'driver_size': '40mm',
            'noise_cancellation': 'Active Noise Cancellation',
            'build_quality': 'Premium metal construction'
        }
        
        score = self.scorer.calculate_quality_score(specs, 'headphones')
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_final_score_calculation(self):
        """Test final score calculation with rating"""
        quality_score = 80.0
        rating = 4.5
        
        final_score = self.scorer.calculate_final_score(quality_score, rating)
        expected = 80.0 * (4.5 / 5.0)
        
        self.assertEqual(final_score, expected)
    
    def test_invalid_category(self):
        """Test handling of invalid category"""
        specs = {'some_feature': 'value'}
        score = self.scorer.calculate_quality_score(specs, 'invalid_category')
        
        self.assertGreater(score, 0)  # Should use general category

class TestTextProcessor(unittest.TestCase):
    """Test text processing utilities"""
    
    def test_price_extraction(self):
        """Test price extraction from text"""
        test_cases = [
            ('₹2,499', 2499.0),
            ('Rs. 1,899', 1899.0),
            ('Price: ₹ 3,999', 3999.0),
            ('INR 5999', 5999.0),
            ('No price here', None)
        ]
        
        for text, expected in test_cases:
            result = TextProcessor.extract_price(text)
            self.assertEqual(result, expected)
    
    def test_rating_extraction(self):
        """Test rating extraction from text"""
        test_cases = [
            ('4.5/5', 4.5),
            ('3.8 out of 5', 3.8),
            ('Rating: 4.2', 4.2),
            ('4 stars', 4.0),
            ('No rating', None)
        ]
        
        for text, expected in test_cases:
            result = TextProcessor.extract_rating(text)
            self.assertEqual(result, expected)

class TestUrlValidator(unittest.TestCase):
    """Test URL validation utilities"""
    
    def test_valid_urls(self):
        """Test valid URL detection"""
        valid_urls = [
            'https://www.amazon.in/product',
            'https://flipkart.com/item',
            'http://myntra.com/clothing'
        ]
        
        for url in valid_urls:
            self.assertTrue(UrlValidator.is_valid_url(url))
    
    def test_invalid_urls(self):
        """Test invalid URL detection"""
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',
            '',
            None
        ]
        
        for url in invalid_urls:
            if url is not None:
                self.assertFalse(UrlValidator.is_valid_url(url))
    
    def test_platform_detection(self):
        """Test platform name detection"""
        test_cases = [
            ('https://www.amazon.in/product', 'amazon'),
            ('https://flipkart.com/item', 'flipkart'),
            ('https://myntra.com/clothing', 'myntra'),
            ('https://unknown-site.com/product', 'unknown')
        ]
        
        for url, expected in test_cases:
            result = UrlValidator.get_platform_name(url)
            self.assertEqual(result, expected)

class TestDataValidator(unittest.TestCase):
    """Test data validation utilities"""
    
    def test_product_data_validation(self):
        """Test product data validation"""
        raw_data = {
            'name': '  Test Product  ',
            'price': '2499',
            'rating': '4.5',
            'category': 'HEADPHONES',
            'platform': 'Amazon',
            'specs': {'feature': 'value'}
        }
        
        validated = DataValidator.validate_product_data(raw_data)
        
        self.assertEqual(validated['name'], 'Test Product')
        self.assertEqual(validated['price'], 2499.0)
        self.assertEqual(validated['rating'], 4.5)
        self.assertEqual(validated['category'], 'headphones')
        self.assertEqual(validated['platform'], 'amazon')
        self.assertIsInstance(validated['specs'], dict)
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        raw_data = {
            'name': '',
            'price': 'invalid',
            'rating': 'invalid',
            'category': 'invalid_category'
        }
        
        validated = DataValidator.validate_product_data(raw_data)
        
        self.assertEqual(validated['name'], 'Unknown Product')
        self.assertEqual(validated['price'], 0)
        self.assertEqual(validated['rating'], 4.0)
        self.assertEqual(validated['category'], 'general')

if __name__ == '__main__':
    unittest.main()
