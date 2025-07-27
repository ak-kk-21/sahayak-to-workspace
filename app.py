from flask import Flask, redirect, render_template, request, make_response, session, abort, jsonify, url_for
import secrets
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import timedelta
import os
from dotenv import load_dotenv
import requests
import json
from urllib.parse import urlencode
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import datetime
import textwrap
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

load_dotenv()



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
OAUTH_REDIRECT_URI = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth')

# Firebase Admin SDK setup
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Realtime Database for messaging
try:
    from firebase_admin import db as rtdb
    # Set up Realtime Database URL
    rtdb.reference().set_url('https://sahayak-to-workspace-default-rtdb.firebaseio.com')
    print("✅ Realtime Database initialized")
except Exception as e:
    print(f"⚠️  Realtime Database not available: {e}")
    rtdb = None

# Sakhaa Chat Configuration
SYSTEM_PROMPT = """You are Sakhaa, a helpful AI assistant. You are knowledgeable, friendly, and always ready to help users with their questions and tasks. You can assist with various topics including:

- General knowledge and information
- Writing and content creation
- Problem-solving and analysis
- Technical questions
- Creative tasks
- And much more!

Please provide clear, helpful, and accurate responses. If you're not sure about something, it's okay to say so. Always be respectful and professional in your interactions."""

# Initialize Gemini chat model
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_chat = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    google_api_key=os.getenv('GEMINI_API_KEY'),
    temperature=0.7,
    max_output_tokens=2048
)

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="chat_memory",
    return_messages=True
)


########################################
""" Authentication and Authorization """

# Decorator for routes that require authentication
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if 'user' not in session:
            return redirect(url_for('login'))
        
        else:
            return f(*args, **kwargs)
        
    return decorated_function

# Decorator for API endpoints that require authentication
def api_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        else:
            return f(*args, **kwargs)
        
    return decorated_function

@app.route('/oauth/google')
def google_oauth():
    code = request.args.get('code')
    state = request.args.get('state')
    if code:
        # This is the callback from Google with the code
        # Exchange code for tokens here
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': OAUTH_REDIRECT_URI
        }
        try:
            response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
            response.raise_for_status()
            tokens = response.json()
            # Get user info using access token
            headers = {'Authorization': f"Bearer {tokens['access_token']}"}
            user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            # Create or get Firebase user
            try:
                firebase_user = auth.get_user_by_email(user_info['email'])
            except auth.UserNotFoundError:
                firebase_user = auth.create_user(
                    email=user_info['email'],
                    display_name=user_info.get('name'),
                    photo_url=user_info.get('picture')
                )
            # Store user info in session
            session['user'] = {
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'display_name': firebase_user.display_name,
                'photo_url': firebase_user.photo_url
            }
            session['access_token'] = tokens['access_token']
            if 'refresh_token' in tokens:
                session['refresh_token'] = tokens['refresh_token']
            
            # Save user to Realtime Database for messaging
            try:
                # Create user data
                user_data = {
                    'name': firebase_user.display_name or firebase_user.email.split('@')[0],
                    'email': firebase_user.email,
                    'photoURL': firebase_user.photo_url,
                    'uid': firebase_user.uid,
                    'lastSeen': int(datetime.datetime.now().timestamp() * 1000)
                }
                
                print(f"🔧 Saving user data: {user_data}")
                
                # Save to Firestore
                try:
                    db.collection('users').document(firebase_user.uid).set(user_data)
                    print(f"✅ User saved to Firestore: {firebase_user.email}")
                except Exception as e:
                    print(f"❌ Error saving to Firestore: {e}")
                
                # Save to Realtime Database for messaging
                if rtdb:
                    try:
                        rtdb.reference(f'users/{firebase_user.uid}').set(user_data)
                        print(f"✅ User saved to Realtime Database: {firebase_user.email}")
                    except Exception as e:
                        print(f"❌ Error saving to Realtime Database: {e}")
                else:
                    print("⚠️  Realtime Database not available")
                
                print(f"🎉 User {firebase_user.email} registration completed")
                
            except Exception as e:
                print(f"❌ Error in user registration: {e}")
                # Don't fail the login if database save fails
            
            return redirect(url_for('dashboard'))
        except requests.RequestException as e:
            return f"OAuth error: {str(e)}", 400
    else:
        # This is the initial request, start the OAuth flow
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        oauth_params = {
            'client_id': GOOGLE_CLIENT_ID,
            'redirect_uri': OAUTH_REDIRECT_URI,
            'scope': ' '.join([
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/firebase',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/presentations'
            ]),
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        oauth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(oauth_params)}"
        return redirect(oauth_url)

