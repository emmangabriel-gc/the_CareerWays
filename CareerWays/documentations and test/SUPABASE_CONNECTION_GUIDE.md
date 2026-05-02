# CareerWays - Supabase Setup & Testing Guide

## ✅ What's Been Fixed

### 1. **OTP Issue with Long Email Addresses**
- ✅ Email column increased from `String(250)` to `String(1024)`
- ✅ Password hash column increased to `String(500)` for security
- ✅ Reset token column increased to `String(500)`

### 2. **Supabase Database Connection**
- ✅ Created `.env` file with PostgreSQL connection string
- ✅ Configured Flask-SQLAlchemy for Supabase
- ✅ Added connection pooling and timeout settings

### 3. **Database Models Verified**
All models are configured for PostgreSQL/Supabase:
- ✅ `User` - User authentication and profile
- ✅ `Assessment` - User assessments and analysis
- ✅ `AssessmentDetail` - Detailed NLP analysis results
- ✅ `Course` - Available courses database
- ✅ `Favorite` - User favorite courses

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies
```bash
cd CareerWays
pip install -r requirements.txt
```

### Step 2: Configure Email (Optional but Recommended)
Edit `.env` file:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**How to get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate and copy the 16-character password
4. Paste into `.env` as `MAIL_PASSWORD`

### Step 3: Initialize Database
```bash
cd backend
python init_db.py
```

This will:
- ✅ Create all tables in Supabase
- ✅ Populate courses database
- ✅ Verify connections

---

## 🧪 Testing the Connection

### Test 1: Check Supabase Connection
```bash
python test_startup.py
```

Expected output:
```
[CareerWays] Database connection: SUCCESSFUL
[CareerWays] Tables created: users, assessments, assessment_details, courses, favorites
```

### Test 2: Manual Connection Test
```python
python -c "
from app import create_app, db
from models import Course

app = create_app()
with app.app_context():
    courses = db.session.query(Course).count()
    print(f'✓ Connected to Supabase')
    print(f'✓ Courses in database: {courses}')
"
```

### Test 3: API Health Check
```bash
python app.py
# Then in another terminal:
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status": "healthy", "message": "CareerWays API is running"}
```

---

## 🔐 Key Environment Variables

```env
# Supabase Connection
DATABASE_URL=postgresql://postgres:PASSWORD@db.sdjtwozfmokhybacutlj.supabase.co:5432/postgres

# Authentication
JWT_SECRET_KEY=your-secret-key

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## 📋 API Endpoints Verification

### Authentication Endpoints
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/forgot-password` - Request password reset (sends OTP)
- `POST /api/auth/verify-otp` - Verify OTP
- `POST /api/auth/reset-password` - Reset password

### Assessment Endpoints
- `POST /api/assessments/analyze` - Analyze user response

### Course Endpoints
- `GET /api/recommendations/courses` - Get all courses
- `GET /api/recommendations/courses/<id>` - Get course details
- `GET /api/recommendations/search` - Search courses

### Favorites Endpoints
- `GET /api/favorites` - Get user favorites
- `POST /api/favorites` - Add favorite course
- `DELETE /api/favorites/<course_id>` - Remove favorite

### User Endpoints
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/change-password` - Change password

---

## 🛠️ Troubleshooting

### Issue: "Connection refused" to Supabase
**Solution:** Check if `.env` has correct `DATABASE_URL`:
```bash
# Verify the connection string format
cat .env | grep DATABASE_URL
```

### Issue: "Table already exists" error
**Solution:** This is normal! Tables were already created. You can safely ignore this.

### Issue: OTP not received
**Solution:** Check email credentials in `.env`:
```env
MAIL_USERNAME=correct-email@gmail.com
MAIL_PASSWORD=correct-app-password
```

### Issue: Long email addresses causing errors
**Solution:** Already fixed! Email column is now `String(1024)`.

---

## ✨ Next Steps

1. **Test signup with long email address** - Try `verylongemailaddress.withsubdomain@company.co.uk`
2. **Test OTP flow** - Use forgot-password endpoint
3. **Test course data** - Get all courses to verify database connection
4. **Deploy to production** - Update `FLASK_ENV=production` in `.env`

---

## 📞 Support

If you encounter any issues:
1. Check `.env` file configuration
2. Verify Supabase credentials
3. Review error logs in terminal
4. Check email configuration for OTP issues
