from app import create_app, db
from models import Assessment, Course

app = create_app()
with app.app_context():
    # Get all assessments first to find user
    all_assessments = Assessment.query.all()
    print(f"Total assessments in DB: {len(all_assessments)}")
    
    # Find the most recent assessment to identify user
    if all_assessments:
        latest_assessment = max(all_assessments, key=lambda a: a.created_at)
        user_id = latest_assessment.user_id
        print(f"Latest assessment user_id: {user_id}")
        
        # Get assessments for this user
        user_assessments = Assessment.query.filter_by(user_id=user_id).all()
        print(f"Found {len(user_assessments)} assessments for user")
        
        all_courses = []
        for assessment in user_assessments:
            print(f"\nAssessment {assessment.id} ({assessment.created_at}):")
            print(f"  Recommended courses: {assessment.recommended_courses}")
            print(f"  Match scores: {assessment.match_scores}")
            
            if assessment.recommended_courses:
                score_map = assessment.match_scores or {}
                for course_id in assessment.recommended_courses:
                    course = Course.query.get(course_id)
                    if course:
                        score = score_map.get(course_id, 0)
                        all_courses.append({
                            'name': course.name,
                            'score': score,
                            'assessment_id': assessment.id
                        })
                        print(f"    - {course.name} (score: {score})")
        
        # Count course occurrences
        from collections import Counter
        course_counts = Counter(course['name'] for course in all_courses)
        print(f"\nCourse recommendation counts:")
        for course_name, count in course_counts.most_common():
            print(f"  {course_name}: {count} times")
        
        # Calculate total scores per course
        course_total_scores = {}
        for course in all_courses:
            name = course['name']
            if name not in course_total_scores:
                course_total_scores[name] = 0
            course_total_scores[name] += course['score']
        
        print(f"\nTotal scores per course:")
        for course_name, total_score in sorted(course_total_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {course_name}: {total_score:.2f}")
