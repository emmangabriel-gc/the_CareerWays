from app import create_app, db
from models import Assessment, Course

app = create_app()
with app.app_context():
    print("=== DEBUGGING TOP-COURSES ENDPOINT ===")
    
    # Get all assessments from all users
    assessments = Assessment.query.all()
    print(f"Found {len(assessments)} assessments")
    
    # Tally courses weighted by match_score
    tally = {}  # courseName -> { score, appearances, abbreviation }
    
    for i, assessment in enumerate(assessments[:3]):  # Check first 3 for debugging
        print(f"\nAssessment {i+1}: {assessment.id}")
        print(f"  Recommended courses: {assessment.recommended_courses}")
        print(f"  Match scores: {assessment.match_scores}")
        
        if not assessment.recommended_courses:
            print("  No recommended courses - skipping")
            continue
            
        score_map = assessment.match_scores or {}
        print(f"  Score map: {score_map}")
        
        for course_id in assessment.recommended_courses:
            course = Course.query.get(course_id)
            print(f"    Course {course_id}: {course.name if course else 'NOT FOUND'}")
            
            if not course or not course.name:
                print("    Skipping - no course or no name")
                continue
                
            score = score_map.get(course_id, 0)
            course_name = str(course.name)  # Ensure it's a string
            
            if course_name not in tally:
                tally[course_name] = { 
                    'score': 0, 
                    'appearances': 0, 
                    'abbreviation': str(course.abbreviation) if course.abbreviation else None 
                }
                print(f"    Added to tally: {course_name}")
            
            tally[course_name]['score'] += score
            tally[course_name]['appearances'] += 1
            print(f"    Updated tally for {course_name}: score={tally[course_name]['score']}, appearances={tally[course_name]['appearances']}")
    
    print(f"\nFinal tally: {tally}")
    
    if not tally:
        print("No tally - returning empty")
        result = {'courses': []}
    else:
        # Sort by score and take top 5
        sorted_courses = sorted(
            tally.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )[:5]
        
        total_score = sum(v['score'] for _, v in sorted_courses) or 1
        
        courses = [
            {
                'name': name,
                'abbreviation': data['abbreviation'],
                'appearances': data['appearances'],
                'percentage': round((data['score'] / total_score) * 100)
            }
            for name, data in sorted_courses
        ]
        
        result = {'courses': courses}
        print(f"Final result: {result}")
    
    print("=" * 40)
