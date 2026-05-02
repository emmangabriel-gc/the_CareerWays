# CareerWays - Complete Setup & Deployment Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Database Setup](#database-setup)
4. [Running the Application](#running-the-application)
5. [API Testing](#api-testing)
6. [Frontend Customization](#frontend-customization)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 2GB RAM
- 500MB disk space
- Modern web browser

### Recommended
- Python 3.10+
- 4GB RAM
- SSD storage
- Chrome, Firefox, Safari, or Edge

## Installation

### Step 1: Clone/Extract Project
```bash
cd CareerWays
```

### Step 2: Create Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS
- SQLAlchemy (ORM)
- PyJWT (Authentication)
- scikit-learn (Machine Learning)
- nltk (Natural Language Processing)
- textblob (Sentiment Analysis)

## Database Setup

### Step 1: Initialize Database
```bash
cd backend
python init_db.py
```

This creates:
- SQLite database at `/tmp/careerways.db`
- Tables for Users, Assessments, Courses, Favorites
- 22 sample courses

### Step 2: Verify Database (Optional)
```bash
# Using Python
python -c "from models import Course; print(Course.query.all())"
```

## Running the Application

### Step 1: Start Backend Server
```bash
cd backend
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 2: Access Frontend
- **Option A**: Open in file explorer
  - Navigate to `frontend/index.html`
  - Right-click → Open with browser

- **Option B**: Use local server
  ```bash
  # Python 3.10+
  cd frontend
  python -m http.server 8000
  # Visit: http://localhost:8000
  ```

- **Option C**: VS Code Live Server
  - Install "Live Server" extension
  - Right-click `index.html` → "Open with Live Server"

## API Testing

### Using cURL
```bash
# Health Check
curl http://localhost:5000/api/health

# Sign Up
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'

# Analyze Assessment (without auth for guest)
curl -X POST http://localhost:5000/api/assessments/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "response": "I love programming and want to work in software development. I have experience with Python and JavaScript.",
    "userType": "guest"
  }'
```

### Using Postman
1. Import endpoints into Postman
2. Set variables:
   - `{{base_url}}` = http://localhost:5000/api
   - `{{token}}` = (obtained from login response)
3. Test each endpoint

### Using Python requests
```python
import requests

BASE_URL = "http://localhost:5000/api"

# Sign up
response = requests.post(f"{BASE_URL}/auth/signup", json={
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "password123"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "jane@example.com",
    "password": "password123"
})
token = response.json()['token']

# Analyze assessment
response = requests.post(f"{BASE_URL}/assessments/analyze", json={
    "response": "I am passionate about healthcare and helping people. I'm interested in nursing.",
    "userType": "guest"
})
assessment = response.json()
```

## Frontend Customization

### Color Theme
Edit `frontend/css/style.css`:
```css
:root {
    --primary-color: #ff5722;      /* Main orange */
    --secondary-color: #ff9100;    /* Lighter orange */
    --success-color: #4caf50;      /* Green */
    --danger-color: #f44336;       /* Red */
}
```

### API Endpoint
Edit `frontend/js/index.js`:
```javascript
const API_BASE_URL = 'http://your-api-url:5000/api';
```

### Course Data
Edit `backend/init_db.py`:
- Add/remove courses in `COURSES_DATA`
- Update course descriptions, skills, etc.
- Re-run: `python init_db.py`

### Page Content
Edit HTML files directly:
- `index.html` - Welcome page
- `dashboard.html` - User dashboard
- `assessment.html` - Assessment interface
- `results.html` - Results page

## Configuration

### Environment Variables
Create `.env` file:
```
FLASK_ENV=development
DATABASE_URL=sqlite:////tmp/careerways.db
JWT_SECRET_KEY=your-super-secret-key-change-this
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

### Production Deployment
```bash
# Use Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use a production server like Nginx
```

## Project Structure
```
CareerWays/
├── frontend/
│   ├── index.html              # Landing page
│   ├── dashboard.html          # Dashboard
│   ├── assessment.html         # Assessment
│   ├── results.html            # Results
│   ├── css/
│   │   ├── style.css           # Global styles
│   │   ├── index.css           # Landing styles
│   │   ├── dashboard.css       # Dashboard styles
│   │   ├── assessment.css      # Assessment styles
│   │   └── results.css         # Results styles
│   └── js/
│       ├── index.js            # Landing logic
│       ├── dashboard.js        # Dashboard logic
│       ├── assessment.js       # Assessment logic
│       └── results.js          # Results logic
├── backend/
│   ├── app.py                  # Main Flask app
│   ├── ml_engine.py            # NLP & ML
│   ├── init_db.py              # DB initialization
│   ├── models/
│   │   └── __init__.py         # Database models
│   ├── routes/
│   │   ├── auth_routes.py      # Authentication
│   │   ├── assessment_routes.py # Assessments
│   │   ├── recommendation_routes.py # Recommendations
│   │   ├── user_routes.py      # User profile
│   │   └── favorites_routes.py # Favorites
│   └── requirements.txt        # Dependencies
├── .env.example                # Environment template
├── README.md                   # Project README
└── STARTUP_GUIDE.md            # This file
```

## Troubleshooting

### Issue: Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Issue: Database Not Found
```bash
cd backend
python init_db.py
```

### Issue: CORS Error
- Ensure Flask CORS is enabled (check app.py)
- Verify API_BASE_URL in frontend JS

### Issue: Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: NLTK Data Missing
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
```

### Issue: Python Version
```bash
python --version
# Should be 3.8 or higher
```

## Performance Tips

1. **Caching**: Enable browser caching in production
2. **Minification**: Minify CSS/JS for production
3. **Database**: Use PostgreSQL for production
4. **CDN**: Use CDN for static files
5. **Compression**: Enable gzip compression

## Security Checklist

- [ ] Change JWT_SECRET_KEY in production
- [ ] Use HTTPS in production
- [ ] Set FLASK_ENV=production
- [ ] Configure CORS properly
- [ ] Use strong database passwords
- [ ] Enable rate limiting
- [ ] Validate all user inputs
- [ ] Update dependencies regularly

## Monitoring

Monitor the application:
```bash
# Check API health
curl http://localhost:5000/api/health

# Monitor logs (production)
tail -f /var/log/careerways/app.log
```

## Backup

Database backup:
```bash
# SQLite
cp /tmp/careerways.db /tmp/careerways.backup.db

# PostgreSQL
pg_dump careerways > careerways.sql
```

## Support & Documentation

- API Documentation: See README.md
- Frontend Customization: Edit CSS/HTML directly
- Backend Extension: Add routes in `backend/routes/`
- Database: Use SQLAlchemy ORM

---

**Questions?** Check README.md or create an issue.
