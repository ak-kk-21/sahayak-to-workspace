#!/usr/bin/env python3
"""
Test script for the messenger functionality
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_messenger_endpoints():
    """Test the messenger endpoints"""
    try:
        print("🧪 Testing Messenger Endpoints...")
        
        # Test simple API endpoint first
        test_response = requests.get('http://localhost:5000/api/test')
        print(f"Test API status: {test_response.status_code}")
        if test_response.status_code == 200:
            try:
                test_data = test_response.json()
                print(f"✅ Test API working: {test_data}")
            except json.JSONDecodeError as e:
                print(f"❌ Test API JSON error: {e}")
        else:
            print(f"❌ Test API failed: {test_response.text[:100]}")
        
        # Test health endpoint
        health_response = requests.get('http://localhost:5000/health')
        print(f"Health check status: {health_response.status_code}")
        
        # Test messenger page (should redirect to login if not authenticated)
        messenger_response = requests.get('http://localhost:5000/messenger')
        print(f"Messenger page status: {messenger_response.status_code}")
        
        if messenger_response.status_code == 302:
            print("ℹ️  Expected 302 - redirect to login (authentication required)")
        elif messenger_response.status_code == 200:
            print("✅ Messenger page accessible")
        else:
            print(f"❌ Unexpected status: {messenger_response.status_code}")
        
        # Test user data API (should return 401 if not authenticated)
        user_data_response = requests.get('http://localhost:5000/api/user-data')
        print(f"User data API status: {user_data_response.status_code}")
        print(f"User data API headers: {dict(user_data_response.headers)}")
        
        if user_data_response.status_code == 401:
            print("ℹ️  Expected 401 - authentication required (not logged in)")
            try:
                error_data = user_data_response.json()
                print(f"✅ Error response: {error_data}")
            except json.JSONDecodeError as e:
                print(f"❌ Error response not JSON: {user_data_response.text[:100]}")
        elif user_data_response.status_code == 200:
            try:
                user_data = user_data_response.json()
                print(f"✅ User data: {user_data}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"❌ Response content (first 200 chars): {user_data_response.text[:200]}")
        else:
            print(f"❌ Unexpected status: {user_data_response.status_code}")
            print(f"❌ Response content (first 200 chars): {user_data_response.text[:200]}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing messenger: {e}")
        return False

def test_firebase_config():
    """Test Firebase configuration"""
    try:
        print("\n🔥 Testing Firebase Configuration...")
        
        # Check if Firebase config file exists
        if os.path.exists('firebase-auth.json'):
            print("✅ Firebase auth file exists")
        else:
            print("❌ Firebase auth file missing")
            return False
        
        # Check if Realtime Database URL is configured
        from firebase_config import FIREBASE_CONFIG
        if 'databaseURL' in FIREBASE_CONFIG:
            print(f"✅ Realtime Database URL: {FIREBASE_CONFIG['databaseURL']}")
        else:
            print("❌ Realtime Database URL not configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Firebase config: {e}")
        return False

if __name__ == "__main__":
    print("💬 Testing Messenger Integration...")
    print("=" * 50)
    
    # Test Firebase configuration
    firebase_ok = test_firebase_config()
    
    # Test endpoints
    endpoints_ok = test_messenger_endpoints()
    
    print("\n📋 Summary:")
    if firebase_ok:
        print("✅ Firebase configuration is correct")
    else:
        print("❌ Firebase configuration has issues")
    
    if endpoints_ok:
        print("✅ Messenger endpoints are accessible")
    else:
        print("❌ Messenger endpoints have issues")
    
    print("\n🚀 To test the full functionality:")
    print("1. Start the Flask app: python app.py")
    print("2. Login to your account")
    print("3. Visit http://localhost:5000/messenger")
    print("4. Make sure your Firebase Realtime Database is enabled")
    print("5. Test messaging between different users")
    
    print("\n⚠️  Important Notes:")
    print("- You need to enable Realtime Database in your Firebase console")
    print("- Set up proper security rules for the Realtime Database")
    print("- Multiple users need to be logged in to test messaging") 