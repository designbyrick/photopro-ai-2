"""
Test suite for PhotoPro AI backend.
Comprehensive testing of API endpoints, authentication, and business logic.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import json

from main import app
from database import get_db, Base
from models import User, GeneratedPhoto, CreditTransaction
from auth import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        credits=10,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_signup_success(self, db_session):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "newpassword123"
        }
        
        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["credits"] == 3  # Welcome bonus
    
    def test_signup_duplicate_email(self, db_session, test_user):
        """Test signup with duplicate email"""
        user_data = {
            "email": "test@example.com",
            "username": "differentuser",
            "full_name": "Different User",
            "password": "password123"
        }
        
        response = client.post("/auth/signup", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_login_success(self, test_user):
        """Test successful login"""
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_user):
        """Test login with invalid credentials"""
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, auth_headers, test_user):
        """Test getting current user info"""
        response = client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

class TestPhotoEndpoints:
    """Test photo-related endpoints"""
    
    @patch('main.s3_client')
    def test_upload_photo_success(self, mock_s3, auth_headers):
        """Test successful photo upload"""
        mock_s3.put_object.return_value = None
        
        # Create a test image file
        test_image = b"fake_image_data"
        
        response = client.post(
            "/photos/upload",
            headers=auth_headers,
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert data["message"] == "File uploaded successfully"
    
    def test_upload_photo_invalid_file(self, auth_headers):
        """Test upload with invalid file type"""
        test_file = b"not_an_image"
        
        response = client.post(
            "/photos/upload",
            headers=auth_headers,
            files={"file": ("test.txt", test_file, "text/plain")}
        )
        
        assert response.status_code == 400
    
    @patch('main.replicate_client')
    @patch('main.s3_client')
    def test_generate_photo_success(self, mock_s3, mock_replicate, auth_headers, test_user):
        """Test successful photo generation"""
        mock_replicate.run.return_value = ["https://example.com/processed.jpg"]
        mock_s3.put_object.return_value = None
        
        response = client.post(
            "/photos/generate",
            headers=auth_headers,
            data={
                "original_url": "https://example.com/original.jpg",
                "style": "corporate"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["processed_url"] == "https://example.com/processed.jpg"
    
    def test_generate_photo_insufficient_credits(self, auth_headers, test_user, db_session):
        """Test photo generation with insufficient credits"""
        # Set user credits to 0
        test_user.credits = 0
        db_session.commit()
        
        response = client.post(
            "/photos/generate",
            headers=auth_headers,
            data={
                "original_url": "https://example.com/original.jpg",
                "style": "corporate"
            }
        )
        
        assert response.status_code == 400
        assert "Insufficient credits" in response.json()["detail"]
    
    def test_get_photo_history(self, auth_headers, test_user, db_session):
        """Test getting photo history"""
        # Create test photos
        photo1 = GeneratedPhoto(
            user_id=test_user.id,
            style="corporate",
            original_url="https://example.com/1.jpg",
            processed_url="https://example.com/processed1.jpg",
            status="completed"
        )
        photo2 = GeneratedPhoto(
            user_id=test_user.id,
            style="creative",
            original_url="https://example.com/2.jpg",
            processed_url="https://example.com/processed2.jpg",
            status="completed"
        )
        
        db_session.add_all([photo1, photo2])
        db_session.commit()
        
        response = client.get("/photos/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["style"] == "creative"  # Most recent first

class TestCreditSystem:
    """Test credit-related functionality"""
    
    def test_get_credits(self, auth_headers, test_user):
        """Test getting user credits"""
        response = client.get("/users/me/credits", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["credits"] == test_user.credits
    
    def test_purchase_credits(self, auth_headers, test_user, db_session):
        """Test credit purchase"""
        response = client.post(
            "/credits/purchase",
            headers=auth_headers,
            json={"plan": "pro"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Successfully upgraded" in data["message"]
        
        # Check user credits were updated
        db_session.refresh(test_user)
        assert test_user.credits >= 50  # Pro plan credits
    
    def test_credit_transaction_history(self, auth_headers, test_user, db_session):
        """Test getting credit transaction history"""
        # Create test transaction
        transaction = CreditTransaction(
            user_id=test_user.id,
            amount=-1,
            transaction_type="photo_generation",
            description="Test transaction"
        )
        db_session.add(transaction)
        db_session.commit()
        
        response = client.get("/credits/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["amount"] == -1

class TestValidation:
    """Test input validation"""
    
    def test_signup_validation(self):
        """Test signup form validation"""
        # Test short password
        response = client.post("/auth/signup", json={
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "123"
        })
        assert response.status_code == 422
        
        # Test invalid email
        response = client.post("/auth/signup", json={
            "email": "invalid-email",
            "username": "testuser",
            "full_name": "Test User",
            "password": "validpassword123"
        })
        assert response.status_code == 422
    
    def test_photo_style_validation(self, auth_headers):
        """Test photo generation style validation"""
        response = client.post(
            "/photos/generate",
            headers=auth_headers,
            data={
                "original_url": "https://example.com/original.jpg",
                "style": "invalid_style"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid style" in response.json()["detail"]

class TestErrorHandling:
    """Test error handling"""
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        response = client.get("/users/me")
        assert response.status_code == 401
    
    def test_invalid_token(self):
        """Test accessing endpoints with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401
    
    def test_nonexistent_photo(self, auth_headers):
        """Test accessing nonexistent photo"""
        response = client.get("/photos/99999", headers=auth_headers)
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__])
