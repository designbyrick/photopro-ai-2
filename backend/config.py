"""
Configuration settings for PhotoPro AI backend.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/photopro_ai"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Replicate API
    REPLICATE_API_TOKEN: str = ""
    
    # CORS Origins
    CORS_ORIGINS: list = ["http://localhost:3000", "https://photopro-ai.vercel.app"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
