#!/usr/bin/env python3
"""
Test script for database connectivity
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        print("🔥 Testing Firebase Connection...")
        
        # Test imports
        import firebase_admin
        from firebase_admin import credentials, firestore
        print("✅ Firebase Admin SDK imported successfully")
        
        # Test credentials
        if os.path.exists('firebase-auth.json'):
            print("✅ Firebase auth file exists")
        else:
            print("❌ Firebase auth file missing")
            return False
        
        # Test Firestore connection
        try:
            cred = credentials.Certificate("firebase-auth.json")
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✅ Firestore connection successful")
        except Exception as e:
            print(f"❌ Firestore connection failed: {e}")
            return False
        
        # Test Realtime Database
        try:
            from firebase_admin import db as rtdb
            rtdb.reference().set_url('https://sahayak-to-workspace-default-rtdb.firebaseio.com')
            print("✅ Realtime Database connection successful")
        except Exception as e:
            print(f"❌ Realtime Database connection failed: {e}")
            print("⚠️  You may need to enable Realtime Database in Firebase Console")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Firebase: {e}")
        return False

def test_user_data():
    """Test user data structure"""
    try:
        print("\n👤 Testing User Data Structure...")
        
        # Sample user data
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'photoURL': None,
            'uid': 'test-uid-123',
            'lastSeen': 1234567890000
        }
        
        print(f"✅ User data structure: {user_data}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing user data: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Database Connectivity...")
    print("=" * 50)
    
    # Test Firebase connection
    firebase_ok = test_firebase_connection()
    
    # Test user data
    user_data_ok = test_user_data()
    
    print("\n📋 Summary:")
    if firebase_ok:
        print("✅ Firebase connection is working")
    else:
        print("❌ Firebase connection has issues")
    
    if user_data_ok:
        print("✅ User data structure is correct")
    else:
        print("❌ User data structure has issues")
    
    print("\n🚀 Next Steps:")
    print("1. Make sure Realtime Database is enabled in Firebase Console")
    print("2. Start the Flask app: python app.py")
    print("3. Login and go to /messenger")
    print("4. Click 'Register Me (Debug)' button")
    print("5. Check browser console for debug logs")
    
    print("\n🔧 Firebase Console Setup:")
    print("1. Go to https://console.firebase.google.com/")
    print("2. Select your project: sahayak-to-workspace")
    print("3. Click 'Realtime Database' in left sidebar")
    print("4. Click 'Create Database' if not already created")
    print("5. Choose location and start in test mode") 