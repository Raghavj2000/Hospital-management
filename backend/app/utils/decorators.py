from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User

def role_required(*roles):
    """Decorator to check if user has required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)

            if not user:
                return jsonify({'error': 'User not found'}), 404

            if not user.is_active:
                return jsonify({'error': 'Account is inactive'}), 403

            if user.is_blacklisted:
                return jsonify({'error': 'Account is blacklisted'}), 403

            if user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def active_user_required(fn):
    """Decorator to check if user is active"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403

        if user.is_blacklisted:
            return jsonify({'error': 'Account is blacklisted'}), 403

        return fn(*args, **kwargs)
    return wrapper
