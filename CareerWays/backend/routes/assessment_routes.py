"""
Assessment Routes for CareerWays
"""

from flask import Blueprint, request, jsonify
from app import db
from models import User, Assessment, AssessmentDetail, Course
from routes.auth_routes import verify_token
import uuid
from datetime import datetime
import json

assessment_bp = Blueprint('assessment', __name__)

_ml_cache = None


def _get_ml():
    """Load NLP stack only when needed (keeps /api/auth/* startup light on the main API process)."""
    global _ml_cache
    if _ml_cache is None:
        from ml_engine import nlp_engine, sentiment_analyzer, RecommendationEngine
        _ml_cache = (nlp_engine, sentiment_analyzer, RecommendationEngine)
    return _ml_cache


def get_all_courses():
    """Get all courses from database"""
    courses = Course.query.all()
    return [course.to_dict() for course in courses]


def get_current_user(request):
    """Get current user from token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    try:
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if 'error' in payload:
            return None
        return User.query.get(payload['user_id'])
    except:
        return None


@assessment_bp.route('/analyze', methods=['POST'])
def analyze_response():
    """Analyze user response and generate recommendations"""
    try:
        data = request.get_json()

        if not data or 'response' not in data:
            return jsonify({'message': 'Missing response text'}), 400

        user_response = data['response'].strip()
        user_type = data.get('userType', 'guest')

        if len(user_response) < 20:
            return jsonify({'message': 'Response too short. Please provide more details.'}), 400

        nlp_engine, sentiment_analyzer, RecommendationEngine = _get_ml()

        # Get current user if logged in
        current_user = None
        if user_type == 'registered':
            current_user = get_current_user(request)
            if not current_user:
                return jsonify({'message': 'Unauthorized'}), 401

        # NLP Analysis
        # 1. Tokenization
        tokens_data = nlp_engine.tokenize(user_response)

        # 2. Sentiment Analysis
        sentiment_data = sentiment_analyzer.analyze(user_response)
        sentiment = sentiment_data['sentiment_level']
        sentiment_score = sentiment_data['polarity_score']

        # 3. Skill Extraction
        skills_data = nlp_engine.extract_skills(user_response)
        skills = skills_data['skills']
        skill_count = skills_data['skill_count']

        # 4. Interest Extraction
        interests = nlp_engine.extract_interests(user_response)

        # 5. Experience Extraction (for actual experiences like clubs, competitions)
        experiences = nlp_engine.extract_experiences(user_response)

        # 6. Create Embedding
        embedding = nlp_engine.create_embedding(user_response)

        # Prepare features for classification
        motivation_score = (
            int(sentiment_data['motivation_indicators']['goal_oriented']) +
            int(sentiment_data['motivation_indicators']['passionate']) +
            int(sentiment_data['motivation_indicators']['growth_mindset'])
        ) / 3

        experience_level = (
            int(sentiment_data['motivation_indicators']['experienced'])
        )

        classification_features = [
            min(skill_count / 10, 1.0),  # Normalized skill count
            # Normalized sentiment (-1 to 1 -> 0 to 1)
            (sentiment_score + 1) / 2,
            motivation_score,             # Motivation level
            experience_level              # Experience indicator
        ]

        # Get all courses
        courses_list = get_all_courses()

        # Enhanced Recommendation Engine
        rec_engine = RecommendationEngine(courses_list)
        recommendations = rec_engine.recommend(
            user_response, top_n=8)  # Get more recommendations for better filtering

        # Calculate enhanced match scores for each course
        top_courses = []
        match_scores = {}
        recommended_course_ids = []
        embedding_data = {}

        for rec in recommendations:
            course_id = rec['course_id']
            course_data = rec['course_data']

            # Calculate detailed match score with enhanced algorithm
            score_data = RecommendationEngine.calculate_match_score(
                skills,
                interests,
                course_data.get('skills_taught', []) or course_data.get(
                    'skills_learned', []),
                course_data.get('keywords', [])
            )

            # Enhanced scoring with semantic and relevance components
            semantic_score = rec.get('semantic_score', 0) or 0
            relevance_score = rec.get('relevance_score', 0) or 0

            # Weighted combination: semantic similarity, skill matching, and relevance
            final_match_score = (
                semantic_score * 0.4 +  # Semantic understanding
                score_data['overall_score'] * 0.4 +  # Traditional matching
                relevance_score * 0.2  # Relevance filtering
            )

            # Only include courses with meaningful match scores
            if final_match_score >= 32:
                match_scores[course_id] = final_match_score
                recommended_course_ids.append(course_id)

                # Store embedding data for visualization
                embedding_data[course_id] = {
                    'semantic_score': semantic_score,
                    'relevance_score': relevance_score,
                    'skill_match': score_data['skill_match'],
                    'interest_match': score_data['interest_match'],
                    'semantic_bonus': score_data.get('semantic_bonus', 0)
                }

                course_data['match_score'] = final_match_score
                course_data['semantic_score'] = semantic_score
                course_data['relevance_score'] = relevance_score
                top_courses.append(course_data)

        # Sort by final match score and take top recommendations
        top_courses.sort(key=lambda x: x['match_score'], reverse=True)
        top_courses = top_courses[:3]  # Limit to top 3 for user display

        # Calculate overall match score
        overall_match_score = sum(match_scores.values(
        )) / len(match_scores) if match_scores else 0

        # Create Assessment record
        assessment_id = str(uuid.uuid4())

        assessment = Assessment(
            id=assessment_id,
            user_id=current_user.id if current_user else None,
            user_response=user_response,
            skills=skills,
            interests=interests,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            experience='; '.join(
                experiences) if experiences else 'No specific experiences mentioned',
            recommended_courses=recommended_course_ids,
            match_scores=match_scores,
            overall_match_score=overall_match_score
        )

        db.session.add(assessment)

        # Create Assessment Details
        assessment_detail = AssessmentDetail(
            assessment_id=assessment_id,
            tokens=tokens_data['words'],
            entities=experiences,  # Now stores actual experiences
            embeddings=embedding,
            features=classification_features,
            classification='General Studies'
        )

        db.session.add(assessment_detail)
        db.session.commit()

        return jsonify({
            'message': 'Assessment analyzed successfully',
            'assessment_id': assessment_id,
            'skills': skills,
            'interests': interests,
            'sentiment': sentiment,
            'experience': ' '.join(experiences) if experiences else 'Not specified',
            'courses': top_courses,
            'match_scores': match_scores,
            'overall_match_score': overall_match_score,
            'embedding_data': embedding_data,
            'recommendation_quality': {
                'total_analyzed': len(courses_list),
                'relevant_matches': len(top_courses),
                'avg_match_score': overall_match_score,
                'uses_semantic_embedding': rec_engine.use_semantic
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Error analyzing response: {str(e)}'}), 500


@assessment_bp.route('/<assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    """Get assessment results"""
    try:
        assessment = Assessment.query.get(assessment_id)

        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404

        # Get course details
        courses_data = []
        for course_id in (assessment.recommended_courses or []):
            course = Course.query.get(course_id)
            if course:
                course_dict = course.to_dict()
                score = assessment.match_scores.get(course_id, 0)
                course_dict['match_score'] = score
                course_dict['semantic_score'] = score
                course_dict['relevance_score'] = score
                courses_data.append(course_dict)

        return jsonify({
            'id': assessment.id,
            'user_response': assessment.user_response,
            'skills': assessment.skills,
            'interests': assessment.interests,
            'sentiment': assessment.sentiment,
            'sentiment_score': assessment.sentiment_score,
            'experience': assessment.experience,
            'courses': courses_data,
            'match_score': assessment.overall_match_score,
            'created_at': assessment.created_at.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@assessment_bp.route('/list', methods=['GET'])
def list_assessments():
    """List all assessments for current user"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(
            Assessment.created_at.desc()
        ).all()

        def get_top_course_data(assessment):
            """Get best-fit course and its compatibility score."""
            if not assessment.recommended_courses:
                return None, 0

            best_course_id = None
            best_score = 0
            score_map = assessment.match_scores or {}

            for course_id in assessment.recommended_courses:
                score = score_map.get(course_id, 0)
                if score >= best_score:
                    best_score = score
                    best_course_id = course_id

            if not best_course_id:
                best_course_id = assessment.recommended_courses[0]

            best_course = Course.query.get(best_course_id)
            best_course_name = best_course.name if best_course else 'Course'
            return best_course_name, best_score

        assessments_data = []
        for assessment in assessments:
            best_fit_course, best_fit_score = get_top_course_data(assessment)
            assessments_data.append({
                'id': assessment.id,
                'date': assessment.created_at.strftime('%Y-%m-%d'),
                'match_score': assessment.overall_match_score,
                'courses': assessment.recommended_courses,
                'best_fit_course': best_fit_course,
                'best_fit_score': best_fit_score,
                'created_at': assessment.created_at.isoformat()
            })

        return jsonify({
            'message': 'Assessments retrieved',
            'assessments': assessments_data
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@assessment_bp.route('/<assessment_id>', methods=['DELETE'])
def delete_assessment(assessment_id):
    """Delete assessment"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        assessment = Assessment.query.get(assessment_id)

        if not assessment:
            return jsonify({'message': 'Assessment not found'}), 404

        if assessment.user_id != current_user.id:
            return jsonify({'message': 'Forbidden'}), 403

        db.session.delete(assessment)
        db.session.commit()

        return jsonify({'message': 'Assessment deleted'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@assessment_bp.route('/top-courses', methods=['GET'])
def get_top_courses():
    """Get top courses with preference for current user's assessments"""
    try:
        # Get current user if authenticated
        current_user = get_current_user(request)

        # Get all assessments from all users
        all_assessments = Assessment.query.all()

        # Tally courses weighted by match_score with user preference
        tally = {}  # courseName -> { score, appearances, abbreviation }

        for assessment in all_assessments:
            if not assessment.recommended_courses:
                continue

            score_map = assessment.match_scores or {}

            # Give higher weight to current user's assessments
            user_weight = 2.0 if current_user and assessment.user_id == current_user.id else 1.0

            for course_id in assessment.recommended_courses:
                course = Course.query.get(course_id)
                if not course or not course.name:
                    continue

                score = score_map.get(course_id, 0) * user_weight
                course_name = str(course.name)  # Ensure it's a string

                if course_name not in tally:
                    tally[course_name] = {
                        'score': 0,
                        'appearances': 0,
                        'abbreviation': None
                    }
                tally[course_name]['score'] += score
                tally[course_name]['appearances'] += 1

        if not tally:
            return jsonify({'courses': []}), 200

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

        return jsonify({'courses': courses}), 200

    except Exception as e:
        print(f"Error in top-courses endpoint: {str(e)}")
        return jsonify({'courses': []}), 200
