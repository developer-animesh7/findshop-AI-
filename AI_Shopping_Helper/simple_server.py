#!/usr/bin/env python3
"""
Simple HTTP server to demonstrate AI Shopping Helper functionality
Uses only built-in Python libraries to avoid dependency issues
"""

import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse
from pathlib import Path

PORT = 8000

# Initialize database using our existing db_connection module
def init_simple_db():
    """Initialize a simple SQLite database"""
    db_path = "data/shopping_assistant.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a simple products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            rating REAL DEFAULT 4.0,
            platform TEXT NOT NULL,
            url TEXT,
            quality_score REAL,
            description TEXT
        )
    """)
    
    # Insert some sample data
    sample_products = [
        ("Sony WH-CH720N Headphones", "headphones", 7999.0, 4.2, "Amazon", "https://amazon.in/sony-headphones", 8.5, "Noise cancelling wireless headphones"),
        ("Apple iPhone 15", "smartphone", 79900.0, 4.5, "Flipkart", "https://flipkart.com/iphone-15", 9.2, "Latest iPhone with 48MP camera"),
        ("Dell Inspiron 15", "laptop", 55999.0, 4.1, "Amazon", "https://amazon.in/dell-inspiron", 7.8, "15.6 inch laptop for everyday use"),
        ("Philips BT3211 Trimmer", "trimmer", 1499.0, 4.0, "Myntra", "https://myntra.com/philips-trimmer", 7.5, "Cordless trimmer with 20 length settings"),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO products (name, category, price, rating, platform, url, quality_score, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_products)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with sample data")

class AIShoppingHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for AI Shopping Helper"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_homepage()
        elif path == '/health':
            self.serve_health()
        elif path == '/api/categories':
            self.serve_categories()
        elif path.startswith('/api/products/'):
            category = path.split('/')[-1]
            self.serve_products_by_category(category)
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/analyze':
            self.handle_analyze()
        else:
            self.send_error(404, "Not Found")
    
    def serve_homepage(self):
        """Serve the main homepage"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Shopping Helper</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
        }
        .feature h3 {
            font-size: 1.5rem;
            margin-bottom: 15px;
        }
        .demo-section {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .product-card {
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .btn {
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #45a049;
        }
        .api-endpoints {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .endpoint {
            margin: 10px 0;
            font-family: monospace;
            background: rgba(0,0,0,0.3);
            padding: 8px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 AI Shopping Helper</h1>
            <p>Smart Product Comparison for India</p>
            <p>Find better deals and save money with AI-powered product analysis</p>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Advanced algorithms analyze product specifications and reviews to provide quality scores</p>
            </div>
            <div class="feature">
                <h3>💰 Price Comparison</h3>
                <p>Compare prices across Amazon, Flipkart, Myntra and other major platforms</p>
            </div>
            <div class="feature">
                <h3>🔍 Smart Alternatives</h3>
                <p>Discover better value products and alternatives that match your needs</p>
            </div>
            <div class="feature">
                <h3>📊 Category Scorecards</h3>
                <p>Specialized analysis for different product categories with custom scoring</p>
            </div>
        </div>
        
        <div class="demo-section">
            <h2>🎯 Sample Products</h2>
            <p>Here are some products in our database:</p>
            <div class="products-grid" id="products-grid">
                <!-- Products will be loaded here -->
            </div>
            <button class="btn" onclick="loadProducts()">Load Sample Products</button>
        </div>
        
        <div class="demo-section">
            <h2>🔌 API Endpoints</h2>
            <p>The following REST API endpoints are available:</p>
            <div class="api-endpoints">
                <div class="endpoint">GET /health - Health check</div>
                <div class="endpoint">GET /api/categories - List product categories</div>
                <div class="endpoint">GET /api/products/{category} - Products by category</div>
                <div class="endpoint">POST /api/analyze - Analyze product from URL/image</div>
            </div>
            <button class="btn" onclick="testAPI()">Test API Endpoints</button>
        </div>
        
        <div class="demo-section">
            <h2>📈 System Status</h2>
            <p id="status">Loading system status...</p>
            <button class="btn" onclick="checkHealth()">Check Health</button>
        </div>
    </div>
    
    <script>
        async function loadProducts() {
            try {
                const response = await fetch('/api/products/headphones');
                const data = await response.json();
                displayProducts(data.products || []);
            } catch (error) {
                console.error('Error loading products:', error);
                document.getElementById('products-grid').innerHTML = '<p>Error loading products</p>';
            }
        }
        
        function displayProducts(products) {
            const grid = document.getElementById('products-grid');
            if (products.length === 0) {
                grid.innerHTML = '<p>No products found</p>';
                return;
            }
            
            grid.innerHTML = products.map(product => `
                <div class="product-card">
                    <h4>${product.name}</h4>
                    <p>₹${product.price}</p>
                    <p>Rating: ${product.rating}/5</p>
                    <p>Quality Score: ${product.quality_score}/10</p>
                    <p>${product.platform}</p>
                </div>
            `).join('');
        }
        
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                document.getElementById('status').innerHTML = `
                    <strong>Status:</strong> ${data.status}<br>
                    <strong>Service:</strong> ${data.service}<br>
                    <strong>Time:</strong> ${new Date().toLocaleString()}
                `;
            } catch (error) {
                document.getElementById('status').innerHTML = 'Error checking health: ' + error.message;
            }
        }
        
        async function testAPI() {
            try {
                const response = await fetch('/api/categories');
                const data = await response.json();
                alert('API Test Successful! Categories: ' + data.categories.join(', '));
            } catch (error) {
                alert('API Test Failed: ' + error.message);
            }
        }
        
        // Load initial data
        checkHealth();
        loadProducts();
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_health(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "service": "AI Shopping Helper (Demo Mode)",
            "message": "Server is running successfully"
        }
        self.send_json_response(response)
    
    def serve_categories(self):
        """Serve available categories"""
        categories = ["headphones", "smartphone", "laptop", "trimmer", "clothing", "general"]
        response = {"categories": categories}
        self.send_json_response(response)
    
    def serve_products_by_category(self, category):
        """Serve products by category"""
        try:
            conn = sqlite3.connect("data/shopping_assistant.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, category, price, rating, platform, url, quality_score, description
                FROM products 
                WHERE category = ? 
                LIMIT 10
            """, (category,))
            
            products = []
            for row in cursor.fetchall():
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "price": row[3],
                    "rating": row[4],
                    "platform": row[5],
                    "url": row[6],
                    "quality_score": row[7],
                    "description": row[8]
                })
            
            conn.close()
            
            response = {"products": products}
            self.send_json_response(response)
            
        except Exception as e:
            self.send_error(500, f"Database error: {str(e)}")
    
    def handle_analyze(self):
        """Handle product analysis request"""
        # Mock response for demonstration
        response = {
            "original_product": {
                "name": "Sample Product",
                "price": 5000.0,
                "quality_score": 8.5,
                "final_score": 8.2,
                "rating": 4.2,
                "specs": {"brand": "Sample", "model": "Demo"}
            },
            "alternatives": [
                {
                    "id": 1,
                    "name": "Better Alternative",
                    "category": "headphones",
                    "price": 4200.0,
                    "rating": 4.5,
                    "platform": "Amazon",
                    "url": "https://amazon.in/alternative",
                    "quality_score": 9.0,
                    "final_score": 8.8
                }
            ],
            "savings": {
                "amount": 800.0,
                "percentage": 16.0
            },
            "recommendation": {
                "id": 1,
                "name": "Recommended Product",
                "price": 4200.0,
                "rating": 4.5
            }
        }
        self.send_json_response(response)
    
    def send_json_response(self, data):
        """Send JSON response"""
        response_data = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_data.encode())

def main():
    """Start the simple server"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    AI Shopping Helper                        ║
║                     Demo Server                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting AI Shopping Helper Demo Server...
""")
    
    # Initialize database
    init_simple_db()
    
    # Start server
    with socketserver.TCPServer(("", PORT), AIShoppingHandler) as httpd:
        print(f"""
✅ Server started successfully!

🌐 Access the application at:
   http://localhost:{PORT}

📚 API Documentation:
   http://localhost:{PORT}/health      - Health check
   http://localhost:{PORT}/api/categories - List categories
   
🛑 Press Ctrl+C to stop the server
""")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")

if __name__ == "__main__":
    main()