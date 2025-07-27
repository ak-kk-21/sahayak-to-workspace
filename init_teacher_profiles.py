#!/usr/bin/env python3
"""
Teacher Profiles Database Initialization Script
This script sets up the Firebase Firestore database for teacher profiles
"""

import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        print("✅ Firebase already initialized")
    except ValueError:
        # Initialize Firebase with service account
        cred = credentials.Certificate("firebase-auth.json")
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    
    return firestore.client()

def create_sample_teacher_profiles(db):
    """Create sample teacher profiles for testing"""
    
    sample_profiles = [
        {
            "uid": "sample_teacher_1",
            "email": "teacher1@school.com",
            "name": "Priya Sharma",
            "school_name": "Delhi Public School",
            "gender": "Female",
            "board": "CBSE",
            "grades_taught": ["6", "7", "8"],
            "languages": ["English", "Hindi"],
            "bio": "Experienced mathematics teacher with 8 years of experience in CBSE schools. Passionate about making math fun and accessible for all students.",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        },
        {
            "uid": "sample_teacher_2", 
            "email": "teacher2@school.com",
            "name": "Rajesh Kumar",
            "school_name": "St. Mary's Convent",
            "gender": "Male",
            "board": "ICSE",
            "grades_taught": ["9", "10", "11", "12"],
            "languages": ["English", "Hindi", "Tamil"],
            "bio": "Senior physics teacher with 12 years of experience. Specializes in preparing students for competitive exams and board examinations.",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        },
        {
            "uid": "sample_teacher_3",
            "email": "teacher3@school.com", 
            "name": "Anita Patel",
            "school_name": "Government High School",
            "gender": "Female",
            "board": "State",
            "grades_taught": ["1", "2", "3", "4", "5"],
            "languages": ["English", "Hindi", "Gujarati"],
            "bio": "Primary school teacher with 6 years of experience. Focuses on creating a nurturing environment for young learners.",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
    ]
    
    print("📝 Creating sample teacher profiles...")
    
    for profile in sample_profiles:
        try:
            db.collection('teacher_profiles').document(profile['uid']).set(profile)
            print(f"✅ Created profile for {profile['name']} ({profile['email']})")
        except Exception as e:
            print(f"❌ Error creating profile for {profile['name']}: {e}")
    
    print(f"🎉 Created {len(sample_profiles)} sample teacher profiles")

def verify_collection_structure(db):
    """Verify the teacher_profiles collection structure"""
    print("\n🔍 Verifying collection structure...")
    
    try:
        # Get all documents in teacher_profiles collection
        profiles = db.collection('teacher_profiles').stream()
        profile_count = 0
        
        for profile in profiles:
            profile_count += 1
            data = profile.to_dict()
            print(f"📋 Profile {profile_count}: {data.get('name', 'Unknown')} - {data.get('email', 'No email')}")
            
            # Check required fields
            required_fields = ['uid', 'email', 'name', 'school_name', 'board', 'grades_taught', 'languages']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
        
        print(f"\n📊 Total teacher profiles: {profile_count}")
        
    except Exception as e:
        print(f"❌ Error verifying collection: {e}")

def create_firestore_indexes():
    """Create Firestore indexes for better query performance"""
    print("\n🔧 Setting up Firestore indexes...")
    
    # Note: Indexes are typically created through the Firebase Console
    # or using the Firebase CLI. This is just for documentation.
    
    indexes = [
        {
            "collection": "teacher_profiles",
            "fields": [
                {"fieldPath": "board", "order": "ASCENDING"},
                {"fieldPath": "created_at", "order": "DESCENDING"}
            ]
        },
        {
            "collection": "teacher_profiles", 
            "fields": [
                {"fieldPath": "grades_taught", "arrayConfig": "CONTAINS"},
                {"fieldPath": "board", "order": "ASCENDING"}
            ]
        },
        {
            "collection": "teacher_profiles",
            "fields": [
                {"fieldPath": "languages", "arrayConfig": "CONTAINS"},
                {"fieldPath": "board", "order": "ASCENDING"}
            ]
        }
    ]
    
    print("📋 Recommended indexes for teacher_profiles collection:")
    for i, index in enumerate(indexes, 1):
        print(f"   {i}. {index['collection']} - {[f['fieldPath'] for f in index['fields']]}")
    
    print("\n💡 To create these indexes:")
    print("   1. Go to Firebase Console > Firestore Database > Indexes")
    print("   2. Click 'Add Index'")
    print("   3. Select 'teacher_profiles' collection")
    print("   4. Add the fields as shown above")

def main():
    """Main function to initialize the teacher profiles database"""
    print("🚀 Initializing Teacher Profiles Database")
    print("=" * 50)
    
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Create sample profiles
        create_sample_teacher_profiles(db)
        
        # Verify structure
        verify_collection_structure(db)
        
        # Setup indexes
        create_firestore_indexes()
        
        print("\n✅ Teacher Profiles Database initialization completed!")
        print("\n📚 Next steps:")
        print("   1. Update Firestore security rules (see firestore_rules_teacher_profiles.txt)")
        print("   2. Test the profile API endpoints")
        print("   3. Verify the frontend profile form works correctly")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure firebase-auth.json exists in the project root")
        print("   2. Check that Firebase project is properly configured")
        print("   3. Verify Firestore is enabled in your Firebase project")

if __name__ == "__main__":
    main() 