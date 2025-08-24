"""
Database connection and management for the AI Shopping Helper using SQLite
"""

import sqlite3
import os
import logging
import json

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages SQLite database connections and operations"""
    
    def __init__(self, db_path="data/shopping_assistant.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.cursor = self.connection.cursor()
            logger.info("SQLite database connection established successfully")
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise e
    
    def disconnect(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params or ())
            rows = self.cursor.fetchall()
            
            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise e
    
    def execute_update(self, query, params=None):
        """Execute an INSERT, UPDATE, or DELETE query"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.rowcount
            
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            self.connection.rollback()
            raise e
    
    def execute_many(self, query, params_list):
        """Execute a query with multiple parameter sets"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            return self.cursor.rowcount
            
        except Exception as e:
            logger.error(f"Error executing batch query: {e}")
            self.connection.rollback()
            raise e
    
    def get_last_insert_id(self):
        """Get the last inserted ID"""
        return self.cursor.lastrowid

def init_db():
    """Initialize database tables"""
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # Create products table
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            rating REAL DEFAULT 4.0,
            platform TEXT NOT NULL,
            url TEXT,
            specs TEXT,  -- JSON as TEXT
            quality_score REAL,
            final_score REAL,
            image_url TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create categories table
        create_categories_table = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            scorecard TEXT,  -- JSON as TEXT
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create user feedback table
        create_feedback_table = """
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            user_rating REAL,
            is_helpful BOOLEAN,
            comments TEXT,
            user_ip TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """
        
        # Create search logs table
        create_search_logs_table = """
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_query TEXT,
            category TEXT,
            user_ip TEXT,
            results_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create indexes for better performance
        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);",
            "CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);",
            "CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating);",
            "CREATE INDEX IF NOT EXISTS idx_products_quality_score ON products(quality_score);",
            "CREATE INDEX IF NOT EXISTS idx_products_final_score ON products(final_score);",
            "CREATE INDEX IF NOT EXISTS idx_feedback_product_id ON user_feedback(product_id);",
            "CREATE INDEX IF NOT EXISTS idx_search_logs_category ON search_logs(category);",
            "CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs(created_at);"
        ]
        
        # Execute table creation queries
        queries = [
            create_products_table,
            create_categories_table,
            create_feedback_table,
            create_search_logs_table
        ] + create_indexes
        
        for query in queries:
            db.cursor.execute(query)
            db.connection.commit()
        
        # Insert default categories
        insert_default_categories(db)
        
        logger.info("SQLite database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e
    finally:
        db.disconnect()

def insert_default_categories(db):
    """Insert default product categories"""
    categories = [
        {
            'name': 'headphones',
            'display_name': 'Headphones & Earphones',
            'description': 'Audio devices including headphones, earphones, and speakers',
            'scorecard': json.dumps({
                'battery_life': 30,
                'driver_size': 25,
                'noise_cancellation': 20,
                'build_quality': 15,
                'frequency_response': 10
            })
        },
        {
            'name': 'smartphone',
            'display_name': 'Smartphones',
            'description': 'Mobile phones and smartphones',
            'scorecard': json.dumps({
                'camera': 25,
                'battery': 25,
                'processor': 20,
                'ram': 15,
                'storage': 15
            })
        },
        {
            'name': 'laptop',
            'display_name': 'Laptops & Computers',
            'description': 'Laptops, desktops, and computer accessories',
            'scorecard': json.dumps({
                'processor': 30,
                'ram': 25,
                'storage': 20,
                'display': 15,
                'battery': 10
            })
        },
        {
            'name': 'trimmer',
            'display_name': 'Trimmers & Grooming',
            'description': 'Personal grooming devices',
            'scorecard': json.dumps({
                'runtime': 30,
                'blade_material': 25,
                'waterproof': 20,
                'attachments': 15,
                'charging_time': 10
            })
        },
        {
            'name': 'mixer',
            'display_name': 'Kitchen Appliances',
            'description': 'Kitchen appliances and mixers',
            'scorecard': json.dumps({
                'power_output': 30,
                'jar_count': 25,
                'speed_settings': 20,
                'warranty': 15,
                'safety_features': 10
            })
        },
        {
            'name': 'clothing',
            'display_name': 'Clothing & Fashion',
            'description': 'Apparel and fashion items',
            'scorecard': json.dumps({
                'material': 30,
                'fit': 25,
                'durability': 20,
                'comfort': 15,
                'design': 10
            })
        },
        {
            'name': 'general',
            'display_name': 'General Products',
            'description': 'Other general products',
            'scorecard': json.dumps({
                'quality': 40,
                'features': 30,
                'durability': 20,
                'value': 10
            })
        }
    ]
    
    try:
        # Check if categories already exist
        check_query = "SELECT COUNT(*) as count FROM categories"
        result = db.execute_query(check_query)
        
        if result[0]['count'] == 0:
            # Insert categories
            insert_query = """
            INSERT INTO categories (name, display_name, description, scorecard)
            VALUES (?, ?, ?, ?)
            """
            
            for category in categories:
                params = (
                    category['name'],
                    category['display_name'],
                    category['description'],
                    category['scorecard']
                )
                db.execute_update(insert_query, params)
            
            logger.info("Default categories inserted successfully")
        else:
            logger.info("Categories already exist, skipping insertion")
            
    except Exception as e:
        logger.error(f"Error inserting default categories: {e}")
        raise e
