#!/usr/bin/env python3
"""
AI Shopping Helper - Demo Runner
================================

This script provides alternative ways to run the AI Shopping Helper:
1. Full launcher with FastAPI (if dependencies are available)
2. Simple demo server (using built-in libraries only)
3. Database initialization and testing
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        return False

def run_full_launcher():
    """Run the full project launcher"""
    print("🚀 Attempting to run full project launcher...")
    try:
        result = subprocess.run([
            sys.executable, "run_project.py", "--no-browser"
        ], check=True, timeout=60)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ Full launcher failed: {e}")
        return False

def run_simple_demo():
    """Run the simple demo server"""
    print("🚀 Running simple demo server...")
    try:
        subprocess.run([sys.executable, "simple_server.py"], check=True)
        return True
    except (subprocess.CalledProcessError, KeyboardInterrupt) as e:
        print(f"✅ Demo server stopped")
        return True
    except Exception as e:
        print(f"❌ Demo server failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("🗄️ Testing database initialization...")
    try:
        from backend.database.db_connection import init_db
        init_db()
        print("✅ Database initialized successfully")
        
        # Test database content
        import sqlite3
        conn = sqlite3.connect("data/shopping_assistant.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        print(f"✅ Found {category_count} categories in database")
        
        cursor.execute("SELECT name FROM categories LIMIT 3")
        categories = [row[0] for row in cursor.fetchall()]
        print(f"✅ Sample categories: {', '.join(categories)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                AI Shopping Helper - Demo Runner              ║
║              Choose your preferred method                    ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Test database first
    if not test_database():
        print("❌ Database initialization failed. Exiting.")
        return False
    
    # Check if full dependencies are available
    if check_dependencies():
        print("✅ FastAPI dependencies are available")
        print("\n📋 Available options:")
        print("1. Full FastAPI launcher (recommended)")
        print("2. Simple demo server")
        print("3. Database testing only")
        
        choice = input("\nChoose option (1-3) [1]: ").strip() or "1"
        
        if choice == "1":
            if not run_full_launcher():
                print("\n⚠️ Full launcher failed, falling back to simple demo...")
                return run_simple_demo()
            return True
        elif choice == "2":
            return run_simple_demo()
        elif choice == "3":
            print("✅ Database testing completed")
            return True
        else:
            print("❌ Invalid choice")
            return False
    else:
        print("⚠️ FastAPI dependencies not available")
        print("🔄 Falling back to simple demo server...")
        return run_simple_demo()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)