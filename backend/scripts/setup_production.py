#!/usr/bin/env python3
"""
Production setup script for PhotoPro AI backend.
Configures database, creates admin user, and sets up initial data.
"""

import os
import sys
import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, CreditTransaction
from auth import get_password_hash
from config import settings

def create_admin_user():
    """Create admin user for production"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("Admin user already exists")
            return admin_user
        
        # Create admin user
        admin_user = User(
            email="admin@photopro.ai",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123!@#"),
            plan="enterprise",
            credits=9999,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create welcome credit transaction
        credit_transaction = CreditTransaction(
            user_id=admin_user.id,
            amount=9999,
            transaction_type="admin_setup",
            description="Initial admin credits"
        )
        db.add(credit_transaction)
        db.commit()
        
        print(f"Admin user created: {admin_user.username}")
        print(f"Admin email: {admin_user.email}")
        print(f"Admin password: admin123!@#")
        print("⚠️  CHANGE THE ADMIN PASSWORD IMMEDIATELY!")
        
        return admin_user
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def setup_database():
    """Set up database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def verify_environment():
    """Verify all required environment variables are set"""
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY", 
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_BUCKET_NAME",
        "AWS_REGION",
        "REPLICATE_API_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_database_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_s3_connection():
    """Test AWS S3 connection"""
    try:
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        s3_client.head_bucket(Bucket=settings.AWS_BUCKET_NAME)
        print("✅ S3 connection successful")
        return True
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

def test_replicate_connection():
    """Test Replicate API connection"""
    try:
        import replicate
        client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
        # Test with a simple model list
        models = client.models.list()
        print("✅ Replicate API connection successful")
        return True
    except Exception as e:
        print(f"❌ Replicate API connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PhotoPro AI Production Setup")
    print("=" * 40)
    
    # Verify environment
    if not verify_environment():
        print("\n❌ Setup failed: Missing environment variables")
        sys.exit(1)
    
    # Test connections
    print("\n🔍 Testing connections...")
    
    if not test_database_connection():
        print("\n❌ Setup failed: Database connection failed")
        sys.exit(1)
    
    if not test_s3_connection():
        print("\n❌ Setup failed: S3 connection failed")
        sys.exit(1)
    
    if not test_replicate_connection():
        print("\n❌ Setup failed: Replicate API connection failed")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("\n❌ Setup failed: Database setup failed")
        sys.exit(1)
    
    # Create admin user
    print("\n👤 Creating admin user...")
    admin_user = create_admin_user()
    if not admin_user:
        print("\n❌ Setup failed: Could not create admin user")
        sys.exit(1)
    
    print("\n🎉 Production setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Change the admin password immediately")
    print("2. Configure your frontend to point to this backend")
    print("3. Test all API endpoints")
    print("4. Set up monitoring and alerts")
    print("\n🔗 API Documentation: /docs")
    print("🔗 Health Check: /health")

if __name__ == "__main__":
    main()
