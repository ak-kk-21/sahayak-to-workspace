# Teacher Profile System Guide

## Overview
The Teacher Profile System allows teachers to create and manage their teaching profiles, which are then used to enhance AI responses with personalized context.

## Features

### 1. Profile Management
- **School Information**: School name
- **Personal Information**: Gender
- **Teaching Information**: Board (CBSE, ICSE, State, IB, Other) and Grades Taught (1-12)
- **Languages**: Comfortable languages for teaching
- **Bio**: Short description about teaching style/experience

### 2. AI Context Enhancement
When a teacher has a profile, the AI will automatically include their context in responses:
- **Board-specific content**: Tailored to CBSE, ICSE, etc.
- **Grade-appropriate material**: Content suitable for the teacher's grade levels
- **Language preferences**: Consideration for preferred languages
- **School context**: School-specific references when relevant

### 3. Integration Points
- **Lekhak (Content Generation)**: Enhanced prompts with teacher context
- **Sakhaa (AI Chat)**: Personalized responses based on teaching profile
- **Dashboard**: Profile completion status indicator

## Database Structure

### Firestore Collection: `teacher_profiles`
```json
{
  "uid": "user_firebase_uid",
  "email": "teacher@school.com",
  "name": "Teacher Name",
  "school_name": "ABC School",
  "gender": "Male/Female/Other",
  "board": "CBSE/ICSE/State/IB/Other",
  "grades_taught": ["1", "2", "3", "4", "5"],
  "languages": ["English", "Hindi", "Tamil"],
  "bio": "Experienced teacher with 5 years...",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## API Endpoints

### GET `/api/profile`
- **Purpose**: Retrieve teacher profile
- **Authentication**: Required
- **Response**: Profile data or 401 if not authenticated

### POST `/api/profile`
- **Purpose**: Save/update teacher profile
- **Authentication**: Required
- **Body**: Profile data (JSON)
- **Response**: Success/error message

### GET `/profile`
- **Purpose**: Profile page
- **Authentication**: Required
- **Response**: HTML page

## Security Rules

### Firestore Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /teacher_profiles/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## How to Use

### 1. Access Profile
1. Login to your account
2. Click the hamburger menu (☰) in the navbar
3. Select "Account" → "Profile"
4. Or use the "Complete Profile" button on the dashboard

### 2. Fill Profile
1. **School Name**: Enter your school name (required)
2. **Gender**: Select your gender
3. **Board**: Choose your school board (required)
4. **Grades Taught**: Check all grades you teach (required)
5. **Languages**: Select languages you're comfortable with (required)
6. **Bio**: Write a short description about your teaching (optional)

### 3. Save Profile
- Click "Update Profile" to save
- The system will validate required fields
- Success message will confirm the save

### 4. Enhanced AI Responses
After saving your profile:
- **Lekhak**: Content will be tailored to your board and grade levels
- **Sakhaa**: Chat responses will consider your teaching context
- **Dashboard**: Profile button will show "Update Profile" in green

## Example Context Enhancement

### Before Profile
```
User: "Create a lesson plan for photosynthesis"
AI: "Here's a general lesson plan for photosynthesis..."
```

### After Profile (CBSE, Grades 6-8, English/Hindi)
```
User: "Create a lesson plan for photosynthesis"
AI: "Here's a CBSE-aligned lesson plan for photosynthesis suitable for grades 6-8. 
     I'll provide explanations in both English and Hindi where helpful..."
```

## Testing

### Run Test Script
```bash
python test_profile.py
```

### Manual Testing
1. Start Flask app: `python app.py`
2. Login to account
3. Visit `/profile`
4. Fill and save profile
5. Test AI features to see enhanced responses

## Troubleshooting

### Common Issues
1. **Profile not saving**: Check required fields are filled
2. **AI not using context**: Ensure profile is saved and user is authenticated
3. **Database errors**: Verify Firestore rules are updated

### Debug Steps
1. Check browser console for JavaScript errors
2. Verify Firestore connection
3. Check authentication status
4. Review server logs for backend errors

## Future Enhancements
- Profile completion percentage
- Multiple school profiles
- Subject-specific preferences
- Teaching experience level
- Professional development tracking 