# Remove the /auth GET route since callback is now handled in /oauth/google

@app.route('/auth', methods=['POST'])
def authorize():
    """Legacy token-based authentication (keep for compatibility)"""
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return "Unauthorized", 401

    token = token[7:]  # Strip off 'Bearer ' to get the actual token

    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60)
        session['user'] = decoded_token
        return redirect(url_for('dashboard'))
    except:
        return "Unauthorized", 401


#####################
""" Public Routes """

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('signup.html')


@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('forgot_password.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from session
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)  # Optionally clear the session cookie
    return response


##############################################
""" Private Routes (Require authorization) """

@app.route('/dashboard')
@auth_required
def dashboard():

    return render_template('dashboard.html')

@app.route('/profile')
@auth_required
def profile_page():
    """Teacher profile page"""
    return render_template('profile.html')

@app.route('/api/profile', methods=['GET'])
@api_auth_required
def get_profile():
    """Get teacher profile from Firestore"""
    try:
        user = session.get('user')
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get profile from Firestore
        profile_doc = db.collection('teacher_profiles').document(user['uid']).get()
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            return jsonify({
                'success': True,
                'profile': profile_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No profile found'
            })
            
    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['POST'])
@api_auth_required
def save_profile():
    """Save teacher profile to Firestore"""
    try:
        user = session.get('user')
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['school_name', 'board', 'grades_taught', 'languages']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Prepare profile data
        profile_data = {
            'uid': user['uid'],
            'email': user['email'],
            'name': user['display_name'] or user['email'].split('@')[0],
            'school_name': data['school_name'],
            'gender': data.get('gender'),
            'board': data['board'],
            'grades_taught': data['grades_taught'],
            'languages': data['languages'],
            'bio': data.get('bio', ''),
            'updated_at': datetime.datetime.now().isoformat(),
            'created_at': datetime.datetime.now().isoformat()
        }
        
        # Check if profile exists to set created_at
        existing_profile = db.collection('teacher_profiles').document(user['uid']).get()
        if existing_profile.exists:
            profile_data['created_at'] = existing_profile.to_dict().get('created_at', profile_data['created_at'])
        
        # Save to Firestore
        db.collection('teacher_profiles').document(user['uid']).set(profile_data)
        
        print(f"✅ Profile saved for user: {user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': profile_data
        })
        
    except Exception as e:
        print(f"❌ Error saving profile: {e}")
        return jsonify({'error': str(e)}), 500

def get_teacher_context(user_id):
    """Get teacher context for LLM prompts"""
    try:
        profile_doc = db.collection('teacher_profiles').document(user_id).get()
        if profile_doc.exists:
            profile = profile_doc.to_dict()
            
            # Build context string
            context_parts = []
            
            if profile.get('board'):
                context_parts.append(f"Board: {profile['board']}")
            
            if profile.get('grades_taught'):
                grades = ', '.join(profile['grades_taught'])
                context_parts.append(f"Grades: {grades}")
            
            if profile.get('languages'):
                languages = ', '.join(profile['languages'])
                context_parts.append(f"Languages: {languages}")
            
            if profile.get('school_name'):
                context_parts.append(f"School: {profile['school_name']}")
            
            if context_parts:
                return f"Teacher Context: {' | '.join(context_parts)}"
        
        return ""
        
    except Exception as e:
        print(f"❌ Error getting teacher context: {e}")
        return ""

