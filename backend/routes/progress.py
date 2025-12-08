"""
Routes for student progress tracking
"""
from flask import Blueprint, jsonify, request
from db import collections

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/progress', methods=['GET'])
def get_progress():
    """Get progress for a user"""
    user_id = request.args.get('user_id')
    email = request.args.get('email')
    
    if not user_id and not email:
        return jsonify({'success': False, 'error': 'user_id or email required'}), 400
    
    try:
        query = {}
        if user_id:
            from bson import ObjectId
            query['_id'] = ObjectId(user_id)
        elif email:
            query['email'] = email
        
        # Get user progress from student_progress collection
        if collections['student_progress'] is not None:
            progress_data = list(collections['student_progress'].find(
                query if email else {},
                {'_id': 0}
            ))
            
            # Also get user info if available
            user_info = None
            if collections['users'] is not None:
                user = collections['users'].find_one(query)
                if user:
                    user_info = {
                        'user_id': str(user['_id']),
                        'name': user.get('name'),
                        'email': user.get('email'),
                        'onboarding_completed': user.get('onboarding_completed', False)
                    }
            
            return jsonify({
                'success': True,
                'data': {
                    'user': user_info,
                    'progress': progress_data
                }
            }), 200
        
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_bp.route('/progress/stats', methods=['GET'])
def get_progress_stats():
    """Get progress statistics for a user"""
    email = request.args.get('email')
    
    if not email:
        return jsonify({'success': False, 'error': 'email required'}), 400
    
    try:
        if collections['student_progress'] is not None:
            # Get all progress for this user
            progress_list = list(collections['student_progress'].find(
                {'email': email},
                {'_id': 0}
            ))
            
            # Calculate statistics
            total_courses = len(progress_list)
            completed_courses = sum(1 for p in progress_list if p.get('is_graduated', 0) == 1)
            total_tutorials = sum(p.get('active_tutorials', 0) + p.get('completed_tutorials', 0) for p in progress_list)
            completed_tutorials = sum(p.get('completed_tutorials', 0) for p in progress_list)
            
            stats = {
                'total_courses': total_courses,
                'completed_courses': completed_courses,
                'in_progress_courses': total_courses - completed_courses,
                'total_tutorials': total_tutorials,
                'completed_tutorials': completed_tutorials,
                'completion_rate': round((completed_courses / total_courses * 100) if total_courses > 0 else 0, 2)
            }
            
            return jsonify({'success': True, 'data': stats}), 200
        
        return jsonify({'success': False, 'error': 'Database not connected'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_bp.route('/progress/update', methods=['POST'])
def update_progress():
    """Update student progress"""
    try:
        data = request.get_json()
        
        required_fields = ['email', 'course_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        if collections['student_progress'] is None:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        # Find existing progress or create new
        query = {
            'email': data['email'],
            'course_name': data['course_name']
        }
        
        update_doc = {
            'email': data['email'],
            'course_name': data['course_name']
        }
        
        if 'completed_tutorials' in data:
            update_doc['completed_tutorials'] = data['completed_tutorials']
        if 'active_tutorials' in data:
            update_doc['active_tutorials'] = data['active_tutorials']
        if 'is_graduated' in data:
            update_doc['is_graduated'] = data['is_graduated']
        if 'exam_score' in data:
            update_doc['exam_score'] = data['exam_score']
        
        # Upsert progress
        result = collections['student_progress'].update_one(
            query,
            {'$set': update_doc},
            upsert=True
        )
        
        # Get updated progress
        updated_progress = collections['student_progress'].find_one(query, {'_id': 0})
        
        return jsonify({
            'success': True,
            'data': updated_progress
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

