"""
User Routes for CareerWays
"""

from flask import Blueprint, request, jsonify
from app import db
from models import User, Favorite, Course
from routes.auth_routes import verify_token

user_bp = Blueprint('user', __name__)


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


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        user_data = current_user.to_dict()

        # Add additional stats
        user_data['assessments_count'] = len(current_user.assessments)
        user_data['favorites_count'] = len(current_user.favorites)

        return jsonify({
            'message': 'Profile retrieved',
            'user': user_data
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        data = request.get_json()

        # Update name if provided
        if 'name' in data:
            name = data['name'].strip()
            if len(name) > 0:
                current_user.name = name

        # Update email if provided (check for uniqueness)
        if 'email' in data:
            email = data['email'].strip().lower()
            if email != current_user.email:
                if User.query.filter_by(email=email).first():
                    return jsonify({'message': 'Email already in use'}), 409
                current_user.email = email

        db.session.commit()

        return jsonify({
            'message': 'Profile updated',
            'user': current_user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@user_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        data = request.get_json()

        if not all(k in data for k in ['old_password', 'new_password']):
            return jsonify({'message': 'Missing required fields'}), 400

        # Verify old password
        if not current_user.check_password(data['old_password']):
            return jsonify({'message': 'Invalid current password'}), 401

        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'message': 'New password must be at least 6 characters'}), 400

        # Update password
        current_user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Password updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@user_bp.route('/favorites', methods=['GET'])
def get_favorites():
    """Get user favorite courses"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        favorites = Favorite.query.filter_by(user_id=current_user.id).all()

        favorites_data = []
        for fav in favorites:
            course = fav.course
            if course:
                course_data = course.to_dict()
                course_data['saved_at'] = fav.created_at.isoformat()
                course_data['priority'] = fav.priority
                course_data['id'] = fav.id  # Use favorite id for removal
                favorites_data.append(course_data)

        return jsonify({
            'message': 'Favorites retrieved',
            'favorites': favorites_data,
            'count': len(favorites_data)
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

# This endpoint is also used in assessment routes


@user_bp.route('/favorites', methods=['POST'])
def add_favorite():
    """Add course to favorites"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        data = request.get_json()

        if 'course_id' not in data:
            return jsonify({'message': 'Missing course_id'}), 400

        course_id = data['course_id']

        # Check if course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'message': 'Course not found'}), 404

        # Check if already favorited
        existing = Favorite.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()

        if existing:
            return jsonify({'message': 'Course already in favorites'}), 409

        # Get priority from request (default to 'saved')
        priority = data.get('priority', 'saved')
        
        # Validate priority value
        valid_priorities = ['first_choice', 'second_choice', 'saved']
        if priority not in valid_priorities:
            priority = 'saved'

        # Add to favorites with priority
        favorite = Favorite(
            user_id=current_user.id, 
            course_id=course_id,
            priority=priority
        )
        db.session.add(favorite)
        db.session.commit()

        return jsonify({'message': 'Course added to favorites'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@user_bp.route('/favorites/<course_id>', methods=['DELETE'])
def remove_favorite(course_id):
    """Remove course from favorites"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()

        if not favorite:
            return jsonify({'message': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({'message': 'Course removed from favorites'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500


@user_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        assessments_count = len(current_user.assessments)
        favorites_count = len(current_user.favorites)

        # Calculate average match score
        average_match_score = 0
        if current_user.assessments:
            total_score = sum(
                a.overall_match_score for a in current_user.assessments if a.overall_match_score)
            average_match_score = total_score / len(current_user.assessments)

        return jsonify({
            'message': 'Statistics retrieved',
            'stats': {
                'assessments_completed': assessments_count,
                'favorite_courses': favorites_count,
                'average_match_score': round(average_match_score, 2)
            }
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500


@user_bp.route('/delete-account', methods=['DELETE'])
def delete_account():
    """Delete user account"""
    try:
        current_user = get_current_user(request)

        if not current_user:
            return jsonify({'message': 'Unauthorized'}), 401

        data = request.get_json() or {}

        # Verify password before deletion
        if 'password' not in data or not current_user.check_password(data['password']):
            return jsonify({'message': 'Invalid password'}), 401

        user_id = current_user.id

        db.session.delete(current_user)
        db.session.commit()

        return jsonify({'message': 'Account deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500
