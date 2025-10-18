#!/usr/bin/env python3
"""
Test script to verify PhotoPro AI deployment is working correctly.
Run this after deployment to verify all services are functioning.
"""

import requests
import json
import sys
from datetime import datetime

def test_backend_health(backend_url):
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check: PASSED")
            return True
        else:
            print(f"❌ Backend health check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend health check: FAILED (Error: {e})")
        return False

def test_api_docs(backend_url):
    """Test API documentation endpoint"""
    try:
        response = requests.get(f"{backend_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation: ACCESSIBLE")
            return True
        else:
            print(f"❌ API documentation: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API documentation: FAILED (Error: {e})")
        return False

def test_detailed_health(backend_url):
    """Test detailed health endpoint"""
    try:
        response = requests.get(f"{backend_url}/health/detailed", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Detailed health check: PASSED")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Uptime: {data.get('uptime_seconds', 0):.0f} seconds")
            return True
        else:
            print(f"❌ Detailed health check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Detailed health check: FAILED (Error: {e})")
        return False

def test_frontend(frontend_url):
    """Test frontend accessibility"""
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend: ACCESSIBLE")
            return True
        else:
            print(f"❌ Frontend: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend: FAILED (Error: {e})")
        return False

def test_api_endpoints(backend_url):
    """Test key API endpoints"""
    print("\n🔍 Testing API Endpoints")
    print("-" * 30)
    
    endpoints = [
        ("/", "API information"),
        ("/health", "Health check"),
        ("/docs", "API documentation")
    ]
    
    passed = 0
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: {description} - OK")
                passed += 1
            else:
                print(f"❌ {endpoint}: {description} - FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint}: {description} - ERROR ({e})")
    
    return passed == len(endpoints)

def test_cors_configuration(backend_url, frontend_url):
    """Test CORS configuration"""
    print("\n🔗 Testing CORS Configuration")
    print("-" * 30)
    
    try:
        headers = {
            'Origin': frontend_url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(f"{backend_url}/photos/upload", headers=headers, timeout=10)
        
        if response.status_code == 200:
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            if frontend_url in cors_headers or cors_headers == '*':
                print("✅ CORS configuration: OK")
                return True
            else:
                print(f"❌ CORS configuration: FAILED (Origin not allowed)")
                return False
        else:
            print(f"❌ CORS configuration: FAILED (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ CORS configuration: ERROR ({e})")
        return False

def main():
    """Main test function"""
    print("🧪 PhotoPro AI Deployment Test")
    print("=" * 40)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Get URLs from user input
    backend_url = input("Enter your Railway backend URL (e.g., https://xxx.railway.app): ").strip()
    if not backend_url.startswith('http'):
        backend_url = f"https://{backend_url}"
    
    frontend_url = input("Enter your Vercel frontend URL (e.g., https://xxx.vercel.app): ").strip()
    if not frontend_url.startswith('http'):
        frontend_url = f"https://{frontend_url}"
    
    print()
    print("🔍 Testing Backend Services...")
    print("-" * 30)
    
    # Test backend
    backend_health = test_backend_health(backend_url)
    api_docs = test_api_docs(backend_url)
    detailed_health = test_detailed_health(backend_url)
    api_endpoints = test_api_endpoints(backend_url)
    
    print()
    print("🎨 Testing Frontend...")
    print("-" * 30)
    
    # Test frontend
    frontend_ok = test_frontend(frontend_url)
    
    print()
    print("🔗 Testing Integration...")
    print("-" * 30)
    
    # Test integration
    cors_ok = test_cors_configuration(backend_url, frontend_url)
    
    print()
    print("📊 Test Results Summary")
    print("=" * 40)
    
    tests_passed = sum([backend_health, api_docs, detailed_health, frontend_ok, api_endpoints, cors_ok])
    total_tests = 6
    
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your deployment is working correctly!")
        print()
        print("🚀 Your PhotoPro AI application is ready!")
        print(f"   Backend: {backend_url}")
        print(f"   Frontend: {frontend_url}")
        print(f"   API Docs: {backend_url}/docs")
        print()
        print("📋 Next steps:")
        print("1. Test user registration and login")
        print("2. Test photo upload and generation")
        print("3. Monitor the application for any issues")
        print("4. Share with beta users for feedback")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print()
        print("🔧 Troubleshooting:")
        print("1. Check Railway logs for backend issues")
        print("2. Check Vercel logs for frontend issues")
        print("3. Verify environment variables are set correctly")
        print("4. Ensure all external services (AWS S3, Replicate) are configured")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
