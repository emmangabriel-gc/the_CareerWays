from app import create_app, db
from models import Assessment

app = create_app()
with app.app_context():
    assessments = Assessment.query.all()
    print(f'Found {len(assessments)} assessments')
    for assessment in assessments:
        print(f'  - {assessment.id}: {assessment.created_at}')
