from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import os

# Create FastAPI app
app = FastAPI(
    title="PhotoPro AI API",
    description="AI-powered professional photo generation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://photopro-ai-2.vercel.app",
        "https://photopro-ai-2-dm1zfb8a3-designbyricks-projects.vercel.app",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "PhotoPro AI API is running!",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# API documentation endpoint
@app.get("/docs")
def get_docs():
    return {"message": "API documentation available at /docs", "status": "success"}

# Authentication endpoints (simplified for Vercel)
@app.post("/auth/signup", response_model=UserResponse)
def signup(user: UserCreate):
    # For now, return a mock response
    # In production, you'd implement actual user creation
    return UserResponse(
        id=1,
        email=user.email,
        username=user.username,
        is_active=True
    )

@app.post("/auth/login", response_model=Token)
def login(user: UserCreate):
    # For now, return a mock token
    # In production, you'd implement actual authentication
    return Token(
        access_token="mock-token-12345",
        token_type="bearer"
    )

# Photo generation endpoint (simplified)
@app.post("/photos/generate")
def generate_photo():
    # For now, return a mock response
    # In production, you'd implement actual photo generation
    return {
        "message": "Photo generation endpoint",
        "status": "success",
        "photo_url": "https://example.com/generated-photo.jpg"
    }

# User profile endpoint
@app.get("/users/me", response_model=UserResponse)
def get_current_user():
    # For now, return a mock user
    # In production, you'd implement actual user retrieval
    return UserResponse(
        id=1,
        email="user@example.com",
        username="testuser",
        is_active=True
    )
