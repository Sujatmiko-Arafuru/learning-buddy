"""
Realtime progress update for tutorials/modules
(Separate from old progress.py to avoid conflicts)
"""

from flask import Blueprint, request, jsonify
from db import collections

progress_update_bp = Blueprint('progress_update', __name__)

@progress_update_bp.route('/progress/update-realtime', methods=['POST'])
def update_progress_realtime():
    """Realtime update when user finishes a tutorial"""
    try:
        data = request.get_json()

        required = ['email', 'course_name', 'completed_tutorials', 'active_tutorials']
        for f in required:
            if f not in data:
                return jsonify({'success': False, 'error': f'Missing: {f}'}), 400

        email = data['email']
        course = data['course_name']
        completed = int(data['completed_tutorials'])
        active = int(data['active_tutorials'])

        # Hitung total tutorial
        total = completed + active

        # Tentukan apakah course sudah selesai
        is_graduated = 1 if completed > 0 and completed == total else 0

        query = {
            'email': email,
            'course_name': course
        }

        update_doc = {
            'email': email,
            'course_name': course,
            'completed_tutorials': completed,
            'active_tutorials': active,
            'is_graduated': is_graduated
        }

        collections['student_progress'].update_one(
            query,
            {'$set': update_doc},
            upsert=True
        )

        updated = collections['student_progress'].find_one(query, {'_id': 0})

        return jsonify({'success': True, 'data': updated}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
