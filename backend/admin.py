"""
Admin endpoints for PhotoPro AI backend.
User management, analytics, and system monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db
from models import User, GeneratedPhoto, CreditTransaction
from schemas import UserResponse, PhotoResponse, CreditHistoryResponse
from auth import get_current_user
import json

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])


def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user.username == "admin" or user.email == "admin@photopro.ai"


@admin_router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system statistics for admin dashboard"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get basic counts
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_photos = db.query(GeneratedPhoto).count()
    completed_photos = db.query(GeneratedPhoto).filter(GeneratedPhoto.status == "completed").count()
    
    # Get credit statistics
    total_credits_used = db.query(func.sum(CreditTransaction.amount)).filter(
        CreditTransaction.amount < 0
    ).scalar() or 0
    
    total_credits_purchased = db.query(func.sum(CreditTransaction.amount)).filter(
        CreditTransaction.amount > 0
    ).scalar() or 0
    
    # Get recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = db.query(User).filter(User.created_at >= week_ago).count()
    recent_photos = db.query(GeneratedPhoto).filter(GeneratedPhoto.created_at >= week_ago).count()
    
    # Get photo generation success rate
    success_rate = (completed_photos / total_photos * 100) if total_photos > 0 else 0
    
    # Get popular styles
    style_stats = db.query(
        GeneratedPhoto.style,
        func.count(GeneratedPhoto.id).label('count')
    ).filter(
        GeneratedPhoto.status == "completed"
    ).group_by(GeneratedPhoto.style).all()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "recent_signups": recent_users
        },
        "photos": {
            "total": total_photos,
            "completed": completed_photos,
            "recent_generations": recent_photos,
            "success_rate": round(success_rate, 2)
        },
        "credits": {
            "total_used": abs(total_credits_used),
            "total_purchased": total_credits_purchased,
            "net_credits": total_credits_purchased + total_credits_used
        },
        "styles": [
            {"style": style, "count": count} 
            for style, count in style_stats
        ]
    }


@admin_router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users with pagination and search"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    
    users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
    return users


@admin_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@admin_router.get("/users/{user_id}/photos", response_model=List[PhotoResponse])
async def get_user_photos(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all photos for a specific user"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    photos = db.query(GeneratedPhoto).filter(
        GeneratedPhoto.user_id == user_id
    ).order_by(desc(GeneratedPhoto.created_at)).all()
    
    return photos


@admin_router.get("/users/{user_id}/transactions", response_model=List[CreditHistoryResponse])
async def get_user_transactions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get credit transactions for a specific user"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    transactions = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == user_id
    ).order_by(desc(CreditTransaction.created_at)).all()
    
    return transactions


@admin_router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user_id": user_id,
        "is_active": user.is_active
    }


@admin_router.post("/users/{user_id}/add-credits")
async def add_credits_to_user(
    user_id: int,
    amount: int,
    description: str = "Admin credit adjustment",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add credits to a user account"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add credits to user
    user.credits += amount
    db.commit()
    
    # Create transaction record
    transaction = CreditTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type="admin_adjustment",
        description=description
    )
    db.add(transaction)
    db.commit()
    
    return {
        "message": f"Added {amount} credits to user",
        "user_id": user_id,
        "new_balance": user.credits
    }


@admin_router.get("/photos", response_model=List[PhotoResponse])
async def get_all_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    style: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all photos with filtering"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(GeneratedPhoto)
    
    if status:
        query = query.filter(GeneratedPhoto.status == status)
    
    if style:
        query = query.filter(GeneratedPhoto.style == style)
    
    photos = query.order_by(desc(GeneratedPhoto.created_at)).offset(skip).limit(limit).all()
    return photos


@admin_router.get("/analytics/daily")
async def get_daily_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily analytics for the specified number of days"""
    
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get daily user registrations
    daily_users = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(func.date(User.created_at)).all()
    
    # Get daily photo generations
    daily_photos = db.query(
        func.date(GeneratedPhoto.created_at).label('date'),
        func.count(GeneratedPhoto.id).label('count')
    ).filter(
        GeneratedPhoto.created_at >= start_date
    ).group_by(func.date(GeneratedPhoto.created_at)).all()
    
    # Get daily credit usage
    daily_credits = db.query(
        func.date(CreditTransaction.created_at).label('date'),
        func.sum(CreditTransaction.amount).label('total')
    ).filter(
        CreditTransaction.created_at >= start_date,
        CreditTransaction.amount < 0
    ).group_by(func.date(CreditTransaction.created_at)).all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "daily_users": [
            {"date": str(date), "count": count} 
            for date, count in daily_users
        ],
        "daily_photos": [
            {"date": str(date), "count": count} 
            for date, count in daily_photos
        ],
        "daily_credits": [
            {"date": str(date), "total": abs(total)} 
            for date, total in daily_credits
        ]
    }
