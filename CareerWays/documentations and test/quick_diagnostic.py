"""
Quick diagnostic script for Supabase connection issues
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*60)
print("CAREERWAYS - SUPABASE CONNECTION DIAGNOSTIC")
print("="*60)

# Check 1: Environment variables
print("\n1. Environment Variables Check:")
database_url = os.getenv('DATABASE_URL', '')
jwt_secret = os.getenv('JWT_SECRET_KEY', '')

if database_url:
    print(f"   ✅ DATABASE_URL is set")
    # Check if it's Supabase
    if 'supabase.co' in database_url:
        print(f"   ✅ Using Supabase PostgreSQL")
        # Extract and show safe connection info
        if '@' in database_url:
            host = database_url.split('@')[1].split(':')[0]
            print(f"   ✅ Host: {host}")
    elif 'sqlite' in database_url:
        print(f"   ⚠️  Using SQLite (Local fallback)")
else:
    print(f"   ❌ DATABASE_URL is NOT set")

if jwt_secret and jwt_secret != 'your-secret-key-change-in-production':
    print(f"   ✅ JWT_SECRET_KEY is configured")
else:
    print(f"   ⚠️  JWT_SECRET_KEY is using default value")

# Check 2: Try to import Flask
print("\n2. Flask Import Check:")
try:
    from flask import Flask
    print(f"   ✅ Flask is installed")
except Exception as e:
    print(f"   ❌ Flask import failed: {str(e)}")
    sys.exit(1)

# Check 3: Try to import SQLAlchemy
print("\n3. SQLAlchemy Import Check:")
try:
    from flask_sqlalchemy import SQLAlchemy
    print(f"   ✅ Flask-SQLAlchemy is installed")
except Exception as e:
    print(f"   ❌ Flask-SQLAlchemy import failed: {str(e)}")
    sys.exit(1)

# Check 4: Try to create Flask app
print("\n4. Flask App Creation Check:")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from app import create_app, db

    app = create_app()
    print(f"   ✅ Flask app created successfully")
    print(f"   ✅ Database URI: {database_url[:50]}...")
except Exception as e:
    print(f"   ❌ Flask app creation failed:")
    print(f"      Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 5: Try to connect to database (with timeout)
print("\n5. Database Connection Check (with 5 second timeout):")
try:
    from contextlib import contextmanager
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError("Connection attempt timed out")

    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5 second timeout

    try:
        with app.app_context():
            # Try simple query
            result = db.session.execute('SELECT 1')
            print(f"   ✅ Database connection successful!")
    finally:
        signal.alarm(0)  # Cancel alarm

except TimeoutError:
    print(f"   ❌ Database connection timed out")
    print(f"      This suggests the Supabase server is not reachable")
    print(f"      Check: 1. Internet connection")
    print(f"             2. Supabase credentials in .env")
    print(f"             3. Supabase project is running")
except Exception as e:
    print(f"   ❌ Database connection failed:")
    print(f"      Error: {str(e)}")

# Check 6: Try to import models
print("\n6. Models Import Check:")
try:
    from models import User, Assessment, Course, Favorite, AssessmentDetail
    print(f"   ✅ All models imported successfully")
except Exception as e:
    print(f"   ❌ Models import failed: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
