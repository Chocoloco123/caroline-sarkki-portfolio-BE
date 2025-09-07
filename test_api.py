#!/usr/bin/env python3
"""
Simple test script to verify the FastAPI application works correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_homepage():
    """Test the homepage endpoint"""
    print("Testing homepage endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Homepage endpoint working!")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Homepage failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on port 8000")
        return False

def test_query_endpoint():
    """Test the query endpoint"""
    print("\nTesting query endpoint...")
    try:
        test_query = {
            "query": "What is Caroline's experience with KQED?"
        }
        
        response = requests.post(
            f"{BASE_URL}/query",
            json=test_query,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Query endpoint working!")
            print(f"   Query: {data.get('query')}")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            print(f"   Model: {data.get('model_used')}")
            return True
        else:
            print(f"❌ Query endpoint failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on port 8000")
        return False

if __name__ == "__main__":
    print("🧪 Testing Caroline Sarkki Portfolio API")
    print("=" * 50)
    
    homepage_ok = test_homepage()
    query_ok = test_query_endpoint()
    
    print("\n" + "=" * 50)
    if homepage_ok and query_ok:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nTo run the API:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
        print("2. Run: python main.py")
        print("3. Or use Docker: docker-compose up --build")
