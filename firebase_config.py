# Firebase configuration for OAuth setup
import os
from dotenv import load_dotenv

load_dotenv()

# Firebase Web SDK Configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAhku4CP7W6fmYMw6Vaq5akDTk4gMzG3_g",
    "authDomain": "sahayak-to-workspace.firebaseapp.com",
    "projectId": "sahayak-to-workspace",
    "storageBucket": "sahayak-to-workspace.firebasestorage.app",
    "messagingSenderId": "565231110834",
    "appId": "1:565231110834:web:e6c658da193cd5521f57ab",
    # Add Realtime Database URL for messaging feature
    "databaseURL": "https://sahayak-to-workspace-default-rtdb.firebaseio.com"
}

# OAuth 2.0 Configuration
OAUTH_CONFIG = {
    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
    "redirect_uri": os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "scope": [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/firebase",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/presentations"
    ]
}

# Firebase Admin SDK Configuration
FIREBASE_ADMIN_CONFIG = {
    "type": "service_account",
    "project_id": "sahayak-to-workspace",
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n') if os.getenv('FIREBASE_PRIVATE_KEY') else None,
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
}