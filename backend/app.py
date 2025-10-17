from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator
import os
import replicate
from PIL import Image
import io
import base64
from storage import storage

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./photopro.db")

if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cloudinary setup
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Replicate API setup
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Initialize Replicate client
if REPLICATE_API_TOKEN:
    replicate.Client(api_token=REPLICATE_API_TOKEN)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be 72 characters or less')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    credits: int
    is_active: bool
    created_at: datetime

class PhotoGenerationRequest(BaseModel):
    style: str
    prompt: str = ""

class PhotoGenerationResponse(BaseModel):
    id: int
    user_id: int
    original_image_url: str
    generated_image_url: str
    style: str
    prompt: str
    status: str
    created_at: datetime

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    credits = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class GeneratedPhoto(Base):
    __tablename__ = "generated_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    original_url = Column(String)
    generated_url = Column(String)
    processed_url = Column(String)
    style = Column(String)
    prompt = Column(String)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.now)

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    amount = Column(Integer)
    transaction_type = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.now)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="PhotoPro AI API",
    description="AI-powered professional photo generation platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "PhotoPro AI API is running!",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if DATABASE_URL.startswith("postgresql") else "sqlite"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected" if DATABASE_URL.startswith("postgresql") else "sqlite",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/init-db")
async def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        return {"message": "Database tables created successfully", "status": "success"}
    except Exception as e:
        return {"message": f"Error creating tables: {str(e)}", "status": "error"}

@app.post("/test-signup")
async def test_signup():
    """Test signup functionality"""
    try:
        # Test database connection
        db = SessionLocal()
        db.close()
        
        # Test password hashing
        test_hash = get_password_hash("test")
        
        return {
            "message": "Signup components working",
            "password_hash": test_hash[:20] + "...",
            "status": "success"
        }
    except Exception as e:
        return {"message": f"Error in signup test: {str(e)}", "status": "error"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": [{"id": u.id, "email": u.email, "username": u.username, "credits": u.credits} for u in users]}

@app.get("/photos")
def get_photos(db: Session = Depends(get_db)):
    photos = db.query(GeneratedPhoto).all()
    return {"photos": [{"id": p.id, "user_id": p.user_id, "style": p.style, "status": p.status} for p in photos]}

# Authentication endpoints
@app.post("/auth/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        credits=10  # Give new users 10 credits
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token for the new user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "credits": db_user.credits,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at
        }
    }

@app.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        credits=current_user.credits,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@app.get("/auth/credits")
def get_user_credits(current_user: User = Depends(get_current_user)):
    return {"credits": current_user.credits}

@app.get("/users/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "credits": current_user.credits,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

# Photo generation endpoints
@app.post("/photos/upload")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a photo for AI generation"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Upload to Cloudinary
        result = await storage.upload_photo(
            file=file,
            user_id=current_user.id,
            folder="originals",
            optimize=True
        )
        
        return {
            "message": "Photo uploaded successfully",
            "image_url": result["url"],
            "public_id": result["public_id"],
            "filename": file.filename,
            "format": result["format"],
            "width": result["width"],
            "height": result["height"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/photos/generate", response_model=PhotoGenerationResponse)
async def generate_photo(
    original_url: str = Form(...),
    style: str = Form(...),
    prompt: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    """Generate AI photo using Replicate API"""
    if not REPLICATE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Replicate API not configured")
    
    if current_user.credits < 1:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    try:
        # Create photo record in database
        db = SessionLocal()
        photo = GeneratedPhoto(
            user_id=current_user.id,
            original_url=original_url,
            style=style,
            prompt=prompt,
            status="processing"
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        
        # Deduct credit
        current_user.credits -= 1
        db.commit()
        
        # Initialize Replicate client
        if not REPLICATE_API_TOKEN:
            raise HTTPException(status_code=500, detail="Replicate API not configured")
        
        replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
        
        try:
            # Select appropriate model and parameters based on style
            model_params = {
                "corporate": {
                    "model": "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
                    "style_strength": 25,
                    "steps": 50
                },
                "creative": {
                    "model": "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
                    "style_strength": 30,
                    "steps": 60
                },
                "formal": {
                    "model": "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
                    "style_strength": 20,
                    "steps": 50
                },
                "casual": {
                    "model": "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
                    "style_strength": 35,
                    "steps": 55
                }
            }
            
            params = model_params.get(style, model_params["corporate"])
            
            # Process with Replicate API using PhotoMaker model
            output = replicate_client.run(
                params["model"],
                input={
                    "input_image": original_url,
                    "style": style,
                    "num_outputs": 1,
                    "style_strength_ratio": params["style_strength"],
                    "num_inference_steps": params["steps"]
                }
            )
            
            # Get processed image URL
            processed_url = output[0] if output else None
            
            if not processed_url:
                raise Exception("No output from AI model")
            
            # Upload generated image to Cloudinary
            try:
                cloudinary_result = await storage.upload_from_url(
                    url=processed_url,
                    user_id=current_user.id,
                    folder="generated",
                    public_id=f"generated_{photo.id}_{style}"
                )
                
                # Generate thumbnail
                thumbnail_url = await storage.generate_thumbnail(
                    public_id=cloudinary_result["public_id"],
                    width=300,
                    height=300
                )
                
                # Update photo record with Cloudinary URLs
                photo.processed_url = cloudinary_result["url"]
                photo.processed_public_id = cloudinary_result["public_id"]
                photo.thumbnail_url = thumbnail_url
                photo.status = "completed"
                db.commit()
                
            except Exception as cloudinary_error:
                # Fallback to original URL if Cloudinary fails
                photo.processed_url = processed_url
                photo.status = "completed"
                db.commit()
                print(f"Cloudinary upload failed, using original URL: {cloudinary_error}")
            
            # Create credit transaction record
            credit_transaction = CreditTransaction(
                user_id=current_user.id,
                amount=-1,
                transaction_type="photo_generation",
                description=f"Photo generation - {style} style"
            )
            db.add(credit_transaction)
            db.commit()
            
            return PhotoGenerationResponse(
                id=photo.id,
                user_id=photo.user_id,
                original_image_url=original_url,
                generated_image_url=processed_url,
                style=photo.style,
                prompt=prompt,
                status=photo.status,
                created_at=photo.created_at
            )
            
        except Exception as replicate_error:
            # Update photo status to failed
            photo.status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail=f"AI processing failed: {str(replicate_error)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)