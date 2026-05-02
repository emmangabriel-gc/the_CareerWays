# CareerWays Project Structure & Files Summary

## 📁 Complete Project Structure

```
CareerWays/
│
├── 📄 README.md                          # Project overview and documentation
├── 📄 STARTUP_GUIDE.md                   # Detailed setup and deployment guide
├── 📄 API_DOCUMENTATION.md               # Complete API reference
├── 📄 requirements.txt                   # Python dependencies
├── 📄 .env.example                       # Environment variables template
│
├── frontend/                             # Frontend files
│   ├── 📄 index.html                     # Landing page with auth (signin/signup)
│   ├── 📄 dashboard.html                 # User dashboard with assessment button
│   ├── 📄 assessment.html                # Chat-like assessment interface
│   ├── 📄 results.html                   # Assessment results & recommendations
│   │
│   ├── css/                              # Stylesheets
│   │   ├── 📄 style.css                  # Global styles & components
│   │   ├── 📄 index.css                  # Landing page styles
│   │   ├── 📄 dashboard.css              # Dashboard styles
│   │   ├── 📄 assessment.css             # Assessment interface styles
│   │   └── 📄 results.css                # Results page styles
│   │
│   └── js/                               # JavaScript files
│       ├── 📄 index.js                   # Landing page logic & auth handling
│       ├── 📄 dashboard.js               # Dashboard functionality
│       ├── 📄 assessment.js              # Assessment chat interface logic
│       └── 📄 results.js                 # Results display & course details
│
├── backend/                              # Flask backend
│   ├── 📄 app.py                         # Main Flask application (26 lines)
│   ├── 📄 ml_engine.py                   # NLP & ML engine (413 lines)
│   │   └── Components:
│   │       • NLPEngine: Tokenization, skill extraction, entity recognition
│   │       • SentimentAnalyzer: Sentiment & motivation analysis
│   │       • RecommendationEngine: Cosine similarity recommendations
│   │       • RandomForestClassifier_Custom: Course category prediction
│   │
│   ├── 📄 init_db.py                     # Database initialization with 22 courses
│   │
│   ├── models/                           # Database models
│   │   └── 📄 __init__.py                # SQLAlchemy ORM models (240 lines)
│   │       • User: User accounts & profiles
│   │       • Assessment: Assessment records & results
│   │       • AssessmentDetail: Detailed NLP analysis
│   │       • Course: Course information & embeddings
│   │       • Favorite: User favorite courses
│   │
│   ├── routes/                           # API endpoints
│   │   ├── 📄 __init__.py                # Package initialization
│   │   ├── 📄 auth_routes.py             # Authentication endpoints (158 lines)
│   │   │   • Signup, Login, Verify, Refresh, Logout
│   │   │
│   │   ├── 📄 assessment_routes.py       # Assessment endpoints (215 lines)
│   │   │   • Analyze responses, Get results, List assessments, Delete
│   │   │
│   │   ├── 📄 recommendation_routes.py   # Recommendation endpoints (105 lines)
│   │   │   • Get courses, Search, Categories, Course details
│   │   │
│   │   ├── 📄 user_routes.py             # User endpoints (240 lines)
│   │   │   • Profile, Favorites, Statistics, Change password
│   │   │
│   │   └── 📄 favorites_routes.py        # Favorites endpoints (backward compat)
│   │
│   └── database/                         # Database storage (auto-created)
│       └── careerways.db                 # SQLite database
│
├── config/                               # Configuration (placeholder)
└── ml_engine/                            # ML models (placeholder for future)
```

## 📊 File Statistics

### Frontend Files
- **HTML Files**: 4 (index, dashboard, assessment, results)
- **CSS Files**: 5 (global + 4 page-specific)
- **JavaScript Files**: 4 (one per page)
- **Total Frontend Lines**: ~3,500 LOC

### Backend Files
- **Main Application**: 1 file (app.py)
- **ML/NLP Engine**: 1 file (ml_engine.py) - 413 lines
- **Database Models**: 1 file (models/__init__.py) - 240 lines
- **API Routes**: 5 files - ~765 lines total
- **Initialization**: 1 file (init_db.py)
- **Total Backend Lines**: ~2,000+ LOC

### Configuration Files
- requirements.txt
- .env.example
- README.md
- STARTUP_GUIDE.md
- API_DOCUMENTATION.md

## 🎯 Key Features by File

### Frontend Components

#### index.html / index.js
- Landing page with welcome section
- Feature highlights
- Sign-up form with validation
- Login form
- Guest access option
- Responsive design

#### dashboard.html / dashboard.js
- User welcome message
- Start Assessment button
- Previous assessments list (for logged-in users)
- Assessment statistics
- Quick stats cards

#### assessment.html / assessment.js
- Chat-like interface
- Initial AI message prompt
- User text input with character count
- Loading indicator
- Modal for taking another assessment
- Login required modal for guests

#### results.html / results.js
- Profile analysis section
- Recommended courses grid
- Course match percentage
- Course detail modal
- Save to favorites functionality
- View results / Dashboard navigation

### Backend Components

#### app.py
- Flask application factory
- Database initialization
- CORS configuration
- Blueprint registration
- Health check endpoint

