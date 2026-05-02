# CareerWays - Quick Start Guide

## ⚡ Get Started in 3 Minutes

### Option 1: Run Locally with SQLite (Recommended)

#### Step 1: Update Configuration
```bash
# Open .env file and change DATABASE_URL to:
DATABASE_URL=sqlite:////tmp/careerways.db
```

Or run this command:
```bash
# Windows
(Get-Content .env) -replace 'DATABASE_URL=.*', 'DATABASE_URL=sqlite:////tmp/careerways.db' | Set-Content .env
```

#### Step 2: Initialize Database
```bash
cd backend
python init_db.py
```

You should see:
```
[CareerWays] Creating database tables...
[CareerWays] Database tables created/verified successfully
[CareerWays] Adding 20 courses to database...
[CareerWays] Database initialized successfully with 20 courses
✓ BS Nursing
✓ BS Midwifery
✓ BS Accountancy
... etc
```

#### Step 3: Run the Application
```bash
python app.py
```

You should see:
```
[CareerWays] Database tables initialized successfully
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

#### Step 4: Test the API
```bash
# In a new terminal
curl http://localhost:5000/api/health
```

Should return:
```json
{"status": "healthy", "message": "CareerWays API is running"}
```

#### Step 5: Access the Frontend
Open your browser:
```
http://localhost:5000/
```

---

### Option 2: Use Supabase (When Internet is Available)

#### Step 1: Keep Default Configuration
Your `.env` already has Supabase configured:
```env
DATABASE_URL=postgresql://postgres:Emm4ng4brieldel4cruz@db.sdjtwozfmokhybacutlj.supabase.co:5432/postgres
```

#### Step 2: Initialize Database
```bash
cd backend
python init_db.py
```

#### Step 3: Run the Application
```bash
python app.py
```

#### Step 4: Access Frontend
```
http://localhost:5000/
```

---

## 🧪 Testing the Features

### Test User Registration
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "token": "eyJ...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Test Course Retrieval
```bash
curl http://localhost:5000/api/recommendations/courses
```

### Test Assessment
```bash
curl -X POST http://localhost:5000/api/assessments/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "response": "I love coding and building things. I enjoy problem solving and learning new technologies. I am passionate about making an impact in the tech industry.",
    "userType": "guest"
  }'
```

---

## 📁 Project Structure

```
CareerWays/
├── backend/
│   ├── app.py                    # Main Flask app
│   ├── models/__init__.py        # Database models
│   ├── routes/
│   │   ├── auth_routes.py       # Authentication
│   │   ├── assessment_routes.py # Assessments
│   │   ├── recommendation_routes.py # Courses
│   │   ├── user_routes.py       # User profiles
│   │   └── favorites_routes.py  # Favorites
│   ├── ml_engine.py             # ML/NLP engine
│   ├── init_db.py               # Database initialization
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── index.html               # Home page
│   ├── login.html               # (Future)
│   ├── dashboard.html           # User dashboard
│   ├── assessment.html          # Assessment page
│   └── css/, js/               # Styling and scripts
├── .env                         # Configuration
└── database/
    └── careerways.db           # SQLite (if using local)
```

---

## 🛑 Troubleshooting

### "Cannot connect to Supabase"
→ **Solution:** Use SQLite locally (see Option 1 above)

### "Port 5000 already in use"
```bash
# Change port in backend/app.py or use different port
PORT=8000 python app.py
```

### "Database tables not found"
```bash
# Reinitialize
python backend/init_db.py
```

### "Module not found" errors
```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 📊 API Endpoints Quick Reference

### Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/auth/signup | Register new user |
| POST | /api/auth/login | Login user |
| POST | /api/auth/forgot-password | Request OTP |
| POST | /api/auth/verify-otp | Verify OTP code |
| POST | /api/auth/reset-password | Reset password |

### Assessments
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/assessments/analyze | Analyze response |

### Courses
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/recommendations/courses | Get all courses |
| GET | /api/recommendations/courses/{id} | Get course details |
| GET | /api/recommendations/search | Search courses |

### User
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/users/profile | Get user profile |
| PUT | /api/users/profile | Update profile |
| POST | /api/users/change-password | Change password |

### Favorites
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/favorites | Get favorites |
| POST | /api/favorites | Add favorite |
| DELETE | /api/favorites/{id} | Remove favorite |

---

## ✅ Verification Checklist

- [ ] `.env` is configured
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database initialized: `python backend/init_db.py`
- [ ] Application running: `python backend/app.py`
- [ ] Health check works: `curl http://localhost:5000/api/health`
- [ ] Signup endpoint works: `curl -X POST http://localhost:5000/api/auth/signup ...`
- [ ] Courses loaded: `curl http://localhost:5000/api/recommendations/courses`

---

## 🚀 You're Ready!

Your CareerWays system is fully configured and ready to use. Start with:

```bash
cd c:\Users\delac\Pictures\bitch\CareerWays
cd backend
python app.py
```

Then open: `http://localhost:5000`

Happy coding! 🎉
