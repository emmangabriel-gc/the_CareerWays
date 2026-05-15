"""
Main Flask Application for CareerWays
AI-Powered College Course Recommendation System
"""

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask import Flask, request
import os
import sys
from pathlib import Path
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from sqlalchemy import text
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


def _strip_env_quotes(value):
    """Deployment platforms sometimes store values wrapped in quotes."""
    s = (value or '').strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1].strip()
    return s


def _parse_cors_origins():
    """Comma-separated CORS_ORIGINS, else FRONTEND_URL, else production default."""
    raw = _strip_env_quotes(os.getenv('CORS_ORIGINS', ''))
    if not raw:
        raw = _strip_env_quotes(os.getenv('FRONTEND_URL', ''))
    if raw:
        return [
            o.strip().rstrip('/')
            for o in raw.split(',')
            if o.strip()
        ]
    return ['https://the-career-ways.vercel.app']


def _remove_pgbouncer_param(uri):
    """Remove pgbouncer=true from Supabase transaction pooler URIs."""
    parsed = urlparse(uri)
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for k, v in query_items if k.lower() != 'pgbouncer']
    if len(filtered) == len(query_items):
        return uri
    return urlunparse(parsed._replace(query=urlencode(filtered, doseq=True)))


def _merge_cors_origins():
    """Env-based origins plus known production frontend (deployment env mistakes won't drop Vercel)."""
    parsed = _parse_cors_origins()
    defaults = [
        'https://the-career-ways.vercel.app',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
    ]
    out = []
    seen = set()
    for o in list(parsed) + defaults:
        o = (o or '').strip().rstrip('/')
        if not o or o in seen:
            continue
        seen.add(o)
        out.append(o)
    return out


