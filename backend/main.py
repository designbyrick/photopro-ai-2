"""
PhotoPro AI - FastAPI Backend
Main application entry point with all routes and middleware configuration.
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import boto3
import replicate
from PIL import Image
import io
import uuid
import asyncio

from database import get_db, engine, Base
from models import User, GeneratedPhoto, CreditTransaction
from schemas import (
    UserCreate, UserResponse, UserLogin, Token, PhotoGenerate, 
    PhotoResponse, CreditPurchase, CreditHistoryResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user, authenticate_user
)
from config import settings
from middleware import RateLimitMiddleware, LoggingMiddleware, ErrorHandlingMiddleware
from websocket import websocket_endpoint, notify_photo_status_update, notify_photo_completed, notify_photo_failed, notify_credits_updated
from utils import validate_image_file, optimize_image_for_upload, generate_thumbnail, validate_style
from admin import admin_router
from docs import custom_openapi
from monitoring import get_system_metrics, get_application_metrics, get_health_status, get_detailed_health

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PhotoPro AI API",
    description="AI-powered professional photo generation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Add custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://photopro-ai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Include admin router
app.include_router(admin_router)

# AWS S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

# Replicate client
replicate_client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)


@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "message": "PhotoPro AI API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system metrics"""
    return get_detailed_health()


@app.get("/metrics/system")
async def system_metrics():
    """Get system performance metrics"""
    return get_system_metrics()


@app.get("/metrics/application")
async def application_metrics(db: Session = Depends(get_db)):
    """Get application-specific metrics"""
    return get_application_metrics(db)


# WebSocket endpoint for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_route(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time photo processing updates"""
    await websocket_endpoint(websocket, user_id)


