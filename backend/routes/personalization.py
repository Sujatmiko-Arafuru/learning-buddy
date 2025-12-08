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
    """Return map interest nodes from Learning_Path collection."""
    try:
        from db import db
        if db is None:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        # Use Learning_Path collection (contains actual learning paths)
        coll = db.get_collection('Learning_Path')
        docs = list(coll.find({}, {'_id': 0}))
        formatted = []
        for doc in docs:
            formatted.append({
                'id': doc.get('learning_path_id'),
                'name': doc.get('learning_path_name'),
                'summary': doc.get('summary', ''),
                'description': doc.get('description', ''),
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


@personalization_bp.route('/personalization/classify-answers', methods=['POST'])
def classify_interest_answers():
    """Classify interest answers and return recommended map interests."""
    try:
        from collections import Counter
        
        data = request.get_json(silent=True) or {}
        answers = data.get('answers', [])
        
        print(f"[DEBUG] Classify answers - Received answers: {answers}")
        
        if not isinstance(answers, list) or len(answers) == 0:
            return jsonify({'success': False, 'error': 'Jawaban tidak boleh kosong'}), 400
        
        # Count answers by category
        category_counts = Counter(answers)
        print(f"[DEBUG] Category counts: {dict(category_counts)}")
        
        # Map categories to learning path IDs
        category_to_lp_ids = {
            'Mobile Development': [2, 12, 10],
            'Artificial Intelligence': [1, 8, 11],
            'Cloud Computing': [6, 9],
            'Web Development': [3, 4, 7, 13]
        }
        
        # Get all map interests from Learning_Path collection
        from db import db
        if db is None:
            print("[ERROR] Database not connected")
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        # Get Learning_Path collection
        try:
            learning_paths_coll = db.get_collection('Learning_Path')
            all_learning_paths = list(learning_paths_coll.find({}, {'_id': 0}))
            print(f"[DEBUG] Found {len(all_learning_paths)} learning paths")
        except Exception as e:
            print(f"[ERROR] Failed to get Learning_Path collection: {e}")
            return jsonify({'success': False, 'error': f'Failed to load learning paths: {str(e)}'}), 500
        
        # Create a map of learning_path_id to map interest
        lp_id_to_map_interest = {}
        
        # Use Learning_Path collection as primary source
        for lp in all_learning_paths:
            lp_id = lp.get('learning_path_id')
            if lp_id is not None:
                lp_id_to_map_interest[lp_id] = {
                    'id': lp_id,
                    'name': lp.get('learning_path_name', ''),
                    'summary': lp.get('summary', ''),
                    'description': lp.get('description', ''),
                    'course_difficulty': lp.get('course_difficulty'),
                    'course_price': lp.get('course_price'),
                    'technologies': lp.get('technologies'),
                    'course_type': lp.get('course_type'),
                }
        
        print(f"[DEBUG] Created map with {len(lp_id_to_map_interest)} learning paths")
        
        # If no learning paths found, return error
        if len(lp_id_to_map_interest) == 0:
            return jsonify({
                'success': False,
                'error': 'Belum ada data Learning Path yang tersedia. Silakan hubungi administrator untuk mengimpor data.'
            }), 404
        
        # Calculate scores for each category
        category_scores = []
        for category, count in category_counts.items():
            lp_ids = category_to_lp_ids.get(category, [])
            map_interests = [lp_id_to_map_interest[lp_id] for lp_id in lp_ids if lp_id in lp_id_to_map_interest]
            category_scores.append({
                'category': category,
                'count': count,
                'map_interests': map_interests
            })
            print(f"[DEBUG] Category {category}: count={count}, map_interests={len(map_interests)}")
        
        # Sort by count (descending)
        category_scores.sort(key=lambda x: x['count'], reverse=True)
        
        # Get most suitable (top 2) and least suitable (bottom 2, excluding most suitable)
        most_suitable = category_scores[:2] if len(category_scores) >= 2 else category_scores
        if len(category_scores) > 2:
            least_suitable = category_scores[-2:]
        elif len(category_scores) == 2:
            # If only 2 categories, show the one with lower count as least suitable
            least_suitable = [category_scores[-1]]
        else:
            least_suitable = []
        
        # Flatten map interests from all categories (prioritize most suitable)
        recommended_map_interests = []
        for cat_score in category_scores:
            recommended_map_interests.extend(cat_score['map_interests'])
        
        # Remove duplicates based on id
        seen_ids = set()
        unique_map_interests = []
        for mi in recommended_map_interests:
            if mi['id'] not in seen_ids:
                seen_ids.add(mi['id'])
                unique_map_interests.append(mi)
        
        print(f"[DEBUG] Total unique map interests: {len(unique_map_interests)}")
        
        # If no map interests found, return all available map interests as fallback
        if len(unique_map_interests) == 0:
            print("[WARNING] No map interests found, using fallback")
            # Fallback: return all map interests sorted by id
            all_map_list = list(lp_id_to_map_interest.values())
            all_map_list.sort(key=lambda x: x.get('id', 0))
            unique_map_interests = all_map_list[:10]  # Limit to 10 to avoid too many options
        
        # Define the 4 main Map Interests
        MAP_INTERESTS = [
            {
                'id': 'web-development',
                'name': 'Web Development',
                'description': 'Membangun aplikasi web modern dengan teknologi front-end dan back-end',
                'category': 'Web Development'
            },
            {
                'id': 'artificial-intelligence',
                'name': 'Artificial Intelligence',
                'description': 'Mengembangkan sistem AI, machine learning, dan kecerdasan buatan',
                'category': 'Artificial Intelligence'
            },
            {
                'id': 'cloud-computing',
                'name': 'Cloud Computing',
                'description': 'Mengelola infrastruktur cloud, DevOps, dan sistem terdistribusi',
                'category': 'Cloud Computing'
            },
            {
                'id': 'mobile-development',
                'name': 'Mobile Development',
                'description': 'Membangun aplikasi mobile untuk Android, iOS, dan multiplatform',
                'category': 'Mobile Development'
            }
        ]
        
        # Update category_scores to include map_interest and learning_path_ids
        updated_category_scores = []
        for cat_score in category_scores:
            category = cat_score['category']
            # Find matching Map Interest
            map_interest = next((mi for mi in MAP_INTERESTS if mi['category'] == category), None)
            if map_interest:
                updated_category_scores.append({
                    'category': category,
                    'count': cat_score['count'],
                    'map_interest': map_interest,
                    'learning_path_ids': category_to_lp_ids.get(category, [])
                })
        
        # Update most_suitable and least_suitable
        updated_most_suitable = []
        for item in most_suitable:
            category = item['category']
            map_interest = next((mi for mi in MAP_INTERESTS if mi['category'] == category), None)
            if map_interest:
                updated_most_suitable.append({
                    'category': category,
                    'count': item['count'],
                    'map_interest': map_interest,
                    'learning_path_ids': category_to_lp_ids.get(category, [])
                })
        
        updated_least_suitable = []
        for item in least_suitable:
            category = item['category']
            map_interest = next((mi for mi in MAP_INTERESTS if mi['category'] == category), None)
            if map_interest:
                updated_least_suitable.append({
                    'category': category,
                    'count': item['count'],
                    'map_interest': map_interest,
                    'learning_path_ids': category_to_lp_ids.get(category, [])
                })
        
        result = {
            'success': True,
            'data': {
                'category_scores': updated_category_scores,
                'most_suitable': updated_most_suitable,
                'least_suitable': updated_least_suitable,
                'map_interests': MAP_INTERESTS  # Always return all 4 Map Interests
            }
        }
        
        print(f"[DEBUG] Returning result with {len(MAP_INTERESTS)} map interests")
        return jsonify(result), 200
        
    except RuntimeError as err:
        print(f"[ERROR] RuntimeError in classify_answers: {err}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        print(f"[ERROR] Exception in classify_answers: {err}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Gagal mengklasifikasikan jawaban: {str(err)}'}), 500


@personalization_bp.route('/personalization/current-interest', methods=['POST'])
def save_current_interest_answers():
    """Persist current interest answers and selected map interests, then return learning paths."""
    try:
        users_coll = _require_collection('users')
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        answers = data.get('answers', [])
        selected_map_interests = data.get('selected_map_interests', [])

        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        if not isinstance(answers, list) or len(answers) == 0:
            return jsonify({'success': False, 'error': 'Jawaban interest tidak boleh kosong'}), 400

        if not isinstance(selected_map_interests, list) or len(selected_map_interests) == 0:
            return jsonify({'success': False, 'error': 'Minimal satu Map Interest harus dipilih'}), 400

        if len(selected_map_interests) > 4:
            return jsonify({'success': False, 'error': 'Maksimal empat Map Interest yang dapat dipilih'}), 400

        # Map categories to learning path IDs
        category_to_lp_ids = {
            'Mobile Development': [2, 12, 10],
            'Artificial Intelligence': [1, 8, 11],
            'Cloud Computing': [6, 9],
            'Web Development': [3, 4, 7, 13]
        }
        
        # Get learning path IDs for selected map interests
        selected_categories = [mi.get('category') for mi in selected_map_interests if mi.get('category')]
        all_learning_path_ids = []
        for category in selected_categories:
            lp_ids = category_to_lp_ids.get(category, [])
            all_learning_path_ids.extend(lp_ids)
        
        # Remove duplicates
        all_learning_path_ids = list(set(all_learning_path_ids))
        
        # Get learning paths from database
        from db import db
        if db is None:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        learning_paths_coll = db.get_collection('Learning_Path')
        learning_paths = list(learning_paths_coll.find(
            {'learning_path_id': {'$in': all_learning_path_ids}},
            {'_id': 0}
        ))
        
        # Format learning paths
        formatted_learning_paths = []
        for lp in learning_paths:
            formatted_learning_paths.append({
                'id': lp.get('learning_path_id'),
                'name': lp.get('learning_path_name', ''),
                'summary': lp.get('summary', ''),
                'description': lp.get('description', ''),
                'course_difficulty': lp.get('course_difficulty'),
                'course_price': lp.get('course_price'),
                'technologies': lp.get('technologies'),
                'course_type': lp.get('course_type'),
            })

        update_doc = {
            'interest_assessment.current_interest_answers': answers,
            'preferences.map_interest_mode': 'guided',
            'preferences.map_interest_choices': selected_map_interests,
            'preferences.selected_learning_path_ids': all_learning_path_ids,
            'personalization_selected_at': datetime.utcnow().isoformat(),
        }

        result = users_coll.update_one({'email': email}, {'$set': update_doc})
        if result.matched_count == 0:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        return jsonify({
            'success': True,
            'message': 'Jawaban interest dan pilihan Map Interest tersimpan',
            'data': {
                'selected_map_interests': selected_map_interests,
                'learning_paths': formatted_learning_paths,
                'learning_path_ids': all_learning_path_ids
            }
        }), 200
    except RuntimeError as err:
        return jsonify({'success': False, 'error': str(err)}), 500
    except Exception as err:
        return jsonify({'success': False, 'error': str(err)}), 500

