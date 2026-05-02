"""
Minimal test to identify the exact issue
"""
from dotenv import load_dotenv
import sys
import os

# Set working directory
os.chdir(r'c:\Users\delac\Pictures\bitch\CareerWays')
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

print("Step 1: Loading .env...")
load_dotenv()
print("✅ .env loaded")

print("\nStep 2: Checking DATABASE_URL...")
db_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {db_url[:50]}..." if db_url else "❌ No DATABASE_URL")

print("\nStep 3: Importing Flask...")
try:
    from flask import Flask
    print("✅ Flask imported")
except Exception as e:
    print(f"❌ Flask import failed: {e}")
    sys.exit(1)

print("\nStep 4: Creating app...")
try:
    from app import create_app
    app = create_app()
    print("✅ App created")
except Exception as e:
    print(f"❌ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Testing database connection...")
try:
    from app import db
    with app.app_context():
        print("  Executing test query...")
        result = db.session.execute('SELECT 1')
        print("✅ Database connection SUCCESS")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

print("\nDone!")
