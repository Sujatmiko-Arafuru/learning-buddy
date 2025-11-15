"""
Routes for course recommendations
"""
from flask import Blueprint, jsonify, request
from services.recommender import RecommenderService
from db import collections

recommendation_bp = Blueprint('recommendation', __name__)
recommender = RecommenderService()

@recommendation_bp.route('/recommendation', methods=['GET'])
def get_recommendation():
    """Get personalized course recommendations for a user"""
    user_id = request.args.get('user_id')
    email = request.args.get('email')
    
    if not user_id and not email:
        return jsonify({'success': False, 'error': 'user_id or email required'}), 400
    
    try:
        # Get user data
        query = {}
        if user_id:
            from bson import ObjectId
            query['_id'] = ObjectId(user_id)
        elif email:
            query['email'] = email
        
        user = None
        if collections['users']:
            user = collections['users'].find_one(query)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get user progress
        user_progress = []
        if collections['student_progress']:
            user_progress = list(collections['student_progress'].find(
                {'email': user.get('email')},
                {'_id': 0}
            ))
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_email=user.get('email'),
            user_progress=user_progress,
            user_preferences=user.get('preferences', {})
        )
        
        return jsonify({
            'success': True,
            'data': recommendations
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@recommendation_bp.route('/recommendation/onboarding', methods=['POST'])
def get_onboarding_recommendation():
    """Get recommendations based on onboarding answers"""
    try:
        data = request.get_json()
        
        # Extract answers from onboarding
        interest_answers = data.get('interest_answers', [])
        tech_answers = data.get('tech_answers', [])
        
        # Get recommendations based on onboarding
        recommendations = recommender.get_onboarding_recommendations(
            interest_answers=interest_answers,
            tech_answers=tech_answers
        )
        
        return jsonify({
            'success': True,
            'data': recommendations
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

