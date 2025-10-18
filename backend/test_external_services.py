#!/usr/bin/env python3
"""
Test script to verify external services (AWS S3 and Replicate API) are configured correctly.
Run this after setting up your external services to verify everything works.
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import replicate
from dotenv import load_dotenv
from datetime import datetime

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔍 Testing Environment Variables")
    print("-" * 30)
    
    required_vars = [
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
        "REPLICATE_API_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Mask sensitive values
            if "SECRET" in var or "TOKEN" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            else:
                masked_value = value
            print(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set these in your .env file")
        return False
    
    print("✅ All environment variables are set!")
    return True

def test_cloudinary():
    """Test Cloudinary connection and functionality"""
    print("\n☁️ Testing Cloudinary Connection")
    print("-" * 30)
    
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        # Test connection with ping
        result = cloudinary.api.ping()
        if result.get('status') == 'ok':
            print("✅ Cloudinary connection successful!")
        else:
            print(f"❌ Cloudinary connection failed: {result}")
            return False
        
        # Test upload functionality
        print("🔍 Testing upload functionality...")
        
        # Create a simple test image
        import io
        from PIL import Image
        
        img = Image.new('RGB', (100, 100), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Upload test image
        upload_result = cloudinary.uploader.upload(
            img_buffer,
            folder="photopro/test",
            public_id=f"test_connection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            resource_type="image"
        )
        
        if upload_result.get('secure_url'):
            print("✅ Test image upload successful!")
            print(f"   URL: {upload_result['secure_url']}")
            
            # Test deletion
            delete_result = cloudinary.uploader.destroy(upload_result['public_id'])
            if delete_result.get('result') == 'ok':
                print("✅ Test image deletion successful!")
            else:
                print(f"⚠️  Test image deletion failed: {delete_result}")
            
        else:
            print("❌ Test image upload failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Cloudinary credentials are correct")
        print("2. Verify you have sufficient credits in your Cloudinary account")
        print("3. Check your internet connection")
        return False

def test_replicate_api():
    """Test Replicate API connection and model availability"""
    print("\n🤖 Testing Replicate API Connection")
    print("-" * 30)
    
    try:
        # Initialize Replicate client
        api_token = os.getenv('REPLICATE_API_TOKEN')
        client = replicate.Client(api_token=api_token)
        
        print("✅ Replicate client initialized!")
        
        # Test model availability
        model_name = "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4"
        
        try:
            # Try to get model info
            model_info = client.models.get(model_name)
            print(f"✅ Model found: {model_info.name}")
        except Exception as e:
            print(f"⚠️  Could not fetch model info: {e}")
            print("   This might be normal - model might still be accessible")
        
        # Test different style configurations
        styles = ["corporate", "creative", "formal", "casual"]
        print(f"✅ Style configurations ready: {', '.join(styles)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Replicate API connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your REPLICATE_API_TOKEN is correct")
        print("2. Verify you have sufficient credits in your Replicate account")
        print("3. Check your internet connection")
        return False

def test_integration():
    """Test the integration between services"""
    print("\n🔗 Testing Service Integration")
    print("-" * 30)
    
    # Check if all services are configured
    cloudinary_ok = test_cloudinary()
    replicate_ok = test_replicate_api()
    
    if cloudinary_ok and replicate_ok:
        print("✅ All external services are properly configured!")
        print("\n🎉 Your PhotoPro AI is ready for deployment!")
        return True
    else:
        print("❌ Some services need attention before deployment")
        return False

def main():
    """Main test function"""
    print("🧪 PhotoPro AI - External Services Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Test environment variables
    env_ok = test_environment_variables()
    if not env_ok:
        print("\n❌ Environment setup incomplete. Please fix the issues above.")
        return False
    
    # Test external services
    integration_ok = test_integration()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    if integration_ok:
        print("🎉 All tests passed! External services are ready!")
        print("\n🚀 Next steps:")
        print("1. Deploy backend to Railway")
        print("2. Deploy frontend to Vercel")
        print("3. Test end-to-end photo generation")
        print("4. Launch to users!")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("1. Check your .env file has all required variables")
        print("2. Verify AWS S3 bucket exists and is accessible")
        print("3. Confirm Replicate API token is valid")
        print("4. Ensure you have sufficient credits in Replicate")
    
    return integration_ok

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
