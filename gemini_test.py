#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 Gemini API Test Script
Simple test to verify Google Gemini API is working correctly
"""

import os
from dotenv import load_dotenv
from google import genai

def test_gemini_api():
    """Test basic Gemini API functionality"""
    print("🧪 GEMINI API TEST STARTING...")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("💡 Please create a .env file with your API key:")
        print("   GEMINI_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Configure Gemini client
        client = genai.Client(api_key=api_key)
        print("✅ Gemini API configured")
        
        # Get model info
        model_name = "gemini-2.0-flash-exp"
        print(f"✅ Using model: {model_name}")
        
        # Simple test prompt
        print("\n📝 Sending test prompt...")
        test_prompt = "Hello! Please respond with a simple greeting and confirm you're working."
        
        response = client.models.generate_content(
            model=model_name,
            contents=test_prompt
        )
        
        print("\n✅ API Response received!")
        print("=" * 60)
        print("📄 RESPONSE:")
        print(response.text)
        print("=" * 60)
        
        # Test with structured data
        print("\n📊 Testing structured analysis...")
        analysis_prompt = """
        Analyze this sample review and provide:
        1. Sentiment (Positive/Negative/Neutral)
        2. Key topics mentioned
        3. Brief summary
        
        Review: "Great place! The service was excellent and the food was delicious. 
        However, it was a bit expensive and the wait time was long."
        """
        
        analysis_response = client.models.generate_content(
            model=model_name,
            contents=analysis_prompt
        )
        
        print("\n✅ Analysis Response:")
        print("=" * 60)
        print(analysis_response.text)
        print("=" * 60)
        
        print("\n🎉 GEMINI API TEST SUCCESSFUL!")
        print("✅ API is working correctly")
        print(f"✅ Model: {model_name}")
        print("✅ Ready for review analysis")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during API test: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Verify your API key is correct")
        print("   2. Check your internet connection")
        print("   3. Ensure you have google-generativeai installed:")
        print("      pip install google-generativeai")
        print("   4. Check API quota limits at: https://aistudio.google.com/")
        return False

def show_model_info():
    """Show available Gemini models"""
    print("\n📋 Available Gemini Models:")
    print("=" * 60)
    
    models_info = """
    🆓 Free Models (Recommended):
    
    1. gemini-2.0-flash-exp
       - Latest experimental model
       - Fastest and most efficient
       - Free tier available
       - Best for most use cases
       - Rate limit: 15 requests/minute (free tier)
    
    2. gemini-1.5-flash
       - Stable flash model
       - Fast and reliable
       - Good for production
    
    3. gemini-1.5-pro
       - Most capable
       - Better reasoning
       - Lower rate limits on free tier
    
    💡 For this project, we'll use gemini-2.0-flash-exp:
       - Latest technology
       - Perfect balance of speed and quality
       - Sufficient for review analysis
       - Generous free tier
    """
    
    print(models_info)

if __name__ == "__main__":
    # Show model information
    show_model_info()
    
    # Run test
    print("\n" + "=" * 60)
    success = test_gemini_api()
    
    if success:
        print("\n✅ You can now use Gemini API for review analysis!")
        print("📝 Next step: Create review analyzer with Gemini")
    else:
        print("\n❌ Please fix the errors above before proceeding")
