"""
Favorites routes that redirect to user routes
This file provides backward compatibility
"""

from flask import Blueprint
from routes.user_routes import add_favorite, remove_favorite, get_favorites

favorites_bp = Blueprint('favorites', __name__)

# Route the favorites endpoints


@favorites_bp.route('', methods=['GET'])
def list_favorites():
    return get_favorites()


@favorites_bp.route('', methods=['POST'])
def create_favorite():
    return add_favorite()


@favorites_bp.route('/<course_id>', methods=['DELETE'])
def delete_favorite(course_id):
    return remove_favorite(course_id)
