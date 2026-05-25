from models import Course
from app import app, db
import sys
sys.path.insert(0, 'backend')

try:
    with app.app_context():
        count = db.session.query(Course).count()
        print(f"Total courses in DB: {count}\n")

        courses = db.session.query(Course).all()
        if courses:
            for c in courses:
                print(f"Course: {c.name}")
                print(f"  ID: {c.id}")
                print(
                    f"  Description: {c.description[:100] if c.description else 'None'}...")
                print(f"  Skills: {c.skills_taught}")
                print(f"  Keywords: {c.keywords}")
                print()
        else:
            print("No courses found in database")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