def push_to_google_slides(access_token, content, title="Gemini Generated Slides"):
    creds = Credentials(token=access_token)
    service = build('slides', 'v1', credentials=creds)
    
    # Split content into slides
    slides_content = [s.strip() for s in content.split('\n\n') if s.strip()]
    if not slides_content:
        slides_content = [content.strip()]

    # Create presentation with first slide
    presentation = service.presentations().create(body={
        "title": title,
        "slides": [{
            "pageElements": [
                {
                    "objectId": "title",
                    "shape": {
                        "shapeType": "RECTANGLE",
                        "text": {
                            "textElements": [{
                                "textRun": {
                                    "content": title
                                }
                            }]
                        }
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 100,
                        "translateY": 100
                    }
                },
                {
                    "objectId": "body",
                    "shape": {
                        "shapeType": "RECTANGLE",
                        "text": {
                            "textElements": [{
                                "textRun": {
                                    "content": slides_content[0]
                                }
                            }]
                        }
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 100,
                        "translateY": 200
                    }
                }
            ]
        }]
    }).execute()
    
    presentation_id = presentation.get('presentationId')

    # Add additional slides
    requests = []
    for i, slide_content in enumerate(slides_content[1:], 1):
        requests.append({
            "createSlide": {
                "slideLayoutReference": {
                    "predefinedLayout": "TITLE_AND_BODY"
                },
                "placeholderIdMappings": [
                    {
                        "layoutPlaceholder": {
                            "type": "TITLE"
                        },
                        "objectId": f"title_{i}"
                    },
                    {
                        "layoutPlaceholder": {
                            "type": "BODY"
                        },
                        "objectId": f"body_{i}"
                    }
                ]
            }
        })
        requests.append({
            "insertText": {
                "objectId": f"title_{i}",
                "text": f"Slide {i+1}"
            }
        })
        requests.append({
            "insertText": {
                "objectId": f"body_{i}",
                "text": slide_content
            }
        })

    if requests:
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests}
        ).execute()

    # Call the Apps Script to add images to the slides
    print(f"Calling add_images_to_slides for presentation: {presentation_id}")
    # Try web app method first (more reliable)
    success = add_images_to_slides_webapp(presentation_id, access_token)
    if not success:
        print("Web app method failed, trying Scripts API method...")
        add_images_to_slides(presentation_id, access_token)

    return f"https://docs.google.com/presentation/d/{presentation_id}/edit"

@app.route('/lekhak', methods=['GET', 'POST'])
@auth_required
def lekhak():
    prompt = ''
    response = None
    doc_url = None
    slides_url = None
    doc_title = None

    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        if prompt.strip():
            try:
                # Get teacher context
                user = session.get('user')
                teacher_context = get_teacher_context(user['uid']) if user else ""
                
                # Enhance prompt with teacher context
                enhanced_prompt = prompt
                if teacher_context:
                    enhanced_prompt = f"{teacher_context}\n\nUser Request: {prompt}\n\nPlease provide content that is appropriate for the teacher's context and grade levels."
                    print(f"🔍 Enhanced prompt with teacher context: {teacher_context}")
                
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
                # Generate the main response
                result = model.generate_content(enhanced_prompt)
                response = result.text if result.text else ""
                # Generate a short, relevant title using Gemini
                title_prompt = f"Generate a short, relevant title (max 8 words, no punctuation at the end) for the following content:\n{response}"
                title_result = model.generate_content(title_prompt)
                doc_title = title_result.text.strip() if title_result.text else "Gemini Generated Doc"
                # Only push to Google Docs/Slides if response is not empty
                if response.strip():
                    access_token = session.get('access_token')
                    if access_token:
                        doc_url = push_to_google_doc(access_token, response, title=doc_title)
                        slides_url = push_to_google_slides(access_token, response, title=doc_title)
            except Exception as e:
                response = f"Error: {str(e)}"

    return render_template('lekhak.html', prompt=prompt, response=response, doc_url=doc_url, slides_url=slides_url)

