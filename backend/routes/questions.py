"""
Routes for questions (interest and tech questions)
"""
from flask import Blueprint, jsonify, request
from db import collections

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/questions/interest', methods=['GET'])
def get_interest_questions():
    """Get interest questions for onboarding"""
    try:
        if collections['current_interest_questions'] is not None:
            questions = list(collections['current_interest_questions'].find({}, {'_id': 0}))
            return jsonify({'success': True, 'data': questions}), 200
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@questions_bp.route('/questions/tech', methods=['GET'])
def get_tech_questions():
    """Get tech questions for skill assessment"""
    try:
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        
        query = {}
        if category:
            query['tech_category'] = category
        if difficulty:
            query['difficulty'] = difficulty
        
        if collections['current_tech_questions'] is not None:
            questions = list(collections['current_tech_questions'].find(query, {'_id': 0}))
            return jsonify({'success': True, 'data': questions}), 200
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

