"""
Pydantic schemas for request/response validation in PhotoPro AI.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: str
    full_name: str


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str  # Can be username or email
    password: str


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)"""
    id: int
    plan: str
    credits: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str


class PhotoGenerate(BaseModel):
    """Schema for photo generation request"""
    original_url: str
    style: str
    
    @validator('style')
    def validate_style(cls, v):
        valid_styles = ["corporate", "creative", "formal", "casual"]
        if v not in valid_styles:
            raise ValueError(f'Style must be one of: {", ".join(valid_styles)}')
        return v


class PhotoResponse(BaseModel):
    """Schema for photo response"""
    id: int
    user_id: int
    style: str
    original_url: str
    processed_url: Optional[str]
    thumbnail_url: Optional[str]
    credits_used: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreditPurchase(BaseModel):
    """Schema for credit purchase request"""
    plan: str
    
    @validator('plan')
    def validate_plan(cls, v):
        valid_plans = ["free", "pro", "enterprise"]
        if v not in valid_plans:
            raise ValueError(f'Plan must be one of: {", ".join(valid_plans)}')
        return v


class CreditHistoryResponse(BaseModel):
    """Schema for credit transaction history response"""
    id: int
    user_id: int
    amount: int
    transaction_type: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True