@app.route('/summarizer', methods=['GET', 'POST'])
@auth_required
def summarizer():
    if request.method == 'POST':
        try:
            # Handle file upload
            if 'pdf_file' not in request.files:
                return jsonify({"error": "No file uploaded"}), 400
            
            file = request.files['pdf_file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({"error": "Please upload a PDF file"}), 400
            
            # Read the file content
            file_content = file.read()
            
            # Check file size (limit to 10MB)
            if len(file_content) > 10 * 1024 * 1024:  # 10MB
                return jsonify({"error": "File too large. Please upload a PDF smaller than 10MB."}), 400
            
            # Extract text from PDF using PyPDF2 or similar
            try:
                import PyPDF2
                import io
                
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                if not text.strip():
                    return jsonify({"error": "No text could be extracted from the PDF. The file might be scanned or image-based."}), 400
                    
            except ImportError:
                return jsonify({"error": "PyPDF2 is required for PDF processing. Please install it with: pip install PyPDF2"}), 500
            except Exception as e:
                return jsonify({"error": f"Error extracting text from PDF: {str(e)}"}), 500
            
            # Limit text length for API
            if len(text) > 100000:
                text = text[:100000]
                print(f"Text truncated to {len(text)} characters")
            
            # Check if Gemini API key is available
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if not gemini_api_key:
                return jsonify({"error": "Gemini API key not configured"}), 500
            
            # Generate summary using Gemini API
            try:
                response = requests.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent",
                    params={"key": gemini_api_key},
                    json={
                        "contents": [{
                            "parts": [{"text": f"Summarize this PDF in 3-5 bullet points:\n{text}"}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "topP": 0.95
                        }
                    },
                    timeout=60
                )
                
                if response.status_code != 200:
                    error_msg = f"Gemini API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            error_msg = f"Gemini API error: {error_data['error'].get('message', 'Unknown error')}"
                    except:
                        pass
                    return jsonify({"error": error_msg}), 500
                
                result = response.json()
                if not result.get("candidates") or not result["candidates"][0].get("content"):
                    return jsonify({"error": "Invalid response from Gemini API"}), 500
                
                summary = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Generate a title for the summary
                try:
                    title_prompt = f"Generate a short, relevant title (max 8 words, no punctuation at the end) for this summary:\n{summary}"
                    title_response = requests.post(
                        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent",
                        params={"key": gemini_api_key},
                        json={
                            "contents": [{
                                "parts": [{"text": title_prompt}]
                            }],
                            "generationConfig": {
                                "temperature": 0.7,
                                "topP": 0.95
                            }
                        },
                        timeout=30
                    )
                    
                    doc_title = "PDF Summary"
                    if title_response.status_code == 200:
                        title_result = title_response.json()
                        if title_result.get("candidates") and title_result["candidates"][0].get("content"):
                            doc_title = title_result["candidates"][0]["content"]["parts"][0]["text"].strip()
                except Exception as e:
                    print(f"Error generating title: {e}")
                    doc_title = "PDF Summary"
                
                # Push to Google Docs if user is authenticated
                doc_url = None
                access_token = session.get('access_token')
                if access_token:
                    try:
                        doc_url = push_to_google_doc(access_token, summary, title=doc_title)
                    except Exception as e:
                        print(f"Error pushing to Google Docs: {e}")
                        # Don't fail the request if Google Docs fails
                
                return jsonify({
                    "summary": summary,
                    "doc_url": doc_url,
                    "filename": file.filename
                })
                
            except requests.exceptions.Timeout:
                return jsonify({"error": "Request to Gemini API timed out. Please try again."}), 500
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Network error: {str(e)}"}), 500
            
        except Exception as e:
            print(f"Unexpected error in summarizer: {e}")
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    
    # GET request - show the form
    return render_template('summarizer.html')

@app.route("/sakhaa", methods=["POST"])
@auth_required
def sakhaa_chat():
    """Sakhaa AI Chat endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        message = data.get("message")
        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get teacher context
        user = session.get('user')
        teacher_context = get_teacher_context(user['uid']) if user else ""
        
        # Get chat history from memory
        chat_history = memory.chat_memory.messages
        
        # Prepare the full message with system prompt and teacher context
        if not chat_history:
            enhanced_system_prompt = SYSTEM_PROMPT
            if teacher_context:
                enhanced_system_prompt += f"\n\nTeacher Context: {teacher_context}\nPlease consider this context when providing responses."
                print(f"🔍 Enhanced Sakhaa system prompt with teacher context: {teacher_context}")
            
            full_message = f"{enhanced_system_prompt}\n\nUser: {message}"
        else:
            # For ongoing conversations, add context to the current message
            if teacher_context:
                full_message = f"Teacher Context: {teacher_context}\n\nUser: {message}"
            else:
                full_message = message

        # Get response from Gemini
        response = gemini_chat.invoke(full_message)
        bot_reply = response.content.strip()

        # Format the reply
        formatted_reply = textwrap.fill(bot_reply, width=80)
        formatted_reply = formatted_reply.replace("**", "").replace("*", "• ")

        # Save context to memory
        memory.save_context({"input": message}, {"output": formatted_reply})
        
        return jsonify({"reply": formatted_reply})

    except Exception as e:
        print("Sakhaa Chat Error:", str(e))
        return jsonify({"error": "Failed to fetch response"}), 500

@app.route("/sakhaa", methods=["GET"])
@auth_required
def sakhaa_page():
    """Sakhaa chat page"""
    return render_template('sakhaa.html')

@app.route('/messenger')
@auth_required
def messenger():
    """Messaging page"""
    return render_template('messenger.html')

@app.route('/api/test')
def test_api():
    """Simple test endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/user-data')
@api_auth_required
def get_user_data():
    """Get current user data for frontend"""
    try:
        user = session.get('user')
        if user:
            user_data = {
                'uid': user['uid'],
                'name': user['display_name'] or user['email'].split('@')[0],
                'email': user['email'],
                'photoURL': user['photo_url']
            }
            print(f"🔍 Returning user data: {user_data}")
            return jsonify(user_data)
        else:
            print("❌ No user found in session")
            return jsonify({'error': 'User not found in session'}), 404
    except Exception as e:
        print(f"❌ Error in get_user_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/register-user', methods=['POST'])
@api_auth_required
def register_user():
    """Manually register current user to databases"""
    try:
        user = session.get('user')
        if not user:
            return jsonify({'error': 'User not found in session'}), 404
        
        # Create user data
        user_data = {
            'name': user['display_name'] or user['email'].split('@')[0],
            'email': user['email'],
            'photoURL': user['photo_url'],
            'uid': user['uid'],
            'lastSeen': int(datetime.datetime.now().timestamp() * 1000)
        }
        
        print(f"🔧 Manually registering user: {user_data}")
        
        # Save to Firestore
        try:
            db.collection('users').document(user['uid']).set(user_data)
            print(f"✅ User saved to Firestore: {user['email']}")
        except Exception as e:
            print(f"❌ Error saving to Firestore: {e}")
        
        # Save to Realtime Database
        if rtdb:
            try:
                rtdb.reference(f'users/{user["uid"]}').set(user_data)
                print(f"✅ User saved to Realtime Database: {user['email']}")
            except Exception as e:
                print(f"❌ Error saving to Realtime Database: {e}")
        else:
            print("⚠️  Realtime Database not available")
        
        return jsonify({
            'success': True,
            'message': f'User {user["email"]} registered successfully',
            'user_data': user_data
        })
        
    except Exception as e:
        print(f"❌ Error in manual registration: {e}")
        return jsonify({'error': str(e)}), 500


def push_to_google_doc(access_token, content, title="Gemini Generated Doc"):
    # Create credentials object from the user's access token
    creds = Credentials(token=access_token)
    # Build the Google Docs API service
    service = build('docs', 'v1', credentials=creds)
    # Create a new document
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc.get('documentId')
    # Insert the content into the document
    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": content
            }
        }
    ]
    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
    # Return the document URL

    return f"https://docs.google.com/document/d/{doc_id}/edit"