def resolve_database_uri():
    """Resolve database URI with smart fallback to SQLite."""
    configured_uri = _strip_env_quotes(os.getenv('DATABASE_URL', '')).strip()
    if configured_uri and configured_uri.lower().startswith(('http://', 'https://')):
        raise RuntimeError(
            "DATABASE_URL must be a PostgreSQL URI (postgresql:// or postgres://). "
            "Copy it from Supabase: Project Settings → Database → Connection string → URI. "
            "Do not paste an https:// Supabase API URL or dashboard link as DATABASE_URL."
        )
    # Heroku-style URLs use postgres:// which SQLAlchemy rejects
    if configured_uri.startswith('postgres://'):
        configured_uri = configured_uri.replace(
            'postgres://', 'postgresql://', 1)

    if not configured_uri:
        print("[CareerWays] No DATABASE_URL configured. Using SQLite.")
        return get_local_sqlite_uri()

    # Supabase / managed Postgres often require TLS; psycopg2 may fail without sslmode
    if configured_uri.startswith('postgresql'):
        low = configured_uri.lower()
        if 'sslmode=' not in low and 'ssl=' not in low:
            joiner = '&' if '?' in configured_uri else '?'
            configured_uri = f'{configured_uri}{joiner}sslmode=require'
        configured_uri = _remove_pgbouncer_param(configured_uri)

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
        connect_args = {'connect_timeout': 10}
        # PgBouncer transaction mode: disable server-side prepares (avoids random DB errors)
        if 'pooler.supabase.com' in database_uri.lower():
            connect_args['prepare_threshold'] = None
        engine_opts['connect_args'] = connect_args
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_opts
    app.config['JWT_SECRET_KEY'] = os.getenv(
        'JWT_SECRET_KEY', '768e254f-6009-471f-b016-3e455c02b30a')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

    # Email configuration
    app.config['MAIL_SERVER'] = _strip_env_quotes(
        os.getenv('MAIL_SERVER', 'smtp.gmail.com'))
    app.config['MAIL_PORT'] = int(
        _strip_env_quotes(os.getenv('MAIL_PORT', '587')))
    app.config['MAIL_USE_TLS'] = _strip_env_quotes(
        os.getenv('MAIL_USE_TLS', 'true')).lower() == 'true'
    app.config['MAIL_USE_SSL'] = _strip_env_quotes(
        os.getenv('MAIL_USE_SSL', 'false')).lower() == 'true'
    app.config['MAIL_USERNAME'] = _strip_env_quotes(
        os.getenv('MAIL_USERNAME', ''))
    app.config['MAIL_PASSWORD'] = _strip_env_quotes(
        os.getenv('MAIL_PASSWORD', ''))
    _mail_user = (app.config['MAIL_USERNAME'] or '').strip()
    app.config['MAIL_DEFAULT_SENDER'] = (
        _strip_env_quotes(os.getenv('MAIL_DEFAULT_SENDER', '')).strip()
        or _mail_user
        or 'noreply@careerways.com'
    )
    app.config['MAIL_TIMEOUT'] = int(
        _strip_env_quotes(os.getenv('MAIL_TIMEOUT', '30')))

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    def _check_database_connection():
        if database_uri.startswith('sqlite'):
            print("[CareerWays] Using local SQLite database.")
            return
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            print("[CareerWays] Supabase/PostgreSQL database connection is available.")
        except Exception as e:
            print(
                "[CareerWays] WARNING: Could not connect to the configured PostgreSQL database.")
            print(f"[CareerWays]   {str(e)}")
            print("[CareerWays]   Check DATABASE_URL, credentials, and network access.")
            print("[CareerWays]   The app may start, but database queries will fail.")

    _check_database_connection()

    cors_origins = _merge_cors_origins()
    cors_origin_set = {o.rstrip('/') for o in cors_origins}

    def _origin_allowed(origin):
        if not origin:
            return False
        key = origin.strip().rstrip('/')
        if key in cors_origin_set:
            return True
        # Vercel preview deployments (*.vercel.app)
        if key.startswith('https://') and '.vercel.app' in key:
            host = key.split('://', 1)[1].split('/', 1)[0]
            if host.endswith('.vercel.app'):
                return True
        return False

    def _apply_cors_headers(resp):
        origin = (request.headers.get('Origin') or '').strip()
        if not origin or not _origin_allowed(origin):
            return resp
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        req_headers = request.headers.get('Access-Control-Request-Headers')
        if req_headers:
            resp.headers['Access-Control-Allow-Headers'] = req_headers
        else:
            resp.headers['Access-Control-Allow-Headers'] = (
                'Content-Type, Authorization'
            )
        resp.headers['Access-Control-Allow-Methods'] = (
            'GET, POST, PUT, DELETE, OPTIONS'
        )
        resp.headers['Access-Control-Max-Age'] = '86400'
        return resp

    @app.before_request
    def _cors_preflight():
        if request.method != 'OPTIONS':
            return None
        if not request.path.startswith('/api/'):
            return None
        origin = (request.headers.get('Origin') or '').strip()
        if not _origin_allowed(origin):
            return None
        # 200 avoids strict clients/proxies that mishandle empty 204 preflights
        r = app.make_response('', 200)
        return _apply_cors_headers(r)

    @app.after_request
    def _cors_after(resp):
        # Flask-CORS can miss error paths; always attach when Origin is allowed
        if resp.headers.get('Access-Control-Allow-Origin'):
            return resp
        return _apply_cors_headers(resp)

    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.assessment_routes import assessment_bp, analyze_response
    from routes.recommendation_routes import recommendation_bp
    from routes.user_routes import user_bp
    from routes.favorites_routes import favorites_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(assessment_bp, url_prefix='/api/assessments')
    app.register_blueprint(
        recommendation_bp, url_prefix='/api/recommendations')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')

    @app.route('/api/assessment', methods=['POST'])
    def legacy_assessment():
        return analyze_response()

    # Create tables
    with app.app_context():
        try:
            db.create_all()
            print("[CareerWays] Database tables initialized successfully")
        except Exception as e:
            err_text = str(e)
            print(
                f"[CareerWays] Warning: Could not create database tables: {err_text}")
            if 'password authentication failed' in err_text.lower():
                print(
                    "[CareerWays] Supabase connection failed due to invalid database credentials.")
                print(
                    "[CareerWays] Check DATABASE_URL and password in your deployment environment.")
            elif 'could not connect to server' in err_text.lower() or 'timeout expired' in err_text.lower():
                print(
                    "[CareerWays] Database host unreachable or port incorrect. Verify DATABASE_URL and network access.")
            else:
                print(
                    "[CareerWays] This is normal if tables already exist in Supabase")

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return {'status': 'healthy', 'message': 'CareerWays API is running'}, 200

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=False, host='0.0.0.0', port=port)
