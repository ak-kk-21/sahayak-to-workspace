#!/usr/bin/env python3
"""
Test Script for Teacher Profile Setup
This script tests the complete profile system
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_server_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    # Test basic API
    try:
        response = requests.get(f"{BASE_URL}/api/test")
        if response.status_code == 200:
            print("✅ Basic API endpoint working")
        else:
            print(f"❌ Basic API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Basic API error: {e}")
    
    # Test profile endpoint (should require auth)
    try:
        response = requests.get(f"{BASE_URL}/api/profile")
        if response.status_code == 401:
            print("✅ Profile endpoint correctly requires authentication")
        else:
            print(f"❌ Profile endpoint should require auth, got: {response.status_code}")
    except Exception as e:
        print(f"❌ Profile endpoint error: {e}")

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if Firebase is initialized
        try:
            firebase_admin.get_app()
            print("✅ Firebase Admin SDK initialized")
        except ValueError:
            print("❌ Firebase Admin SDK not initialized")
            return False
        
        # Test Firestore connection
        db = firestore.client()
        
        # Try to read from teacher_profiles collection
        profiles = db.collection('teacher_profiles').limit(1).stream()
        profile_count = 0
        for profile in profiles:
            profile_count += 1
        
        print(f"✅ Firestore connection working (found {profile_count} profiles)")
        return True
        
    except ImportError:
        print("❌ Firebase Admin SDK not available")
        return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_profile_creation():
    """Test creating a sample profile"""
    print("\n📝 Testing profile creation...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        import datetime
        
        db = firestore.client()
        
        # Create test profile
        test_profile = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test Teacher",
            "school_name": "Test School",
            "gender": "Female",
            "board": "CBSE",
            "grades_taught": ["6", "7", "8"],
            "languages": ["English", "Hindi"],
            "bio": "Test teacher profile created by test script",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        # Save to Firestore
        db.collection('teacher_profiles').document('test_user_123').set(test_profile)
        print("✅ Test profile created successfully")
        
        # Read it back
        doc = db.collection('teacher_profiles').document('test_user_123').get()
        if doc.exists:
            data = doc.to_dict()
            print(f"✅ Profile read back: {data['name']} - {data['school_name']}")
        else:
            print("❌ Profile not found after creation")
        
        # Clean up
        db.collection('teacher_profiles').document('test_user_123').delete()
        print("✅ Test profile cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Teacher Profile System Test")
    print("=" * 50)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server is not running. Please start the Flask app first:")
        print("   python app.py")
        return
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test database connection
    if test_database_connection():
        # Test profile creation
        test_profile_creation()
    
    print("\n🎉 Test completed!")
    print("\n📋 Next steps:")
    print("   1. Start the Flask app: python app.py")
    print("   2. Login to your account")
    print("   3. Go to /profile")
    print("   4. Fill out the form and submit")
    print("   5. Check browser console for any errors")
    print("   6. Check Firebase Console for the saved profile")

if __name__ == "__main__":
    main() 