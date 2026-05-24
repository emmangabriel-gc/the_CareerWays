"""
Database models for CareerWays
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Import db - this is set up in app.py to handle circular imports correctly
from app import db


class User(db.Model):
    """User model for registered users"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(1024), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(500), nullable=False)

    # Email verification fields
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    verification_token_expires = db.Column(db.DateTime, nullable=True)

    # Password reset fields
    password_reset_otp = db.Column(db.String(10), nullable=True)
    password_reset_otp_expires = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String(500), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = db.relationship(
        'Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship(
        'Favorite', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()
        }


class Assessment(db.Model):
    """Assessment model for storing user assessments"""
    __tablename__ = 'assessments'

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=True, index=True)
    user_response = db.Column(db.Text, nullable=False)

    # Analysis results
    skills = db.Column(db.JSON, nullable=True)  # List of identified skills
    interests = db.Column(db.JSON, nullable=True)  # List of interests
    # Positive, Negative, Neutral
    sentiment = db.Column(db.String(50), nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)  # -1 to 1
    experience = db.Column(db.Text, nullable=True)  # Summarized experience

    # Recommendation results
    # List of recommended course IDs
    recommended_courses = db.Column(db.JSON, nullable=True)
    # Match scores for each course
    match_scores = db.Column(db.JSON, nullable=True)
    overall_match_score = db.Column(
        db.Float, nullable=True)  # Average match score

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analysis_details = db.relationship(
        'AssessmentDetail', backref='assessment', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_courses=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'user_response': self.user_response,
            'skills': self.skills or [],
            'interests': self.interests or [],
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'experience': self.experience,
            'match_score': self.overall_match_score,
            'created_at': self.created_at.isoformat(),
            'date': self.created_at.strftime('%Y-%m-%d')
        }

        if include_courses:
            data['courses'] = [
                Course.query.get(course_id).to_dict()
                for course_id in (self.recommended_courses or [])
            ]

        return data


class AssessmentDetail(db.Model):
    """Detailed analysis results for assessments"""
    __tablename__ = 'assessment_details'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.String(36), db.ForeignKey(
        'assessments.id'), nullable=False, index=True)

    # NLP analysis details
    tokens = db.Column(db.JSON, nullable=True)  # Tokenized words
    entities = db.Column(db.JSON, nullable=True)  # Named entities
    embeddings = db.Column(db.JSON, nullable=True)  # Vector embeddings

    # Feature analysis
    features = db.Column(db.JSON, nullable=True)  # Extracted features
    feature_importance = db.Column(
        db.JSON, nullable=True)  # Feature importance scores

    # Classification results
    # Random Forest classification
    classification = db.Column(db.String(100), nullable=True)
    classification_confidence = db.Column(
        db.Float, nullable=True)  # 0-1 confidence score

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Course(db.Model):
    """Course model for available courses"""
    __tablename__ = 'courses'

    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    # Beginner, Intermediate, Advanced
    difficulty = db.Column(db.String(50), nullable=True)
    career_path = db.Column(db.String(255), nullable=True)

    # Course details
    skills_taught = db.Column(db.JSON, nullable=True)  # List of skills
    prerequisites = db.Column(db.JSON, nullable=True)  # List of prerequisites
    career_prospects = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)

    # ML features
    keywords = db.Column(db.JSON, nullable=True)  # Related keywords
    # Vector embedding for similarity
    embedding = db.Column(db.JSON, nullable=True)
    category = db.Column(db.String(100), nullable=True)  # Course category

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    favorites = db.relationship(
        'Favorite', backref='course', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'difficulty': self.difficulty,
            'career_path': self.career_path,
            'skills_taught': self.skills_taught or [],
            'skills_learned': self.skills_taught or [],
            'keywords': self.keywords or [],
            'prerequisites': self.prerequisites or [],
            'career_prospects': self.career_prospects,
            'requirements': self.requirements,
            'category': self.category
        }


class Favorite(db.Model):
    """Model for user favorite courses"""
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, index=True)
    course_id = db.Column(db.String(50), db.ForeignKey(
        'courses.id'), nullable=False, index=True)
    priority = db.Column(db.String(20), default='saved')  # first_choice, second_choice, saved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure unique combination of user and course
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'course_id', name='uq_user_course'),)
