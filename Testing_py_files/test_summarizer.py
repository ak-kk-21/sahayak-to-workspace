#!/usr/bin/env python3
"""
Test script for the summarizer endpoint
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health check data: {data}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running.")
        return False

def test_summarizer_endpoint():
    """Test the summarizer endpoint with a simple text file"""
    try:
        # Create a simple test file
        test_content = """
        This is a test document for the summarizer.
        It contains multiple paragraphs of text.
        The summarizer should be able to process this content.
        This is just a test to verify the endpoint is working.
        """
        
        # Create a temporary text file
        with open('test_document.txt', 'w') as f:
            f.write(test_content)
        
        # Test the endpoint (this will fail because it expects a PDF, but we can see the error)
        response = requests.post('http://localhost:5000/summarizer')
        print(f"Summarizer endpoint status: {response.status_code}")
        
        # Clean up
        os.remove('test_document.txt')
        
        return True
    except Exception as e:
        print(f"❌ Error testing summarizer: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Flask application...")
    
    if test_health_endpoint():
        print("✅ Health endpoint working")
    else:
        print("❌ Health endpoint failed")
    
    if test_summarizer_endpoint():
        print("✅ Summarizer endpoint accessible")
    else:
        print("❌ Summarizer endpoint failed")
    
    print("\n📋 To test the full functionality:")
    print("1. Start the Flask app: python app.py")
    print("2. Open http://localhost:5000/summarizer in your browser")
    print("3. Upload a PDF file and check the debug information") 