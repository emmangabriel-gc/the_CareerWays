# CareerWays - AI-Powered College Course Recommendation System

CareerWays is an intelligent system that uses Natural Language Processing (NLP), Machine Learning, and Sentiment Analysis to provide personalized college course recommendations based on student profiles.

## 🌟 Features

### Core Features
- **AI-Powered Assessment**: Students answer one comprehensive question about their interests, skills, experience, and goals
- **NLP Analysis**: Tokenization, entity extraction, and natural language understanding
- **Sentiment Analysis**: Analyzes student motivation and career mindset
- **ML-Based Classification**: Random Forest classifier for course category prediction
- **Recommendation Engine**: Cosine similarity-based course matching
- **Vector Embeddings**: TF-IDF vectorization for semantic understanding

### User Features
- **Authentication**: Secure user registration and login
- **Guest Access**: Try the system without creating an account
- **Assessment History**: Registered users can view and manage previous assessments
- **Favorite Courses**: Save favorite courses for later reference
- **Profile Management**: Update personal information and preferences

## 🏗️ Architecture

```
CareerWays/
├── frontend/              # Vue.js frontend application
│   ├── index.html        # Landing page with auth
│   ├── dashboard.html    # User dashboard
│   ├── assessment.html   # Assessment interface
│   ├── results.html      # Results and recommendations
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript functionality
├── backend/              # Flask backend
│   ├── app.py           # Main application
│   ├── ml_engine.py     # NLP and ML engines
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── init_db.py       # Database initialization
│   └── requirements.txt  # Python dependencies
├── database/            # Database files
└── config/              # Configuration files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js/npm (optional, for frontend development)
- SQLite or PostgreSQL

### Backend Setup

1. **Clone and navigate to project**
```bash
cd CareerWays
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python backend/init_db.py
```

6. **Run Flask application**
```bash
cd backend
python app.py
```

The backend will start at `http://localhost:5000`

### Frontend Setup

1. **Open frontend files**
   - The frontend is built with vanilla HTML/CSS/JavaScript
   - No build process required
   - Open `frontend/index.html` in your browser

2. **Configure API endpoint**
   - Update `API_BASE_URL` in frontend JavaScript files if needed
   - Default: `http://localhost:5000/api`

## 📚 Available Courses

The system includes 22 course programs:

### Healthcare
- BS Nursing
- BS Midwifery

### Business
- BS Accountancy
- BS Business Administration (Financial Management, HR, Marketing)
- BS Custom Administration

### Information Technology
- BS Information Technology
- BS Computer Science
- BS Entertainment and Multimedia Computing (Game Development, Digital Animation)

### Education
- Bachelor of Secondary Education (Math, English, Filipino)
- Bachelor of Elementary Education
- Bachelor of Early Childhood Education
- Bachelor of Physical Education
- Bachelor of Culture and Arts Education

### Arts & Communication
- Bachelor of Arts and Communication

### Hospitality & Tourism
- BS Hospitality Management
- BS Tourism Management

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/verify` - Verify token
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout user

### Assessments
- `POST /api/assessments/analyze` - Analyze student response
- `GET /api/assessments/<id>` - Get assessment results
- `GET /api/assessments/list` - List user assessments
- `DELETE /api/assessments/<id>` - Delete assessment

### Recommendations
- `GET /api/recommendations/courses` - Get all courses
- `GET /api/recommendations/courses/<id>` - Get course details
- `GET /api/recommendations/search?q=query` - Search courses
- `GET /api/recommendations/categories` - Get categories

### User
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/change-password` - Change password
- `GET /api/users/favorites` - Get favorite courses
- `POST /api/users/favorites` - Add favorite
- `DELETE /api/users/favorites/<course_id>` - Remove favorite
- `GET /api/users/stats` - Get user statistics

## 🧠 ML & NLP Pipeline

### 1. Tokenization
- Word and sentence tokenization
- Stop word removal
- Stemming/lemmatization

### 2. Sentiment Analysis
- Polarity and subjectivity analysis
- Motivation indicators extraction
- Career mindset assessment

### 3. Skill Extraction
- Keyword-based skill identification
- Skill categorization
- Relevance scoring

### 4. Interest Extraction
- Topic modeling
- Interest category mapping
- Frequency analysis

### 5. Recommendation Engine
- TF-IDF vectorization
- Cosine similarity matching
- Multi-factor scoring (skill + interest + sentiment)

### 6. Classification
- Random Forest classifier
- Course category prediction
- Confidence scoring

## 📊 User Assessment Flow

```
1. User Input
   ↓
2. NLP Processing
   ├─ Tokenization
   ├─ Entity Extraction
   ├─ Skill Extraction
   └─ Interest Analysis
   ↓
3. Sentiment & Motivation Analysis
   ↓
4. Feature Extraction
   ↓
5. ML Classification
   ↓
6. Recommendation Engine
   ├─ Similarity Calculation
   ├─ Score Calculation
   └─ Ranking
   ↓
7. Results & Recommendations
```

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- CORS protection
- Token expiration (30 days)
- Input validation
- SQL injection prevention (SQLAlchemy ORM)

## 📱 Responsive Design

- Mobile-first responsive layout
- Touch-friendly interface
- Accessible color contrast
- Semantic HTML5
- CSS Grid and Flexbox

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=backend tests/
```

## 🚢 Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker (Optional)
```bash
docker build -t careerways .
docker run -p 5000:5000 careerways
```

## 📝 Database Models

### Users
- Store user accounts and authentication
- Profile information
- Assessment history

### Assessments
- Student responses
- Analysis results
- Recommended courses
- Match scores

### Courses
- Course information
- Skills taught
- Keywords and category
- Vector embeddings

### Favorites
- User favorite courses
- Save timestamps
- Quick access to preferences

## 🛠️ Configuration

### Environment Variables
- `FLASK_ENV`: Development or production
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `SERVER_HOST`: Server host address
- `SERVER_PORT`: Server port number

### Database Configuration
- SQLite (default): `sqlite:////tmp/careerways.db`
- PostgreSQL: `postgresql://user:pass@localhost:5432/careerways`

## 📄 License

This project is provided as-is for educational purposes.

## 👥 Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Support

For issues and questions, please create an issue in the repository.

## 🎯 Future Enhancements

- [ ] Video tutorials for users
- [ ] Integration with course enrollment systems
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] AI-powered chatbot for Q&A
- [ ] Course comparison tools
- [ ] Alumni success tracking
- [ ] Real-time notifications

---

**Made with ❤️ for educational excellence**
#   C a r e e r - W a y s  
 