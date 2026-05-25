from app import app, db
from models import Course
from ml_engine import RecommendationEngine
import os
import sys
import unittest
base_dir = os.path.abspath(os.path.dirname(__file__) or '.')
sys.path.insert(0, os.path.join(base_dir, 'backend'))


class RecommendationEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        with cls.app.app_context():
            courses = db.session.query(Course).all()
            cls.engine = RecommendationEngine([c.to_dict() for c in courses])

    def test_education_recommendations(self):
        text = "I love teaching children and helping them learn. I'm passionate about education."
        recommendations = self.engine.recommend(text, top_n=5)
        self.assertTrue(recommendations)
        names = [rec['course_name'].lower() for rec in recommendations]
        self.assertTrue(any(
            'education' in name or 'teaching' in name or 'child' in name for name in names))
        self.assertFalse(any(
            'nursing' in name or 'accounting' in name or 'hotel' in name for name in names))

    def test_programming_recommendations(self):
        text = "I'm interested in programming, coding, and building software applications."
        recommendations = self.engine.recommend(text, top_n=5)
        self.assertTrue(recommendations)
        names = [rec['course_name'].lower() for rec in recommendations]
        self.assertTrue(any(
            'it' in name or 'computer' in name or 'software' in name or 'program' in name for name in names))
        self.assertFalse(any(
            'hospitality' in name or 'teaching' in name or 'journalism' in name for name in names))

    def test_healthcare_recommendations(self):
        text = "I want to work in healthcare, helping patients and providing medical care."
        recommendations = self.engine.recommend(text, top_n=5)
        self.assertTrue(recommendations)
        names = [rec['course_name'].lower() for rec in recommendations]
        self.assertTrue(any(
            'nurse' in name or 'health' in name or 'medical' in name or 'care' in name for name in names))
        self.assertFalse(
            any('business' in name or 'hotel' in name or 'music' in name for name in names))


if __name__ == '__main__':
    unittest.main()
