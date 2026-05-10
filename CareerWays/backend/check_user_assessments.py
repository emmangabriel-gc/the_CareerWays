from app import create_app, db
from models import Assessment, Course

app = create_app()
with app.app_context():
    # Get assessments for the specific user
    user_assessments = Assessment.query.filter_by(user_id='47f12452-6891-472b-9ade-7712b43e49f6').all()
    print(f"Found {len(user_assessments)} assessments for user")
    
    all_courses = []
    for assessment in user_assessments:
        print(f"\nAssessment {assessment.id}:")
        print(f"  Recommended courses: {assessment.recommended_courses}")
        print(f"  Match scores: {assessment.match_scores}")
        
        if assessment.recommended_courses:
            for course_id in assessment.recommended_courses:
                course = Course.query.get(course_id)
                if course:
                    score = assessment.match_scores.get(course_id, 0) if assessment.match_scores else 0
                    all_courses.append({
                        'name': course.name,
                        'score': score,
                        'assessment_id': assessment.id
                    })
                    print(f"    - {course.name} (score: {score})")
    
    # Count course occurrences
    from collections import Counter
    course_counts = Counter(course['name'] for course in all_courses)
    print(f"\nCourse counts:")
    for course_name, count in course_counts.most_common():
        print(f"  {course_name}: {count} times")
    
    # Calculate average scores per course
    course_scores = {}
    for course in all_courses:
        name = course['name']
        if name not in course_scores:
            course_scores[name] = []
        course_scores[name].append(course['score'])
    
    print(f"\nAverage scores per course:")
    for course_name, scores in course_scores.items():
        avg_score = sum(scores) / len(scores)
        print(f"  {course_name}: {avg_score:.2f} (from {len(scores)} assessments)")
