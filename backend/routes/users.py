"""
Routes for user management
"""
from flask import Blueprint, jsonify, request
from db import collections
from datetime import datetime
import hashlib

users_bp = Blueprint('users', __name__)

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
        if collections['users']:
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
        if collections['users']:
            result = collections['users'].insert_one(user_doc)
            user_doc['_id'] = str(result.inserted_id)
        
        return jsonify({'success': True, 'data': user_doc}), 201
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    try:
        if collections['users']:
            from bson import ObjectId
            user = collections['users'].find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                return jsonify({'success': True, 'data': user}), 200
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@users_bp.route('/users/email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Get user by email"""
    try:
        if collections['users']:
            user = collections['users'].find_one({'email': email})
            if user:
                user['_id'] = str(user['_id'])
                return jsonify({'success': True, 'data': user}), 200
            return jsonify({'success': False, 'error': 'User not found'}), 404
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

