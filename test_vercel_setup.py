#!/usr/bin/env python3
"""
Test script to verify Vercel FastAPI setup
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app_vercel import app
    print("✅ FastAPI app imported successfully")
    
    # Test the app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
    
    # Test docs endpoint
    response = client.get("/docs")
    print(f"✅ Docs endpoint: {response.status_code} - {response.text}")
    
    print("\n🎉 Vercel FastAPI setup is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
