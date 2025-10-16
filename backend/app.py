from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./photopro.db")

if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    credits = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedPhoto(Base):
    __tablename__ = "generated_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    original_url = Column(String)
    generated_url = Column(String)
    style = Column(String)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

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
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if DATABASE_URL.startswith("postgresql") else "sqlite"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected" if DATABASE_URL.startswith("postgresql") else "sqlite",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": [{"id": u.id, "email": u.email, "username": u.username, "credits": u.credits} for u in users]}

@app.get("/photos")
def get_photos(db: Session = Depends(get_db)):
    photos = db.query(GeneratedPhoto).all()
    return {"photos": [{"id": p.id, "user_id": p.user_id, "style": p.style, "status": p.status} for p in photos]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)