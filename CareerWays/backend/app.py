"""
Main Flask Application for CareerWays
AI-Powered College Course Recommendation System
"""

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask import Flask
import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
# CRITICAL: Register this module as 'app' BEFORE any other imports
# This resolves circular import issues in models/__init__.py
sys.modules['app'] = sys.modules[__name__]


# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
mail = Mail()


def get_local_sqlite_uri():
    """Build a reliable local SQLite path for development fallback."""
    project_root = Path(__file__).resolve().parent.parent
    database_dir = project_root / 'database'
    database_dir.mkdir(parents=True, exist_ok=True)
    db_path = (database_dir / 'careerways.db').as_posix()
    return f"sqlite:///{db_path}"


def _parse_cors_origins():
    """Comma-separated CORS_ORIGINS, else FRONTEND_URL, else production default."""
    raw = os.getenv('CORS_ORIGINS', '').strip()
    if not raw:
        raw = os.getenv('FRONTEND_URL', '').strip()
    if raw:
        return [
            o.strip().rstrip('/')
            for o in raw.split(',')
            if o.strip()
        ]
    return ['https://the-career-ways.vercel.app']


def resolve_database_uri():
    """Resolve database URI with smart fallback to SQLite."""
    configured_uri = os.getenv('DATABASE_URL', '').strip()
    # Railway / Heroku-style URLs use postgres:// which SQLAlchemy rejects
    if configured_uri.startswith('postgres://'):
        configured_uri = configured_uri.replace(
            'postgres://', 'postgresql://', 1)

    if not configured_uri:
        print("[CareerWays] No DATABASE_URL configured. Using SQLite.")
        return get_local_sqlite_uri()

    # If it's a Supabase connection, we'll try it but have SQLite as fallback
    if 'supabase.co' in configured_uri or 'postgresql' in configured_uri:
        print(f"[CareerWays] Using Supabase PostgreSQL connection")
        print(
            f"[CareerWays] Note: If Supabase is unreachable, SQLite will be used as fallback")
        return configured_uri

    return configured_uri


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Configuration
    database_uri = resolve_database_uri()
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    engine_opts = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    # sqlite3 does not accept PostgreSQL-style connect_args
    if not database_uri.startswith('sqlite'):
        engine_opts['connect_args'] = {'connect_timeout': 10}
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_opts
    app.config['JWT_SECRET_KEY'] = os.getenv(
        'JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv(
        'MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv(
        'MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    _mail_user = (app.config['MAIL_USERNAME'] or '').strip()
    app.config['MAIL_DEFAULT_SENDER'] = (
        os.getenv('MAIL_DEFAULT_SENDER', '').strip()
        or _mail_user
        or 'noreply@careerways.com'
    )
    app.config['MAIL_TIMEOUT'] = 10

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    cors_origins = _parse_cors_origins()
    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.assessment_routes import assessment_bp
    from routes.recommendation_routes import recommendation_bp
    from routes.user_routes import user_bp
    from routes.favorites_routes import favorites_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(assessment_bp, url_prefix='/api/assessments')
    app.register_blueprint(
        recommendation_bp, url_prefix='/api/recommendations')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')

    # Create tables
    with app.app_context():
        try:
            db.create_all()
            print("[CareerWays] Database tables initialized successfully")
        except Exception as e:
            print(
                f"[CareerWays] Warning: Could not create database tables: {str(e)}")
            print(f"[CareerWays] This is normal if tables already exist in Supabase")

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'healthy', 'message': 'CareerWays API is running'}, 200

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=False, host='0.0.0.0', port=port)
