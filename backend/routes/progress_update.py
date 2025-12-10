"""
Realtime progress update for tutorials/modules
(Separate from old progress.py to avoid conflicts)
"""

from flask import Blueprint, request, jsonify
from db import collections, db
from datetime import datetime

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

@progress_update_bp.route('/progress/material/complete', methods=['POST'])
def mark_material_complete():
    """Mark a material as completed"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required = ['email', 'course_name', 'tutorial_title']
        for f in required:
            if f not in data:
                print(f"[ERROR] Missing required field: {f}")
                return jsonify({'success': False, 'error': f'Missing: {f}'}), 400
        
        email = data['email']
        course_name = data['course_name']
        tutorial_title = data['tutorial_title']
        
        # Decode jika perlu (untuk konsistensi)
        import urllib.parse
        decoded_course_name = urllib.parse.unquote(course_name) if course_name else ""
        decoded_tutorial_title = urllib.parse.unquote(tutorial_title) if tutorial_title else ""
        
        print(f"[MATERIAL] Marking material as complete: {email} - {decoded_course_name} - {decoded_tutorial_title}")
        
        # Get or create material progress document
        if db is None:
            print("[ERROR] Database not connected")
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        try:
            material_progress_coll = db['material_progress']
        except Exception as e:
            print(f"[ERROR] Failed to get material_progress collection: {e}")
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        
        # Check if material already completed
        # Gunakan decoded values untuk konsistensi
        query = {
            'email': email,
            'course_name': decoded_course_name,
            'tutorial_title': decoded_tutorial_title
        }
        
        try:
            existing = material_progress_coll.find_one(query)
        except Exception as e:
            print(f"[ERROR] Failed to find existing material: {e}")
            return jsonify({'success': False, 'error': f'Database query error: {str(e)}'}), 500
        
        current_time = datetime.utcnow().isoformat()
        
        try:
            if existing:
                # Update existing record
                material_progress_coll.update_one(
                    query,
                    {
                        '$set': {
                            'is_completed': True,
                            'completed_at': current_time,
                            'last_updated': current_time
                        }
                    }
                )
                print(f"[MATERIAL] Updated existing material record")
            else:
                # Create new record
                material_progress_coll.insert_one({
                    'email': email,
                    'course_name': decoded_course_name,
                    'tutorial_title': decoded_tutorial_title,
                    'is_completed': True,
                    'completed_at': current_time,
                    'last_updated': current_time,
                    'read_count': 1
                })
                print(f"[MATERIAL] Created new material record")
        except Exception as e:
            print(f"[ERROR] Failed to save material progress: {e}")
            return jsonify({'success': False, 'error': f'Failed to save progress: {str(e)}'}), 500
        
        # Update course progress (count completed materials)
        # Use LP+Course collection to count total materials (excluding exam)
        total_materials = 0
        if db is not None:
            try:
                lp_course_coll = db.get_collection('LP+Course')
                if lp_course_coll is not None:
                    # Count total non-exam tutorials in this course
                    # Exclude "Ujian Akhir" from count
                    total_materials = lp_course_coll.count_documents({
                        'course_name': decoded_course_name,
                        'tutorial_title': {'$ne': 'Ujian Akhir'}
                    })
            except Exception as e:
                print(f"[WARNING] Failed to count total materials: {e}")
                total_materials = 0
        
        # Count completed materials for this user
        try:
            completed_count = material_progress_coll.count_documents({
                'email': email,
                'course_name': decoded_course_name,
                'is_completed': True
            })
            print(f"[MATERIAL] Completed count: {completed_count}/{total_materials}")
        except Exception as e:
            print(f"[WARNING] Failed to count completed materials: {e}")
            completed_count = 1  # At least this one is completed
        
        # Update student_progress
        progress_coll = collections.get('student_progress')
        if progress_coll is not None:
                progress_query = {
                    'email': email,
                    'course_name': decoded_course_name
                }
                
                # Get current progress
                current_progress = progress_coll.find_one(progress_query)
                
                update_doc = {
                    'email': email,
                    'course_name': decoded_course_name,
                    'completed_tutorials': completed_count,
                    'active_tutorials': max(0, total_materials - completed_count)
                }
                
                # Check if all materials completed (excluding exam)
                if completed_count >= total_materials:
                    update_doc['is_graduated'] = 0  # Not graduated until exam passed
                    update_doc['all_materials_completed'] = True
                else:
                    update_doc['all_materials_completed'] = False
                
                try:
                    progress_coll.update_one(
                        progress_query,
                        {'$set': update_doc},
                        upsert=True
                    )
                    print(f"[MATERIAL] Updated student progress")
                except Exception as e:
                    print(f"[WARNING] Failed to update student progress: {e}")
                    # Don't fail the whole request if progress update fails
        
        # Get updated material status
        try:
            updated = material_progress_coll.find_one(query, {'_id': 0})
        except Exception as e:
            print(f"[WARNING] Failed to get updated status: {e}")
            updated = None
        
        print(f"[MATERIAL] Successfully marked material as complete")
        return jsonify({
            'success': True,
            'data': updated,
            'message': 'Material marked as completed'
        }), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Exception in mark_material_complete: {e}")
        print(f"[ERROR] Traceback: {error_trace}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@progress_update_bp.route('/progress/material/status', methods=['GET'])
def get_material_status():
    """Get completion status for all materials in a course"""
    try:
        email = request.args.get('email')
        course_name = request.args.get('course_name')
        
        if not email or not course_name:
            return jsonify({'success': False, 'error': 'email and course_name are required'}), 400
        
        if db is None:
            return jsonify({'success': True, 'data': {}}), 200
        
        material_progress_coll = db['material_progress']
        
        # Get all completed materials for this user and course
        completed_materials = material_progress_coll.find(
            {
                'email': email,
                'course_name': course_name,
                'is_completed': True
            },
            {'_id': 0, 'tutorial_title': 1, 'completed_at': 1}
        )
        
        # Convert to dictionary for easy lookup
        status_map = {}
        for material in completed_materials:
            status_map[material.get('tutorial_title', '')] = {
                'is_completed': True,
                'completed_at': material.get('completed_at')
            }
        
        return jsonify({
            'success': True,
            'data': status_map
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_update_bp.route('/progress/material/check-all-completed', methods=['GET'])
def check_all_materials_completed():
    """Check if all materials in a course are completed (excluding exam)"""
    try:
        email = request.args.get('email')
        course_name = request.args.get('course_name')
        
        if not email or not course_name:
            return jsonify({'success': False, 'error': 'email and course_name are required'}), 400
        
        # Get total materials (excluding exam)
        if db is None:
            return jsonify({
                'success': True,
                'data': {
                    'all_completed': False,
                    'total_materials': 0,
                    'completed_materials': 0
                }
            }), 200
        
        # Use LP+Course collection to count total materials (excluding exam)
        lp_course_coll = db.get_collection('LP+Course')
        if lp_course_coll is None:
            return jsonify({
                'success': True,
                'data': {
                    'all_completed': False,
                    'total_materials': 0,
                    'completed_materials': 0
                }
            }), 200
        
        # Decode course_name jika perlu
        import urllib.parse
        decoded_course_name = urllib.parse.unquote(course_name)
        
        print(f"[MATERIAL CHECK] Checking completion for: {email} - {decoded_course_name}")
        print(f"[MATERIAL CHECK] Original course_name: {course_name}")
        
        # Count total non-exam tutorials (exclude "Ujian Akhir")
        # Gunakan distinct untuk mendapatkan unique tutorial titles
        all_tutorials = []
        try:
            # Method 1: Gunakan distinct untuk mendapatkan unique tutorial titles
            all_tutorials = lp_course_coll.distinct('tutorial_title', {
                'course_name': decoded_course_name,
                'tutorial_title': {'$ne': 'Ujian Akhir'}
            })
            total_materials = len(all_tutorials)
            print(f"[MATERIAL CHECK] Total materials (distinct): {total_materials}")
            print(f"[MATERIAL CHECK] All tutorial titles ({len(all_tutorials)}): {sorted(all_tutorials)}")
        except Exception as e:
            print(f"[ERROR] Failed to get distinct tutorials: {e}")
            # Method 2: Fallback - ambil semua dan buat unique
            try:
                all_courses_data = list(lp_course_coll.find({
                    'course_name': decoded_course_name,
                    'tutorial_title': {'$ne': 'Ujian Akhir'}
                }, {'_id': 0, 'tutorial_title': 1}))
                all_tutorials = list(set([c.get('tutorial_title') for c in all_courses_data if c.get('tutorial_title')]))
                total_materials = len(all_tutorials)
                print(f"[MATERIAL CHECK] Total materials (manual distinct): {total_materials}")
                print(f"[MATERIAL CHECK] All tutorial titles ({len(all_tutorials)}): {sorted(all_tutorials)}")
            except Exception as e2:
                print(f"[ERROR] Fallback also failed: {e2}")
                total_materials = 0
        
        # Count completed materials dari material_progress
        # Coba dengan beberapa variasi course_name untuk memastikan match
        material_progress_coll = db['material_progress']
        completed_count = 0
        completed_tutorial_titles = []
        
        if material_progress_coll is not None:
            try:
                # Coba dengan decoded_course_name dulu
                completed_materials = list(material_progress_coll.find({
                    'email': email,
                    'course_name': decoded_course_name,
                    'is_completed': True
                }, {'_id': 0, 'tutorial_title': 1, 'course_name': 1}))
                
                # Jika tidak ada hasil, coba dengan course_name asli
                if len(completed_materials) == 0:
                    completed_materials = list(material_progress_coll.find({
                        'email': email,
                        'course_name': course_name,
                        'is_completed': True
                    }, {'_id': 0, 'tutorial_title': 1, 'course_name': 1}))
                
                completed_tutorial_titles = [m.get('tutorial_title') for m in completed_materials if m.get('tutorial_title')]
                # Gunakan set untuk menghindari duplikasi
                completed_tutorial_titles = list(set(completed_tutorial_titles))
                completed_count = len(completed_tutorial_titles)
                
                print(f"[MATERIAL CHECK] Completed materials: {completed_count}")
                print(f"[MATERIAL CHECK] Completed tutorial titles ({len(completed_tutorial_titles)}): {sorted(completed_tutorial_titles)}")
            except Exception as e:
                print(f"[ERROR] Failed to count completed materials: {e}")
                import traceback
                traceback.print_exc()
                completed_count = 0
        
        # Check if all materials are completed
        # Pastikan semua tutorial titles yang ada di total juga ada di completed
        if total_materials > 0 and len(all_tutorials) > 0:
            # Normalize tutorial titles (strip whitespace, case insensitive comparison)
            def normalize_title(title):
                if not title:
                    return ""
                return str(title).strip()
            
            # Convert to normalized sets for comparison
            all_tutorials_set = set(normalize_title(t) for t in all_tutorials if normalize_title(t))
            completed_tutorials_set = set(normalize_title(t) for t in completed_tutorial_titles if normalize_title(t))
            
            missing_tutorials = all_tutorials_set - completed_tutorials_set
            if missing_tutorials:
                print(f"[MATERIAL CHECK] Missing tutorials ({len(missing_tutorials)}): {sorted(missing_tutorials)}")
            else:
                print(f"[MATERIAL CHECK] All tutorials completed! ✓")
            
            # All completed jika tidak ada yang missing DAN completed_count >= total_materials
            all_completed = len(missing_tutorials) == 0 and completed_count >= total_materials
            
            print(f"[MATERIAL CHECK] Comparison:")
            print(f"[MATERIAL CHECK]   Total unique tutorials: {len(all_tutorials_set)}")
            print(f"[MATERIAL CHECK]   Completed unique tutorials: {len(completed_tutorials_set)}")
            print(f"[MATERIAL CHECK]   Missing: {len(missing_tutorials)}")
            print(f"[MATERIAL CHECK]   All completed: {all_completed}")
        else:
            all_completed = False
            print(f"[MATERIAL CHECK] Cannot check: total_materials={total_materials}, all_tutorials={len(all_tutorials) if 'all_tutorials' in locals() else 0}")
        
        print(f"[MATERIAL CHECK] ========================================")
        print(f"[MATERIAL CHECK] Total materials: {total_materials}")
        print(f"[MATERIAL CHECK] Completed materials: {completed_count}")
        print(f"[MATERIAL CHECK] All completed: {all_completed}")
        print(f"[MATERIAL CHECK] ========================================")
        
        return jsonify({
            'success': True,
            'data': {
                'all_completed': all_completed,
                'total_materials': total_materials,
                'completed_materials': completed_count,
                'remaining_materials': max(0, total_materials - completed_count)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_update_bp.route('/progress/material/track-learning', methods=['POST'])
def track_learning_behavior():
    """Track learning behavior for ML analysis"""
    try:
        data = request.get_json()
        
        required = ['email', 'course_name', 'tutorial_title', 'action']
        for f in required:
            if f not in data:
                return jsonify({'success': False, 'error': f'Missing: {f}'}), 400
        
        email = data['email']
        course_name = data['course_name']
        tutorial_title = data['tutorial_title']
        action = data['action']  # 'start_reading', 'complete', 'revisit', etc.
        
        # Get or create learning behavior collection
        if db is None:
            return jsonify({'success': False, 'error': 'Database not connected'}), 500
        
        learning_behavior_coll = db['learning_behavior']
        
        current_time = datetime.utcnow().isoformat()
        
        # Log learning behavior
        behavior_log = {
            'email': email,
            'course_name': course_name,
            'tutorial_title': tutorial_title,
            'action': action,
            'timestamp': current_time,
            'metadata': data.get('metadata', {})  # Additional data like time_spent, scroll_depth, etc.
        }
        
        learning_behavior_coll.insert_one(behavior_log)
        
        return jsonify({
            'success': True,
            'message': 'Learning behavior tracked successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
