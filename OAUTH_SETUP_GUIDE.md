# Firebase OAuth Setup Guide

This guide will walk you through setting up OAuth access to Firebase from Google Cloud Platform.

## Prerequisites
- A Google Cloud Platform account
- A Firebase project
- Python 3.7+ installed

## Step 1: Google Cloud Platform Setup

### 1.1 Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select your existing project (`sahayak-to-workspace`)
3. Note down your Project ID

### 1.2 Enable Required APIs
In the Google Cloud Console, enable these APIs:
- **Firebase API**
- **Google Identity and Access Management (IAM) API**
- **Google OAuth2 API**

### 1.3 Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Add authorized JavaScript origins:
   - `http://localhost:5000` (for development)
   - `https://yourdomain.com` (for production)
5. Add authorized redirect URIs:
   - `http://localhost:5000/auth` (for development)
   - `https://yourdomain.com/auth` (for production)
6. Click "Create"
7. **Save the Client ID and Client Secret** - you'll need these for the `.env` file

## Step 2: Firebase Setup

### 2.1 Configure Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (`sahayak-to-workspace`)
3. Go to Project Settings (gear icon)
4. In the "Service accounts" tab, click "Generate new private key"
5. Download the JSON file and save it as `firebase-auth.json` in your project root

### 2.2 Enable Authentication Methods
1. In Firebase Console, go to "Authentication" > "Sign-in method"
2. Enable "Google" as a sign-in provider
3. Add your OAuth 2.0 Client ID and Client Secret from Step 1.3

## Step 3: Environment Configuration

### 3.1 Create .env File
1. Copy `env_template.txt` to `.env`
2. Fill in the following values:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here

# Google OAuth 2.0 Configuration
GOOGLE_CLIENT_ID=your-google-client-id-from-step-1.3
GOOGLE_CLIENT_SECRET=your-google-client-secret-from-step-1.3
OAUTH_REDIRECT_URI=http://localhost:5000/auth

# Firebase Admin SDK Configuration
FIREBASE_PRIVATE_KEY_ID=from-firebase-auth.json
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key from firebase-auth.json\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=from-firebase-auth.json
FIREBASE_CLIENT_ID=from-firebase-auth.json
FIREBASE_CLIENT_CERT_URL=from-firebase-auth.json
```

### 3.2 Extract Firebase Service Account Details
From your `firebase-auth.json` file, copy these values to your `.env` file:
- `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
- `private_key` → `FIREBASE_PRIVATE_KEY` (keep the quotes and \n characters)
- `client_email` → `FIREBASE_CLIENT_EMAIL`
- `client_id` → `FIREBASE_CLIENT_ID`
- `client_x509_cert_url` → `FIREBASE_CLIENT_CERT_URL`

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Test the Setup

### 5.1 Run the Application
```bash
python app.py
```

### 5.2 Test OAuth Flow
1. Navigate to `http://localhost:5000/login`
2. Click "Sign in with Google"
3. Complete the OAuth flow
4. You should be redirected to the dashboard upon successful authentication

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI" error**
   - Ensure the redirect URI in your OAuth credentials matches exactly
   - Check for trailing slashes or protocol mismatches

2. **"Client ID not found" error**
   - Verify your `GOOGLE_CLIENT_ID` in the `.env` file
   - Ensure the OAuth credentials are for a "Web application"

3. **"Invalid state parameter" error**
   - This is a security feature. Try clearing your browser cookies and session

4. **Firebase authentication errors**
   - Verify your `firebase-auth.json` file is in the project root
   - Check that all Firebase Admin SDK environment variables are set correctly

### Security Considerations

1. **Never commit sensitive files**
   - Add `.env` and `firebase-auth.json` to your `.gitignore`
   - Use environment variables in production

2. **Use HTTPS in production**
   - Update `SESSION_COOKIE_SECURE = True` in production
   - Use proper SSL certificates

3. **Rotate credentials regularly**
   - Regularly update your OAuth client secrets
   - Monitor for suspicious activity

## Production Deployment

For production deployment:

1. Update OAuth redirect URIs to your production domain
2. Set `SESSION_COOKIE_SECURE = True`
3. Use a proper secret key (not the default)
4. Configure HTTPS
5. Set up proper logging and monitoring
6. Consider using a secure session store (Redis, etc.)

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Firebase Authentication Documentation](https://firebase.google.com/docs/auth)
- [Flask Session Documentation](https://flask.palletsprojects.com/en/2.3.x/quickstart/#sessions) 