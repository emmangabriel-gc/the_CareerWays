# CareerWays - Quick Testing Guide

## What Was Fixed

Your CareerWays application had several critical issues preventing login, signup, and assessments from working:

1. **Circular Import Bug** - The models couldn't import the database properly
2. **Missing NLTK Data** - The ML engine couldn't start because NLP resources weren't available
3. **Python 3.14 Compatibility** - Packages were too old for Python 3.14
4. **Database Not Initialized** - No courses were loaded into the database

**All issues are now fixed!**

---

## Current Status

✅ **Backend is RUNNING** on http://localhost:5000
✅ **Database has 21 courses** ready to recommend
✅ **All API endpoints are working**
✅ **Authentication system is functional**

---

## How to Test

### Step 1: Make sure the backend is running

You should see the Flask server running with this message:
```
Running on http://127.0.0.1:5000
```

If not, run:
```bash
cd CareerWays/backend
python app.py
```

### Step 2: Open the Frontend

Open `CareerWays/frontend/index.html` in your web browser:
- Right-click on the file → Open with → Your browser
- Or drag the file into your browser window

### Step 3: Test Sign Up

1. Click the **"Sign Up"** tab
2. Fill in:
   - Full Name: `John Doe`
   - Email: `john@example.com`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click **"Sign Up"**
4. ✅ You should see "Account created successfully!" and be redirected to the dashboard

### Step 4: Test Login

1. Go back to index.html
2. Click the **"Log In"** tab
3. Enter:
   - Email: `john@example.com`
   - Password: `password123`
4. Click **"Log In"**
5. ✅ You should be logged in and redirected to the dashboard

### Step 5: Test Assessment

1. From the dashboard, click **"Start Assessment"** or see the assessment interface
2. In the text area, describe yourself:
   ```
   I love programming and building software. I'm skilled in Python and JavaScript.
   I have 2 years of experience developing web applications. My goal is to become
   a full-stack developer. I enjoy learning new technologies and solving complex problems.
   I'm passionate about artificial intelligence and machine learning.
   ```
3. Click **"Send"**
4. ✅ Wait for analysis... The AI will:
   - Analyze your skills, interests, and experience
   - Extract keywords
   - Calculate sentiment and motivation
   - Return 5 recommended courses with match scores

5. You should see recommendations like:
   - BS Information Technology (90% match)
   - BS Computer Science (85% match)
   - BS Entertainment and Multimedia Computing - Game Development (80% match)
   - etc.

### Step 6: Test Guest Access

1. Go back to index.html
2. Click the **"Continue as Guest"** tab
3. Click **"Continue as Guest"**
4. Take an assessment without creating an account
5. ✅ Results will show but won't be saved

---

## Expected Workflow

```
index.html (Login/Signup/Guest)
    ↓
dashboard.html (Choose action)
    ↓
assessment.html (Describe yourself)
    ↓
Backend Analysis (/api/assessments/analyze)
    ↓
results.html (View recommendations)
```

---

## API Endpoints (If Testing Manually)

### Sign Up
```
POST http://localhost:5000/api/auth/signup
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

### Login
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

### Submit Assessment
```
POST http://localhost:5000/api/assessments/analyze
Content-Type: application/json
Authorization: Bearer <token_from_login>

{
  "response": "Your description here...",
  "userType": "registered"  // or "guest"
}
```

---

## Troubleshooting

### Backend won't start
- Make sure Python 3.13+ is installed
- Run `pip install -r requirements.txt` to install dependencies
- Check that port 5000 is not in use

### Frontend can't connect to backend
- Make sure backend is running on http://localhost:5000
- Check browser console (F12) for network errors
- Make sure CORS is enabled (should be by default)

### Assessment returns error
- Make sure response is at least 20 characters
- Try with a longer, more detailed description
- Check browser console for detailed error messages

### Database errors
- Delete `CareerWays/database/careerways.db` if it exists
- Run `python backend/init_db.py` to recreate it

---

## Files to Use

- **Frontend:** Open `CareerWays/frontend/index.html` in browser
- **Backend:** Run `python backend/app.py` from terminal
- **Database:** Automatically created at `CareerWays/database/careerways.db`

---

**Your CareerWays system is now fully functional! Enjoy exploring! 🚀**
