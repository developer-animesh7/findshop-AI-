"""
Configuration settings for the AI Shopping Helper
"""

import os
from decouple import config

class Config:
    """Base configuration"""
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
    
    # Database
    # Database (SQLite)
    # Use a file-based SQLite database by default. DATABASE_URL follows SQLAlchemy
    # style (sqlite:///./path/to/dbfile). The default puts the DB under ./data/.
    DATABASE_URL = config('DATABASE_URL', default='sqlite:///./data/shopping_assistant.db')
    
    # Environment
    ENV = config('ENV', default='development')
    DEBUG = config('DEBUG', default=True, cast=bool)
    
    # API
    API_BASE_URL = config('API_BASE_URL', default='http://localhost:5000')
    API_RATE_LIMIT = config('API_RATE_LIMIT', default=100, cast=int)
    
    # Scraping
    SCRAPING_DELAY = config('SCRAPING_DELAY', default=2, cast=int)
    USER_AGENT = config('USER_AGENT', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Image Processing
    TESSERACT_PATH = config('TESSERACT_PATH', default='/usr/local/bin/tesseract')
    MAX_IMAGE_SIZE = config('MAX_IMAGE_SIZE', default=10485760, cast=int)  # 10MB
    
    # Logging
    LOG_LEVEL = config('LOG_LEVEL', default='INFO')
    LOG_FILE = config('LOG_FILE', default='app.log')
    
    # Cache
    CACHE_TYPE = config('CACHE_TYPE', default='simple')
    CACHE_TIMEOUT = config('CACHE_TIMEOUT', default=3600, cast=int)
    
    # Affiliate
    AMAZON_AFFILIATE_TAG = config('AMAZON_AFFILIATE_TAG', default='')
    FLIPKART_AFFILIATE_TAG = config('FLIPKART_AFFILIATE_TAG', default='')
    
    # External APIs
    GOOGLE_VISION_API_KEY = config('GOOGLE_VISION_API_KEY', default='')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production values
    SECRET_KEY = config('SECRET_KEY')  # Required in production
    
class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use test database
    DATABASE_URL = config('TEST_DATABASE_URL', default='sqlite:///./data/shopping_assistant_test.db')

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