def add_images_to_slides(presentation_id, access_token):
    """Call Google Apps Script to add images to slides"""
    creds = Credentials(token=access_token)
    service = build('script', 'v1', credentials=creds)
    
    script_id = 'AKfycbyzN-3wIF2LCjxb-6uLMMg3lZaA-MsRfBTpxsPjxkGq_I3dgr7k1ORorTCzxcfu6efvfQ'  # Replace this with your actual Script ID
    
    try:
        print(f"Attempting to call Apps Script with ID: {script_id}")
        print(f"Presentation ID: {presentation_id}")
        
        # Call the Apps Script function
        result = service.scripts().run(
            body={
                'function': 'addImagesToSlides',
                'parameters': [presentation_id]
            },
            scriptId=script_id
        ).execute()
        
        print(f"Apps Script result: {result}")
        return result
        
    except Exception as e:
        print(f"Error calling Apps Script: {e}")
        print(f"Error type: {type(e)}")
        return None

def add_images_to_slides_webapp(presentation_id, access_token):
    """Call Google Apps Script web app to add images to slides"""
    
    # Your deployed web app URL (get this from the deployment)
    webapp_url = 'https://script.google.com/macros/s/AKfycbyzN-3wIF2LCjxb-6uLMMg3lZaA-MsRfBTpxsPjxkGq_I3dgr7k1ORorTCzxcfu6efvfQ/exec'
    
    try:
        print(f"Calling web app: {webapp_url}")
        print(f"Presentation ID: {presentation_id}")
        
        # Send data as form data (Google Apps Script web apps expect this format)
        data = {
            'presentation_id': presentation_id,
            'access_token': access_token
        }
        
        response = requests.post(webapp_url, data=data, timeout=30)
        
        print(f"Web app response status: {response.status_code}")
        print(f"Web app response headers: {dict(response.headers)}")
        print(f"Web app response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Images added successfully via web app")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout error calling web app")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error calling web app: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error calling web app: {e}")
        return False

@app.route('/health')
def health_check():
    """Health check endpoint to verify server is running"""
    try:
        # Test PyPDF2 import
        import PyPDF2
        pypdf2_status = "OK"
    except ImportError:
        pypdf2_status = "MISSING"
    
    # Test Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    gemini_status = "CONFIGURED" if gemini_key else "MISSING"
    
    return jsonify({
        "status": "healthy",
        "timestamp": str(datetime.datetime.now()),
        "dependencies": {
            "PyPDF2": pypdf2_status,
            "Gemini_API_Key": gemini_status
        }
    })

if __name__ == '__main__':
    app.run(debug=True)