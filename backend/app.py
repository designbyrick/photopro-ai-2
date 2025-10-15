"""
PhotoPro AI - FastAPI Backend
Alternative entry point for Railway deployment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Initialize FastAPI app
app = FastAPI(
    title="PhotoPro AI API",
    description="AI-powered professional photo generation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "message": "PhotoPro AI API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify deployment"""
    return {
        "message": "PhotoPro AI is running successfully!",
        "deployment": "successful",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
