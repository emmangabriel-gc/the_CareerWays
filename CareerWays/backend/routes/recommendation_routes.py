"""
Recommendation Routes for CareerWays
"""

from flask import Blueprint, request, jsonify
from app import db
from models import Course, Favorite, User
from routes.auth_routes import verify_token

recommendation_bp = Blueprint('recommendation', __name__)


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


@recommendation_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """Get all available courses"""
    try:
        courses = Course.query.all()
        courses_data = [course.to_dict() for course in courses]

        return jsonify({
            'message': 'Courses retrieved',
            'courses': courses_data,
            'count': len(courses_data)
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@recommendation_bp.route('/courses/<course_id>', methods=['GET'])
def get_course_detail(course_id):
    """Get detailed course information"""
    try:
        course = Course.query.get(course_id)

        if not course:
            return jsonify({'message': 'Course not found'}), 404

        course_data = course.to_dict()

        # Add additional information
        course_data['favorites_count'] = Favorite.query.filter_by(
            course_id=course_id
        ).count()

        # Check if current user has saved this course
        current_user = get_current_user(request)
        if current_user:
            is_favorited = Favorite.query.filter_by(
                user_id=current_user.id,
                course_id=course_id
            ).first() is not None
            course_data['is_favorited'] = is_favorited

        return jsonify({
            'message': 'Course retrieved',
            'course': course_data
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@recommendation_bp.route('/search', methods=['GET'])
def search_courses():
    """Search courses by keyword"""
    try:
        query = request.args.get('q', '').strip()

        if not query or len(query) < 2:
            return jsonify({'message': 'Query too short'}), 400

        # Search in course names, descriptions, and categories
        courses = Course.query.filter(
            (Course.name.ilike(f'%{query}%')) |
            (Course.description.ilike(f'%{query}%')) |
            (Course.category.ilike(f'%{query}%'))
        ).limit(20).all()

        courses_data = [course.to_dict() for course in courses]

        return jsonify({
            'message': 'Search completed',
            'query': query,
            'courses': courses_data,
            'count': len(courses_data)
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@recommendation_bp.route('/categories', methods=['GET'])
def get_course_categories():
    """Get all course categories"""
    try:
        categories = db.session.query(Course.category).distinct().filter(
            Course.category != None
        ).all()

        category_list = [cat[0] for cat in categories if cat[0]]

        return jsonify({
            'message': 'Categories retrieved',
            'categories': category_list
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@recommendation_bp.route('/categories/<category>', methods=['GET'])
def get_courses_by_category(category):
    """Get courses by category"""
    try:
        courses = Course.query.filter_by(category=category).all()
        courses_data = [course.to_dict() for course in courses]

        return jsonify({
            'message': 'Courses retrieved',
            'category': category,
            'courses': courses_data,
            'count': len(courses_data)
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
