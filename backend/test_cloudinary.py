#!/usr/bin/env python3
"""
Test script to verify Cloudinary integration is working correctly.
Run this to test the Cloudinary connection and functionality.
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
from datetime import datetime

def test_cloudinary_connection():
    """Test Cloudinary API connection and configuration"""
    print("🧪 Testing Cloudinary Integration")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get Cloudinary credentials
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Cloudinary credentials not found in environment variables")
        print("   Please set the following in your .env file:")
        print("   CLOUDINARY_CLOUD_NAME=your-cloud-name")
        print("   CLOUDINARY_API_KEY=your-api-key")
        print("   CLOUDINARY_API_SECRET=your-api-secret")
        return False
    
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        print("✅ Cloudinary client configured successfully")
        
        # Test connection with ping
        result = cloudinary.api.ping()
        if result.get('status') == 'ok':
            print("✅ Cloudinary connection successful!")
        else:
            print(f"❌ Cloudinary connection failed: {result}")
            return False
        
        # Test upload functionality with a simple image
        print("\n🔍 Testing upload functionality...")
        
        # Create a simple test image (1x1 pixel PNG)
        import io
        from PIL import Image
        
        # Create a simple test image
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
            print(f"   Public ID: {upload_result['public_id']}")
            
            # Test deletion
            delete_result = cloudinary.uploader.destroy(upload_result['public_id'])
            if delete_result.get('result') == 'ok':
                print("✅ Test image deletion successful!")
            else:
                print(f"⚠️  Test image deletion failed: {delete_result}")
            
        else:
            print("❌ Test image upload failed")
            return False
        
        # Test different transformations
        print("\n🎨 Testing image transformations...")
        
        # Test thumbnail generation
        thumbnail_url = cloudinary.utils.cloudinary_url(
            upload_result['public_id'],
            width=50,
            height=50,
            crop="fill",
            quality="auto",
            fetch_format="auto"
        )[0]
        
        print(f"✅ Thumbnail URL generated: {thumbnail_url}")
        
        print("\n🎉 All Cloudinary tests passed!")
        print("\n📋 Next steps:")
        print("1. Update your .env.production with Cloudinary credentials")
        print("2. Deploy backend to Railway")
        print("3. Test end-to-end photo generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Cloudinary test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Cloudinary credentials are correct")
        print("2. Verify you have sufficient credits in your Cloudinary account")
        print("3. Check your internet connection")
        print("4. Try again in a few minutes")
        return False

def main():
    """Main test function"""
    success = test_cloudinary_connection()
    
    if success:
        print("\n✅ All tests passed! Cloudinary is ready for integration.")
    else:
        print("\n❌ Tests failed. Please fix the issues above before proceeding.")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
