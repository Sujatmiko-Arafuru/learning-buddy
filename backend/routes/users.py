"""
Routes for user management
"""
from flask import Blueprint, jsonify, request
from db import collections
from datetime import datetime
from bson import ObjectId
import secrets

users_bp = Blueprint('users', __name__)


def _get_json():
    data = request.get_json(silent=True)
    return data or {}


def _sanitize_user(user_doc):
    """Remove sensitive fields before sending user data to clients."""
    if not user_doc:
        return user_doc
    user_doc = dict(user_doc)
    user_doc.pop('password_hash', None)
    user_doc.pop('auth_token', None)
    if '_id' in user_doc:
        user_doc['_id'] = str(user_doc['_id'])
    return user_doc


@users_bp.route('/auth/register', methods=['POST'])
def register_user():
    """User registration endpoint with password hashing."""
    if collections['users'] is None:
        return jsonify({'success': False, 'error': 'Database not connected'}), 500

    data = _get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'success': False, 'error': 'Name, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400

    existing_user = collections['users'].find_one({'email': email})
    if existing_user:
        return jsonify({'success': False, 'error': 'User with this email already exists'}), 400

    user_doc = {
        'name': name,
        'email': email,
        'password': password,
        'created_at': datetime.utcnow().isoformat(),
        'onboarding_completed': False,
        'preferences': {},
        'current_learning_path': None,
        'skill_assessment': {},
        'last_login': None,
        'auth_token': None,
    }

    result = collections['users'].insert_one(user_doc)
    user_doc['_id'] = result.inserted_id

    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'data': _sanitize_user(user_doc),
    }), 201


@users_bp.route('/auth/login', methods=['POST'])
def login_user():
    """Authenticate user credentials and issue a session token."""
    if collections['users'] is None:
        return jsonify({'success': False, 'error': 'Database not connected'}), 500

    data = _get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400

    user = collections['users'].find_one({'email': email})
    if not user or user.get('password') != password:
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

    token = secrets.token_urlsafe(32)
    collections['users'].update_one(
        {'_id': user['_id']},
        {'$set': {'last_login': datetime.utcnow().isoformat(), 'auth_token': token}}
    )

    sanitized_user = _sanitize_user(user)
    sanitized_user['token'] = token

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': sanitized_user,
    }), 200

@users_bp.route('/users', methods=['POST'])
def create_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        if collections['users'] is not None:
            existing_user = collections['users'].find_one({'email': data['email']})
            if existing_user:
                return jsonify({'success': False, 'error': 'User with this email already exists'}), 400
        
        # Create user document
        user_doc = {
            'name': data['name'],
            'email': data['email'],
            'created_at': datetime.utcnow().isoformat(),
            'onboarding_completed': False,
            'preferences': data.get('preferences', {}),
            'current_learning_path': None,
            'skill_assessment': {}
        }
        
        # Insert user
        if collections['users'] is not None:
            result = collections['users'].insert_one(user_doc)
            user_doc['_id'] = str(result.inserted_id)
        
        return jsonify({'success': True, 'data': user_doc}), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        if collections['users'] is not None:
            user = collections['users'].find_one({'_id': ObjectId(user_id)})
            if user:
                return jsonify({'success': True, 'data': _sanitize_user(user)}), 200
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/users/email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Get user by email"""
    try:
        if collections['users'] is not None:
            user = collections['users'].find_one({'email': email})
            if user:
                return jsonify({'success': True, 'data': _sanitize_user(user)}), 200
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user preferences and onboarding status"""
    try:
        data = request.get_json()
        
        if collections['users'] is None:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        from bson import ObjectId
        query = {'_id': ObjectId(user_id)}
        
        # Build update document
        update_doc = {}
        if 'onboarding_completed' in data:
            update_doc['onboarding_completed'] = data['onboarding_completed']
        if 'preferences' in data:
            update_doc['preferences'] = data['preferences']
        if 'skill_assessment' in data:
            update_doc['skill_assessment'] = data['skill_assessment']
        if 'current_learning_path' in data:
            update_doc['current_learning_path'] = data['current_learning_path']
        
        if not update_doc:
            return jsonify({'success': False, 'error': 'No fields to update'}), 400
        
        result = collections['users'].update_one(query, {'$set': update_doc})
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Return updated user
        updated_user = collections['users'].find_one(query)
        
        return jsonify({'success': True, 'data': _sanitize_user(updated_user)}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

