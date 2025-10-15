"""
SQLAlchemy database models for PhotoPro AI.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    plan = Column(String(20), default="free", nullable=False)  # free, pro, enterprise
    credits = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    generated_photos = relationship("GeneratedPhoto", back_populates="user")
    credit_transactions = relationship("CreditTransaction", back_populates="user")


class GeneratedPhoto(Base):
    """Generated photo model for tracking AI-processed images"""
    __tablename__ = "generated_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    style = Column(String(20), nullable=False)  # corporate, creative, formal, casual
    original_url = Column(Text, nullable=False)
    processed_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    credits_used = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default="processing", nullable=False)  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="generated_photos")


class CreditTransaction(Base):
    """Credit transaction model for tracking credit usage and purchases"""
    __tablename__ = "credit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for credits added, negative for credits used
    transaction_type = Column(String(30), nullable=False)  # welcome_bonus, purchase, photo_generation
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")
