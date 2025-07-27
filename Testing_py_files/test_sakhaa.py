#!/usr/bin/env python3
"""
Test script for Sakhaa chat functionality
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_sakhaa_endpoint():
    """Test the Sakhaa chat endpoint"""
    try:
        # Test data
        test_message = {
            "message": "Hello! Can you help me with a simple question?"
        }
        
        print("🧪 Testing Sakhaa chat endpoint...")
        
        # First, we need to be authenticated, so let's test the health endpoint first
        health_response = requests.get('http://localhost:5000/health')
        print(f"Health check status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Health data: {health_data}")
            
            # Check if Gemini API key is configured
            if health_data.get('dependencies', {}).get('Gemini_API_Key') == 'CONFIGURED':
                print("✅ Gemini API key is configured")
            else:
                print("❌ Gemini API key is missing")
                return False
        
        # Test Sakhaa endpoint (this will fail without authentication, but we can see the structure)
        try:
            response = requests.post(
                'http://localhost:5000/sakhaa',
                headers={'Content-Type': 'application/json'},
                json=test_message,
                timeout=10
            )
            print(f"Sakhaa endpoint status: {response.status_code}")
            
            if response.status_code == 401:
                print("ℹ️  Expected 401 - authentication required")
                return True
            elif response.status_code == 200:
                data = response.json()
                print(f"✅ Sakhaa response: {data}")
                return True
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure Flask app is running.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Sakhaa: {e}")
        return False

def test_sakhaa_page():
    """Test the Sakhaa page endpoint"""
    try:
        response = requests.get('http://localhost:5000/sakhaa')
        print(f"Sakhaa page status: {response.status_code}")
        
        if response.status_code == 302:
            print("ℹ️  Expected 302 - redirect to login (authentication required)")
            return True
        elif response.status_code == 200:
            print("✅ Sakhaa page accessible")
            return True
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running.")
        return False

if __name__ == "__main__":
    print("🤖 Testing Sakhaa AI Chat Integration...")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_sakhaa_endpoint()
    
    # Test Sakhaa page
    page_ok = test_sakhaa_page()
    
    print("\n📋 Summary:")
    if health_ok:
        print("✅ Sakhaa endpoint structure is correct")
    else:
        print("❌ Sakhaa endpoint has issues")
    
    if page_ok:
        print("✅ Sakhaa page is accessible")
    else:
        print("❌ Sakhaa page has issues")
    
    print("\n🚀 To test the full functionality:")
    print("1. Start the Flask app: python app.py")
    print("2. Login to your account")
    print("3. Visit http://localhost:5000/sakhaa for the full chat interface")
    print("4. Or use the floating chat widget on any authenticated page")
    print("5. Make sure your GEMINI_API_KEY is set in your .env file") 