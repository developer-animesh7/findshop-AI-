"""
Main FastAPI application for AI Shopping Helper
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as api_router
from backend.database.db_connection import init_db
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="AI Shopping Helper",
        description="Smart Product Comparison for India",
        version="1.0.0"
    )
    
    # Enable CORS for Next.js frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Initialize database
    init_db()
    
    @app.get("/")
    async def root():
        """Root endpoint - API information"""
        return {
            "message": "AI Shopping Helper API",
            "version": "2.0.0",
            "frontend": "Next.js + React + TypeScript",
            "backend": "FastAPI + SQLite",
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "AI Shopping Helper"}
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