#### ml_engine.py
- **NLPEngine**: 
  - Text tokenization
  - Skill keyword extraction
  - Interest categorization
  - Entity recognition
  - TF-IDF embeddings
  
- **SentimentAnalyzer**:
  - Polarity & subjectivity analysis
  - Motivation indicators
  - Career mindset assessment
  
- **RecommendationEngine**:
  - Cosine similarity calculation
  - Match score computation
  - Course ranking
  
- **ClassificationEngine**:
  - Random Forest classification
  - Category prediction

#### routes/auth_routes.py
- User registration with validation
- Login with password verification
- Token verification
- Token refresh
- Logout endpoint

#### routes/assessment_routes.py
- Response analysis endpoint
- NLP processing pipeline
- ML recommendation generation
- Assessment retrieval
- Assessment listing & deletion

#### routes/recommendation_routes.py
- Get all courses
- Course search
- Category browsing
- Course detail retrieval

#### routes/user_routes.py
- Profile management
- Password change
- Favorites management
- User statistics
- Account deletion

## 📚 Database Schema

### Users Table
- id (PK)
- name
- email (unique)
- password_hash
- created_at
- updated_at

### Assessments Table
- id (PK)
- user_id (FK, nullable for guests)
- user_response (text)
- skills (JSON array)
- interests (JSON array)
- sentiment
- sentiment_score
- experience
- recommended_courses (JSON array)
- match_scores (JSON object)
- overall_match_score
- created_at
- updated_at

### AssessmentDetails Table
- id (PK)
- assessment_id (FK)
- tokens (JSON)
- entities (JSON)
- embeddings (JSON vector)
- features (JSON)
- feature_importance (JSON)
- classification
- classification_confidence

### Courses Table
- id (PK)
- name (unique)
- description
- duration
- difficulty
- career_path
- skills_taught (JSON)
- prerequisites (JSON)
- career_prospects
- requirements
- keywords (JSON)
- embedding (JSON vector)
- category
- created_at
- updated_at

### Favorites Table
- id (PK)
- user_id (FK)
- course_id (FK)
- created_at
- Unique constraint: (user_id, course_id)

## 🔌 API Endpoints Summary

### Authentication (5 endpoints)
- POST /auth/signup
- POST /auth/login
- POST /auth/verify
- POST /auth/refresh
- POST /auth/logout

### Assessments (4 endpoints)
- POST /assessments/analyze
- GET /assessments/<id>
- GET /assessments/list
- DELETE /assessments/<id>

### Recommendations (4 endpoints)
- GET /recommendations/courses
- GET /recommendations/courses/<id>
- GET /recommendations/search
- GET /recommendations/categories

### Users (7 endpoints)
- GET /users/profile
- PUT /users/profile
- POST /users/change-password
- GET /users/favorites
- POST /users/favorites
- DELETE /users/favorites/<course_id>
- GET /users/stats

### Favorites (3 endpoints - aliases)
- GET /favorites
- POST /favorites
- DELETE /favorites/<course_id>

### System (1 endpoint)
- GET /health

**Total: 24 API Endpoints**

## 📦 Dependencies

### Python Packages (10 main)
1. Flask (2.3.2) - Web framework
2. Flask-CORS (4.0.0) - CORS handling
3. Flask-SQLAlchemy (3.0.5) - ORM
4. SQLAlchemy (2.0.19) - Database toolkit
5. PyJWT (2.8.0) - JWT authentication
6. Werkzeug (2.3.6) - Security utilities
7. nltk (3.8.1) - NLP
8. textblob (0.17.1) - Sentiment analysis
9. scikit-learn (1.3.0) - Machine learning
10. numpy (1.24.3) - Numerical computing

## 🎓 Included Courses (22 Total)

### Healthcare (2)
- BS Nursing
- BS Midwifery

### Business (4)
- BS Accountancy
- BS Business Administration - Financial Management
- BS Business Administration - Human Resource Management
- BS Business Administration - Marketing Management

### IT/Computing (5)
- BS Information Technology
- BS Computer Science
- BS Custom Administration
- BS Entertainment and Multimedia Computing - Game Development
- BS Entertainment and Multimedia Computing - Digital Animation

### Education (6)
- Bachelor of Secondary Education - Math
- Bachelor of Secondary Education - English
- Bachelor of Secondary Education - Filipino
- Bachelor of Elementary Education
- Bachelor of Early Childhood Education
- Bachelor of Physical Education

### Arts & Communication (1)
- Bachelor of Arts and Communication
- Bachelor of Culture and Arts Education

### Hospitality & Tourism (2)
- BS Hospitality Management
- BS Tourism Management

## 🚀 Getting Started

1. **Read**: STARTUP_GUIDE.md
2. **Install**: `pip install -r requirements.txt`
3. **Setup**: `python backend/init_db.py`
4. **Run**: `python backend/app.py`
5. **Access**: `frontend/index.html`

## 📝 Documentation Files

1. **README.md** - Project overview, features, architecture
2. **STARTUP_GUIDE.md** - Installation, setup, deployment
3. **API_DOCUMENTATION.md** - Complete API reference
4. **This File** - Project structure overview

---

**Total Lines of Code**: ~5,500+ LOC (excluding comments & blank lines)
**Development Ready**: ✅ Yes
**Production Ready**: ⚠️ Needs security hardening
**Last Updated**: April 24, 2026
