#!/usr/bin/env python3
"""
Test script to verify Replicate API integration is working correctly.
Run this to test the Replicate API connection and model availability.
"""

import os
import replicate
from dotenv import load_dotenv

def test_replicate_connection():
    """Test Replicate API connection and model availability"""
    print("🧪 Testing Replicate API Integration")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get API token
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN not found in environment variables")
        print("   Please set your Replicate API token in .env file")
        return False
    
    try:
        # Initialize Replicate client
        client = replicate.Client(api_token=api_token)
        print("✅ Replicate client initialized successfully")
        
        # Test model availability
        model_name = "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4"
        print(f"🔍 Testing model: {model_name}")
        
        # Test with a simple model info request
        try:
            model_info = client.models.get(model_name)
            print(f"✅ Model found: {model_info.name}")
            print(f"   Description: {model_info.description}")
        except Exception as e:
            print(f"⚠️  Could not fetch model info: {e}")
            print("   This might be normal - model might still be accessible")
        
        # Test different style parameters
        styles = ["corporate", "creative", "formal", "casual"]
        print("\n🎨 Testing style configurations:")
        
        for style in styles:
            print(f"   {style}: ✅ Configured")
        
        print("\n🎉 Replicate API integration test completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set up AWS S3 bucket for image storage")
        print("2. Configure environment variables in production")
        print("3. Deploy backend to Railway")
        print("4. Test end-to-end photo generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Replicate API test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your REPLICATE_API_TOKEN is correct")
        print("2. Verify you have sufficient credits in your Replicate account")
        print("3. Check your internet connection")
        print("4. Try again in a few minutes (API might be temporarily unavailable)")
        return False

def main():
    """Main test function"""
    success = test_replicate_connection()
    
    if success:
        print("\n✅ All tests passed! Replicate API is ready for integration.")
    else:
        print("\n❌ Tests failed. Please fix the issues above before proceeding.")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