# Authentication endpoints
@app.post("/auth/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with 3 free credits"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        plan="free",
        credits=3,  # Welcome bonus: 3 free credits
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create welcome credit transaction
    credit_transaction = CreditTransaction(
        user_id=db_user.id,
        amount=3,
        transaction_type="welcome_bonus",
        description="Welcome bonus - 3 free credits"
    )
    db.add(credit_transaction)
    db.commit()
    
    return db_user


@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username/email and password"""
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@app.get("/users/me/credits")
async def get_user_credits(current_user: User = Depends(get_current_user)):
    """Get user's current credit balance"""
    return {"credits": current_user.credits}


# Photo endpoints
@app.post("/photos/upload")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and validate image file with enhanced validation"""
    
    # Read file content
    file_content = await file.read()
    
    # Validate image file
    is_valid, error_message = validate_image_file(file_content, file.filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Optimize image for upload
    optimized_content = optimize_image_for_upload(file_content)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_key = f"uploads/{current_user.id}/{unique_filename}"
    
    try:
        # Upload to S3
        s3_client.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=file_key,
            Body=optimized_content,
            ContentType=file.content_type,
            Metadata={
                'user_id': str(current_user.id),
                'original_filename': file.filename,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Generate S3 URL
        s3_url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        
        # Get image dimensions for response
        image = Image.open(io.BytesIO(optimized_content))
        width, height = image.size
        
        return {
            "message": "File uploaded successfully",
            "url": s3_url,
            "filename": file.filename,
            "size": len(optimized_content),
            "original_size": len(file_content),
            "dimensions": {"width": width, "height": height},
            "optimized": len(optimized_content) < len(file_content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@app.post("/photos/generate", response_model=PhotoResponse)
async def generate_photo(
    original_url: str = Form(...),
    style: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate professional photo using AI with real-time updates"""
    
    # Check if user has enough credits
    if current_user.credits < 1:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    # Validate style
    if not validate_style(style):
        raise HTTPException(status_code=400, detail="Invalid style. Must be one of: corporate, creative, formal, casual")
    
    # Create photo record
    photo = GeneratedPhoto(
        user_id=current_user.id,
        style=style,
        original_url=original_url,
        status="processing"
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    # Notify user that processing has started
    await notify_photo_status_update(current_user.id, photo.id, "processing", "Starting photo generation...")
    
    try:
        # Process with Replicate API
        await notify_photo_status_update(current_user.id, photo.id, "processing", "Processing with AI model...")
        
        output = replicate_client.run(
            "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
            input={
                "input_image": original_url,
                "style": style,
                "num_outputs": 1,
                "style_strength_ratio": 20,
                "num_inference_steps": 50
            }
        )
        
        # Get processed image URL
        processed_url = output[0] if output else None
        
        if not processed_url:
            raise Exception("No output from AI model")
        
        # Notify user that processing is complete
        await notify_photo_status_update(current_user.id, photo.id, "processing", "Generating thumbnail...")
        
        # Generate thumbnail
        thumbnail_data = generate_thumbnail(processed_url)
        thumbnail_url = processed_url  # Fallback to original if thumbnail fails
        
        if thumbnail_data:
            # Upload thumbnail to S3
            thumbnail_key = f"thumbnails/{current_user.id}/{uuid.uuid4()}.jpg"
            try:
                s3_client.put_object(
                    Bucket=settings.AWS_BUCKET_NAME,
                    Key=thumbnail_key,
                    Body=thumbnail_data,
                    ContentType='image/jpeg'
                )
                thumbnail_url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{thumbnail_key}"
            except Exception as e:
                print(f"Thumbnail upload failed: {e}")
        
        # Update photo record
        photo.processed_url = processed_url
        photo.thumbnail_url = thumbnail_url
        photo.status = "completed"
        photo.credits_used = 1
        db.commit()
        
        # Deduct credits
        current_user.credits -= 1
        db.commit()
        
        # Create credit transaction
        credit_transaction = CreditTransaction(
            user_id=current_user.id,
            amount=-1,
            transaction_type="photo_generation",
            description=f"Photo generation - {style} style"
        )
        db.add(credit_transaction)
        db.commit()
        
        # Notify user that photo is completed
        await notify_photo_completed(current_user.id, photo.id, processed_url, thumbnail_url)
        await notify_credits_updated(current_user.id, current_user.credits, "photo_generation")
        
        return photo
        
    except Exception as e:
        # Update photo status to failed
        photo.status = "failed"
        db.commit()
        
        # Notify user of failure
        await notify_photo_failed(current_user.id, photo.id, str(e))
        
        raise HTTPException(status_code=500, detail=f"Photo generation failed: {str(e)}")


async def generate_thumbnail(image_url: str) -> str:
    """Generate thumbnail for processed image"""
    try:
        # Download image
        import requests
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        
        # Create thumbnail
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Upload thumbnail to S3
        thumbnail_key = f"thumbnails/{uuid.uuid4()}.jpg"
        
        # Convert to bytes
        thumbnail_buffer = io.BytesIO()
        image.save(thumbnail_buffer, format='JPEG', quality=85)
        thumbnail_buffer.seek(0)
        
        s3_client.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=thumbnail_key,
            Body=thumbnail_buffer.getvalue(),
            ContentType='image/jpeg'
        )
        
        return f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{thumbnail_key}"
        
    except Exception:
        return image_url  # Return original if thumbnail generation fails


@app.get("/photos/history", response_model=List[PhotoResponse])
async def get_photo_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's photo generation history (limit 20)"""
    
    photos = db.query(GeneratedPhoto).filter(
        GeneratedPhoto.user_id == current_user.id
    ).order_by(GeneratedPhoto.created_at.desc()).limit(20).all()
    
    return photos


@app.get("/photos/{photo_id}", response_model=PhotoResponse)
async def get_photo_details(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific photo details"""
    
    photo = db.query(GeneratedPhoto).filter(
        GeneratedPhoto.id == photo_id,
        GeneratedPhoto.user_id == current_user.id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return photo


# Credit endpoints
@app.post("/credits/purchase")
async def purchase_credits(
    purchase_data: CreditPurchase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase credits or upgrade plan"""
    
    # Define plans and credit amounts
    plans = {
        "free": 3,
        "pro": 50,
        "enterprise": 999
    }
    
    if purchase_data.plan not in plans:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Calculate credits to add
    credits_to_add = plans[purchase_data.plan] - current_user.credits
    
    if credits_to_add <= 0:
        raise HTTPException(status_code=400, detail="Plan provides same or fewer credits than current")
    
    # Update user
    current_user.plan = purchase_data.plan
    current_user.credits += credits_to_add
    db.commit()
    
    # Create credit transaction
    credit_transaction = CreditTransaction(
        user_id=current_user.id,
        amount=credits_to_add,
        transaction_type="purchase",
        description=f"Upgraded to {purchase_data.plan} plan"
    )
    db.add(credit_transaction)
    db.commit()
    
    return {
        "message": f"Successfully upgraded to {purchase_data.plan} plan",
        "credits_added": credits_to_add,
        "total_credits": current_user.credits
    }


@app.get("/credits/history", response_model=List[CreditHistoryResponse])
async def get_credit_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's credit transaction history"""
    
    transactions = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == current_user.id
    ).order_by(CreditTransaction.created_at.desc()).all()
    
    return transactions


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
