"""
Routes for personalization flow (map interest selection & current interest answers)
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from db import collections

personalization_bp = Blueprint('personalization', __name__)


def _require_collection(name: str):
    coll = collections.get(name)
    if coll is None:
        raise RuntimeError('Database not connected')
    return coll


@personalization_bp.route('/personalization/map-interests', methods=['GET'])
def get_map_interests():
    """Return map interest nodes from learning_path_answers collection."""
    try:
        coll = _require_collection('learning_path_answers')
        docs = list(coll.find({}, {'_id': 0}))
        formatted = []
        for doc in docs:
            formatted.append({
                'id': doc.get('id'),
                'name': doc.get('name'),
                'summary': doc.get('summary'),
                'description': doc.get('description'),
                'course_difficulty': doc.get('course_difficulty'),
                'course_price': doc.get('course_price'),
                'technologies': doc.get('technologies'),
                'course_type': doc.get('course_type'),
            })
        return jsonify({'success': True, 'data': formatted}), 200
    except RuntimeError as err:
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        return jsonify({'success': False, 'error': str(err)}), 500


@personalization_bp.route('/personalization/map-interests/select', methods=['POST'])
def save_map_interest_selection():
    """Persist user selection when choosing their own learning path."""
    try:
        users_coll = _require_collection('users')
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        selections = data.get('selections', [])

        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        if not isinstance(selections, list) or len(selections) == 0:
            return jsonify({'success': False, 'error': 'Minimal satu Map Interest harus dipilih'}), 400

        update_doc = {
            'preferences.map_interest_mode': 'manual',
            'preferences.map_interest_choices': selections,
            'personalization_selected_at': datetime.utcnow().isoformat(),
        }

        result = users_coll.update_one({'email': email}, {'$set': update_doc})
        if result.matched_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        return jsonify({'success': True, 'message': 'Pilihan Map Interest tersimpan'}), 200
    except RuntimeError as err:
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        return jsonify({'success': False, 'error': str(err)}), 500


@personalization_bp.route('/personalization/current-interest', methods=['POST'])
def save_current_interest_answers():
    """Persist current interest answers for users who need guidance."""
    try:
        users_coll = _require_collection('users')
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        answers = data.get('answers', [])

        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        if not isinstance(answers, list) or len(answers) == 0:
            return jsonify({'success': False, 'error': 'Jawaban interest tidak boleh kosong'}), 400

        update_doc = {
            'interest_assessment.current_interest_answers': answers,
            'preferences.map_interest_mode': 'guided',
            'personalization_selected_at': datetime.utcnow().isoformat(),
        }

        result = users_coll.update_one({'email': email}, {'$set': update_doc})
        if result.matched_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        return jsonify({'success': True, 'message': 'Jawaban interest tersimpan'}), 200
    except RuntimeError as err:
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        return jsonify({'success': False, 'error': str(err)}), 500

