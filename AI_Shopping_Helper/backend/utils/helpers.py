"""
Utility functions for the AI Shopping Helper
"""

import re
import json
import hashlib
import requests
from urllib.parse import urlparse
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processing utilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\.,\(\)₹$%]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_price(text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None
        
        # Price patterns for Indian currency
        patterns = [
            r'₹[\s]*([0-9,]+\.?\d*)',
            r'Rs\.?[\s]*([0-9,]+\.?\d*)',
            r'INR[\s]*([0-9,]+\.?\d*)',
            r'Price[\s]*:[\s]*₹?[\s]*([0-9,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def extract_rating(text: str) -> Optional[float]:
        """Extract rating from text"""
        if not text:
            return None
        
        patterns = [
            r'(\d+\.?\d*)\s*/\s*5',
            r'(\d+\.?\d*)\s*out\s*of\s*5',
            r'Rating[\s]*:[\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*stars?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rating = float(match.group(1))
                    if 0 <= rating <= 5:
                        return rating
                except ValueError:
                    continue
        
        return None

class UrlValidator:
    """URL validation utilities"""
    
    SUPPORTED_DOMAINS = [
        'amazon.in', 'amazon.com',
        'flipkart.com',
        'myntra.com',
        'snapdeal.com',
        'paytmmall.com',
        'ajio.com',
        'nykaa.com'
    ]
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_supported_platform(url: str) -> bool:
        """Check if URL is from a supported platform"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            domain = domain.replace('www.', '')
            
            return any(supported in domain for supported in UrlValidator.SUPPORTED_DOMAINS)
        except Exception:
            return False
    
    @staticmethod
    def get_platform_name(url: str) -> str:
        """Get platform name from URL"""
        try:
            domain = urlparse(url).netloc.lower()
            domain = domain.replace('www.', '')
            
            if 'amazon' in domain:
                return 'amazon'
            elif 'flipkart' in domain:
                return 'flipkart'
            elif 'myntra' in domain:
                return 'myntra'
            elif 'snapdeal' in domain:
                return 'snapdeal'
            elif 'paytmmall' in domain:
                return 'paytm'
            elif 'ajio' in domain:
                return 'ajio'
            elif 'nykaa' in domain:
                return 'nykaa'
            else:
                return 'unknown'
        except Exception:
            return 'unknown'

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_product_data(data: Dict) -> Dict:
        """Validate and clean product data"""
        validated = {}
        
        # Name validation
        name = data.get('name', '').strip()
        validated['name'] = name if len(name) > 0 else 'Unknown Product'
        
        # Price validation
        price = data.get('price', 0)
        try:
            validated['price'] = max(0, float(price))
        except (ValueError, TypeError):
            validated['price'] = 0
        
        # Rating validation
        rating = data.get('rating', 4.0)
        try:
            rating = float(rating)
            validated['rating'] = max(0, min(5, rating))
        except (ValueError, TypeError):
            validated['rating'] = 4.0
        
        # Category validation
        category = data.get('category', 'general').lower().strip()
        valid_categories = [
            'headphones', 'smartphone', 'laptop', 'trimmer', 
            'mixer', 'clothing', 'shoes', 'charger', 'general'
        ]
        validated['category'] = category if category in valid_categories else 'general'
        
        # Platform validation
        platform = data.get('platform', '').lower().strip()
        validated['platform'] = platform if platform else 'unknown'
        
        # URL validation
        url = data.get('url', '').strip()
        validated['url'] = url if UrlValidator.is_valid_url(url) else ''
        
        # Specs validation
        specs = data.get('specs', {})
        validated['specs'] = specs if isinstance(specs, dict) else {}
        
        # Score validation
        quality_score = data.get('quality_score', 0)
        try:
            validated['quality_score'] = max(0, min(100, float(quality_score)))
        except (ValueError, TypeError):
            validated['quality_score'] = 0
        
        final_score = data.get('final_score', 0)
        try:
            validated['final_score'] = max(0, float(final_score))
        except (ValueError, TypeError):
            validated['final_score'] = 0
        
        # Optional fields
        validated['image_url'] = data.get('image_url', '').strip()
        validated['description'] = data.get('description', '').strip()
        
        return validated

class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self, max_size: int = 1000):
        self._cache = {}
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        if len(self._cache) >= self._max_size:
            # Remove oldest item (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = value
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
    
    def generate_key(self, *args) -> str:
        """Generate cache key from arguments"""
        key_string = '|'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

class ResponseFormatter:
    """Format API responses"""
    
    @staticmethod
    def success_response(data: Any, message: str = "Success") -> Dict:
        """Format success response"""
        return {
            'status': 'success',
            'message': message,
            'data': data
        }
    
    @staticmethod
    def error_response(error: str, code: int = 400) -> Dict:
        """Format error response"""
        return {
            'status': 'error',
            'error': error,
            'code': code
        }
    
    @staticmethod
    def paginated_response(data: List, page: int, limit: int, total: int) -> Dict:
        """Format paginated response"""
        return {
            'status': 'success',
            'data': data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        import time
        
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            key: timestamps for key, timestamps in self.requests.items()
            if any(ts > current_time - self.window_seconds for ts in timestamps)
        }
        
        # Get recent requests for this identifier
        recent_requests = [
            ts for ts in self.requests.get(identifier, [])
            if ts > current_time - self.window_seconds
        ]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Add current request
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        self.requests[identifier].append(current_time)
        return True

class Logger:
    """Enhanced logging utilities"""
    
    @staticmethod
    def log_request(endpoint: str, params: Dict, user_ip: str = None):
        """Log API request"""
        logger.info(f"API Request - Endpoint: {endpoint}, IP: {user_ip}, Params: {params}")
    
    @staticmethod
    def log_error(error: Exception, context: Dict = None):
        """Log error with context"""
        error_msg = f"Error: {str(error)}"
        if context:
            error_msg += f", Context: {context}"
        logger.error(error_msg)
    
    @staticmethod
    def log_performance(operation: str, duration: float, details: Dict = None):
        """Log performance metrics"""
        perf_msg = f"Performance - Operation: {operation}, Duration: {duration:.3f}s"
        if details:
            perf_msg += f", Details: {details}"
        logger.info(perf_msg)

# Global instances
cache_manager = CacheManager()
rate_limiter = RateLimiter()

def format_currency(amount: float, currency: str = '₹') -> str:
    """Format currency amount"""
    if amount >= 10000000:  # 1 crore
        return f"{currency}{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"{currency}{amount/100000:.1f}L"
    elif amount >= 1000:  # 1 thousand
        return f"{currency}{amount/1000:.1f}K"
    else:
        return f"{currency}{amount:,.0f}"

def calculate_savings_percentage(original_price: float, discounted_price: float) -> float:
    """Calculate savings percentage"""
    if original_price <= 0:
        return 0
    
    savings = original_price - discounted_price
    return (savings / original_price) * 100

def normalize_product_name(name: str) -> str:
    """Normalize product name for comparison"""
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove common words
    common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    words = name.split()
    words = [word for word in words if word not in common_words]
    
    # Remove special characters
    name = ' '.join(words)
    name = re.sub(r'[^\w\s]', '', name)
    
    return name.strip()

def extract_brand_from_name(name: str) -> str:
    """Extract brand name from product name"""
    if not name:
        return ""
    
    # Common brand patterns
    brand_patterns = [
        r'^([A-Za-z]+)\s+',  # First word is usually brand
        r'by\s+([A-Za-z]+)',  # "by Brand"
        r'from\s+([A-Za-z]+)',  # "from Brand"
    ]
    
    for pattern in brand_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Fallback: return first word
    words = name.split()
    return words[0] if words else ""
